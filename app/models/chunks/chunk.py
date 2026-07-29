import uuid

from sqlalchemy import (
    ForeignKey,
    Integer,
    LargeBinary,
    String,
)

from sqlalchemy.dialects.postgresql import UUID

from sqlalchemy.orm import (
    Mapped,
    mapped_column,
)

from app.db.session import Base


class Chunk(Base):

    __tablename__ = "chunks"

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
    )