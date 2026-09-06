from sqlalchemy import (
    Column,
    String,
    Integer,
    DateTime,
    ForeignKey
)
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
import uuid
from sqlalchemy import Column, Boolean, JSON

from app.db.session import Base

class WorkspaceConfig(Base):
    __tablename__ = "workspace_configs"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )

    # 1-to-1 relationship with your existing Workspace model
    workspace_id = Column(
        UUID(as_uuid=True),
        ForeignKey("workspaces.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
        index=True
    )

    # --- Database Connection Details (The Muscle) ---
    db_type = Column(String, nullable=False, default="postgresql")
    db_host = Column(String, nullable=False)
    db_port = Column(Integer, nullable=False)
    db_name = Column(String, nullable=False)
    db_username = Column(String, nullable=False)
    
    # 🚨 CRITICAL: Encrypted at rest. Never store raw passwords.
    db_password_encrypted = Column(String, nullable=False)

    # --- Identity Verification (The Iron Wall) ---
    # The URL where we fetch the company's public keys to verify JWTs
    jwks_url = Column(String, nullable=False)

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )
    
    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )

    # Add these to WorkspaceConfig
    sync_all_tables = Column(Boolean, default=True, nullable=False)
    allowed_tables = Column(JSON, default=list, nullable=False) # Stores ["users", "orders"] if sync_all_tables is False

    # Relationship back to the Workspace
    workspace = relationship(
        "Workspace",
        back_populates="config"
    )