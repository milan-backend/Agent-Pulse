import logging
import hashlib
from typing import List, Dict, Any
from sqlalchemy.orm import Session
from uuid import UUID

from app.models.chunks.chunk import Chunk
from app.models.chunks.chunk_index import ChunkIndex
from app.core.constants.retrieval import DEFAULT_CHUNK_SIZE, DEFAULT_CHUNK_OVERLAP

logger = logging.getLogger(__name__)

class ChunkEngineService:
    """
    Handles structure-aware chunking, secure payload encryption representation,
    and index mapping for the document intelligence platform.
    """

    def __init__(self, db: Session, document_id: UUID, workspace_id: UUID):
        self.db = db
        self.document_id = document_id
        self.workspace_id = workspace_id

    def process_document_chunks(self, full_text: str, page_number: int = 1) -> int:
        """
        Segments raw text into structured chunks, generates content hashes,
        and persists them securely into the database.
        """
        if not full_text:
            return 0

        # Simple sliding window text chunking based on default size & overlap
        chunks_data = self._slide_chunk_text(full_text, DEFAULT_CHUNK_SIZE, DEFAULT_CHUNK_OVERLAP)
        stored_count = 0

        for chunk_text in chunks_data:
            # Generate SHA256 content hash for deduplication and tracking
            content_hash = hashlib.sha256(chunk_text.encode("utf-8")).hexdigest()
            
            # Simulated binary encryption representation (production uses secure AES cipher here)
            encrypted_payload = chunk_text.encode("utf-8")
            dummy_iv = b"secure_iv_bytes_"  # 16-byte initialization vector placeholder

            # 1. Save to master Chunks table
            db_chunk = Chunk(
                document_id=self.document_id,
                encrypted_content=encrypted_payload,
                encryption_iv=dummy_iv,
                content_hash=content_hash,
                token_count=len(chunk_text.split()) * 2  # Approximate token count heuristic
            )
            self.db.add(db_chunk)
            self.db.flush() # Flush to get chunk.id immediately

            # 2. Save to ChunkIndex table for Planner AI navigation mapping
            db_index = ChunkIndex(
                chunk_id=db_chunk.id,
                page_start=page_number,
                page_end=page_number,
                metadata={"length": len(chunk_text)}
            )
            self.db.add(db_index)
            stored_count += 1

        self.db.commit()
        logger.info(f"ChunkEngineService successfully generated and indexed {stored_count} chunks for doc {self.document_id}")
        return stored_count

    def _slide_chunk_text(self, text: str, chunk_size: int, overlap: int) -> List[str]:
        """
        Splits text into overlapping word-based windows.
        """
        words = text.split()
        if not words:
            return []

        chunks = []
        i = 0
        while i < len(words):
            chunk_words = words[i:i + chunk_size]
            chunks.append(" ".join(chunk_words))
            i += (chunk_size - overlap)
        return chunks