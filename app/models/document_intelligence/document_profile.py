from sqlalchemy import (
    Boolean,
    ForeignKey,
    Integer,
    String,
    Float,
)

from sqlalchemy.dialects.postgresql import UUID, JSONB

from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship

from app.db.session import Base


class DocumentProfile(Base):

    __tablename__ = "document_profiles"

    document_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "uploaded_documents.id",
            ondelete="CASCADE",
        ),
        primary_key=True,
    )

    # ------------------------------
    # Document Classification
    # ------------------------------

    category: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
        index=True,
    )

    language: Mapped[str | None] = mapped_column(
        String(25),
        nullable=True,
        index=True,
    )

    summary: Mapped[str | None] = mapped_column(
        String(5000),
        nullable=True,
    )

    # ------------------------------
    # Statistics
    # ------------------------------

    total_pages: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
    )

    total_words: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
    )

    total_chunks: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
    )

    reading_time_minutes: Mapped[float] = mapped_column(
        Float,
        default=0,
        nullable=False,
    )

    # ------------------------------
    # Intelligence
    # ------------------------------

    keywords: Mapped[list] = mapped_column(
        JSONB,
        default=list,
        nullable=False,
    )

    topics: Mapped[list] = mapped_column(
        JSONB,
        default=list,
        nullable=False,
    )

    metadata: Mapped[dict] = mapped_column(
        JSONB,
        default=dict,
        nullable=False,
    )

    # ------------------------------
    # Processing
    # ------------------------------

    is_processed: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
    )

    profile_version: Mapped[int] = mapped_column(
        Integer,
        default=1,
        nullable=False,
    )

    # ------------------------------
    # Relationship
    # ------------------------------

    document = relationship(
        "UploadedDocument",
        backref="document_profile",
        uselist=False,
    )