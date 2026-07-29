from uuid import UUID

from app.python_intelligence.schemas.shared.base import PIBaseSchema


class Relationship(PIBaseSchema):

    relationship_id: UUID | None = None

    source_entity_id: UUID

    target_entity_id: UUID

    relationship_type: str

    confidence: float