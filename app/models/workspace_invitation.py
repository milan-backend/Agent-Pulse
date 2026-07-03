from sqlalchemy import (
    Column,
    String,
    DateTime,
    ForeignKey,
    Boolean,
    Enum
)
from sqlalchemy.orm import relationship  # 🟢 FIX: Imported from sqlalchemy.orm instead!
from sqlalchemy.dialects.postgresql import UUID
from app.db.session import Base
from app.db.enums import WorkspaceRole # 🛡️ Reuse your exact Enum system safely!
from datetime import datetime
import secrets
import uuid

class WorkspaceInvitation(Base):
    __tablename__ = "workspace_invitations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String, nullable=False, index=True)
    
    # Links directly to your existing workspace UUID types
    workspace_id = Column(
        UUID(as_uuid=True), 
        ForeignKey("workspaces.id", ondelete="CASCADE"), 
        nullable=False, 
        index=True
    )
    
    # 🛡️ Uses your exact internal structural RBAC Enum options
    role = Column(Enum(WorkspaceRole), nullable=False, default=WorkspaceRole.VIEWER)
    
    # Tracking links context strings
    token = Column(String, unique=True, nullable=False, index=True, default=lambda: secrets.token_urlsafe(32))
    is_accepted = Column(Boolean, default=False)
    
    invited_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime, nullable=False) # Configured during generation logic

    # Bidirectional link back to workspace
    workspace = relationship(
        "Workspace",
        back_populates="invitations"
    )