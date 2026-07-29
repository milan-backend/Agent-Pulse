from __future__ import annotations

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.uploaded_document import UploadedDocument
from app.models.document_intelligence.document_profile import DocumentProfile
from app.models.document_intelligence.processing_session import ProcessingSession
from app.models.document_intelligence.document_signal import DocumentSignal
from app.models.document_intelligence.detector_execution import DetectorExecution

from app.repositories.base.base_repository import BaseRepository


class DocumentRepository(BaseRepository[UploadedDocument]):

    model = UploadedDocument

    def __init__(self, session: AsyncSession):
        super().__init__(session)

    # =====================================================
    # UploadedDocument
    # =====================================================

    async def get_document(
        self,
        document_id: UUID,
    ) -> UploadedDocument | None:

        statement = (
            select(UploadedDocument)
            .where(
                UploadedDocument.id == document_id
            )
        )

        result = await self.session.execute(statement)

        return result.scalar_one_or_none()

    async def get_by_sha256(
        self,
        sha256_hash: str,
    ) -> UploadedDocument | None:

        statement = (
            select(UploadedDocument)
            .where(
                UploadedDocument.sha256_hash == sha256_hash
            )
        )

        result = await self.session.execute(statement)

        return result.scalar_one_or_none()

    async def get_workspace_documents(
        self,
        workspace_id: UUID,
        *,
        offset: int = 0,
        limit: int = 100,
    ) -> list[UploadedDocument]:

        statement = (
            select(UploadedDocument)
            .where(
                UploadedDocument.workspace_id == workspace_id
            )
            .offset(offset)
            .limit(limit)
        )

        result = await self.session.execute(statement)

        return list(result.scalars().all())

    async def get_agent_documents(
        self,
        agent_id: UUID,
        *,
        offset: int = 0,
        limit: int = 100,
    ) -> list[UploadedDocument]:

        statement = (
            select(UploadedDocument)
            .where(
                UploadedDocument.agent_id == agent_id
            )
            .offset(offset)
            .limit(limit)
        )

        result = await self.session.execute(statement)

        return list(result.scalars().all())

    async def document_exists(
        self,
        document_id: UUID,
    ) -> bool:

        return await self.exists(id=document_id)

    async def sha256_exists(
        self,
        sha256_hash: str,
    ) -> bool:

        return await self.exists(
            sha256_hash=sha256_hash
        )

    # =====================================================
    # Document Profile
    # =====================================================

    async def get_document_profile(
        self,
        document_id: UUID,
    ) -> DocumentProfile | None:

        statement = (
            select(DocumentProfile)
            .where(
                DocumentProfile.document_id == document_id
            )
        )

        result = await self.session.execute(statement)

        return result.scalar_one_or_none()

    # =====================================================
    # Processing Sessions
    # =====================================================

    async def get_processing_sessions(
        self,
        document_id: UUID,
    ) -> list[ProcessingSession]:

        statement = (
            select(ProcessingSession)
            .where(
                ProcessingSession.document_id == document_id
            )
            .order_by(
                ProcessingSession.started_at.desc()
            )
        )

        result = await self.session.execute(statement)

        return list(result.scalars().all())

    async def get_latest_processing_session(
        self,
        document_id: UUID,
    ) -> ProcessingSession | None:

        statement = (
            select(ProcessingSession)
            .where(
                ProcessingSession.document_id == document_id
            )
            .order_by(
                ProcessingSession.started_at.desc()
            )
            .limit(1)
        )

        result = await self.session.execute(statement)

        return result.scalar_one_or_none()

    # =====================================================
    # Document Signals
    # =====================================================

    async def get_document_signals(
        self,
        document_id: UUID,
    ) -> list[DocumentSignal]:

        statement = (
            select(DocumentSignal)
            .where(
                DocumentSignal.document_id == document_id
            )
        )

        result = await self.session.execute(statement)

        return list(result.scalars().all())

    # =====================================================
    # Detector Executions
    # =====================================================

    async def get_detector_executions(
        self,
        processing_session_id: UUID,
    ) -> list[DetectorExecution]:

        statement = (
            select(DetectorExecution)
            .where(
                DetectorExecution.processing_session_id
                == processing_session_id
            )
        )

        result = await self.session.execute(statement)

        return list(result.scalars().all())