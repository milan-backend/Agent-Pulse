import logging
from typing import List, Any
from sqlalchemy.orm import Session
from uuid import UUID

from app.models.navigation.navigation_node import NavigationNode
from app.models.navigation.navigation_edge import NavigationEdge
from app.core.enums.navigation import NavigationRelationship
from app.core.enums.signals import SignalType
from app.python_intelligence.signal_store import SignalStore

logger = logging.getLogger(__name__)

class NavigationService:
    """
    Builds and manages document navigation node trees and relationship graphs
    from Python Intelligence heading signals.
    """

    def __init__(self, db: Session, document_id: UUID, workspace_id: UUID):
        self.db = db
        self.document_id = document_id
        self.workspace_id = workspace_id
        self.signal_store = SignalStore(db, document_id, workspace_id)

    def build_navigation_tree(self) -> int:
        """
        Reads heading signals and constructs navigation nodes and edges
        for precise Planner AI traversal.
        """
        try:
            logger.info(f"Building navigation tree for Document {self.document_id}")
            heading_signals = self.signal_store.get_signals_by_type(SignalType.HEADING)

            if not heading_signals:
                logger.warning(f"No heading signals found for document {self.document_id}. Skipping navigation tree build.")
                return 0

            created_nodes = []
            
            # Create root document node
            root_node = NavigationNode(
                document_id=self.document_id,
                title="Document Root",
                node_type="root",
                hierarchy_level=0,
                page_number=1,
                metadata={"type": "root_container"}
            )
            self.db.add(root_node)
            self.db.flush()
            created_nodes.append(root_node)

            previous_node = root_node

            # Convert heading signals to navigation nodes
            for sig in heading_signals:
                level = sig.metadata.get("heading_level", 1)
                node = NavigationNode(
                    document_id=self.document_id,
                    signal_id=sig.id,
                    title=sig.content,
                    node_type=f"heading_l{level}",
                    hierarchy_level=level,
                    page_number=sig.page_number,
                    metadata=sig.metadata
                )
                self.db.add(node)
                self.db.flush()

                # Create sequential edge (FOLLOWS relationship)
                edge = NavigationEdge(
                    document_id=self.document_id,
                    source_node_id=previous_node.id,
                    target_node_id=node.id,
                    relationship_type=NavigationRelationship.FOLLOWS
                )
                self.db.add(edge)
                
                previous_node = node
                created_nodes.append(node)

            self.db.commit()
            logger.info(f"Successfully created {len(created_nodes)} navigation nodes for doc {self.document_id}")
            return len(created_nodes)

        except Exception as e:
            self.db.rollback()
            logger.error(f"Failed to build navigation tree: {e}")
            return 0