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
from app.core.rag_crypto import decrypt_text_string

# =====================================================================
# 1. AI Output Schema (Upgraded to Target Chunks Directly)
# =====================================================================
class RoutingDecision(BaseModel):
    # 🟢 NEW: The LLM outputs the exact chunk ID, not just the broad section!
    target_chunk_ids: List[str] = Field(
        description="The exact list of string UUIDs for the chunks containing the most accurate answers."
    )
    routing_reasoning: str = Field(
        description="Brief explanation of why these specific chunks were chosen."
    )

# =====================================================================
# 2. Reciprocal Rank Fusion (RRF) Math Function
# =====================================================================
def calculate_rrf(vector_rank: int, keyword_rank: int, k: int = 60) -> float:
    """Calculates the RRF score. If a chunk isn't in a list, its rank is infinity."""
    v_score = 1.0 / (k + vector_rank) if vector_rank else 0.0
    k_score = 1.0 / (k + keyword_rank) if keyword_rank else 0.0
    return v_score + k_score

# =====================================================================
# 3. The New Hybrid Smart Router
# =====================================================================
def execute_smart_routing(
    user_prompt: str, 
    workspace_id: uuid.UUID, 
    db: Session,
    document_ids: List[uuid.UUID] = None
) -> List[str]:
    
    gemini_key = os.getenv("INTELLIGENCE_LAYER_API_KEY") or os.getenv("GEMINI_API_KEY")
    client = genai.Client(api_key=gemini_key)

    CHROMA_HOST = os.getenv("CHROMA_HOST")
    CHROMA_TOKEN = os.getenv("CHROMA_TOKEN")
    chroma_client = chromadb.HttpClient(
        host=str(CHROMA_HOST).strip().rstrip("/"),
        headers={"Authorization": f"Bearer {CHROMA_TOKEN}"} if CHROMA_TOKEN else None
    )
    
    # 🟢 We only use the ONE unified collection now!
    collection = chroma_client.get_or_create_collection(
        name="rag_enterprise_vectors_v1",
        metadata={"hnsw:space": "cosine"}
    )

    print("🔍 Executing Dual Hybrid Search (Vector + Keyword)...")
    
    # Extract naive keywords from prompt for the BM25-style dragnet
    keywords = [word for word in user_prompt.split() if len(word) > 4]

    # 🟢 NEW: Strict Workspace & Document Boundary Filter
    where_filter = {"workspace_id": str(workspace_id)}
    if document_ids:
        where_filter = {
            "$and": [
                {"workspace_id": str(workspace_id)},
                {"document_id": {"$in": document_ids}}
            ]
        }
    
    # 1. VECTOR SEARCH (Finds Meaning)
    query_vector_resp = client.models.embed_content(
        model="models/gemini-embedding-001",
        contents=user_prompt
    )
    query_vector = query_vector_resp.embeddings[0].values

    vector_results = collection.query(
        query_embeddings=[query_vector],
        n_results=15,
        where=where_filter
    )
    
    # 2. KEYWORD SEARCH
    keyword_filter = {"$or": [{"chunk_keywords": {"$contains": kw}} for kw in keywords]} if keywords else {}
    keyword_where = {"$and": [{"workspace_id": str(workspace_id)}, keyword_filter]} if keyword_filter else where_filter
    
    keyword_results = collection.query(
        query_embeddings=[query_vector], 
        n_results=15,
        where=keyword_where
    )

    # =====================================================================
    # 🟢 STEP 2: RRF MERGE, DEDUPLICATION, & DECRYPTION PREVIEW
    # =====================================================================
    vector_ids = vector_results["ids"][0] if vector_results.get("ids") else []
    vector_metas = vector_results["metadatas"][0] if vector_results.get("metadatas") else []
    vector_docs = vector_results["documents"][0] if vector_results.get("documents") else []
    
    keyword_ids = keyword_results["ids"][0] if keyword_results.get("ids") else []
    keyword_metas = keyword_results["metadatas"][0] if keyword_results.get("metadatas") else []
    keyword_docs = keyword_results["documents"][0] if keyword_results.get("documents") else []
    
    master_metadata_map = {}
    
    for idx, cid in enumerate(vector_ids):
        # 🟢 Decrypt a 300-character sneak peek so the LLM knows the answer is here!
        snippet = decrypt_text_string(vector_docs[idx], workspace_id)[:300] if vector_docs else ""
        master_metadata_map[cid] = {"meta": vector_metas[idx], "v_rank": idx + 1, "k_rank": None, "preview": snippet}
        
    for idx, cid in enumerate(keyword_ids):
        if cid in master_metadata_map:
            master_metadata_map[cid]["k_rank"] = idx + 1
        else:
            snippet = decrypt_text_string(keyword_docs[idx], workspace_id)[:300] if keyword_docs else ""
            master_metadata_map[cid] = {"meta": keyword_metas[idx], "v_rank": None, "k_rank": idx + 1, "preview": snippet}

    rrf_scores = []
    for cid, data in master_metadata_map.items():
        score = calculate_rrf(data["v_rank"], data["k_rank"])
        rrf_scores.append((score, cid, data))
    
    rrf_scores.sort(key=lambda x: x[0], reverse=True)
    top_5_cards = rrf_scores[:5]

    if not top_5_cards:
        return []

    # =====================================================================
    # 🟢 STEP 3: THE SMART ROUTER (LLM JUDGE)
    # =====================================================================
    index_cards = []
    for score, cid, data in top_5_cards:
        meta = data["meta"]
        index_cards.append({
            "chunk_id": cid,
            "path": meta.get("parent_path"),
            "summary": meta.get("semantic_summary"),
            "data_preview": data["preview"] + "..." # 🟢 The LLM can now see the text!
        })

    # 🟢 We softened the prompt so it stops rejecting valid data!
    system_instruction = (
        "You are the Smart Query Router for an Enterprise RAG pipeline.\n"
        "Read the user's question and review ALL 5 Document Index Cards.\n"
        "You MUST evaluate every card. Select the `chunk_id`s that are RELEVANT or LIKELY to contain pieces of the answer. "
        "Do not be overly strict; if a card's data_preview or summary seems related to the topic, select it.\n\n"
        "OUTPUT EXACT JSON matching this schema:\n"
        "{\"target_chunk_ids\": [\"uuid-string\"], \"routing_reasoning\": \"string\"}"
    )

    prompt = f"USER QUESTION: \"{user_prompt}\"\n\nINDEX CARDS:\n{json.dumps(index_cards, indent=2)}"
    
    response = client.models.generate_content(
        model="gemini-3.1-flash-lite", 
        contents=prompt,
        config={
            "system_instruction": system_instruction,
            "response_mime_type": "application/json",
            "temperature": 0.0
        }
    )
    
    decision = RoutingDecision.model_validate_json(response.text)
    
    # =====================================================================
    # 🟢 STEP 4: THE POSTGRESQL LINKED-LIST FETCH (No 2nd Vector Search!)
    # =====================================================================
    print(f"🎯 Router selected Chunk IDs: {decision.target_chunk_ids}")
    final_chunk_ids_to_fetch = set(decision.target_chunk_ids)

    # Fetch the neighbors from Postgres to guarantee unbreakable context
    target_chunks = db.query(DocumentChunk).filter(DocumentChunk.id.in_(decision.target_chunk_ids)).all()
    
    for chunk in target_chunks:
        if chunk.prev_chunk_id:
            final_chunk_ids_to_fetch.add(str(chunk.prev_chunk_id))
        if chunk.next_chunk_id:
            final_chunk_ids_to_fetch.add(str(chunk.next_chunk_id))

    # Return the exact list of IDs. The next file will just run chroma.get(ids=...)
    return list(final_chunk_ids_to_fetch)