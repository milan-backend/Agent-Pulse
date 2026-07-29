from pydantic import Field

from app.python_intelligence.schemas.shared.base import PIBaseSchema

from .retrieved_chunk import RetrievedChunk


class RetrievedContext(PIBaseSchema):

    chunks: list[RetrievedChunk] = Field(default_factory=list)

    retrieval_time_ms: float = 0

    total_chunks: int = 0