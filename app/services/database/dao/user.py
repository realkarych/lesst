from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession

from app.dtos.converters import convert_db_user_to_dto_user
from app.dtos.user import UserDTO
from app.services.database.dao.base import BaseDAO
from app.services.database.exception_mapper import exception_mapper
from app.services.database.models import User


class UserDAO(BaseDAO[User]):

    def __init__(self, session: AsyncSession):
        super().__init__(User, session)

    @exception_mapper
    async def add_user(self, user: UserDTO) -> None:
        """
        Add user to database if not added yet. If added, tries to update parameters.
        :param user: Telegram user.
        """

        await self._session.merge(user.to_db_model())
        await self.commit()

    @exception_mapper
    async def get_all_users(self) -> tuple[UserDTO] | None:
        return await self.get_all(dto_converter=convert_db_user_to_dto_user)
