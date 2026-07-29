from pydantic import Field

from app.python_intelligence.schemas.shared.base import PIBaseSchema


class IntentResult(PIBaseSchema):

    intent: str

    confidence: float = Field(
        ge=0,
        le=1,
    )

    requires_retrieval: bool = True

    requires_reasoning: bool = False

    filters: dict = Field(default_factory=dict)