from typing import Any

from pydantic import Field

from app.python_intelligence.schemas.shared.base import PIBaseSchema


class SemanticMetadata(PIBaseSchema):

    summary: str | None = None

    keywords: list[str] = Field(default_factory=list)

    topics: list[str] = Field(default_factory=list)

    language: str | None = None

    metadata: dict[str, Any] = Field(default_factory=dict)