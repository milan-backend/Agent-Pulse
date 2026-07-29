import uuid

from sqlalchemy import (
    Float,
    ForeignKey,
    Integer,
    String,
)

from sqlalchemy.dialects.postgresql import UUID

from sqlalchemy.orm import (
    Mapped,
    mapped_column,
)

from app.db.session import Base


class DetectorExecution(Base):

    __tablename__ = "detector_executions"

    id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    processing_session_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "processing_sessions.id",
            ondelete="CASCADE",
        ),
    )

    detector_name: Mapped[str] = mapped_column(
        String(100),
    )

    status: Mapped[str] = mapped_column(
        String(50),
    )

    execution_time_ms: Mapped[float] = mapped_column(
        Float,
    )

    signals_generated: Mapped[int] = mapped_column(
        Integer,
        default=0,
    )

    error_message: Mapped[str | None] = mapped_column(
        String,
    )