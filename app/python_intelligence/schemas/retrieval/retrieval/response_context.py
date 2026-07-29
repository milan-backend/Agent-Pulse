from pydantic import Field

from app.python_intelligence.schemas.shared.base import PIBaseSchema

from .citation import Citation
from .retrieved_context import RetrievedContext


class ResponseContext(PIBaseSchema):

    question: str

    retrieved_context: RetrievedContext

    citations: list[Citation] = Field(default_factory=list)