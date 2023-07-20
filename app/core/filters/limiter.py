from contextlib import suppress
from typing import Callable, Coroutine

from aiogram import Bot
from aiogram.exceptions import TelegramBadRequest
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from fluentogram import TranslatorRunner
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.database.dao.email import EmailDAO
from app.settings import settings


def limits_not_reached(handler: callable) -> Callable[[Message], Coroutine]:
    async def wrapper(m: Message, bot: Bot, state: FSMContext, session: AsyncSession, i18n: TranslatorRunner):
        dao = EmailDAO(session)
        current_emails_count = await dao.get_user_emails_count(user_id=m.from_user.id)
        if current_emails_count < settings.MAX_EMAILS_COUNT_FOR_DEFAULT_USER:
            return await handler(m, bot, i18n, state)

        #  Say to remove some Email because of max count of user-Emails exceeded.
        with suppress(TelegramBadRequest):
            await m.reply(i18n.auth.emails_count_limit_exceeded(max_emails_count=current_emails_count))
        return

    return wrapper
