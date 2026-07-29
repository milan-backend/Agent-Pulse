from pydantic import Field

from app.python_intelligence.schemas.shared.base import PIBaseSchema


class Citation(PIBaseSchema):

    filename: str

    page_number: int = Field(ge=1)

    chunk_id: str

    score: float