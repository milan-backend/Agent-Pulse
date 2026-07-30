import uuid
from sqlalchemy import Column, String, Integer, Text, DateTime, ForeignKey, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import declarative_base, relationship

# Use your existing Base if you were importing this, but for testing in a standalone file:
Base = declarative_base()

# ====================================================================
# 1. DOCUMENT SECTIONS (The Navigation Map)
# ====================================================================
class DocumentSection(Base):
    __tablename__ = "document_sections"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    
    # Links directly to your existing uploaded_documents table
    document_id = Column(UUID(as_uuid=True), ForeignKey("uploaded_documents.id", ondelete="CASCADE"), index=True, nullable=False)
    
    # Tenant Isolation matching your main table
    workspace_id = Column(UUID(as_uuid=True), index=True, nullable=False)
    agent_id = Column(UUID(as_uuid=True), index=True, nullable=True)

    section_code = Column(String(50), nullable=False)  # e.g., '1.1', '2.3.1'
    title = Column(String(255), nullable=False)
    
    # Self-referencing FK for nested headers (e.g., 1.1 -> 1.1.1)
    parent_section_id = Column(UUID(as_uuid=True), ForeignKey("document_sections.id", ondelete="CASCADE"), nullable=True)
    
    start_page = Column(Integer, nullable=True)
    end_page = Column(Integer, nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationship for nested tree logic
    subsections = relationship("DocumentSection", backref="parent_section", remote_side=[parent_section_id], cascade="all, delete-orphan")


# ====================================================================
# 2. DOCUMENT CHUNKS (Telemetry & Vector Mapping)
# ====================================================================
class DocumentChunk(Base):
    __tablename__ = "document_chunks"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    document_id = Column(UUID(as_uuid=True), ForeignKey("uploaded_documents.id", ondelete="CASCADE"), index=True, nullable=False)
    section_id = Column(UUID(as_uuid=True), ForeignKey("document_sections.id", ondelete="SET NULL"), index=True, nullable=True)
    
    # Tenant Isolation
    workspace_id = Column(UUID(as_uuid=True), index=True, nullable=False)
    agent_id = Column(UUID(as_uuid=True), index=True, nullable=True)

    chroma_vector_id = Column(String(255), unique=True, index=True, nullable=False)
    sequence_number = Column(Integer, nullable=False)
    
    telemetry_summary = Column(String(2000), nullable=False)  # Read by Planner AI
    
    # Linked List pointers for relational fetching (fetching depth)
    prev_chunk_id = Column(UUID(as_uuid=True), ForeignKey("document_chunks.id", ondelete="SET NULL"), nullable=True)
    next_chunk_id = Column(UUID(as_uuid=True), ForeignKey("document_chunks.id", ondelete="SET NULL"), nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())


# ====================================================================
# 3. EXTRACTED ENTITIES (Knowledge Concepts)
# ====================================================================
class ExtractedEntity(Base):
    __tablename__ = "extracted_entities"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    document_id = Column(UUID(as_uuid=True), ForeignKey("uploaded_documents.id", ondelete="CASCADE"), index=True, nullable=False)
    
    # Tenant Isolation
    workspace_id = Column(UUID(as_uuid=True), index=True, nullable=False)
    agent_id = Column(UUID(as_uuid=True), index=True, nullable=True)

    name = Column(String(255), index=True, nullable=False)
    category = Column(String(100), nullable=True)
    description = Column(Text, nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())


# ====================================================================
# 4. ENTITY RELATIONSHIPS (Knowledge Graph)
# ====================================================================
class EntityRelationship(Base):
    __tablename__ = "entity_relationships"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    
    # Tenant Isolation
    workspace_id = Column(UUID(as_uuid=True), index=True, nullable=False)
    agent_id = Column(UUID(as_uuid=True), index=True, nullable=True)

    source_entity_id = Column(UUID(as_uuid=True), ForeignKey("extracted_entities.id", ondelete="CASCADE"), index=True, nullable=False)
    target_entity_id = Column(UUID(as_uuid=True), ForeignKey("extracted_entities.id", ondelete="CASCADE"), index=True, nullable=False)
    
    relationship_type = Column(String(100), nullable=False)
    section_id = Column(UUID(as_uuid=True), ForeignKey("document_sections.id", ondelete="SET NULL"), index=True, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships for easy ORM querying
    source_entity = relationship("ExtractedEntity", foreign_keys=[source_entity_id])
    target_entity = relationship("ExtractedEntity", foreign_keys=[target_entity_id])
    section = relationship("DocumentSection")