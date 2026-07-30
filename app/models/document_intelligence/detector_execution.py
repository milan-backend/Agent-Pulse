# detector_execution.py
import uuid
from sqlalchemy import ForeignKey, String
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column
from app.db.session import Base


class DetectorExecution(Base):
    __tablename__ = "detector_executions"

    id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    document_id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("uploaded_documents.id", ondelete="CASCADE"), index=True)
    detector_name: Mapped[str] = mapped_column(String(150), index=True)
    status: Mapped[str] = mapped_column(String(50), default="pending")
    execution_metadata: Mapped[dict] = mapped_column("metadata", JSONB, default=dict)