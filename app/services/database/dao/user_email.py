from __future__ import annotations

from sqlalchemy import update
from sqlalchemy.exc import NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession

from app.dtos import dto
from app.dtos.database import UserEmail
from app.services.database.dao import mapper
from app.services.database.dao.base import BaseDAO


class UserEmailDAO(BaseDAO[UserEmail]):
    """ORM queries for users table"""

    def __init__(self, session: AsyncSession):
        super().__init__(UserEmail, session)

    async def add_user_email(self, user_email: dto.UserEmail) -> None:
        await self._session.merge(mapper.map_to_db_user_email(user_email))
        await self._session.commit()

    async def get_user_email(self, user_id: int) -> dto.UserEmail | None:
        try:
            return dto.UserEmail.from_db(
                user_email=await self.get_by_id(user_id)
            )
        except NoResultFound:
            return None

    async def set_topic(self, user_id: int, forum_id: int) -> None:
        await self._session.execute(update(UserEmail).where(UserEmail.id == user_id).values(
            forum_id=forum_id
        ))
        await self._session.commit()
