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


class SemanticMetadata(Base):

    __tablename__ = "semantic_metadata"

    document_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "uploaded_documents.id",
            ondelete="CASCADE",
        ),
        primary_key=True,
    )

    summary: Mapped[str | None] = mapped_column(
        String,
    )

    language: Mapped[str | None] = mapped_column(
        String(30),
    )

    keywords: Mapped[list] = mapped_column(
        JSONB,
        default=list,
    )

    topics: Mapped[list] = mapped_column(
        JSONB,
        default=list,
    )

    metadata: Mapped[dict] = mapped_column(
        JSONB,
        default=dict,
    )