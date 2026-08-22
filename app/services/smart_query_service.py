import os
import uuid
import json
import time
import chromadb
from typing import List, Dict
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from google import genai

from app.models.new_arch import DocumentSection, DocumentChunk

# =====================================================================
# 1. AI Output Schema (Strict & Simple)
# =====================================================================
class RoutingDecision(BaseModel):
    target_section_ids: List[str] = Field(
        description="The exact list of string UUIDs for the sections containing the answer."
    )
    retrieval_mode: str = Field(
        default="sniper",
        description="Must be 'sniper' for specific facts/numbers/single-rows, or 'full_section' for broad explanations, full procedures, or complete tables."
    )
    routing_reasoning: str = Field(
        description="A brief explanation of why these specific sections and retrieval mode were chosen."
    )

# =====================================================================
# 2. The Smart Query Engine (Option 3: Hierarchical Vector Search)
# =====================================================================
def execute_smart_routing(
    user_prompt: str, 
    workspace_id: uuid.UUID, 
    db: Session,
    document_ids: List[uuid.UUID] = None
) -> List[str]:
    
    gemini_key = os.getenv("INTELLIGENCE_LAYER_API_KEY") or os.getenv("GEMINI_API_KEY")
    if not gemini_key:
        raise ValueError("CRITICAL: API key for Smart Router AI is missing.")
        
    client = genai.Client(api_key=gemini_key)

    # =====================================================================
    # 🟢 STEP 1: VECTOR SEARCH FILTER (ChromaDB gets the Top 15)
    # =====================================================================
    CHROMA_HOST = os.getenv("CHROMA_HOST")
    CHROMA_TOKEN = os.getenv("CHROMA_TOKEN")
    chroma_client = chromadb.HttpClient(
        host=str(CHROMA_HOST).strip().rstrip("/"),
        headers={"Authorization": f"Bearer {CHROMA_TOKEN}"} if CHROMA_TOKEN else None
    )
    
    nav_collection = chroma_client.get_or_create_collection(
        name="navigation_index_cards",
        metadata={"hnsw:space": "cosine"}
    )

    print("🔍 Embedding user question for Navigation Search...")
    try:
        # 1. Turn the question into a mathematical vector
        query_vector_resp = client.models.embed_content(
            model="models/gemini-embedding-001",
            contents=user_prompt
        )
        query_vector = query_vector_resp.embeddings[0].values

        # 2. Setup the Workspace Filter
        # 2. Setup the Workspace Filter (Fixed for ChromaDB Strict Syntax)
        if document_ids:
            where_filter = {
                "$and": [
                    {"workspace_id": str(workspace_id)},
                    {"document_id": {"$in": [str(d) for d in document_ids]}}
                ]
            }
        else:
            where_filter = {"workspace_id": str(workspace_id)}

        # 3. Pull strictly the Top 15 best semantic matches
        chroma_results = nav_collection.query(
            query_embeddings=[query_vector],
            n_results=15,
            where=where_filter
        )
        
        top_section_ids = chroma_results["ids"][0] if chroma_results["ids"] else []
    except Exception as e:
        print(f"❌ Navigation Vector Search failed: {e}")
        return []

    if not top_section_ids:
        print("⚠️ No relevant index cards found in ChromaDB.")
        return []

    # =====================================================================
    # 🟢 STEP 2: BUILD THE MINI-CATALOG & ASK GEMINI
    # =====================================================================
    # Fetch full details from Postgres ONLY for the 15 IDs Chroma found
    available_sections = db.query(DocumentSection).filter(
        DocumentSection.id.in_(top_section_ids)
    ).all()
    
    index_cards = []
    for sec in available_sections:
        hint = sec.chunking_strategy_hint or {}
        snippet = hint.get("normalized_text", "")[:150]
        
        index_cards.append({
            "section_id": str(sec.id),
            "path": sec.parent_path,
            "title": sec.title,
            "type": sec.content_type,
            "summary": sec.semantic_summary,
            "entities": sec.key_entities,   
            "data_preview": snippet          
        })

    system_instruction = (
        "You are the Smart Query Router for AgentPulse.\n"
        "MISSION:\n"
        "Read the user's question and review the provided Document Index Catalog.\n"
        "Select ONLY the `section_id`s that semantically match the user's intent. "
        "Use the `path`, `summary`, `entities`, and `data_preview` to determine relevance. If the user asks for a broad overview, prioritize sections with `type: master_scheme_table`.\n\n"
        "RETRIEVAL MODE RULES:\n"
        "- Use 'sniper' if the user asks for a specific fact, definition, number, or a single row of data.\n"
        "- Use 'full_section' if the user asks for a complete list, a full procedure, an entire timetable, or a broad summary.\n\n"
        "OUTPUT EXACT JSON matching this schema:\n"
        "{\"target_section_ids\": [\"uuid-string\"], \"retrieval_mode\": \"sniper or full_section\", \"routing_reasoning\": \"string\"}"
    )

    prompt = (
        f"USER QUESTION: \"{user_prompt}\"\n\n"
        f"DOCUMENT INDEX CATALOG:\n"
        f"{json.dumps(index_cards, indent=2)}"
    )

    print(f"\n{'='*60}")
    print("🧠 [TRANSPARENCY] SMART ROUTER PROMPT (What the Router sees)")
    print(json.dumps(index_cards, indent=2))
    print(f"{'='*60}\n")

    print(f"🧠 Routing Query through Smart Navigation AI (Scanning {len(index_cards)} Filtered Index Cards)...")
    
    # 🟢 THE FIX: 3-Attempt Retry Loop for Google API 503/429 Errors
    max_retries = 3
    response = None
    for attempt in range(max_retries):
        try:
            response = client.models.generate_content(
                model="gemini-3.1-flash-lite", 
                contents=prompt,
                config={
                    "system_instruction": system_instruction,
                    "response_mime_type": "application/json",
                    "temperature": 0.0
                }
            )
            break  # Break out if successful
        except Exception as e:
            error_str = str(e)
            if ("503" in error_str or "429" in error_str) and attempt < max_retries - 1:
                sleep_time = (attempt + 1) * 3
                print(f"⚠️ Google API busy ({error_str[:30]}). Retrying in {sleep_time} seconds...")
                time.sleep(sleep_time)
            else:
                print(f"❌ Smart Router LLM call permanently failed: {e}")
                return []

    if not response:
        return []

    if hasattr(response, "usage_metadata") and response.usage_metadata:
        meta = response.usage_metadata
        print(f"📊 [SMART ROUTER TOKEN USAGE]")
        print(f"   - Prompt Tokens     : {getattr(meta, 'prompt_token_count', 0)}")
        print(f"   - Completion Tokens : {getattr(meta, 'candidates_token_count', 0)}")
        print(f"   - Total Tokens      : {getattr(meta, 'total_token_count', 0)}")

    try:
        decision = RoutingDecision.model_validate_json(response.text)
        print(f"✅ Router AI Decision: {decision.routing_reasoning}")
        print(f"🎯 Selected Sections: {len(decision.target_section_ids)}")
    except Exception as e:
        print(f"❌ Failed to parse Router AI output: {e}")
        return []

    if not decision.target_section_ids:
        return []

   # =====================================================================
    # 🟢 PHASE 3: DYNAMIC RETRIEVAL (Sniper vs. Full Section)
    # =====================================================================
    print(f"🎯 Activating {decision.retrieval_mode.upper()} Mode...")
    
    final_vector_ids = []

    if decision.retrieval_mode == "full_section":
        # Broad Search: Pull EVERY chunk from the AI's selected sections
        target_chunks = db.query(DocumentChunk).filter(
            DocumentChunk.section_id.in_(decision.target_section_ids),
            DocumentChunk.workspace_id == workspace_id
        ).order_by(DocumentChunk.sequence_number.asc()).all()
        
        final_vector_ids = [chunk.chroma_vector_id for chunk in target_chunks]
        print(f"📡 Retrieved {len(final_vector_ids)} chunks for Full Section reading.")
        
    else:
        # 🟢 THE SNIPER FIX: Unleash the Vector DB! 
        # Do not restrict by section_id. Let Chroma mathematically search the entire document!
        chunk_collection = chroma_client.get_or_create_collection(
            name="rag_enterprise_vectors_v1",
            metadata={"hnsw:space": "cosine"}
        )
        
        if document_ids:
            where_chunk_filter = {
                "$and": [
                    {"workspace_id": str(workspace_id)},
                    {"document_id": {"$in": [str(d) for d in document_ids]}}
                ]
            }
        else:
            where_chunk_filter = {"workspace_id": str(workspace_id)}

        try:
            # Pull the top 10 best matching chunks from ANYWHERE in the document
            chunk_results = chunk_collection.query(
                query_embeddings=[query_vector],
                n_results=10,  
                where=where_chunk_filter
            )
            final_vector_ids = chunk_results["ids"][0] if chunk_results["ids"] else []
        except Exception as e:
            print(f"❌ Chunk-level Vector Search failed: {e}")
            final_vector_ids = []
            
        print(f"📡 Sniper resolved {len(final_vector_ids)} highly-targeted vector chunks across all sections.")

    return final_vector_ids