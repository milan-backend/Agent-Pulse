from enum import Enum


class ProcessingStatus(str, Enum):
    """
    Lifecycle state of a document.
    """

    UPLOADED = "uploaded"
    QUEUED = "queued"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    RETRYING = "retrying"
    CANCELLED = "cancelled"


class DocumentCategory(str, Enum):
    """
    High-level document classification.
    """

    UNKNOWN = "unknown"

    POLICY = "policy"
    HANDBOOK = "handbook"
    SOP = "sop"
    REPORT = "report"
    MANUAL = "manual"
    CONTRACT = "contract"
    PRESENTATION = "presentation"
    TECHNICAL = "technical"
    GUIDE = "guide"