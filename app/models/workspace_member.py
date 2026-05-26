from sqlalchemy import (
    Column,
    DateTime,
    ForeignKey,
    UniqueConstraint,
    Enum
)

from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID

from app.db.session import Base
from app.db.enums import WorkspaceRole

from datetime import datetime
import uuid


class WorkspaceMember(Base):
    __tablename__ = "workspace_members"

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

    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    role = Column(
        Enum(WorkspaceRole),
        nullable=False,
        default=WorkspaceRole.VIEWER
    )

    invited_by = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id"),
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
        back_populates="members"
    )

    user = relationship(
        "User",
        foreign_keys=[user_id],
        back_populates="memberships"
    )

    __table_args__ = (
        UniqueConstraint(
            "workspace_id",
            "user_id",
            name="uq_workspace_user"
        ),
    )