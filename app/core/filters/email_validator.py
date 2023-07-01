from typing import Callable, Coroutine

from aiogram import types, Bot
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from fluentogram import TranslatorRunner

from app.core.keyboards import inline
from app.core.responses import edit_or_build_email_message
from app.core.states.callbackdata_ids import EMAIL_PIPELINE_MESSAGE, EMAIL_SERVICE
from app.services.email import validator


def valid_email(handler: callable) -> Callable[[Message], Coroutine]:
    """Handlers for non-anon users with @username in Telegram"""

    async def wrapper(m: types.Message, bot: Bot, state: FSMContext, i18n: TranslatorRunner):
        data = await state.get_data()
        email = m.text.lower()
        if validator.is_valid_email(email):
            return await handler(m, bot, state, i18n, email)

        await edit_or_build_email_message(
            bot=bot, m=m, text=i18n.auth.incorrect_email(email_service=data.get(EMAIL_SERVICE).value.title),
            markup=inline.return_to_services,
            message_id=data.get(EMAIL_PIPELINE_MESSAGE), state=state
        )
        return

    return wrapper
