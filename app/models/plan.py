from sqlalchemy import (
    Column,
    String,
    Float,
    Integer,
    JSON,
    DateTime
)

from sqlalchemy.dialects.postgresql import UUID

from datetime import datetime

import uuid

from sqlalchemy.orm import relationship

from app.db.session import Base


class Plan(Base):
    __tablename__ = "plans"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )

    name = Column(
        String,
        nullable=False,
        unique=True,
        index=True
    )

    price = Column(
        Float,
        default=0
    )

    max_agents = Column(
        Integer,
        default=1
    )

    max_monthly_cost = Column(
        Float,
        default=10
    )

    max_concurrent_runs = Column(
        Integer,
        default=1
    )

    features = Column(
        JSON,
        nullable=True,
        default=lambda: {

            # CORE EXECUTION
            "agent_execution": True,
            "background_agents": True,
            "mcp_access": False,

            # RUNTIME CONTROL
            "single_agent_pause": True,
            "single_agent_resume": True,
            "single_agent_kill": True,

            "workspace_kill_all": False,
            "workspace_resume_all": False,

            # ADVANCED GOVERNANCE
            "advanced_runtime_controls": True,
            "loop_detection": True,
            "budget_control": True,
            "retry_control": True,
            "execution_timeout_control": True,

            # OBSERVABILITY
            "analytics": True,
            "audit_logs": True,
            "usage_logs": True,
            "missions": True,
            "live_websocket_updates": True,

            # TEAM FEATURES
            "multi_workspace": False,
            "team_collaboration": False,
            "rbac": False,

            # ENTERPRISE FEATURES
            "priority_execution": False,
            "dedicated_runtime": False,
            "maintenance_mode": False
        }
    )

    limits = Column(
        JSON,
        nullable=True,
        default=lambda: {

            "max_agents": 1,

            "max_monthly_cost": 10,

            "max_concurrent_runs": 1,

            "max_team_members": 1,

            "max_runtime_hours": 10
        }
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

    subscriptions = relationship(
    "WorkspaceSubscription",
    back_populates="plan",
    cascade="all, delete"
)