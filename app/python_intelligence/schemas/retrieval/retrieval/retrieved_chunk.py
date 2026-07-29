from pydantic import Field

from app.python_intelligence.schemas.shared.base import PIBaseSchema


class RetrievedChunk(PIBaseSchema):

    chunk_id: str

    content: str

    score: float = Field(
        ge=0,
        le=1,
    )

    page_number: int

    metadata: dict = Field(default_factory=dict)