import os
import uuid
import json
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
    routing_reasoning: str = Field(
        description="A brief explanation of why these specific sections were chosen based on their semantic summaries."
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
        where_filter = {"workspace_id": str(workspace_id)}
        if document_ids:
            if len(document_ids) == 1:
                where_filter["document_id"] = str(document_ids[0])
            else:
                where_filter["document_id"] = {"$in": [str(d) for d in document_ids]}

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
        # 🟢 Grab the first 500 characters of the table the Navigation AI built
        hint = sec.chunking_strategy_hint or {}
        snippet = hint.get("normalized_text", "")[:500]
        
        index_cards.append({
            "section_id": str(sec.id),
            "path": sec.parent_path,
            "title": sec.title,
            "type": sec.content_type,
            "summary": sec.semantic_summary,
            "entities": sec.key_entities,    # 🟢 Give the Router the keywords!
            "data_preview": snippet          # 🟢 Give the Router the table preview!
        })

    system_instruction = (
        "You are the Smart Query Router for AgentPulse.\n"
        "MISSION:\n"
        "Read the user's question and review the provided Document Index Catalog.\n"
        "Select ONLY the `section_id`s that semantically match the user's intent. "
        "Use the `path`, `summary`, `entities`, and `data_preview` to determine relevance. If the user asks for a broad overview, prioritize sections with `type: master_scheme_table`.\n\n"
        "OUTPUT EXACT JSON matching this schema:\n"
        "{\"target_section_ids\": [\"uuid-string\"], \"routing_reasoning\": \"string\"}"
    )

    prompt = (
        f"USER QUESTION: \"{user_prompt}\"\n\n"
        f"DOCUMENT INDEX CATALOG:\n"
        f"{json.dumps(index_cards, indent=2)}"
    )

    # =====================================================================
    # 🟢 2. TRANSPARENCY PRINT: See the exact Catalog the Router reads
    # =====================================================================
    print(f"\n{'='*60}")
    print("🧠 [TRANSPARENCY] SMART ROUTER PROMPT (What the Router sees)")
    print(json.dumps(index_cards, indent=2))
    print(f"{'='*60}\n")
    # =====================================================================

    print(f"🧠 Routing Query through Smart Navigation AI (Scanning {len(index_cards)} Filtered Index Cards)...")
    
    response = client.models.generate_content(
        model="gemini-3.1-flash-lite", 
        contents=prompt,
        config={
            "system_instruction": system_instruction,
            "response_mime_type": "application/json",
            "temperature": 0.0
        }
    )

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
    # 🟢 PHASE 3: EXACT CHUNK FILTERING (Kill the Token Bloat)
    # Instead of grabbing all chunks in the section, search ChromaDB 
    # to find the exact 3 chunks inside this section that answer the question!
    # =====================================================================
    print(f"🎯 Narrowing down exact chunks inside the selected sections...")
    
    chunk_collection = chroma_client.get_or_create_collection(
        name="rag_enterprise_vectors_v1",
        metadata={"hnsw:space": "cosine"}
    )
    
    # 🟢 THE FIX: Always use $and for ChromaDB multiple-key filters
    where_chunk_filter = {
        "$and": [
            {"workspace_id": str(workspace_id)},
            {"section_id": {"$in": decision.target_section_ids}}
        ]
    }

    try:
        # Pass the exact same query vector we calculated at the top of the file
        chunk_results = chunk_collection.query(
            query_embeddings=[query_vector],
            n_results=3,  # 🟢 LIMIT TO TOP 3 EXACT MATCHES
            where=where_chunk_filter
        )
        final_vector_ids = chunk_results["ids"][0] if chunk_results["ids"] else []
    except Exception as e:
        print(f"❌ Chunk-level Vector Search failed: {e}")
        final_vector_ids = []

    print(f"📡 Resolved {len(decision.target_section_ids)} sections into {len(final_vector_ids)} highly-targeted vector chunks.")
    
    return final_vector_ids