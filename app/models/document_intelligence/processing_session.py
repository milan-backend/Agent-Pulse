# processing_session.py
import uuid
from sqlalchemy import Boolean, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column
from app.db.session import Base


class ProcessingSession(Base):
    __tablename__ = "processing_sessions"

    id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    document_id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("uploaded_documents.id", ondelete="CASCADE"), index=True)
    current_stage: Mapped[str] = mapped_column(String(100), default="initialized")
    is_complete: Mapped[bool] = mapped_column(Boolean, default=False)