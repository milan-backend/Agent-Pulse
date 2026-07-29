import time
import logging
from typing import Dict, Any, List
from sqlalchemy.orm import Session
from uuid import UUID

from app.models.uploaded_document import UploadedDocument
from app.models.document_intelligence.processing_session import ProcessingSession
from app.models.document_intelligence.detector_execution import DetectorExecution
from app.models.document_intelligence.document_signal import DocumentSignal
from app.core.enums.signals import SignalType
from app.core.enums.detector import DetectorType, DetectorStatus
from app.core.enums.processing import ProcessingStage

logger = logging.getLogger(__name__)

class PythonIntelligencePipeline:
    """
    Orchestrates the deterministic Python Intelligence extraction pipeline
    running before any LLM or vector embedding occurs.
    """

    def __init__(self, db: Session, document_id: UUID, workspace_id: UUID):
        self.db = db
        self.document_id = document_id
        self.workspace_id = workspace_id

    def execute_pipeline(self, extracted_pages: List[str]) -> bool:
        """
        Runs the full Python Intelligence extraction sweep across document pages.
        """
        session_id = self._initialize_processing_session()
        if not session_id:
            return False

        try:
            logger.info(f"Starting Python Intelligence Pipeline for Document {self.document_id}")
            
            # 1. Run Layout and Structure Detectors
            self._run_detector(
                session_id=session_id,
                detector_name=DetectorType.HEADING,
                detector_func=self._extract_headings,
                pages=extracted_pages
            )

            self._run_detector(
                session_id=session_id,
                detector_name=DetectorType.TABLE,
                detector_func=self._extract_tables,
                pages=extracted_pages
            )

            self._run_detector(
                session_id=session_id,
                detector_name=DetectorType.ENTITY,
                detector_func=self._extract_entities,
                pages=extracted_pages
            )

            # Mark session completed
            self._update_session_status(session_id, "completed")
            return True

        except Exception as e:
            logger.error(f"Error during Python Intelligence pipeline execution: {str(e)}")
            self._update_session_status(session_id, "failed", error_message=str(e))
            return False

    def _initialize_processing_session(self) -> UUID | None:
        try:
            session = ProcessingSession(
                document_id=self.document_id,
                workspace_id=self.workspace_id,
                status=ProcessingStage.PYTHON_INTELLIGENCE
            )
            self.db.add(session)
            self.db.commit()
            self.db.refresh(session)
            return session.id
        except Exception as e:
            logger.error(f"Failed to initialize processing session: {e}")
            self.db.rollback()
            return None

    def _update_session_status(self, session_id: UUID, status: str, error_message: str = None):
        session = self.db.query(ProcessingSession).filter(ProcessingSession.id == session_id).first()
        if session:
            session.status = status
            if error_message:
                pass  # Handle error logging if column allows
            self.db.commit()

    def _run_detector(self, session_id: UUID, detector_name: str, detector_func, pages: List[str]):
        start_time = time.time()
        signals_generated = 0
        status = DetectorStatus.RUNNING
        error_msg = None

        try:
            signals = detector_func(pages)
            for sig in signals:
                db_signal = DocumentSignal(
                    processing_session_id=session_id,
                    document_id=self.document_id,
                    detector=detector_name,
                    signal_type=sig.get("signal_type", SignalType.HEADING),
                    page_number=sig.get("page_number", 1),
                    confidence=sig.get("confidence", 1.0),
                    content=sig.get("content", ""),
                    metadata=sig.get("metadata", {})
                )
                self.db.add(db_signal)
                signals_generated += 1

            self.db.commit()
            status = DetectorStatus.COMPLETED
        except Exception as e:
            self.db.rollback()
            status = DetectorStatus.FAILED
            error_msg = str(e)
            logger.error(f"Detector {detector_name} failed: {e}")

        execution_time = (time.time() - start_time) * 1000

        # Log detector telemetry
        telemetry = DetectorExecution(
            processing_session_id=session_id,
            detector_name=detector_name,
            status=status,
            execution_time_ms=execution_time,
            signals_generated=signals_generated,
            error_message=error_msg
        )
        self.db.add(telemetry)
        self.db.commit()

    def _extract_headings(self, pages: List[str]) -> List[Dict[str, Any]]:
        # Placeholder deterministic extraction logic for headings
        extracted = []
        for idx, page_text in enumerate(pages):
            lines = page_text.split("\n")
            for line in lines:
                if len(line.strip()) > 0 and len(line.strip()) < 100 and line.strip().istitle():
                    extracted.append({
                        "signal_type": SignalType.HEADING,
                        "page_number": idx + 1,
                        "confidence": 0.95,
                        "content": line.strip(),
                        "metadata": {"level": 1}
                    })
        return extracted

    def _extract_tables(self, pages: List[str]) -> List[Dict[str, Any]]:
        # Placeholder detector for tables
        return []

    def _extract_entities(self, pages: List[str]) -> List[Dict[str, Any]]:
        # Placeholder detector for entities
        return []