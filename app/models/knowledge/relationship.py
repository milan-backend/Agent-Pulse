import uuid

from sqlalchemy import (
    Float,
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


class Relationship(Base):

    __tablename__ = "relationships"

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

    source_entity_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "entities.id",
            ondelete="CASCADE",
        ),
    )

    target_entity_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "entities.id",
            ondelete="CASCADE",
        ),
    )

    relationship_type: Mapped[str] = mapped_column(
        String(100),
        index=True,
    )

    confidence: Mapped[float] = mapped_column(
        Float,
    )

    relationship_metadata: Mapped[dict] = mapped_column("metadata",
        JSONB,
        default=dict,
    )