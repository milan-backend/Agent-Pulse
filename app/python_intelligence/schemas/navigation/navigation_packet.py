from app.python_intelligence.schemas.navigation.navigation_graph import NavigationGraph
from app.python_intelligence.schemas.shared.document_reference import DocumentReference
from app.python_intelligence.schemas.shared.base import PIBaseSchema


class NavigationPacket(PIBaseSchema):

    document: DocumentReference

    graph: NavigationGraph