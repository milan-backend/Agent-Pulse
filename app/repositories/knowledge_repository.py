from __future__ import annotations

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.knowledge.semantic_metadata import SemanticMetadata
from app.models.knowledge.entity import Entity
from app.models.knowledge.relationship import Relationship

from app.repositories.base.base_repository import BaseRepository


class KnowledgeRepository(BaseRepository[SemanticMetadata]):

    model = SemanticMetadata

    def __init__(
        self,
        session: AsyncSession,
    ):
        super().__init__(session)

    # =====================================================
    # Semantic Metadata
    # =====================================================

    async def get_semantic_metadata(
        self,
        document_id: UUID,
    ) -> SemanticMetadata | None:

        statement = (
            select(SemanticMetadata)
            .where(
                SemanticMetadata.document_id == document_id
            )
        )

        result = await self.session.execute(statement)

        return result.scalar_one_or_none()

    # =====================================================
    # Entities
    # =====================================================

    async def get_entities(
        self,
        document_id: UUID,
    ) -> list[Entity]:

        statement = (
            select(Entity)
            .where(
                Entity.document_id == document_id
            )
        )

        result = await self.session.execute(statement)

        return list(result.scalars().all())

    async def get_entity(
        self,
        entity_id: UUID,
    ) -> Entity | None:

        statement = (
            select(Entity)
            .where(
                Entity.id == entity_id
            )
        )

        result = await self.session.execute(statement)

        return result.scalar_one_or_none()

    async def get_entities_by_type(
        self,
        document_id: UUID,
        entity_type: str,
    ) -> list[Entity]:

        statement = (
            select(Entity)
            .where(
                Entity.document_id == document_id,
                Entity.entity_type == entity_type,
            )
        )

        result = await self.session.execute(statement)

        return list(result.scalars().all())

    async def get_chunk_entities(
        self,
        chunk_id: UUID,
    ) -> list[Entity]:

        statement = (
            select(Entity)
            .where(
                Entity.chunk_id == chunk_id
            )
        )

        result = await self.session.execute(statement)

        return list(result.scalars().all())

    # =====================================================
    # Relationships
    # =====================================================

    async def get_relationships(
        self,
        document_id: UUID,
    ) -> list[Relationship]:

        statement = (
            select(Relationship)
            .where(
                Relationship.document_id == document_id
            )
        )

        result = await self.session.execute(statement)

        return list(result.scalars().all())

    async def get_entity_relationships(
        self,
        entity_id: UUID,
    ) -> list[Relationship]:

        statement = (
            select(Relationship)
            .where(
                (Relationship.source_entity_id == entity_id)
                |
                (Relationship.target_entity_id == entity_id)
            )
        )

        result = await self.session.execute(statement)

        return list(result.scalars().all())

    async def get_relationships_by_type(
        self,
        document_id: UUID,
        relationship_type: str,
    ) -> list[Relationship]:

        statement = (
            select(Relationship)
            .where(
                Relationship.document_id == document_id,
                Relationship.relationship_type == relationship_type,
            )
        )

        result = await self.session.execute(statement)

        return list(result.scalars().all())