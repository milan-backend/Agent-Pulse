from sqlalchemy import (
    Column,
    Integer,
    Float,
    DateTime,
    ForeignKey
)

from sqlalchemy.orm import relationship

from sqlalchemy.dialects.postgresql import UUID

from datetime import datetime

import uuid

from app.db.session import Base


class WorkspaceUsageLimit(Base):
    __tablename__ = "workspace_usage_limits"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
       default=uuid.uuid4
    )

    workspace_id = Column(
        UUID(as_uuid=True),
        ForeignKey(
            "workspaces.id",
            ondelete="CASCADE"
        ),
        nullable=False,
        unique=True,
        index=True
    )

    max_monthly_tokens = Column(
        Integer,
        default=100000
    )

    max_monthly_cost = Column(
        Float,
        default=10
    )

    max_agents = Column(
        Integer,
        default=5
    )

    max_parallel_runs = Column(
        Integer,
        default=2
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

    workspace = relationship(
        "Workspace",
        back_populates="usage_limits"
    )