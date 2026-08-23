import os
import uuid
import json
import re
from typing import List, Dict, Optional
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from google import genai
import chromadb

from app.models.new_arch import DocumentChunk, DocumentSection
from app.core.rag_crypto import decrypt_text_string


# =====================================================================
# 1. AI Output Schema
# =====================================================================
class RoutingDecision(BaseModel):
    target_chunk_ids: List[str] = Field(
        default_factory=list,
        description="The exact list of string UUIDs for the chunks containing the relevant facts or answer."
    )
    routing_reasoning: str = Field(
        description="Brief explanation of why these specific chunks or sections were selected based on keywords, previews, and match percentage."
    )


# =====================================================================
# 2. Math & Confidence Helpers
# =====================================================================
def calculate_rrf(vector_rank: Optional[int], keyword_rank: Optional[int], k: int = 60) -> float:
    """Calculates standard Reciprocal Rank Fusion score."""
    v_score = 1.0 / (k + vector_rank) if vector_rank else 0.0
    k_score = 1.0 / (k + keyword_rank) if keyword_rank else 0.0
    return v_score + k_score


def distance_to_match_percentage(distance: float) -> int:
    """
    Converts ChromaDB cosine distance (0.0 to 2.0) into an intuitive 0-100% similarity score.
    Cosine Similarity = 1 - distance.
    """
    similarity = 1.0 - distance
    pct = int(round(max(0.0, min(1.0, similarity)) * 100))
    return pct


def extract_query_keywords(prompt: str) -> List[str]:
    """
    Extracts Acronyms, Numbers, and words longer than 5 letters.
    This prevents flooding with generic words but captures proper nouns like 'Indira'.
    """
    # Grab acronyms, numbers, and any word 5+ letters long
    tokens = re.findall(r'\b[A-Z]{2,}\b|\b\d+(?:\.\d+)?\b|\b[a-zA-Z]{5,}\b', prompt)
    
    # Filter out common annoying stop words just in case
    stopwords = {"which", "where", "there", "their", "about", "would", "could", "should"}
    valid_tokens = [t for t in tokens if t.lower() not in stopwords]
    
    return list(dict.fromkeys(valid_tokens))


# =====================================================================
# 3. The Core Smart Routing Pipeline
# =====================================================================
def execute_smart_routing(
    user_prompt: str, 
    workspace_id: uuid.UUID, 
    db: Session,
    document_ids: Optional[List[uuid.UUID]] = None
) -> List[str]:
    
    gemini_key = os.getenv("INTELLIGENCE_LAYER_API_KEY") or os.getenv("GEMINI_API_KEY")
    client = genai.Client(api_key=gemini_key)

    CHROMA_HOST = os.getenv("CHROMA_HOST", "").strip().rstrip("/")
    CHROMA_TOKEN = os.getenv("CHROMA_TOKEN")
    chroma_client = chromadb.HttpClient(
        host=CHROMA_HOST,
        headers={"Authorization": f"Bearer {CHROMA_TOKEN}"} if CHROMA_TOKEN else None
    )
    
    collection = chroma_client.get_or_create_collection(
        name="rag_enterprise_vectors_v1",
        metadata={"hnsw:space": "cosine"}
    )

    # -----------------------------------------------------------------
    # Step A: Generate Embedding & Prompt Keywords
    # -----------------------------------------------------------------
    query_vector_resp = client.models.embed_content(
        model="models/gemini-embedding-001",
        contents=user_prompt
    )
    query_vector = query_vector_resp.embeddings[0].values
    prompt_keywords = extract_query_keywords(user_prompt)

    # Base workspace filter
    where_filter: Dict = {"workspace_id": str(workspace_id)}
    if document_ids:
        where_filter = {
            "$and": [
                {"workspace_id": str(workspace_id)},
                {"document_id": {"$in": [str(d) for d in document_ids]}}
            ]
        }

    # -----------------------------------------------------------------
    # Step B: Primary Dual Search (Vector + Chunk Keywords)
    # -----------------------------------------------------------------
    print("🔍 Executing Primary Dual Search on Candidate Chunks...")
    
    vector_results = collection.query(
        query_embeddings=[query_vector],
        n_results=15,
        where=where_filter,
        include=["metadatas", "documents", "distances"]
    )

    keyword_filter_list = []
    for kw in prompt_keywords:
        keyword_filter_list.append({"chunk_keywords": {"$contains": kw}})
        keyword_filter_list.append({"parent_keywords": {"$contains": kw}})

    keyword_where = where_filter
    if keyword_filter_list:
        keyword_where = {
            "$and": [
                where_filter,
                {"$or": keyword_filter_list}
            ]
        }

    keyword_results = collection.query(
        query_embeddings=[query_vector],
        n_results=15,
        where=keyword_where,
        include=["metadatas", "documents", "distances"]
    )

    # -----------------------------------------------------------------
    # Step C: Fallback Trigger (When 0 Section/Keyword Matches Found)
    # -----------------------------------------------------------------
    v_ids = vector_results["ids"][0] if vector_results.get("ids") else []
    k_ids = keyword_results["ids"][0] if keyword_results.get("ids") else []

    if not v_ids and not k_ids:
        print("⚠️ 0 primary matches found. Triggering Workspace-Wide Chunk Fallback...")
        fallback_results = collection.query(
            query_embeddings=[query_vector],
            n_results=10,
            where={"workspace_id": str(workspace_id)},
            include=["metadatas", "documents", "distances"]
        )
        v_ids = fallback_results["ids"][0] if fallback_results.get("ids") else []
        vector_results = fallback_results

    if not v_ids and not k_ids:
        print("❌ No matching chunks found in workspace.")
        return []

    # -----------------------------------------------------------------
    # Step D: Fusion, Normalization, & Deduplication
    # -----------------------------------------------------------------
    master_candidates: Dict[str, Dict] = {}

    # Process Vector Results
    if vector_results.get("ids") and vector_results["ids"][0]:
        for rank, cid in enumerate(vector_results["ids"][0]):
            meta = vector_results["metadatas"][0][rank]
            dist = vector_results["distances"][0][rank] if "distances" in vector_results else 0.5
            enc_doc = vector_results["documents"][0][rank] if "documents" in vector_results else ""
            
            preview_text = decrypt_text_string(enc_doc, workspace_id)[:250] if enc_doc else ""
            match_pct = distance_to_match_percentage(dist)

            master_candidates[cid] = {
                "meta": meta,
                "v_rank": rank + 1,
                "k_rank": None,
                "match_pct": match_pct,
                "preview": preview_text
            }

    # Process Keyword Results
    if keyword_results.get("ids") and keyword_results["ids"][0]:
        for rank, cid in enumerate(keyword_results["ids"][0]):
            meta = keyword_results["metadatas"][0][rank]
            dist = keyword_results["distances"][0][rank] if "distances" in keyword_results else 0.5
            enc_doc = keyword_results["documents"][0][rank] if "documents" in keyword_results else ""

            if cid in master_candidates:
                master_candidates[cid]["k_rank"] = rank + 1
            else:
                preview_text = decrypt_text_string(enc_doc, workspace_id)[:250] if enc_doc else ""
                match_pct = distance_to_match_percentage(dist)
                master_candidates[cid] = {
                    "meta": meta,
                    "v_rank": None,
                    "k_rank": rank + 1,
                    "match_pct": match_pct,
                    "preview": preview_text
                }

    # Score and select Top 5
    scored_pool = []
    for cid, data in master_candidates.items():
        rrf = calculate_rrf(data["v_rank"], data["k_rank"])
        scored_pool.append((rrf, cid, data))

    scored_pool.sort(key=lambda x: x[0], reverse=True)
    top_5_candidates = scored_pool[:5]

    # -----------------------------------------------------------------
    # Step E: Build Enriched Index Cards for Smart Router AI
    # -----------------------------------------------------------------
    index_cards = []
    for score, cid, item in top_5_candidates:
        meta = item["meta"]
        index_cards.append({
            "chunk_id": cid,
            "parent_section": meta.get("parent_path") or meta.get("title", "Unknown Section"),
            "section_summary": meta.get("semantic_summary", "No summary available"),
            "chunk_keywords": meta.get("chunk_keywords", ""),
            "semantic_match_confidence": f"{item['match_pct']}%",
            "snippet_preview": item["preview"] + "..."
        })

    # -----------------------------------------------------------------
    # Step F: Smart Router AI Verification
    # -----------------------------------------------------------------
    system_instruction = (
        "You are the Enterprise RAG Verification & Routing Engine.\n"
        "Your task is to analyze candidate Index Cards for a user query and select the most relevant `chunk_id`s.\n\n"
        "Decision Rules:\n"
        "1. Check `chunk_keywords` and `snippet_preview` for exact entities, acronyms, or numbers mentioned in the user query.\n"
        "2. High confidence (>70%) or strong keyword overlap indicates high relevance.\n"
        "3. If a section summary is broad but the `chunk_keywords` or `snippet_preview` contain the specific needle data, select that card.\n"
        "4. If none of the cards contain relevant facts or related context, return an empty list: {\"target_chunk_ids\": [], \"routing_reasoning\": \"...\"}.\n\n"
        "Respond STRICTLY with valid JSON following this schema:\n"
        "{\n"
        "  \"target_chunk_ids\": [\"chunk-uuid-1\", \"chunk-uuid-2\"],\n"
        "  \"routing_reasoning\": \"string explanation\"\n"
        "}"
    )

    prompt = (
        f"USER QUESTION: \"{user_prompt}\"\n\n"
        f"CANDIDATE INDEX CARDS:\n{json.dumps(index_cards, indent=2)}"
    )

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
    print(f"🎯 Router Decision ({len(decision.target_chunk_ids)} selected): {decision.routing_reasoning}")

    if not decision.target_chunk_ids:
        return []

    # -----------------------------------------------------------------
    # Step G: PostgreSQL Linked-List Context Assembly
    # -----------------------------------------------------------------
    final_chunk_ids = set(decision.target_chunk_ids)

    # Fetch previous and next chunk neighbors for full context continuity
    target_chunks = db.query(DocumentChunk).filter(DocumentChunk.id.in_(decision.target_chunk_ids)).all()
    for chk in target_chunks:
        if chk.prev_chunk_id:
            final_chunk_ids.add(str(chk.prev_chunk_id))
        if chk.next_chunk_id:
            final_chunk_ids.add(str(chk.next_chunk_id))

    return list(final_chunk_ids)