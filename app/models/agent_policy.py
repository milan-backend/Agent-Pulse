from sqlalchemy import (
    Column,
    Integer,
    Float,
    Boolean,
    DateTime,
    ForeignKey
)

from sqlalchemy.dialects.postgresql import UUID

from datetime import datetime
import uuid

from app.db.session import Base


class AgentPolicy(Base):
    __tablename__ = "agent_policies"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )

    agent_id = Column(
        UUID(as_uuid=True),
        ForeignKey(
            "agents.id",
            ondelete="CASCADE"
        ),
        nullable=False,
        unique=True,
        index=True
    )

    max_steps = Column(
        Integer,
        default=25
    )

    max_retries = Column(
        Integer,
        default=3
    )

    max_cost = Column(
        Float,
        default=10
    )

    max_repeated_tasks = Column(
        Integer,
        default=3
    )

    enable_idempotency = Column(
        Boolean,
        default=True
    )

    enable_budget_control = Column(
        Boolean,
        default=True
    )

    enable_retry_control = Column(
        Boolean,
        default=True
    )

    enable_loop_detection = Column(
        Boolean,
        default=True
    )

    max_execution_time_seconds = Column(
        Integer,
        default=300
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )

    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )