import uuid
from sqlalchemy import ForeignKey, Integer, LargeBinary, String
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column
from app.db.session import Base


class Chunk(Base):
    __tablename__ = "chunks"

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

    encrypted_content: Mapped[bytes] = mapped_column(
        LargeBinary,
        nullable=False,
    )

    encryption_iv: Mapped[bytes] = mapped_column(
        LargeBinary,
        nullable=False,
    )

    content_hash: Mapped[str] = mapped_column(
        String(64),
        index=True,
    )

    token_count: Mapped[int] = mapped_column(
        Integer,
        default=0,
    )

    # Safe Python attribute name mapped to the physical "metadata" column in PostgreSQL
    chunk_metadata: Mapped[dict] = mapped_column(
        "metadata",
        JSONB,
        default=dict,
    )