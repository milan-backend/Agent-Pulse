import os
import uuid
import json
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
import chromadb
from google import genai

# =====================================================================
# 1. Output Schema for Pass 2 (SQL Extraction)
# =====================================================================
class SQLExtractionSpec(BaseModel):
    target_table: str = Field(
        description="The exact name of the table to query, chosen strictly from candidate schemas."
    )
    columns: List[str] = Field(
        description="The list of specific column names to fetch (e.g., ['id', 'status', 'delivery_date'])."
    )
    filters: Dict[str, Any] = Field(
        default_factory=dict,
        description="Key-value pairs for WHERE clauses extracted from user prompt (e.g., {'status': 'shipped'}). NEVER guess or hardcode user identity."
    )
    sort_by: Optional[str] = Field(
        default=None,
        description="Column to sort by, with direction if relevant (e.g., 'created_at DESC')."
    )
    limit: Optional[int] = Field(
        default=1,
        description="Number of rows to return (default is 1 for latest/single entity queries)."
    )
    routing_reasoning: str = Field(
        description="Brief explanation of why this table, columns, and filters were chosen."
    )


# =====================================================================
# 2. Math Helper
# =====================================================================
def calculate_rrf(vector_rank: Optional[int], keyword_rank: Optional[int], k: int = 60) -> float:
    """Calculates standard Reciprocal Rank Fusion score."""
    v_score = 1.0 / (k + vector_rank) if vector_rank else 0.0
    k_score = 1.0 / (k + keyword_rank) if keyword_rank else 0.0
    return v_score + k_score


# =====================================================================
# 3. Core Service: Search + Extraction in One Place
# =====================================================================
class SmartSQLQueryService:
    @classmethod
    def execute_sql_routing(
        cls,
        user_prompt: str,
        workspace_id: uuid.UUID,
        schema_keywords: List[str]
    ) -> Optional[SQLExtractionSpec]:
        """
        Executes Pass 2 for Live SQL:
        1. Embeds user prompt & runs dual search (Vector + Keywords) on content_type='db_schema'.
        2. Merges candidates using RRF.
        3. Prompts Gemini with candidate table cards to produce the strict SQLExtractionSpec JSON.
        """
        gemini_key = os.getenv("INTELLIGENCE_LAYER_API_KEY") or os.getenv("GEMINI_API_KEY")
        client = genai.Client(api_key=gemini_key)

        chroma_host = os.getenv("CHROMA_HOST", "").strip().rstrip("/")
        chroma_token = os.getenv("CHROMA_TOKEN")
        chroma_client = chromadb.HttpClient(
            host=chroma_host,
            headers={"Authorization": f"Bearer {chroma_token}"} if chroma_token else None
        )

        collection = chroma_client.get_or_create_collection(
            name="rag_enterprise_vectors_v1",
            metadata={"hnsw:space": "cosine"}
        )

        workspace_id_str = str(workspace_id)

        # -------------------------------------------------------------
        # Step A: Vector Embedding & Base Filters
        # -------------------------------------------------------------
        query_vector_resp = client.models.embed_content(
            model="models/gemini-embedding-001",
            contents=user_prompt
        )
        query_vector = query_vector_resp.embeddings[0].values

        base_filter = {
            "$and": [
                {"workspace_id": workspace_id_str},
                {"content_type": "db_schema"}
            ]
        }

        # -------------------------------------------------------------
        # Step B: Semantic Vector Search
        # -------------------------------------------------------------
        print("🔍 [SQL ROUTER] Executing Vector Search on Schema Chunks...")
        vector_results = collection.query(
            query_embeddings=[query_vector],
            n_results=6,
            where=base_filter,
            include=["metadatas", "documents", "distances"]
        )

        # -------------------------------------------------------------
        # Step C: Keyword Search on Schemas
        # -------------------------------------------------------------
        keyword_filters = [{"schema_keywords": {"$contains": kw.lower()}} for kw in schema_keywords if kw]
        
        keyword_where = base_filter
        if keyword_filters:
            keyword_where = {
                "$and": [
                    base_filter,
                    {"$or": keyword_filters}
                ]
            }

        print("🔍 [SQL ROUTER] Executing Keyword Search on Schema Chunks...")
        keyword_results = collection.query(
            query_embeddings=[query_vector],
            n_results=6,
            where=keyword_where,
            include=["metadatas", "documents", "distances"]
        )

        # -------------------------------------------------------------
        # Step D: Fusion (RRF) & Deduplication
        # -------------------------------------------------------------
        candidates: Dict[str, Dict[str, Any]] = {}

        if vector_results.get("ids") and vector_results["ids"][0]:
            for rank, cid in enumerate(vector_results["ids"][0]):
                candidates[cid] = {
                    "table_name": vector_results["metadatas"][0][rank].get("table_name", "Unknown"),
                    "schema_text": vector_results["documents"][0][rank],
                    "v_rank": rank + 1,
                    "k_rank": None
                }

        if keyword_results.get("ids") and keyword_results["ids"][0]:
            for rank, cid in enumerate(keyword_results["ids"][0]):
                if cid in candidates:
                    candidates[cid]["k_rank"] = rank + 1
                else:
                    candidates[cid] = {
                        "table_name": keyword_results["metadatas"][0][rank].get("table_name", "Unknown"),
                        "schema_text": keyword_results["documents"][0][rank],
                        "v_rank": None,
                        "k_rank": rank + 1
                    }

        if not candidates:
            print("❌ [SQL ROUTER] No matching database schemas found for this workspace.")
            return None

        # Rank candidates using RRF and pick Top 3 tables
        scored_pool = []
        for cid, data in candidates.items():
            score = calculate_rrf(data["v_rank"], data["k_rank"])
            scored_pool.append((score, data))

        scored_pool.sort(key=lambda x: x[0], reverse=True)
        top_schema_cards = [item[1] for item in scored_pool[:3]]

        # Format schemas for LLM prompt
        schema_prompt_section = "\n\n".join([
            f"=== TABLE: {card['table_name']} ===\n{card['schema_text']}"
            for card in top_schema_cards
        ])

        # -------------------------------------------------------------
        # Step E: Smart SQL Extraction AI (Pass 2)
        # -------------------------------------------------------------
        system_instruction = (
            "You are the Enterprise SQL Extraction Engine.\n"
            "Your task is to analyze candidate database table schemas and determine the exact table, "
            "columns, and filters required to fulfill the user request.\n\n"
            "DECISION RULES:\n"
            "1. Select ONLY ONE target_table that best answers the query.\n"
            "2. Select only necessary columns relevant to the answer.\n"
            "3. Extract filters strictly from the question (e.g., status, dates). NEVER invent user IDs.\n"
            "4. For queries asking for 'my latest', 'my recent', or 'where is my', sort by the relevant timestamp DESC and set limit=1.\n"
            "5. If none of the tables can answer the request, output empty columns and target_table.\n\n"
            "Respond STRICTLY with valid JSON adhering to the SQLExtractionSpec schema."
        )

        prompt = (
            f"USER QUESTION: \"{user_prompt}\"\n\n"
            f"CANDIDATE DATABASE SCHEMAS:\n{schema_prompt_section}"
        )

        response = client.models.generate_content(
            model="gemini-3.1-flash-lite",
            contents=prompt,
            config={
                "system_instruction": system_instruction,
                "response_mime_type": "application/json",
                "response_schema": SQLExtractionSpec,
                "temperature": 0.0
            }
        )

        if response.usage_metadata:
            p_tok = response.usage_metadata.prompt_token_count
            c_tok = response.usage_metadata.candidates_token_count
            print(f"📊 [SQL ROUTER TOKENS] Prompt: {p_tok} | Completion: {c_tok} | Total: {p_tok + c_tok}")

        spec = SQLExtractionSpec.model_validate_json(response.text)
        print(f"🎯 [SQL ROUTER SPEC]: Table={spec.target_table} | Columns={spec.columns} | Filters={spec.filters}")

        return spec