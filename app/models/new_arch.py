import uuid
from sqlalchemy import Column, String, Integer, Text, DateTime, ForeignKey, Index
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

# 🟢 Import the REAL Base from your app
from app.db.session import Base 

# ====================================================================
# 1. DOCUMENT SECTIONS (The Parent-Child State Machine)
# ====================================================================
# This tracks the folder hierarchy and manages multi-page table continuity.
class DocumentSection(Base):
    __tablename__ = "document_sections"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    document_id = Column(UUID(as_uuid=True), ForeignKey("uploaded_documents.id", ondelete="CASCADE"), index=True, nullable=False)
    workspace_id = Column(UUID(as_uuid=True), index=True, nullable=False)

    # 🟢 Relational Map
    title = Column(String(255), nullable=False)
    parent_path = Column(String(500), nullable=True)  # Breadcrumbs (e.g., "MINISTRY > Dept of Education")
    parent_section_id = Column(UUID(as_uuid=True), ForeignKey("document_sections.id", ondelete="CASCADE"), nullable=True)
    
    # 🟢 State Machine for Multi-Page Tables (NEW)
    # "OPEN" if table continues to next page, "CLOSED" when ready for the 5-row ChunkEngine.
    status = Column(String(50), default="CLOSED", nullable=False) 
    start_page = Column(Integer, nullable=True)
    end_page = Column(Integer, nullable=True)

    # 🟢 Semantic & Keyword Nets for Smart Router
    content_type = Column(String(100), default="narrative", nullable=False) # "data_table" or "narrative"
    semantic_summary = Column(Text, nullable=True) # 1-sentence AI summary of the section
    parent_keywords = Column(Text, nullable=True)  # Broad BM25 Hooks (e.g., "Ministry, Budget, Education")
    
    # 🟢 Table Handoff Data (NEW - Replaces complex chunking_strategy_hint)
    # Stores the extracted top row so Python can glue it to every 5-row slice.
    table_headers = Column(Text, nullable=True) 
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    parent_section = relationship("DocumentSection", remote_side=[id], back_populates="subsections")
    subsections = relationship("DocumentSection", back_populates="parent_section", cascade="all, delete-orphan")


# ====================================================================
# 2. DOCUMENT CHUNKS (The Linked-List Retrieval Targets)
# ====================================================================
# The Smart Query LLM outputs the ID from this table directly, bypassing the 2nd Chroma search.
class DocumentChunk(Base):
    __tablename__ = "document_chunks"

    # 🟢 The Master Pointer
    # This ID is the EXACT same ID saved into ChromaDB. 
    # Python uses this to instantly run `chroma.get(id)` without any vector math.
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    
    document_id = Column(UUID(as_uuid=True), ForeignKey("uploaded_documents.id", ondelete="CASCADE"), index=True, nullable=False)
    section_id = Column(UUID(as_uuid=True), ForeignKey("document_sections.id", ondelete="SET NULL"), index=True, nullable=True)
    workspace_id = Column(UUID(as_uuid=True), index=True, nullable=False)

    sequence_number = Column(Integer, nullable=False)
    
    # 🟢 Sniper Keyword Net (NEW)
    # The exact numbers/acronyms in this specific 5-row slice (e.g., "IIT, 11288.00").
    chunk_keywords = Column(Text, nullable=True) 
    
    # 🟢 The Linked-List Safety Net (Table Reassembly)
    # Completely replaces the need for the AI to guess row relationships. 
    # The retriever just pulls the target + these two neighbors.
    prev_chunk_id = Column(UUID(as_uuid=True), ForeignKey("document_chunks.id", ondelete="SET NULL"), nullable=True)
    next_chunk_id = Column(UUID(as_uuid=True), ForeignKey("document_chunks.id", ondelete="SET NULL"), nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())