from sqlalchemy import (
    Column,
    String,
    Boolean,
    DateTime
)
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
import uuid
from app.db.session import Base

class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False, index=True)
    
    # ⚡ MODIFIED FOR SSO: password_hash is now optional (nullable=True)
    password_hash = Column(String, nullable=True)

    # 🔮 NEW FOR SSO: Track authentication provider profiles safely
    sso_provider = Column(String, nullable=True, index=True) # e.g., "google", "github"
    sso_id = Column(String, nullable=True, index=True)       # Provider's unique user string

    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    email_verification_token = Column(String, nullable=True, index=True)
    email_verification_expiry = Column(DateTime, nullable=True)
    reset_password_token = Column(String, nullable=True, index=True)
    reset_password_expires = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships remain exactly the same
    workspaces = relationship("Workspace", foreign_keys="Workspace.owner_id", back_populates="owner")
    memberships = relationship("WorkspaceMember", foreign_keys="WorkspaceMember.user_id", back_populates="user")
    created_agents = relationship("Agent", foreign_keys="Agent.created_by", back_populates="creator")
    refresh_tokens = relationship("RefreshToken", back_populates="user", cascade="all, delete-orphan")