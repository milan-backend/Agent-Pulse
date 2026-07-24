from pydantic import BaseModel, Field
from typing import List


class DynamicMetadataItem(BaseModel):
    key: str = Field(description="Discovered metadata field name, e.g., 'Semester', 'Department', 'Authority'")
    value: str = Field(description="Extracted value for the metadata field")


class ConceptRelationshipItem(BaseModel):
    source: str = Field(description="Origin entity or concept")
    relation: str = Field(description="Relationship verb/connector, e.g., 'contains', 'taught_by'")
    target: str = Field(description="Target entity or concept")
    strength: float = Field(description="Relationship connection strength from 0.0 (weak) to 1.0 (strong)")


class KnowledgeIngestionPlan(BaseModel):
    # Flattened Document Profile
    document_type: str = Field(description="Catalog classification, e.g., 'University Regulation', 'Research Paper', 'SOP Manual'")
    structure: str = Field(description="Document organizational layout, e.g., 'Hierarchical', 'Sequential', 'Q&A Style', 'Tabular'")
    document_purpose: str = Field(description="Primary business or operational objective of the text")
    summary: str = Field(description="Dense structural overview for retrieval planning")

    # Dynamic Metadata & Relationships
    metadata: List[DynamicMetadataItem] = Field(description="Dynamic key-value pairs discovered from text context (max 10)")
    relationships: List[ConceptRelationshipItem] = Field(description="Key concept relationships discovered from text context")

    # Flattened Chunking Recommendation
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