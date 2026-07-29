from pydantic import Field, field_validator

from .base import PIBaseSchema


class ConfidenceScore(PIBaseSchema):

    score: float = Field(
        ge=0.0,
        le=1.0,
        description="Detector confidence between 0 and 1.",
    )

    source: str | None = Field(
        default=None,
        description="Detector generating the score.",
    )

    @field_validator("score")
    @classmethod
    def round_score(cls, value: float) -> float:
        return round(value, 4)