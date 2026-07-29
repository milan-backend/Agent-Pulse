from uuid import UUID
from pydantic import Field

from app.core.enums.signals import SignalType
from app.python_intelligence.schemas.shared.base import PIBaseSchema
from app.python_intelligence.schemas.shared.page_location import PageLocation


class NavigationNode(PIBaseSchema):

    node_id: UUID | None = None

    signal_type: SignalType

    title: str

    level: int = Field(
        ge=0,
        description="Hierarchy level."
    )

    page_location: PageLocation

    parent_node_id: UUID | None = None

    metadata: dict = Field(default_factory=dict)