from pathlib import Path
from uuid import UUID

from pydantic import Field

from app.python_intelligence.schemas.shared.base import PIBaseSchema


class DocumentContext(PIBaseSchema):
    """
    Context supplied to every detector.
    """

    workspace_id: UUID

    document_id: UUID

    processing_session_id: UUID

    filename: str

    file_path: Path

    mime_type: str

    total_pages: int = Field(ge=1)

    language: str | None = None

    metadata: dict = Field(default_factory=dict)