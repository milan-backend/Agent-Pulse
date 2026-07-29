from typing import Any
from uuid import UUID

from pydantic import Field

from app.core.enums.detector import DetectorType
from app.core.enums.signals import SignalType
from app.python_intelligence.schemas.shared.base import PIBaseSchema
from app.python_intelligence.schemas.shared.bounding_box import BoundingBox
from app.python_intelligence.schemas.shared.confidence import ConfidenceScore
from app.python_intelligence.schemas.shared.page_location import PageLocation


class DetectorSignal(PIBaseSchema):
    """
    Universal detector output.
    """

    signal_id: UUID | None = None

    detector: DetectorType

    signal_type: SignalType

    page_number: int = Field(ge=1)

    confidence: ConfidenceScore

    location: PageLocation | None = None

    bounding_box: BoundingBox | None = None

    content: str | None = None

    metadata: dict[str, Any] = Field(default_factory=dict)

    tags: list[str] = Field(default_factory=list)