class RetrievalError(Exception):
    pass


class ChunkNotFoundError(RetrievalError):
    pass


class EmbeddingError(RetrievalError):
    pass