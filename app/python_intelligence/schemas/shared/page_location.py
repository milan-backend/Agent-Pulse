from pydantic import Field

from .base import PIBaseSchema


class PageLocation(PIBaseSchema):

    page_number: int = Field(
        ge=1,
    )

    line_start: int | None = None

    line_end: int | None = None

    character_start: int | None = None

    character_end: int | None = None