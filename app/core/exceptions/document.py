class DocumentProcessingError(Exception):
    """Raised when document processing fails."""


class DocumentValidationError(Exception):
    """Raised when uploaded document is invalid."""


class DocumentEncryptionError(Exception):
    """Raised when document encryption fails."""