from sqlalchemy import (
    Column,
    String,
    Boolean,
    DateTime,
    ForeignKey,
    Float,
    Integer,
    Enum
)

from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID

from app.db.session import Base
from app.db.enums import AgentStatus

from datetime import datetime
import uuid


class Agent(Base):
    __tablename__ = "agents"

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

    created_by = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id"),
        nullable=False,
        index=True
    )

    name = Column(
        String,
        nullable=False,
        index=True
    )

    description = Column(
        String,
        nullable=True
    )

    status = Column(
        Enum(AgentStatus),
        nullable=False,
        default=AgentStatus.ACTIVE,
        index=True
    )

    api_key_hash = Column(
        String,
        nullable=False
    )

    key_id = Column(
        String,
        nullable=False,
        unique=True,
        index=True
    )

    allowed_tasks = Column(
        String,
        nullable=True
    )

    total_cost = Column(
        Float,
        default=0
    )

    mission_count = Column(
        Integer,
        default=0
    )

    is_active = Column(
        Boolean,
        default=True
    )

    is_killed = Column(
        Boolean,
        default=False
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

    workspace = relationship(
        "Workspace",
        back_populates="agents"
    )

    creator = relationship(
        "User",
        foreign_keys=[created_by],
        back_populates="created_agents"
    )

    steps = relationship(
        "DurableStep",
        back_populates="agent",
        cascade="all, delete"
    )

    usage_events = relationship(
        "Usage",
        back_populates="agent",
        cascade="all, delete"
    )

    policy = relationship(
        "AgentPolicy",
        backref="agent",
        uselist=False,
        cascade="all, delete"
    )