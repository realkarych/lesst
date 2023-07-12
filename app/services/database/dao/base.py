from __future__ import annotations

from typing import TypeVar, Type, Generic, Callable

from sqlalchemy import delete, func, Row
from sqlalchemy.exc import NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.services.database.base import BASE

Model = TypeVar('Model', BASE, BASE)
DTO = TypeVar('DTO', BASE, BASE)


class BaseDAO(Generic[Model]):
    """ORM queries for abstract table"""

    def __init__(self, model: Type[Model], session: AsyncSession):
        """
        :param model:
        :param session:
        """

        self._model = model
        self._session = session

    async def get_all(self, dto_converter: Callable) -> list[DTO] | None:
        """
        :return: List of models.
        """
        try:
            result = await self._session.execute(select(self._model))
            return [dto_converter(model) for model in result.scalars()]
        except NoResultFound:
            return None

    async def get_by_id(self, id_: int) -> DTO | None:
        """
        :param id_: input id
        :return:
        """
        result = await self._session.execute(
            select(self._model).where(self._model.id == id_)
        )
        return result.scalar_one_or_none()

    async def delete_all(self) -> None:
        """
        Clear table
        :return:
        """

        await self._session.execute(delete(self._model))

    async def count(self) -> int:
        """
        :return: count of model.
        """

        result = await self._session.execute(select(func.count(self._model.id)))
        return result.scalar_one()

    async def commit(self) -> None:
        """
        Commit re-impl
        :return:
        """

        await self.commit()
