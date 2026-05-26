from sqlalchemy import (
    Column,
    String,
    DateTime,
    ForeignKey,
    Float,
    Integer,
    Boolean,
    Enum,
    JSON
)

from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID

from app.db.session import Base
from app.db.enums import UsageType

from datetime import datetime
import uuid


class Usage(Base):
    __tablename__ = "usage_events"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
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

    step_id = Column(
        UUID(as_uuid=True),
        ForeignKey("durable_steps.id", ondelete="SET NULL"),
        nullable=True,
        index=True
    )

    event_type = Column(
        Enum(UsageType),
        nullable=False,
        index=True
    )

    status = Column(
        String,
        nullable=True,
        index=True
    )

    model_used = Column(
        String,
        nullable=True
    )

    request_id = Column(
        String,
        nullable=True,
        index=True
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

    total_tokens = Column(
        Integer,
        default=0
    )

    latency_ms = Column(
        Integer,
        nullable=True
    )

    cache_hit = Column(
        Boolean,
        default=False
    )

    event_metadata = Column(
        JSON,
        nullable=True
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow,
        index=True
    )

    agent = relationship(
        "Agent",
        back_populates="usage_events"
    )

    step = relationship(
        "DurableStep",
        back_populates="usage_events"
    )