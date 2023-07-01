from __future__ import annotations

from contextlib import suppress
from typing import Iterable

from aiogram import types, Router, Bot
from aiogram.enums import ChatType, ParseMode
from aiogram.exceptions import TelegramBadRequest
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardMarkup, ReplyKeyboardMarkup, Message, FSInputFile
from fluentogram import TranslatorRunner

from app.core import urls
from app.core.filters.chat_type import ChatTypeFilter
from app.core.filters.email_validator import valid_email
from app.core.keyboards import inline
from app.core.responses import edit_or_build_email_message
from app.core.states.callbackdata_ids import EMAIL_PIPELINE_MESSAGE, EMAIL_SERVICE, MESSAGE_TO_REMOVE_ID, EMAIL, \
    PHOTO_TO_REMOVE_ID
from app.core.states.callbacks import EmailServiceCallbackFactory
from app.core.states.mail_authorization import EmailAuth
from app.services.email.entities import get_service_by_id, EmailServices
from app.settings import paths


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
async def handle_valid_email(m: Message, bot: Bot, state: FSMContext, i18n: TranslatorRunner, email: str):
    data = await state.get_data()
    await _remove_messages(chat_id=m.from_user.id, bot=bot,
                           ids=(m.message_id, data.get(MESSAGE_TO_REMOVE_ID, data.get(EMAIL_PIPELINE_MESSAGE))))

    await edit_or_build_email_message(
        bot=bot,
        m=m,
        text=_get_imap_params_message(i18n=i18n, email_service=data.get(EMAIL_SERVICE), email=email),
        markup=None,
        message_id=data.get(EMAIL_PIPELINE_MESSAGE),
        state=state
    )
    photo_message = await m.answer_photo(
        photo=FSInputFile(path=_get_imap_image_path(data.get(EMAIL_SERVICE))),
        caption=_enter_password_message(data.get(EMAIL_SERVICE), i18n),
        reply_markup=inline.return_to_email
    )

    await state.update_data({EMAIL: email})
    await state.update_data({PHOTO_TO_REMOVE_ID: photo_message.message_id})
    await state.set_state(EmailAuth.password)


def _enter_password_message(email_service: EmailServices, i18n: TranslatorRunner) -> str:
    match email_service:
        case EmailServices.yandex:
            tutorial_url = urls.YANDEX_KEY_TUTORIAL_URL
        case EmailServices.gmail:
            tutorial_url = urls.GOOGLE_KEY_TUTORIAL_URL
        case EmailServices.mail_ru:
            tutorial_url = urls.MAIL_RU_KEY_TUTORIAL_URL
        case _:
            tutorial_url = urls.GOOGLE_KEY_TUTORIAL_URL
    if tutorial_url:
        return i18n.auth.enter_password(tutorial_url=tutorial_url)


def _get_imap_image_path(email_service: EmailServices) -> str:
    match email_service:
        case EmailServices.yandex:
            path = paths.YANDEX_IMAP_IMAGE_PATH
        case EmailServices.gmail:
            path = paths.GOOGLE_IMAP_IMAGE_PATH
        case EmailServices.mail_ru:
            path = paths.MAIL_RU_IMAP_IMAGE_PATH
        case _:
            path = paths.GOOGLE_IMAP_IMAGE_PATH
    return path


def _get_imap_params_message(i18n: TranslatorRunner, email_service: EmailServices, email: str) -> str:
    match email_service:
        case EmailServices.yandex:
            return i18n.auth.set_imap_params.yandex(email_service=email_service.value.title, email=email)
        case EmailServices.gmail:
            return i18n.auth.set_imap_params.gmail(email_service=email_service.value.title, email=email)
        case EmailServices.mail_ru:
            return i18n.auth.set_imap_params.mail_ru(email_service=email_service.value.title, email=email)


async def _remove_messages(chat_id: int, bot: Bot, ids: Iterable[int]) -> None:
    for message_id in ids:
        if message_id:
            with suppress(TelegramBadRequest):
                await bot.delete_message(chat_id, message_id)


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
