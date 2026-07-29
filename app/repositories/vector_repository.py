from __future__ import annotations

from abc import ABC, abstractmethod
from uuid import UUID


class VectorRepository(ABC):
    """
    Abstract repository for vector databases.
    """

    @abstractmethod
    async def add_embedding(
        self,
        *,
        chunk_id: UUID,
        vector: list[float],
        metadata: dict,
    ) -> str:
        """
        Store a vector.

        Returns
        -------
        Vector database identifier.
        """
        raise NotImplementedError

    @abstractmethod
    async def add_embeddings(
        self,
        *,
        vectors: list[dict],
    ) -> list[str]:
        """
        Batch insert vectors.
        """
        raise NotImplementedError

    @abstractmethod
    async def similarity_search(
        self,
        *,
        query_vector: list[float],
        top_k: int = 5,
        filters: dict | None = None,
    ) -> list[dict]:
        """
        Return nearest neighbours.
        """
        raise NotImplementedError

    @abstractmethod
    async def get_embedding(
        self,
        vector_id: str,
    ) -> dict | None:
        """
        Retrieve vector metadata.
        """
        raise NotImplementedError

    @abstractmethod
    async def delete_embedding(
        self,
        vector_id: str,
    ) -> None:
        """
        Delete a single vector.
        """
        raise NotImplementedError

    @abstractmethod
    async def delete_document_embeddings(
        self,
        document_id: UUID,
    ) -> None:
        """
        Delete all vectors belonging to a document.
        """
        raise NotImplementedError

    @abstractmethod
    async def update_embedding(
        self,
        *,
        vector_id: str,
        vector: list[float],
        metadata: dict,
    ) -> None:
        """
        Replace vector and metadata.
        """
        raise NotImplementedError