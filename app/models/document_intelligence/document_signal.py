import uuid

from sqlalchemy import (
    Float,
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


class DocumentSignal(Base):

    __tablename__ = "document_signals"

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
    )

    processing_session_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "processing_sessions.id",
            ondelete="CASCADE",
        ),
    )

    document_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "uploaded_documents.id",
            ondelete="CASCADE",
        ),
    )

    detector: Mapped[str] = mapped_column(
        String(100),
    )

    signal_type: Mapped[str] = mapped_column(
        String(100),
    )

    page_number: Mapped[int] = mapped_column(
        Integer,
    )

    confidence: Mapped[float] = mapped_column(
        Float,
    )

    content: Mapped[str | None] = mapped_column(
        String,
    )

    signal_metadata: Mapped[dict] = mapped_column("metadata",
        JSONB,
        default=dict,
    )