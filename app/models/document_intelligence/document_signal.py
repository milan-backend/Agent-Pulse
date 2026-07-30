import uuid
from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column
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
        index=True,
    )

    signal_type: Mapped[str] = mapped_column(
        String(100),
        index=True,
    )

    content: Mapped[str] = mapped_column(
        Text,
    )

    signal_metadata: Mapped[dict] = mapped_column(
        "metadata",
        JSONB,
        default=dict,
    )