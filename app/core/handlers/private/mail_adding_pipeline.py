from __future__ import annotations

from aiogram import types, Router, Bot
from aiogram.enums import ChatType, ParseMode
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import Command, Text
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardMarkup, ReplyKeyboardMarkup
from fluentogram import TranslatorRunner
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.filters.chat_type import ChatTypeFilter
from app.core.filters.email_validator import valid_email
from app.core.keyboards import reply, inline
from app.core.navigations.command import Commands
from app.core.responses import send_response
from app.core.states.callbackdata_ids import EMAIL_PIPELINE_MESSAGE, MESSAGE_TO_REMOVE_ID, EMAIL_SERVICE
from app.core.states.callbacks import EmailServiceCallbackFactory
from app.core.states.mail_authorization import EmailAuth
from app.dtos.user import UserDTO
from app.services.database.dao.user import UserDAO
from app.services.email.entities import get_service_by_id


async def cbq_email_service(
        c: types.CallbackQuery,
        callback_data: EmailServiceCallbackFactory,
        i18n: TranslatorRunner,
        state: FSMContext
):
    service = get_service_by_id(service_id=callback_data.service_id)
    await c.message.edit_text(i18n.auth.enter_email(email_service=service.value.title),
                              reply_markup=inline.return_to_services)
    await state.update_data({EMAIL_SERVICE: service})
    await state.update_data({EMAIL_PIPELINE_MESSAGE: c.message.message_id})
    await state.set_state(EmailAuth.email)


@valid_email
async def handle_valid_email(m: types.Message, bot: Bot, state: FSMContext, i18n: TranslatorRunner, email: str):
    pass


async def _edit_or_build_email_message(
        bot: Bot,
        m: types.Message,
        message_id: int,
        text: str,
        markup: InlineKeyboardMarkup | ReplyKeyboardMarkup | None,
        state: FSMContext,
        disable_web_page_preview: bool = True,
        parse_mode: ParseMode | None = ParseMode.HTML
) -> None:
    """
    Method implements updates mail message. If it has been removed by user, creates new and update message id in
    MemoryStorage
    """

    try:
        await bot.edit_message_text(
            chat_id=m.from_user.id,
            message_id=message_id,
            text=text,
            disable_web_page_preview=disable_web_page_preview,
            reply_markup=markup,
            parse_mode=parse_mode
        )

    except TelegramBadRequest:
        new_message = await m.answer(
            text=text,
            disable_web_page_preview=disable_web_page_preview,
            reply_markup=markup,
            parse_mode=parse_mode
        )
        await state.update_data({EMAIL_PIPELINE_MESSAGE: new_message.message_id})


def register() -> Router:
    router = Router()

    router.callback_query.register(
        cbq_email_service,
        ChatTypeFilter(chat_type=ChatType.PRIVATE),
        EmailServiceCallbackFactory.filter(),
        EmailAuth.service
    )

    router.message.register(
        handle_valid_email,
        ChatTypeFilter(chat_type=ChatType.PRIVATE),
        EmailAuth.email
    )

    return router
