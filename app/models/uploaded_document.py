import uuid
from sqlalchemy import Column, String, Integer, LargeBinary, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from app.db.session import Base

class UploadedDocument(Base):
    __tablename__ = "uploaded_documents"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    filename = Column(String(255), nullable=False)
    
    # Secure Two-Tier Storage: Encrypted raw binary bytes and its random Initialization Vector (IV)
    encrypted_file_data = Column(LargeBinary, nullable=False)
    encryption_iv = Column(LargeBinary, nullable=False)
    
    # Isolation Boundary Context Scopes
    workspace_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    agent_id = Column(UUID(as_uuid=True), nullable=True, index=True)  # Null means shared across all workspace agents
    
    # File Audit Metadata
    file_size = Column(Integer, nullable=False)  # Stored in bytes to calculate premium limit thresholds
    mime_type = Column(String(100), nullable=False)  # e.g., 'application/pdf', 'text/plain'
    status = Column(String(50), default="processing", nullable=False)  # processing, ready, failed
    
    # Operational Audit Tracking Tracker
    uploaded_by = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now())