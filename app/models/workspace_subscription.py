from sqlalchemy import (
    Column,
    String,
    DateTime,
    ForeignKey
)

from sqlalchemy.orm import relationship

from sqlalchemy.dialects.postgresql import UUID

from datetime import datetime

import uuid

from app.db.session import Base


class WorkspaceSubscription(Base):
    __tablename__ = "workspace_subscriptions"

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

    plan_id = Column(
        UUID(as_uuid=True),
        ForeignKey(
            "plans.id"
        ),
        nullable=False,
        index=True
    )

    status = Column(
        String,
        default="active"
    )

    stripe_customer_id = Column(
        String,
        nullable=True
    )

    stripe_subscription_id = Column(
        String,
        nullable=True
    )

    current_period_end = Column(
        DateTime,
        nullable=True
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
        back_populates="subscription"
    )

    plan = relationship(
        "Plan",
        back_populates="subscriptions"
    )