import uuid
from sqlalchemy import ForeignKey, String
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column
from app.db.session import Base


class DocumentProfile(Base):
    __tablename__ = "document_profiles"

    id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    document_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("uploaded_documents.id", ondelete="CASCADE"),
        index=True,
    )

    document_role: Mapped[str] = mapped_column(
        String(150),
        index=True,
    )

    department: Mapped[str | None] = mapped_column(
        String(150),
        nullable=True,
    )

    profile_metadata: Mapped[dict] = mapped_column(
        "metadata",
        JSONB,
        default=dict,
    )