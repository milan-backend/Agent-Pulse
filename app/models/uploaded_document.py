import uuid
from sqlalchemy import Column, String, Integer, LargeBinary, DateTime, ForeignKey, Boolean, Float
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func
from app.db.session import Base
from sqlalchemy.orm import relationship
class UploadedDocument(Base):
    __tablename__ = "uploaded_documents"

    # ====================================================================
    # 🔒 EXISTING INFRASTRUCTURE CORE CODES & IDENTIFIERS
    # ====================================================================
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

    # ====================================================================
    # ⚡ FAST LOOKUP CHANNELS (METADATA COLUMNS)
    # ====================================================================
    document_type = Column(String(100), nullable=True, index=True)      # e.g., 'Board Meeting Minutes'
    document_role = Column(String(100), nullable=True, index=True)      # e.g., 'Decision Making', 'Evidence'
    
    # FIXED: Using callable 'list' factory to prevent shared mutable state bugs
    departments = Column(JSONB, default=list, nullable=False)           # List of owner groups, e.g., ['Finance', 'Executive']
    topics = Column(JSONB, default=list, nullable=False)               # High-level categorical concept tags
    
    document_purpose = Column(String(500), nullable=True)               # Explicit target reason file exists
    planner_summary = Column(String(2000), nullable=True)               # Data-dense index summary read by upstream AI
    
    # Numerical Rankers & Weights
    authority_score = Column(Integer, default=50, nullable=False)       # Strict rule-based weight multiplier
    importance_score = Column(Integer, default=50, nullable=False)      # Structural density score
    freshness = Column(Float, default=1.0, nullable=False)              # Time-decay coefficient baseline
    
    # Temporal & Governance Primitives
    time_scope = Column(String(100), nullable=True, index=True)         # e.g., 'Q2 2026', 'Annual'
    document_status = Column(String(50), nullable=True, index=True)     # e.g., 'Approved', 'Draft'
    version = Column(String(50), default="1.0.0", nullable=False)       # Incremental variation step tracking
    approved = Column(Boolean, default=False, index=True, nullable=False)# Strict authorization gateway check flag
    
    # 🚀 FUTURE-PROOFING: Tracking schema revisions for easy downstream re-indexing campaigns
    knowledge_schema_version = Column(Integer, default=1, nullable=False)
    
    # Integrity Checksums
    sha256_hash = Column(String(64), nullable=True, index=True)         # Deduplication fingerprint token

    # ====================================================================
    # 📦 SLOW LOOKUP STORAGE (DEEP INTELLIGENCE CORE JSONB)
    # ====================================================================
    # RENAMED & FIXED: Clean knowledge context column using python 'dict' factory object
    knowledge_metadata = Column(JSONB, default=dict, nullable=False)

    # ====================================================================
    # ⏱️ TIMESTAMPS
    # ====================================================================
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now())

    # ====================================================================
    # 🔗 VIRTUAL RELATIONSHIPS (Does not modify SQL columns)
    # ====================================================================
    # Allows you to dynamically access child chunks in Python if needed
    # Make sure to add: from sqlalchemy.orm import relationship (at top of file)
    chunks = relationship("DocumentChunk", back_populates="document", cascade="all, delete-orphan")