from app.python_intelligence.schemas.shared.base import PIBaseSchema
from app.python_intelligence.schemas.shared.document_reference import (
    DocumentReference,
)

from .knowledge_graph import KnowledgeGraph
from .semantic_metadata import SemanticMetadata


class SemanticPacket(PIBaseSchema):

    document: DocumentReference

    knowledge_graph: KnowledgeGraph

    semantic_metadata: SemanticMetadata