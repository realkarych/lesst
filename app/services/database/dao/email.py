from __future__ import annotations

from sqlalchemy import update, select, delete, func
from sqlalchemy.exc import NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession

from app.dtos import converters
from app.dtos.email import UserEmailDTO
from app.services.database.dao.base import BaseDAO
from app.services.database.exception_mapper import exception_mapper
from app.services.database.models import Email


class EmailDAO(BaseDAO[Email]):

    def __init__(self, session: AsyncSession):
        super().__init__(Email, session)

    @exception_mapper
    async def add_email(self, email: UserEmailDTO) -> None:
        await self._session.merge(email.to_db_model())
        await self.commit()

    @exception_mapper
    async def email_already_added(self, email_address: str) -> bool:
        result = await self._session.execute(
            select(Email).where(Email.mail_address == email_address)
        )
        return bool(result.scalar_one_or_none())

    @exception_mapper
    async def get_email(self, user_id: int, forum_id: int) -> UserEmailDTO | None:
        try:
            result = await self._session.execute(
                select(Email).where(Email.user_id == user_id, Email.forum_id == forum_id)
            )
            return converters.db_email_to_dto(result.scalar_one())
        except NoResultFound:
            return None

    @exception_mapper
    async def get_emails_with_forums(self) -> list[UserEmailDTO] | list[None]:
        try:
            result = await self._session.execute(
                select(Email).where(Email.forum_id.isnot(None))
            )
            return [converters.db_email_to_dto(email) for email in result.scalars()]
        except NoResultFound:
            return []

    @exception_mapper
    async def get_user_emails(self, user_id: int) -> tuple[UserEmailDTO] | None:
        try:
            result = await self._session.execute(
                select(Email).where(Email.user_id == user_id)
            )
            return tuple([converters.db_email_to_dto(email) for email in result.scalars()])
        except NoResultFound:
            return None

    @exception_mapper
    async def get_user_emails_count(self, user_id: int) -> int:
        result = await self._session.execute(select(func.count(Email.id)).where(Email.user_id == user_id))
        return result.scalar_one()

    @exception_mapper
    async def get_email_without_forum(self, user_id: int) -> UserEmailDTO | None:
        try:
            result = await self._session.execute(
                select(Email).where(Email.user_id == user_id, Email.forum_id.is_(None))
            )
            return converters.db_email_to_dto(result.scalar_one())
        except NoResultFound:
            return None

    @exception_mapper
    async def set_last_sent_email_id(self, user_id: int, email_address: str, last_email_id: int) -> None:
        await self._session.execute(
            update(Email).where(
                Email.user_id == user_id,
                Email.mail_address == email_address,
                Email.last_email_id < last_email_id).
            values(last_email_id=last_email_id)
        )
        await self.commit()

    @exception_mapper
    async def set_last_sent_email_id_by_email_id(self, email_db_id: int, last_email_id: int) -> None:
        await self._session.execute(
            update(Email).where(
                Email.id == email_db_id,
                Email.last_email_id < last_email_id).
            values(last_email_id=last_email_id)
        )
        await self.commit()

    @exception_mapper
    async def set_forum(self, user_id: int, email_address: str, forum_id: int) -> None:
        await self._session.execute(
            update(Email).where(Email.user_id == user_id, Email.mail_address == email_address).values(
                forum_id=forum_id
            )
        )
        await self.commit()

    @exception_mapper
    async def unset_forum(self, user_id: int, email_address: str) -> None:
        await self._session.execute(
            update(Email).where(Email.user_id == user_id, Email.mail_address == email_address).values(
                forum_id=None
            )
        )
        await self.commit()

    @exception_mapper
    async def remove_email(self, user_id: int, email_address: str) -> None:
        await self._session.execute(
            delete(Email).where(Email.user_id == user_id, Email.mail_address == email_address)
        )
        await self.commit()
