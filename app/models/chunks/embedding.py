import uuid

from sqlalchemy import (
    ForeignKey,
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


class Embedding(Base):

    __tablename__ = "embeddings"

    id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    chunk_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "chunks.id",
            ondelete="CASCADE",
        ),
        unique=True,
    )

    vector_provider: Mapped[str] = mapped_column(
        String(100),
    )

    embedding_model: Mapped[str] = mapped_column(
        String(200),
    )

    vector_id: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        index=True,
    )

    embedding_metadata: Mapped[dict] = mapped_column("metadata",
        JSONB,
        default=dict,
    )