from typing import Any
from uuid import UUID

from pydantic import Field

from app.python_intelligence.schemas.shared.base import PIBaseSchema
from app.python_intelligence.schemas.shared.confidence import ConfidenceScore
from app.python_intelligence.schemas.shared.page_location import PageLocation


class Entity(PIBaseSchema):

    entity_id: UUID | None = None

    name: str

    entity_type: str

    confidence: ConfidenceScore

    page_location: PageLocation

    metadata: dict[str, Any] = Field(default_factory=dict)