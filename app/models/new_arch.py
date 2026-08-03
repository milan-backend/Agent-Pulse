import uuid
from sqlalchemy import Column, String, Integer, Text, DateTime, ForeignKey, Index
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

# 🟢 Import the REAL Base from your app
from app.db.session import Base 

# ====================================================================
# 1. DOCUMENT SECTIONS (The Universal Navigation Model)
# ====================================================================
# The Smart Navigation AI reads this table directly to route queries.
class DocumentSection(Base):
    __tablename__ = "document_sections"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    document_id = Column(UUID(as_uuid=True), ForeignKey("uploaded_documents.id", ondelete="CASCADE"), index=True, nullable=False)
    workspace_id = Column(UUID(as_uuid=True), index=True, nullable=False)
    agent_id = Column(UUID(as_uuid=True), index=True, nullable=True)

    section_code = Column(String(50), nullable=False)
    title = Column(String(255), nullable=False)
    
    # 🟢 Materialized Path (Breadcrumbs)
    # Eliminates the need for the LLM to do relational joins.
    parent_path = Column(String(500), nullable=True) 
    parent_section_id = Column(UUID(as_uuid=True), ForeignKey("document_sections.id", ondelete="CASCADE"), nullable=True)
    
    start_page = Column(Integer, nullable=True)
    end_page = Column(Integer, nullable=True)

    # 🟢 Semantic Routing Attributes (Read by the Querying Navigation AI)
    content_type = Column(String(100), default="narrative_paragraph", nullable=False)  
    semantic_summary = Column(Text, nullable=True)                                     
    key_entities = Column(JSONB, default=list, nullable=False)                       
    chunking_strategy_hint = Column(JSONB, default=dict, nullable=False)             
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    parent_section = relationship("DocumentSection", remote_side=[id], back_populates="subsections")
    subsections = relationship("DocumentSection", back_populates="parent_section", cascade="all, delete-orphan")


# ====================================================================
# 2. DOCUMENT CHUNKS (Direct Retrieval Targets)
# ====================================================================
# The Smart Navigation AI outputs targets that fetch from this table.
class DocumentChunk(Base):
    __tablename__ = "document_chunks"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    document_id = Column(UUID(as_uuid=True), ForeignKey("uploaded_documents.id", ondelete="CASCADE"), index=True, nullable=False)
    section_id = Column(UUID(as_uuid=True), ForeignKey("document_sections.id", ondelete="SET NULL"), index=True, nullable=True)
    
    workspace_id = Column(UUID(as_uuid=True), index=True, nullable=False)
    agent_id = Column(UUID(as_uuid=True), index=True, nullable=True)

    chroma_vector_id = Column(String(255), unique=True, index=True, nullable=False)
    sequence_number = Column(Integer, nullable=False)
    
    # Read by the Smart Navigation AI to confirm chunk relevance if needed
    telemetry_summary = Column(String(2000), nullable=False)  
    
    prev_chunk_id = Column(UUID(as_uuid=True), ForeignKey("document_chunks.id", ondelete="SET NULL"), nullable=True)
    next_chunk_id = Column(UUID(as_uuid=True), ForeignKey("document_chunks.id", ondelete="SET NULL"), nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())