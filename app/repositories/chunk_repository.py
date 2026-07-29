from __future__ import annotations

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.chunks.chunk import Chunk
from app.models.chunks.chunk_index import ChunkIndex
from app.models.chunks.embedding import Embedding

from app.repositories.base.base_repository import BaseRepository


class ChunkRepository(BaseRepository[Chunk]):

    model = Chunk

    def __init__(
        self,
        session: AsyncSession,
    ):
        super().__init__(session)

    # =====================================================
    # Chunk
    # =====================================================

    async def get_chunk(
        self,
        chunk_id: UUID,
    ) -> Chunk | None:

        statement = (
            select(Chunk)
            .where(
                Chunk.id == chunk_id
            )
        )

        result = await self.session.execute(statement)

        return result.scalar_one_or_none()

    async def get_document_chunks(
        self,
        document_id: UUID,
    ) -> list[Chunk]:

        statement = (
            select(Chunk)
            .where(
                Chunk.document_id == document_id
            )
        )

        result = await self.session.execute(statement)

        return list(result.scalars().all())

    async def get_chunk_by_hash(
        self,
        content_hash: str,
    ) -> Chunk | None:

        statement = (
            select(Chunk)
            .where(
                Chunk.content_hash == content_hash
            )
        )

        result = await self.session.execute(statement)

        return result.scalar_one_or_none()

    # =====================================================
    # Chunk Index
    # =====================================================

    async def get_chunk_index(
        self,
        chunk_id: UUID,
    ) -> ChunkIndex | None:

        statement = (
            select(ChunkIndex)
            .where(
                ChunkIndex.chunk_id == chunk_id
            )
        )

        result = await self.session.execute(statement)

        return result.scalar_one_or_none()

    async def get_navigation_chunks(
        self,
        navigation_node_id: UUID,
    ) -> list[ChunkIndex]:

        statement = (
            select(ChunkIndex)
            .where(
                ChunkIndex.navigation_node_id == navigation_node_id
            )
        )

        result = await self.session.execute(statement)

        return list(result.scalars().all())

    # =====================================================
    # Embedding Metadata
    # =====================================================

    async def get_embedding(
        self,
        chunk_id: UUID,
    ) -> Embedding | None:

        statement = (
            select(Embedding)
            .where(
                Embedding.chunk_id == chunk_id
            )
        )

        result = await self.session.execute(statement)

        return result.scalar_one_or_none()

    async def get_embedding_by_vector_id(
        self,
        vector_id: str,
    ) -> Embedding | None:

        statement = (
            select(Embedding)
            .where(
                Embedding.vector_id == vector_id
            )
        )

        result = await self.session.execute(statement)

        return result.scalar_one_or_none()

    async def get_document_embeddings(
        self,
        document_id: UUID,
    ) -> list[Embedding]:

        statement = (
            select(Embedding)
            .join(
                Chunk,
                Chunk.id == Embedding.chunk_id,
            )
            .where(
                Chunk.document_id == document_id
            )
        )

        result = await self.session.execute(statement)

        return list(result.scalars().all())