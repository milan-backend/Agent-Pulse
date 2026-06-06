from sqlalchemy import (
    Column,
    String,
    DateTime,
    ForeignKey,
    UniqueConstraint,
    Boolean
)
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID

from datetime import datetime
import uuid

from app.db.session import Base


class UserAPIKey(Base):
    __tablename__ = "user_api_keys"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )

    # User Link: For personal user-level keys
    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=True,
        index=True
    )

    # Workspace Link: For shared workspace-level keys
    workspace_id = Column(
        UUID(as_uuid=True),
        ForeignKey("workspaces.id", ondelete="CASCADE"),
        nullable=True,
        index=True
    )

    provider = Column(
        String,
        nullable=False,
        index=True  # 'gemini', 'openai', etc.
    )

    encrypted_api_key = Column(
        String,
        nullable=False
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

    is_default = Column(Boolean, 
     default=False, 
     nullable=False)

    # Relationships
    user = relationship(
        "User",
        backref="api_keys"
    )
    
    workspace = relationship(
        "Workspace", 
        backref="workspace_api_keys"
    )

    # Database Security Constraints:
    # Prevents duplicate keys for the same provider inside a workspace or personal account
    __table_args__ = (
        UniqueConstraint("user_id", "provider", name="uq_user_provider_key"),
        UniqueConstraint("workspace_id", "provider", name="uq_workspace_provider_key"),
    )