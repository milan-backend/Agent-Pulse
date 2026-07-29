import uuid

from sqlalchemy import (
    ForeignKey,
    Integer,
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


class ChunkIndex(Base):

    __tablename__ = "chunk_index"

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

    navigation_node_id: Mapped[UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "navigation_nodes.id",
            ondelete="SET NULL",
        ),
    )

    page_start: Mapped[int] = mapped_column(
        Integer,
    )

    page_end: Mapped[int] = mapped_column(
        Integer,
    )

    chunk_metadata: Mapped[dict] = mapped_column("metadata",
        JSONB,
        default=dict,
    )