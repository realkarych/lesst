from typing import Callable, Coroutine

from aiogram import Bot
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from fluentogram import TranslatorRunner
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.keyboards import inline
from app.core.messages import remove_messages
from app.core.responses import edit_or_build_email_message
from app.core.states.callbackdata_ids import EMAIL_PIPELINE_MESSAGE, EMAIL_SERVICE, MESSAGE_TO_REMOVE_ID
from app.services.database.dao.email import EmailDAO
from app.services.email import validator


def valid_email(handler: callable) -> Callable[[Message], Coroutine]:
    async def wrapper(m: Message, bot: Bot, state: FSMContext, session: AsyncSession, i18n: TranslatorRunner):
        data = await state.get_data()
        await remove_messages(chat_id=m.from_user.id, bot=bot,
                              ids=(m.message_id, data.get(MESSAGE_TO_REMOVE_ID, data.get(EMAIL_PIPELINE_MESSAGE))))
        email = m.text.lower()
        if validator.is_valid_email(email):
            return await handler(m, bot, state, session, i18n, email)

        await edit_or_build_email_message(
            bot=bot, m=m, text=i18n.auth.incorrect_email(email_service=data.get(EMAIL_SERVICE).value.title),
            markup=inline.return_to_services(i18n),
            message_id=data.get(EMAIL_PIPELINE_MESSAGE),
            state=state
        )
        return

    return wrapper


def new_email(handler: callable) -> Callable[[Message], Coroutine]:
    async def wrapper(m: Message, bot: Bot, state: FSMContext, session: AsyncSession, i18n: TranslatorRunner,
                      email: str):
        data = await state.get_data()
        dao = EmailDAO(session)
        if not await dao.email_already_added(email_address=email):
            return await handler(m, bot, state, i18n, email)

        await edit_or_build_email_message(
            bot=bot, m=m, text=i18n.auth.incorrect_email(email_service=data.get(EMAIL_SERVICE).value.title),
            markup=inline.return_to_services(i18n),
            message_id=data.get(EMAIL_PIPELINE_MESSAGE),
            state=state
        )
        return

    return wrapper
