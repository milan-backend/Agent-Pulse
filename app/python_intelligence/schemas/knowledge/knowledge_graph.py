from pydantic import Field

from app.python_intelligence.schemas.shared.base import PIBaseSchema

from .entity import Entity
from .relationship import Relationship


class KnowledgeGraph(PIBaseSchema):

    entities: list[Entity] = Field(default_factory=list)

    relationships: list[Relationship] = Field(default_factory=list)