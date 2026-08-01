import os
from google import genai
from pydantic import BaseModel, Field
from typing import List
from app.services.intent_service import IntentAnalysisSchema


class RetrievalBlueprintSchema(BaseModel):
    target_chroma_vector_ids: List[str] = Field(
        description="Exact Chroma Vector IDs of chunks selected to fulfill the query."
    )
    target_section_ids: List[str] = Field(
        description="Section UUIDs from which chunks should be fetched."
    )
    include_neighbor_chunks: bool = Field(
        description="Whether Retrieval Service should traverse prev_chunk_id / next_chunk_id pointers in SQL."
    )
    max_chunks_budget: int = Field(
        description="Calculated max chunk budget based on query depth."
    )
    planner_notes: str = Field(
        description="Summary of planning rationale and selection strategy."
    )


def execute_retrieval_planning_triage(
    user_prompt: str,
    intent_strategy: IntentAnalysisSchema,
    chunk_telemetry_candidates: List[dict]
) -> RetrievalBlueprintSchema:
    """
    Planner AI: Examines Chunk Telemetry Summaries and Intent Diagnostics to resolve 
    the exact list of target Chunk IDs for direct SQL/Vector retrieval.
    """
    if not chunk_telemetry_candidates:
        return RetrievalBlueprintSchema(
            target_chroma_vector_ids=[],
            target_section_ids=[],
            include_neighbor_chunks=False,
            max_chunks_budget=5,
            planner_notes="No candidate chunks available."
        )

    gemini_key = os.getenv("INTENT_API_KEY") or os.getenv("GEMINI_API_KEY")
    if not gemini_key:
        raise ValueError("CRITICAL: API Key for Retrieval Planner is missing.")
        
    client = genai.Client(api_key=gemini_key)
    
    telemetry_blocks = []
    for c in chunk_telemetry_candidates:
        telemetry_blocks.append(
            f"🔹 [CHUNK ID: {c['id']} | CHROMA VECTOR ID: {c.get('chroma_vector_id')}]\n"
            f" - Section Code: {c.get('section_code', 'N/A')} ({c.get('section_title', '')})\n"
            f" - Telemetry Summary: {c.get('telemetry_summary', '')}\n"
            f"--------------------------------------------------"
        )
    candidates_context = "\n".join(telemetry_blocks)
    
    system_instruction = (
        "You are the Core Director of the AgentPulse Retrieval Planner AI Layer.\n\n"
        "🎯 MISSION:\n"
        "Review Intent Diagnostics and Chunk Telemetry Summaries to select the precise target chunks.\n"
        "Bypass generic vector similarity search by picking the exact Chroma Vector IDs needed to answer the prompt.\n\n"
        "🎯 DEPTH & BUDGET RULES:\n"
        "- Shallow: Select 1 to 3 exact chunks, set include_neighbor_chunks = False.\n"
        "- Medium: Select 4 to 6 chunks, set include_neighbor_chunks = True.\n"
        "- Deep: Select 6 to 10 chunks, set include_neighbor_chunks = True.\n"
    )
    
    # Injected target_document_ids into the prompt context for better alignment
    prompt = (
        f"USER QUESTION: \"{user_prompt}\"\n\n"
        f"INTENT DIAGNOSTICS:\n"
        f" - Intent Type: {intent_strategy.intent_type}\n"
        f" - Main Topic: {intent_strategy.main_topic}\n"
        f" - Target Documents: {intent_strategy.target_document_ids}\n"
        f" - Requested Depth: {intent_strategy.retrieval_depth}\n"
        f" - Target Sections: {intent_strategy.target_section_codes}\n"
        f"---------------------------------\n\n"
        f"CHUNK TELEMETRY CANDIDATES:\n"
        f"{candidates_context}"
    )

    response = client.models.generate_content(
        model="gemini-3.1-flash-lite",
        contents=prompt,
        config={
            "system_instruction": system_instruction,
            "response_mime_type": "application/json",
            "response_schema": RetrievalBlueprintSchema,
            "temperature": 0.0
        }
    )

    return RetrievalBlueprintSchema.model_validate_json(response.text)