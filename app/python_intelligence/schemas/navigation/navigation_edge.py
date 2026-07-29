from uuid import UUID

from app.core.enums.navigation import NavigationRelation
from app.python_intelligence.schemas.shared.base import PIBaseSchema


class NavigationEdge(PIBaseSchema):

    source_node_id: UUID

    target_node_id: UUID

    relation: NavigationRelation