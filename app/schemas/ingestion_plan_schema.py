from pydantic import BaseModel, Field
from typing import List


class KnowledgeIngestionPlan(BaseModel):
    # Document Profile Attributes
    document_type: str = Field(description="Catalog classification, e.g., 'University Regulation', 'Research Paper', 'SOP Manual'")
    structure: str = Field(description="Document organizational layout, e.g., 'Hierarchical', 'Sequential', 'Q&A Style', 'Tabular'")
    document_purpose: str = Field(description="Primary business or operational objective of the text")
    summary: str = Field(description="Dense structural overview for retrieval planning")

    # Metadata & Relationships as Clean String Arrays
    metadata: List[str] = Field(
        description="Dynamic metadata items. Format each item strictly as 'Key: Value'. Example: 'Semester: 6'."
    )
    relationships: List[str] = Field(
        description="Concept relationships. Format each item strictly as 'Source | Relation | Target | Strength'. Example: 'Compiler Design | taught_in | Semester 6 | 0.9'."
    )

    # Chunking Recommendation Attributes
    chunk_strategy: str = Field(
        description="Recommended chunk strategy. MUST be one of: ['Section Based', 'Heading Based', 'Paragraph Based', 'Question Answer', 'Page Based', 'Semantic']"
    )
    chunk_size: int = Field(description="Recommended token/character window size (500 to 1500)")
    overlap: int = Field(description="Recommended sliding overlap window size (50 to 300)")
    chunk_reasoning: str = Field(description="Structural justification for why this strategy was chosen")

    # Questions & Confidence
    questions_this_document_can_answer: List[str] = Field(description="3-8 concrete business/operational questions answered by this document")
    metadata_confidence: float = Field(description="Confidence score for metadata extraction (0.0 to 1.0)")
    chunk_strategy_confidence: float = Field(description="Confidence score for chunking recommendation (0.0 to 1.0)")