from datetime import datetime
from pydantic import BaseModel, ConfigDict


class PIBaseSchema(BaseModel):
    """
    Base schema for every Python Intelligence object.
    """

    model_config = ConfigDict(
        extra="forbid",
        validate_assignment=True,
        populate_by_name=True,
        frozen=False,
        arbitrary_types_allowed=True,
    )


class TimestampMixin(BaseModel):
    """
    Optional timestamp mixin for processing events.
    """

    created_at: datetime | None = None
    updated_at: datetime | None = None