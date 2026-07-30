import uuid
from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column
from app.db.session import Base


class NavigationNode(Base):
    __tablename__ = "navigation_nodes"

    id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    workspace_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("workspaces.id", ondelete="CASCADE"),
        index=True,
    )

    document_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("uploaded_documents.id", ondelete="CASCADE"),
        index=True,
    )

    signal_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("document_signals.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    title: Mapped[str] = mapped_column(
        String(255),
    )

    node_type: Mapped[str] = mapped_column(
        String(100),
        default="section",
    )

    hierarchy_level: Mapped[int] = mapped_column(
        Integer,
        default=1,
    )

    page_number: Mapped[int] = mapped_column(
        Integer,
        default=1,
    )

    node_metadata: Mapped[dict] = mapped_column(
        "metadata",
        JSONB,
        default=dict,
    )