import uuid
from sqlalchemy import ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column
from app.db.session import Base


class NavigationEdge(Base):
    __tablename__ = "navigation_edges"

    id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    document_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("uploaded_documents.id", ondelete="CASCADE"),
        index=True,
    )

    source_node_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("navigation_nodes.id", ondelete="CASCADE"),
        index=True,
    )

    target_node_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("navigation_nodes.id", ondelete="CASCADE"),
        index=True,
    )

    relationship_type: Mapped[str] = mapped_column(
        String(100),
        default="parent_child",
    )