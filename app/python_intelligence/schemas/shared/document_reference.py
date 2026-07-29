from uuid import UUID

from .base import PIBaseSchema


class DocumentReference(PIBaseSchema):

    workspace_id: UUID

    document_id: UUID

    filename: str