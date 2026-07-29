from __future__ import annotations

from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.repositories.document_repository import DocumentRepository
from app.repositories.navigation_repository import NavigationRepository
from app.repositories.chunk_repository import ChunkRepository
from app.repositories.knowledge_repository import KnowledgeRepository


class UnitOfWork:
    """
    Coordinates repositories and a single SQL transaction.
    """

    def __init__(
        self,
        session_factory: async_sessionmaker[AsyncSession],
    ) -> None:

        self._session_factory = session_factory

        self._session: Optional[AsyncSession] = None

        self._documents: Optional[DocumentRepository] = None
        self._navigation: Optional[NavigationRepository] = None
        self._chunks: Optional[ChunkRepository] = None
        self._knowledge: Optional[KnowledgeRepository] = None

    # =====================================================
    # Context Manager
    # =====================================================

    async def __aenter__(self) -> "UnitOfWork":

        self._session = self._session_factory()

        self._documents = DocumentRepository(self._session)
        self._navigation = NavigationRepository(self._session)
        self._chunks = ChunkRepository(self._session)
        self._knowledge = KnowledgeRepository(self._session)

        return self

    async def __aexit__(
        self,
        exc_type,
        exc_value,
        traceback,
    ) -> None:

        try:

            if exc_type is None:
                await self.commit()
            else:
                await self.rollback()

        finally:
            await self.close()

    # =====================================================
    # Session
    # =====================================================

    @property
    def session(self) -> AsyncSession:

        if self._session is None:
            raise RuntimeError(
                "UnitOfWork has not been entered."
            )

        return self._session

    # =====================================================
    # Repositories
    # =====================================================

    @property
    def documents(self) -> DocumentRepository:

        if self._documents is None:
            raise RuntimeError(
                "UnitOfWork has not been entered."
            )

        return self._documents

    @property
    def navigation(self) -> NavigationRepository:

        if self._navigation is None:
            raise RuntimeError(
                "UnitOfWork has not been entered."
            )

        return self._navigation

    @property
    def chunks(self) -> ChunkRepository:

        if self._chunks is None:
            raise RuntimeError(
                "UnitOfWork has not been entered."
            )

        return self._chunks

    @property
    def knowledge(self) -> KnowledgeRepository:

        if self._knowledge is None:
            raise RuntimeError(
                "UnitOfWork has not been entered."
            )

        return self._knowledge

    # =====================================================
    # Transaction Control
    # =====================================================

    async def commit(self) -> None:
        await self.session.commit()

    async def rollback(self) -> None:
        await self.session.rollback()

    async def flush(self) -> None:
        await self.session.flush()

    async def refresh(self, instance) -> None:
        await self.session.refresh(instance)

    # =====================================================
    # Cleanup
    # =====================================================

    async def close(self) -> None:

        if self._session is not None:

            await self._session.close()

            self._session = None

            self._documents = None
            self._navigation = None
            self._chunks = None
            self._knowledge = None