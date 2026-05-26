from sqlalchemy import (
    Column,
    String,
    Float,
    DateTime,
    ForeignKey
)

from sqlalchemy.orm import relationship

from sqlalchemy.dialects.postgresql import UUID

from datetime import datetime

import uuid

from app.db.session import Base


class PaymentTransaction(Base):
    __tablename__ = "payment_transactions"

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

    stripe_payment_intent_id = Column(
        String,
        nullable=True,
        index=True
    )

    amount = Column(
        Float,
        default=0
    )

    currency = Column(
        String,
        default="usd"
    )

    status = Column(
        String,
        default="pending"
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )

    workspace = relationship(
        "Workspace",
        back_populates="payment_transactions"
    )