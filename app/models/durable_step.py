from sqlalchemy import (
    Column,
    String,
    DateTime,
    ForeignKey,
    Float,
    Integer,
    Boolean,
    UniqueConstraint,
    Enum,
    JSON
)

from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID

from app.db.session import Base
from app.db.enums import StepStatus

from datetime import datetime
import uuid


class DurableStep(Base):
    __tablename__ = "durable_steps"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )

    retry_of_step_id = Column(
        UUID(as_uuid=True),
        ForeignKey("durable_steps.id"),
        nullable=True,
        index=True
    )

    workspace_id = Column(
        UUID(as_uuid=True),
        ForeignKey("workspaces.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    agent_id = Column(
        UUID(as_uuid=True),
        ForeignKey("agents.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    task_name = Column(
        String,
        nullable=False,
        index=True
    )

    status = Column(
        Enum(StepStatus),
        nullable=False,
        default=StepStatus.PENDING,
        index=True
    )

    input_data = Column(
        JSON,
        nullable=True
    )

    output_data = Column(
        JSON,
        nullable=True
    )

    idempotency_key = Column(
        String,
        nullable=False,
        index=True
    )

    cache_hit = Column(
        Boolean,
        default=False
    )

    retry_count = Column(
        Integer,
        default=0
    )

    execution_time_ms = Column(
        Integer,
        nullable=True
    )

    model_used = Column(
        String,
        nullable=True
    )

    cost = Column(
        Float,
        default=0
    )

    prompt_tokens = Column(
        Integer,
        default=0
    )

    completion_tokens = Column(
        Integer,
        default=0
    )

    runtime_controlled = Column(
        Boolean,
        default=False
    )

    pause_reason = Column(
        String,
        nullable=True
    )

    paused_at = Column(
        DateTime,
        nullable=True
    )

    resumed_at = Column(
        DateTime,
        nullable=True
    )

    killed_at = Column(
        DateTime,
        nullable=True
    )

    killed_by = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id"),
        nullable=True
    )

    resumed_by = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id"),
        nullable=True
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow,
        index=True
    )

    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )

    error_message = Column(
        String,
        nullable=True
    )

    started_at = Column(
        DateTime,
        nullable=True
    )

    completed_at = Column(
        DateTime,
        nullable=True
    )

    agent = relationship(
        "Agent",
        back_populates="steps"
    )

    usage_events = relationship(
        "Usage",
        back_populates="step"
    )

    __table_args__ = (
        UniqueConstraint(
            "workspace_id",
            "idempotency_key",
            name="uq_workspace_idempotency"
        ),
    )