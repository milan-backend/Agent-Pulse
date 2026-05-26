from sqlalchemy import (
    Column,
    String,
    Float,
    DateTime,
    ForeignKey,
    JSON
)

from sqlalchemy.orm import relationship

from sqlalchemy.dialects.postgresql import UUID

from datetime import datetime

import uuid

from app.db.session import Base


class BillingEvent(Base):
    __tablename__ = "billing_events"

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
        index=True
    )

    agent_id = Column(
        UUID(as_uuid=True),
        ForeignKey(
            "agents.id",
            ondelete="SET NULL"
        ),
        nullable=True,
        index=True
    )

    step_id = Column(
        UUID(as_uuid=True),
        ForeignKey(
            "durable_steps.id",
            ondelete="SET NULL"
        ),
        nullable=True,
        index=True
    )

    event_type = Column(
        String,
        nullable=False
    )

    amount = Column(
        Float,
        default=0
    )

    currency = Column(
        String,
        default="usd"
    )

    event_metadata = Column(
        JSON,
        nullable=True
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )

    workspace = relationship(
        "Workspace",
        back_populates="billing_events"
    )