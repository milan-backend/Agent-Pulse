import os
from google import genai
from pydantic import BaseModel, Field
from typing import List

# =====================================================================
# 📊 PHASE A SCHEMA: DOCUMENT LEVEL METADATA PRIMITIVES
# =====================================================================

class DocumentLevelMetadataSchema(BaseModel):
    document_type: str = Field(description="The functional catalog classification of the file. Prefer standard classifications like 'Board Meeting Minutes', 'HR Policy Manual', 'Technical Specification'. If none fit perfectly, return the closest matching organizational tag.")
    document_role: str = Field(description="The strategic retrieval purpose. Prefer: 'Evidence', 'Decision Making', 'Compliance', 'Supporting Context'. If none fit, output a clean custom retrieval role identifier.")
    time_scope: str = Field(description="The temporal framework bounds of the text, e.g., 'Q2 2026', 'Annual', 'Historical', 'Future Plan'")
    document_status: str = Field(description="The operational status phase. Prefer: 'Draft', 'Approved', 'Archived', 'Superseded'. If alternative corporate state matches closer, utilize that description.")
    document_purpose: str = Field(description="The explicit operational reason why this document was compiled, e.g., 'Quarterly Performance Tracking'")
    planner_summary: str = Field(description="A dense, highly technical synthesis optimized strictly for an upstream AI Retrieval Planner, detailing what core data can be located here.")
    departments: List[str] = Field(description="List of corporate organizational divisions that own or use this document, e.g., ['Finance', 'Executive']")
    topics: List[str] = Field(description="Top 3-6 macro high-level categorical concepts present across the text payload")
    classification_confidence: str = Field(description="Confidence classification routing assessment score. MUST choose strictly from: ['High', 'Medium', 'Low']")


# =====================================================================
# 📊 PHASE B SCHEMA: CHUNK LEVEL KNOWLEDGE GRAPH PRIMITIVES
# =====================================================================

class TypedEntity(BaseModel):
    name: str = Field(description="The canonical name of the core concept, metric, system, or organization, e.g., 'Revenue'")
    entity_type: str = Field(description="The domain classification of this entity, e.g., 'Financial Metric', 'Software Component'")

class KnowledgeTriplet(BaseModel):
    source: str = Field(description="The originating subject entity name, e.g., 'Revenue'")
    relation: str = Field(description="The explicit semantic link categorization verb. Prefer: ['causes', 'supports', 'depends_on', 'part_of', 'owned_by', 'measures', 'contains', 'supersedes']. Can use domain specific variations if necessary.")
    target: str = Field(description="The recipient object entity name, e.g., 'Expenses'")
    confidence: str = Field(description="Confidence indicator for this individual connection triplet. MUST choose strictly from: ['High', 'Medium', 'Low']")

class ChunkLevelMetadataSchema(BaseModel):
    entities: List[TypedEntity] = Field(description="Structured concepts, metrics, systems, or tools identified in this specific text chunk")
    relationships: List[KnowledgeTriplet] = Field(description="Directional structural logic connections linking the extracted entities with individual confidence metrics")
    facts: List[str] = Field(description="Atomic, verifiable factual declarations or historical timeline shifts made in this chunk text")
    retrieval_keywords: List[str] = Field(description="Conceptual synonyms or search queries that bridge user natural language syntax to this specific text")
    questions_this_document_can_answer: List[str] = Field(description="List of explicit, practical operational questions an operator might ask that this specific text segment has the exact data to answer.")
    extraction_confidence: str = Field(description="Overall granular evaluation score for this chunk payload. MUST choose strictly from: ['High', 'Medium', 'Low']")


# =====================================================================
# 📐 SYSTEM AUTHORITY & COMPOUND IMPORTANCE SCORING LOGIC
# =====================================================================

def calculate_document_authority(doc_type: str) -> int:
    """Calculates strict system authority weightings based on explicit system rules."""
    dt = str(doc_type).lower().strip()
    if "board meeting" in dt: return 100
    if "policy" in dt or "handbook" in dt or "manual" in dt: return 95
    if "financial" in dt or "audit" in dt: return 92
    if "success" in dt or "support" in dt: return 88
    if "notes" in dt or "memo" in dt: return 55
    if "draft" in dt: return 35
    return 50

def calculate_compound_importance(meta_a: DocumentLevelMetadataSchema, answers_count: int, relationships_count: int) -> int:
    """
    Measures compound contextual weight by balancing strategic role, system authority rules,
    relationship depth, and question coverage together. Prevents flat list glossaries from hijacking priority.
    """
    base_authority = calculate_document_authority(meta_a.document_type)
    
    role_weights = {
        "decision making": 30,
        "compliance": 25,
        "evidence": 20,
        "supporting context": 10
    }
    role_score = role_weights.get(str(meta_a.document_role).lower().strip(), 15)
    
    question_factor = min(answers_count * 5, 25)
    relationship_factor = min(relationships_count * 3, 20)
    
    final_score = int((base_authority * 0.4) + role_score + question_factor + relationship_factor)
    return max(10, min(100, final_score))


# =====================================================================
# 🚀 INITIALIZE SHARED CLIENT INTERFACE (REUSE FOR EFFICIENCY)
# =====================================================================

def get_intelligence_client() -> genai.Client:
    """Fetches a configured client utilizing the isolated key environment channel."""
    gemini_key = os.getenv("INTELLIGENCE_LAYER_API_KEY")
    if not gemini_key:
        raise ValueError("CRITICAL RUNTIME ERROR: INTELLIGENCE_LAYER_API_KEY environment variable is missing.")
    return genai.Client(api_key=gemini_key)


# =====================================================================
# 🚀 TWO-PHASE EXTRACTION RUNNERS
# =====================================================================

def run_phase_a_document_extraction(global_document_sample: str, client: genai.Client) -> DocumentLevelMetadataSchema:
    """
    PHASE A: Extracts structural document-level attributes once using a global text context window sample.
    Optimizes for structural catalog typing and system classification assignments.
    """
    system_instruction = (
        "You are the Core Computational Cataloger for the AgentPulse Retrieval Layer.\n\n"
        "🎯 OPERATIONAL OBJECTIVE:\n"
        "Your generated output serves as a global structural record consumed by an upstream automated "
        "AI Retrieval Planner to verify if this document fits macro intent parameters. Optimize for machine lookups.\n\n"
        "⚠️ RULES & ALIGNMENT STRATEGIES:\n"
        "- Classify the overall document properties from a macro perspective using the text sample.\n"
        "- Do NOT provide friendly summaries, text evaluations, or human narrative flows.\n"
        "- If standard classification labels (for role, type, status) do not fit perfectly due to unique corporate formatting, "
        "output the closest possible description instead."
    )
    
    response = client.models.generate_content(
        model="gemini-2.5-flash-lite",
        contents=f"Analyze the following document context sample and extract global document metadata columns:\n\n{global_document_sample}",
        config={
            "system_instruction": system_instruction,
            "response_mime_type": "application/json",
            "response_schema": DocumentLevelMetadataSchema,
            "temperature": 0.1
        }
    )
    return DocumentLevelMetadataSchema.model_validate_json(response.text)


def run_phase_b_chunk_extraction(chunk_text: str, client: genai.Client) -> ChunkLevelMetadataSchema:
    """
    PHASE B: Extracts granular knowledge components, retrieval keywords, and triplets for a single chunk.
    Enforces strict grounding boundaries to protect the structural network from hallucinated inference.
    """
    system_instruction = (
        "You are the Core Computational Graph Indexer for the AgentPulse Retrieval Layer.\n\n"
        "🎯 OPERATIONAL OBJECTIVE:\n"
        "Your output maps local data points inside text chunks to handle semantic bridges and precise factual lookups.\n\n"
        "⚠️ GROUNDING RULES & CONSTRAINTS:\n"
        "- Relationships and connections should ONLY link entities that are explicitly supported and stated within the chunk text.\n"
        "- 🛑 DO NOT infer relationships or properties from general world knowledge or external context logic.\n"
        "- Assume future users will input search queries using different wording than appears in the text. Extract retrieval "
        "keywords and operational questions that bridge user language to the chunk's content.\n"
        "- Select confidence values strictly from ['High', 'Medium', 'Low']."
    )
    
    # FIXED: Replaced non-existent variable {chunk} with matching function parameter {chunk_text}
    response = client.models.generate_content(
        model="gemini-2.5-flash-lite",
        contents=f"Execute structural indexing and factual extraction across the following targeted text chunk:\n\n{chunk_text}",
        config={
            "system_instruction": system_instruction,
            "response_mime_type": "application/json",
            "response_schema": ChunkLevelMetadataSchema,
            "temperature": 0.1
        }
    )
    return ChunkLevelMetadataSchema.model_validate_json(response.text)