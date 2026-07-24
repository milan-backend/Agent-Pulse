from app.schemas.ingestion_plan_schema import KnowledgeIngestionPlan

ALLOWED_STRATEGIES = [
    "Section Based", 
    "Heading Based", 
    "Paragraph Based", 
    "Question Answer", 
    "Page Based", 
    "Semantic"
]

def validate_and_sanitize_ingestion_plan(plan: KnowledgeIngestionPlan) -> KnowledgeIngestionPlan:
    """
    Enforces strict backend boundaries over Extraction AI output:
    - Clamps chunk_size between 500 and 1500.
    - Clamps overlap between 50 and 300.
    - Reverts invalid chunking strategies to 'Paragraph Based'.
    - Limits metadata items to a maximum of 10.
    """
    # 1. Validate Strategy
    if plan.chunking.strategy not in ALLOWED_STRATEGIES:
        print(f"⚠️ Validation Warning: Strategy '{plan.chunking.strategy}' invalid. Defaulting to 'Paragraph Based'.")
        plan.chunking.strategy = "Paragraph Based"

    # 2. Validate & Clamp Chunk Size
    if plan.chunking.chunk_size < 500 or plan.chunking.chunk_size > 1500:
        clamped_size = max(500, min(1500, plan.chunking.chunk_size))
        print(f"⚠️ Validation Warning: chunk_size {plan.chunking.chunk_size} out of bounds. Clamped to {clamped_size}.")
        plan.chunking.chunk_size = clamped_size

    # 3. Validate & Clamp Overlap
    if plan.chunking.overlap < 50 or plan.chunking.overlap > 300:
        clamped_overlap = max(50, min(300, plan.chunking.overlap))
        print(f"⚠️ Validation Warning: overlap {plan.chunking.overlap} out of bounds. Clamped to {clamped_overlap}.")
        plan.chunking.overlap = clamped_overlap

    # 4. Limit Metadata Count
    if len(plan.metadata) > 10:
        plan.metadata = plan.metadata[:10]

    return plan