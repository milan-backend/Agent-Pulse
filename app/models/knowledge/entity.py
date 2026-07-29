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


class Entity(Base):

    __tablename__ = "entities"

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

    chunk_id: Mapped[UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "chunks.id",
            ondelete="SET NULL",
        ),
    )

    name: Mapped[str] = mapped_column(
        String(500),
    )

    entity_type: Mapped[str] = mapped_column(
        String(100),
        index=True,
    )

    confidence: Mapped[float] = mapped_column(
        Float,
    )

    page_number: Mapped[int] = mapped_column(
        Integer,
    )

    metadata: Mapped[dict] = mapped_column(
        JSONB,
        default=dict,
    )