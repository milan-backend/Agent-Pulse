import uuid
from datetime import datetime
from sqlalchemy import (
    Column,
    String,
    Integer,
    DateTime,
    ForeignKey,
    Boolean,
    JSON,
    UniqueConstraint
)
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID

from app.db.session import Base

class WorkspaceConfig(Base):
    __tablename__ = "workspace_configs"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )

    # 1. WORKSPACE LINK: Removed unique=True
    workspace_id = Column(
        UUID(as_uuid=True),
        ForeignKey("workspaces.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    # 2. AGENT LINK: Added to scope databases to specific agents
    agent_id = Column(
        UUID(as_uuid=True),
        ForeignKey("agents.id", ondelete="CASCADE"),
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

    sync_all_tables = Column(Boolean, default=True, nullable=False)
    allowed_tables = Column(JSON, default=list, nullable=False) 

    # 3. RELATIONSHIPS
    workspace = relationship(
        "Workspace",
        back_populates="configs" # 👈 Matches the new plural name in workspace.py
    )

    agent = relationship(
        "Agent",
        backref="db_configs" # 👈 Automatically adds .db_configs to the Agent model
    )

    # 4. COMPOSITE UNIQUE CONSTRAINT
    __table_args__ = (
        UniqueConstraint("workspace_id", "agent_id", name="uq_workspace_agent_db_config"),
    )