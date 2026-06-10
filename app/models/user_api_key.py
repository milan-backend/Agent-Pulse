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

    # Agent Link: Existing Tier-1 Agent-specific override tracking
    agent_id = Column(
        UUID(as_uuid=True),
        ForeignKey("agents.id", ondelete="CASCADE"),
        nullable=True,
        index=True
    )

    # Core Provider Engine ('openai' or 'gemini' stored as clean lowercase)
    provider = Column(
        String,
        nullable=False,
        index=True  
    )

    # Existing field acting as model_name (e.g., 'gpt-4o', 'gemini-2.5-flash-lite')
    model_version = Column(
        String,
        nullable=True,
        index=True  
    )

    encrypted_api_key = Column(
        String,
        nullable=False
    )

    # Existing default marker (Acts as your Workspace Global Default Fallback)
    is_default = Column(
        Boolean, 
        default=False, 
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

    # =========================================================================
    # NEW ARCHITECTURE UPGRADE ADDITIONS
    # =========================================================================
    
    # Custom Label to distinguish multiple keys from the same provider
    provider_name = Column(
        String,
        nullable=True,
        default="Workspace Provider"
    )

    # Stores assigned agent UUIDs cleanly as a comma-separated text string
    assigned_agents_data = Column(
        String,
        nullable=True,
        default=""
    )

    # --- PYTHON PROPERTY ALIASES FOR CLEAN UPGRADE ARCHITECTURE ---

    @property
    def is_global_default(self) -> bool:
        """Alias for frontend/service clarity mapping to existing is_default column."""
        return self.is_default

    @is_global_default.setter
    def is_global_default(self, value: bool):
        self.is_default = value

    @property
    def model_name(self) -> str:
        """Alias for frontend/service clarity mapping to existing model_version column."""
        return self.model_version

    @model_name.setter
    def model_name(self, value: str):
        self.model_version = value

    @property
    def assigned_agents(self) -> list:
        """Parses and exposes assigned_agents_data string elements cleanly as a Python list array."""
        if not self.assigned_agents_data or not self.assigned_agents_data.strip():
            return []
        return [s.strip() for s in self.assigned_agents_data.split(",") if s.strip()]

    @assigned_agents.setter
    def assigned_agents(self, agent_id_list: list):
        """Converts incoming lists/arrays cleanly into a structured string format pattern for the DB."""
        if not agent_id_list:
            self.assigned_agents_data = ""
        else:
            self.assigned_agents_data = ",".join([str(uid).strip() for uid in agent_id_list if uid])

    # =========================================================================
    # RELATIONSHIPS & CONSTRAINTS
    # =========================================================================
    user = relationship("User", backref="api_keys")
    workspace = relationship("Workspace", backref="workspace_api_keys")
    agent = relationship("Agent", backref="agent_api_keys")

    __table_args__ = (
        UniqueConstraint("user_id", "provider", "model_version", name="uq_user_provider_model_key"),
        # Note: We omitted a strict single workspace+provider constraint here to allow 
        # users to add unlimited keys of the same type under one workspace.
    )