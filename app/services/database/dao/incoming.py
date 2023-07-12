from __future__ import annotations

from typing import Iterable

from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.dtos.converters import convert_db_incoming_email_message_to_dto
from app.dtos.incoming_email import IncomingEmailMessageDTO
from app.services.database.dao.base import BaseDAO
from app.services.database.exception_mapper import exception_mapper
from app.services.database.models import IncomingEmailMessage


class IncomingEmailMessageDAO(BaseDAO[IncomingEmailMessage]):

    def __init__(self, session: AsyncSession):
        super().__init__(IncomingEmailMessage, session)

    @exception_mapper
    async def add_email_message(self, email_message: IncomingEmailMessageDTO):
        await self._session.merge(email_message.to_db_model())
        await self.commit()

    @exception_mapper
    async def add_email_messages(self, email_messages: Iterable[IncomingEmailMessageDTO]):
        self._session.add_all([email_message.to_db_model() for email_message in email_messages])
        await self.commit()

    @exception_mapper
    async def remove_email_message(self, email_message: IncomingEmailMessageDTO) -> None:
        await self._session.execute(
            delete(IncomingEmailMessage).where(IncomingEmailMessage.id == email_message.email_db_id)
        )
        await self.commit()

    @exception_mapper
    async def get_email_messages(self, limit: int = 10) -> tuple[IncomingEmailMessageDTO]:
        result = await self._session.execute(
            select(IncomingEmailMessage).
            order_by(IncomingEmailMessage.mailbox_email_id).
            limit(limit)
        )
        return tuple([convert_db_incoming_email_message_to_dto(topic) for topic in result.scalars()])
