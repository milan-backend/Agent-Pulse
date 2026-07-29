from enum import Enum


class DetectorType(str, Enum):
    """
    Registered Python Intelligence detectors.
    """

    OCR = "ocr"

    LAYOUT = "layout"

    HEADING = "heading"

    SECTION = "section"

    TABLE = "table"

    ENTITY = "entity"

    KEYWORD = "keyword"

    RULE = "rule"

    DEFINITION = "definition"

    REFERENCE = "reference"

    QUALITY = "quality"


class DetectorStatus(str, Enum):
    """
    Detector execution status.
    """

    PENDING = "pending"

    RUNNING = "running"

    COMPLETED = "completed"

    FAILED = "failed"

    SKIPPED = "skipped"