import uuid

from sqlalchemy import (
    ForeignKey,
    Integer,
    String,
)

from sqlalchemy.dialects.postgresql import (
    JSONB,
    UUID,
)

from sqlalchemy.orm import (
    Mapped,
    mapped_column,
)

from app.db.session import Base


class NavigationNode(Base):

    __tablename__ = "navigation_nodes"

    id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    document_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "uploaded_documents.id",
            ondelete="CASCADE",
        ),
        index=True,
    )

    signal_id: Mapped[UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "document_signals.id",
            ondelete="SET NULL",
        ),
    )

    title: Mapped[str] = mapped_column(
        String(500),
    )

    node_type: Mapped[str] = mapped_column(
        String(100),
        index=True,
    )

    hierarchy_level: Mapped[int] = mapped_column(
        Integer,
    )

    page_number: Mapped[int] = mapped_column(
        Integer,
    )

    metadata: Mapped[dict] = mapped_column(
        JSONB,
        default=dict,
    )