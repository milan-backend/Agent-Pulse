from enum import Enum


class ChunkStatus(str, Enum):
    """
    Chunk processing state.
    """

    PENDING = "pending"

    CREATED = "created"

    EMBEDDING = "embedding"

    EMBEDDED = "embedded"

    FAILED = "failed"


class ChunkType(str, Enum):
    """
    Logical chunk type.
    """

    TEXT = "text"

    TABLE = "table"

    IMAGE = "image"

    MIXED = "mixed"