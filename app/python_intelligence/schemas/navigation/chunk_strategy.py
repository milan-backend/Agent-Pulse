from uuid import UUID

from pydantic import Field

from app.python_intelligence.schemas.shared.base import PIBaseSchema


class ChunkInstruction(PIBaseSchema):

    node_id: UUID

    start_page: int = Field(ge=1)

    end_page: int = Field(ge=1)

    preserve_children: bool = True

    preserve_tables: bool = True

    preserve_figures: bool = True


class ChunkStrategy(PIBaseSchema):

    instructions: list[ChunkInstruction] = Field(default_factory=list)