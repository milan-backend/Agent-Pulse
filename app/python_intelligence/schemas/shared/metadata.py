from typing import Any

from .base import PIBaseSchema


class Metadata(PIBaseSchema):

    values: dict[str, Any] = {}