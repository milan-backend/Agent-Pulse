from __future__ import annotations

from typing import Any, Generic, Sequence, TypeVar

from sqlalchemy import delete
from sqlalchemy import func
from sqlalchemy import select

from sqlalchemy.ext.asyncio import AsyncSession

ModelType = TypeVar("ModelType")


class BaseRepository(Generic[ModelType]):

    model: type[ModelType]

    def __init__(self, session: AsyncSession):

        self.session = session

    # -----------------------------------------------------
    # Create
    # -----------------------------------------------------

    async def create(
        self,
        instance: ModelType,
    ) -> ModelType:

        self.session.add(instance)

        await self.session.flush()

        return instance

    async def create_many(
        self,
        instances: list[ModelType],
    ) -> list[ModelType]:

        self.session.add_all(instances)

        await self.session.flush()

        return instances

    # -----------------------------------------------------
    # Read
    # -----------------------------------------------------

    async def get_by_id(
        self,
        object_id: Any,
    ) -> ModelType | None:

        statement = (
            select(self.model)
            .where(self.model.id == object_id)
        )

        result = await self.session.execute(statement)

        return result.scalar_one_or_none()

    async def get_all(
        self,
        *,
        offset: int = 0,
        limit: int = 100,
    ) -> Sequence[ModelType]:

        statement = (
            select(self.model)
            .offset(offset)
            .limit(limit)
        )

        result = await self.session.execute(statement)

        return result.scalars().all()

    async def exists(
        self,
        **filters: Any,
    ) -> bool:

        statement = (
            select(func.count())
            .select_from(self.model)
            .filter_by(**filters)
        )

        count = await self.session.scalar(statement)

        return bool(count)

    async def count(
        self,
        **filters: Any,
    ) -> int:

        statement = (
            select(func.count())
            .select_from(self.model)
            .filter_by(**filters)
        )

        result = await self.session.scalar(statement)

        return result or 0

    # -----------------------------------------------------
    # Update
    # -----------------------------------------------------

    async def update(
        self,
        instance: ModelType,
    ) -> ModelType:

        await self.session.flush()

        return instance

    # -----------------------------------------------------
    # Delete
    # -----------------------------------------------------

    async def delete(
        self,
        instance: ModelType,
    ) -> None:

        await self.session.delete(instance)

        await self.session.flush()

    async def delete_by_id(
        self,
        object_id: Any,
    ) -> None:

        statement = (
            delete(self.model)
            .where(self.model.id == object_id)
        )

        await self.session.execute(statement)

        await self.session.flush()