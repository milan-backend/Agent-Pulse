from app.core.enums.detector import DetectorStatus
from app.python_intelligence.schemas.detector.signal_batch import SignalBatch
from app.python_intelligence.schemas.shared.base import PIBaseSchema


class ProcessingResult(PIBaseSchema):
    """
    Result of one detector execution.
    """

    status: DetectorStatus

    batch: SignalBatch | None = None

    error_message: str | None = None