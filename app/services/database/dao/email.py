from __future__ import annotations

from sqlalchemy import update, select
from sqlalchemy.exc import NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession

from app.dtos.converters import convert_db_email_to_dto_email
from app.dtos.email import EmailDTO
from app.services.database.dao.base import BaseDAO
from app.services.database.exception_mapper import exception_mapper
from app.services.database.models import Email


class EmailDAO(BaseDAO[Email]):

    def __init__(self, session: AsyncSession):
        super().__init__(Email, session)

    @exception_mapper
    async def add_email(self, email: EmailDTO) -> None:
        await self._session.merge(email.to_db_model())
        await self._session.commit()

    @exception_mapper
    async def email_already_added(self, email_address: str) -> bool:
        result = await self._session.execute(
            select(Email).where(Email.mail_address == email_address)
        )
        return bool(result.scalar_one_or_none())

    @exception_mapper
    async def get_email(self, user_id: int, forum_id: int) -> EmailDTO | None:
        try:
            result = await self._session.execute(
                select(Email).where(Email.user_id == user_id, Email.forum_id == forum_id)
            )
            return convert_db_email_to_dto_email(result.scalar_one())
        except NoResultFound:
            return None

    @exception_mapper
    async def get_email_without_forum(self, user_id: int) -> EmailDTO | None:
        try:
            result = await self._session.execute(
                select(Email).where(Email.user_id == user_id, Email.forum_id == None)
            )
            return convert_db_email_to_dto_email(result.scalar_one())
        except NoResultFound:
            return None

    @exception_mapper
    async def set_forum(self, user_id: int, mail_address: str, forum_id: int) -> None:
        await self._session.execute(
            update(Email).where(Email.user_id == user_id, Email.mail_address == mail_address).values(
                forum_id=forum_id
            ))
        await self._session.commit()
