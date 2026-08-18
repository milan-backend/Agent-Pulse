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
    Enforces strict backend boundaries over Extraction AI output.
    """
    # 1. Validate Strategy
    if plan.chunk_strategy not in ALLOWED_STRATEGIES:
        print(f"⚠️ Validation Warning: Strategy '{plan.chunk_strategy}' invalid. Defaulting to 'Paragraph Based'.")
        plan.chunk_strategy = "Paragraph Based"

    # 2. Validate & Clamp Chunk Size
    if plan.chunk_size < 500 or plan.chunk_size > 1500:
        clamped_size = max(500, min(1500, plan.chunk_size))
        print(f"⚠️ Validation Warning: chunk_size {plan.chunk_size} out of bounds. Clamped to {clamped_size}.")
        plan.chunk_size = clamped_size

    # 3. Validate & Clamp Overlap
    if plan.overlap < 50 or plan.overlap > 300:
        clamped_overlap = max(50, min(300, plan.overlap))
        print(f"⚠️ Validation Warning: overlap {plan.overlap} out of bounds. Clamped to {clamped_overlap}.")
        plan.overlap = clamped_overlap

    # 4. Limit Metadata Count
    if len(plan.metadata) > 10:
        plan.metadata = plan.metadata[:10]

    return plan