from datetime import datetime

from pydantic import Field

from app.core.enums.detector import DetectorType
from app.python_intelligence.schemas.detector.detector_signal import (
    DetectorSignal,
)
from app.python_intelligence.schemas.shared.base import PIBaseSchema


class SignalBatch(PIBaseSchema):
    """
    Groups detector output into a single object.
    """

    detector: DetectorType

    started_at: datetime

    completed_at: datetime

    execution_time_ms: float = Field(ge=0)

    total_signals: int = Field(ge=0)

    signals: list[DetectorSignal] = Field(default_factory=list)