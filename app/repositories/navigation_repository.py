from __future__ import annotations

from uuid import UUID

from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.navigation.navigation_edge import NavigationEdge
from app.models.navigation.navigation_node import NavigationNode

from app.repositories.base.base_repository import BaseRepository


class NavigationRepository(BaseRepository[NavigationNode]):

    model = NavigationNode

    def __init__(
        self,
        session: AsyncSession,
    ):
        super().__init__(session)

    # =====================================================
    # Navigation Nodes
    # =====================================================

    async def get_node(
        self,
        node_id: UUID,
    ) -> NavigationNode | None:

        statement = (
            select(NavigationNode)
            .where(
                NavigationNode.id == node_id
            )
        )

        result = await self.session.execute(statement)

        return result.scalar_one_or_none()

    async def get_document_nodes(
        self,
        document_id: UUID,
    ) -> list[NavigationNode]:

        statement = (
            select(NavigationNode)
            .where(
                NavigationNode.document_id == document_id
            )
            .order_by(
                NavigationNode.page_number,
                NavigationNode.hierarchy_level,
            )
        )

        result = await self.session.execute(statement)

        return list(result.scalars().all())

    async def get_nodes_by_page(
        self,
        document_id: UUID,
        page_number: int,
    ) -> list[NavigationNode]:

        statement = (
            select(NavigationNode)
            .where(
                NavigationNode.document_id == document_id,
                NavigationNode.page_number == page_number,
            )
        )

        result = await self.session.execute(statement)

        return list(result.scalars().all())

    async def get_nodes_by_type(
        self,
        document_id: UUID,
        node_type: str,
    ) -> list[NavigationNode]:

        statement = (
            select(NavigationNode)
            .where(
                NavigationNode.document_id == document_id,
                NavigationNode.node_type == node_type,
            )
        )

        result = await self.session.execute(statement)

        return list(result.scalars().all())

    # =====================================================
    # Navigation Edges
    # =====================================================

    async def get_document_edges(
        self,
        document_id: UUID,
    ) -> list[NavigationEdge]:

        statement = (
            select(NavigationEdge)
            .where(
                NavigationEdge.document_id == document_id
            )
        )

        result = await self.session.execute(statement)

        return list(result.scalars().all())

    async def get_outgoing_edges(
        self,
        node_id: UUID,
    ) -> list[NavigationEdge]:

        statement = (
            select(NavigationEdge)
            .where(
                NavigationEdge.source_node_id == node_id
            )
        )

        result = await self.session.execute(statement)

        return list(result.scalars().all())

    async def get_incoming_edges(
        self,
        node_id: UUID,
    ) -> list[NavigationEdge]:

        statement = (
            select(NavigationEdge)
            .where(
                NavigationEdge.target_node_id == node_id
            )
        )

        result = await self.session.execute(statement)

        return list(result.scalars().all())

    async def get_connected_edges(
        self,
        node_id: UUID,
    ) -> list[NavigationEdge]:

        statement = (
            select(NavigationEdge)
            .where(
                or_(
                    NavigationEdge.source_node_id == node_id,
                    NavigationEdge.target_node_id == node_id,
                )
            )
        )

        result = await self.session.execute(statement)

        return list(result.scalars().all())

    async def get_edges_by_relationship(
        self,
        document_id: UUID,
        relationship_type: str,
    ) -> list[NavigationEdge]:

        statement = (
            select(NavigationEdge)
            .where(
                NavigationEdge.document_id == document_id,
                NavigationEdge.relationship_type == relationship_type,
            )
        )

        result = await self.session.execute(statement)

        return list(result.scalars().all())