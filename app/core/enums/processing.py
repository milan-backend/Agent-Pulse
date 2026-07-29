from enum import Enum


class ProcessingStage(str, Enum):
    """
    Current pipeline stage.
    """

    UPLOAD = "upload"

    OCR = "ocr"

    PREPROCESSING = "preprocessing"

    PYTHON_INTELLIGENCE = "python_intelligence"

    NAVIGATION_AI = "navigation_ai"

    KNOWLEDGE_ENRICHMENT = "knowledge_enrichment"

    CHUNK_ENGINE = "chunk_engine"

    EMBEDDING = "embedding"

    INDEXING = "indexing"

    COMPLETED = "completed"