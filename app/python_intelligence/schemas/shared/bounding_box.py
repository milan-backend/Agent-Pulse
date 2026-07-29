from pydantic import Field

from .base import PIBaseSchema


class BoundingBox(PIBaseSchema):

    x: float = Field(ge=0)

    y: float = Field(ge=0)

    width: float = Field(gt=0)

    height: float = Field(gt=0)

    page_number: int = Field(ge=1)