from pydantic import Field

from app.python_intelligence.schemas.navigation.navigation_edge import NavigationEdge
from app.python_intelligence.schemas.navigation.navigation_node import NavigationNode
from app.python_intelligence.schemas.shared.base import PIBaseSchema


class NavigationGraph(PIBaseSchema):

    nodes: list[NavigationNode] = Field(default_factory=list)

    edges: list[NavigationEdge] = Field(default_factory=list)