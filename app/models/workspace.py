from sqlalchemy import (
    Column,
    String,
    DateTime,
    ForeignKey,
    Boolean
)

from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID

from app.db.session import Base

from app.models.workspace_subscription import (
    WorkspaceSubscription
)

from app.models.billing_event import (
    BillingEvent
)

from app.models.payment_transaction import (
    PaymentTransaction
)

from app.models.workspace_usage_limit import (
    WorkspaceUsageLimit
)

from datetime import datetime
import uuid


class Workspace(Base):
    __tablename__ = "workspaces"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )

    name = Column(
        String,
        nullable=False
    )

    slug = Column(
        String,
        unique=True,
        nullable=True,
        index=True
    )

    type = Column(
        String,
        nullable=False,
        default="personal"
    )

    owner_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id"),
        nullable=False,
        index=True
    )

    is_active = Column(
        Boolean,
        default=True
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

    owner = relationship(
        "User",
        foreign_keys=[owner_id],
        back_populates="workspaces"
    )

    members = relationship(
        "WorkspaceMember",
        back_populates="workspace",
        cascade="all, delete"
    )

    agents = relationship(
        "Agent",
        back_populates="workspace",
        cascade="all, delete"
    )

    subscription = relationship(
        WorkspaceSubscription,
        back_populates="workspace",
        uselist=False,
        cascade="all, delete"
    )

    billing_events = relationship(
        BillingEvent,
        back_populates="workspace",
        cascade="all, delete"
    )

    payment_transactions = relationship(
        PaymentTransaction,
        back_populates="workspace",
        cascade="all, delete"
    )

    usage_limits = relationship(
        WorkspaceUsageLimit,
        back_populates="workspace",
        uselist=False,
        cascade="all, delete"
    )


    invitations = relationship(
        "WorkspaceInvitation",
        back_populates="workspace",
        cascade="all, delete-orphan"
    )