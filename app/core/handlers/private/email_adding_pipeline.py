from __future__ import annotations

from aiogram import types, Router, Bot
from aiogram.enums import ChatType
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, FSInputFile
from fluentogram import TranslatorRunner
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.filters.chat_type import ChatTypeFilter
from app.core.filters.email_connection import connection_success
from app.core.filters.email_validator import valid_email, new_email
from app.core.keyboards import inline
from app.core.messages import remove_messages, enter_password_message
from app.core.responses import edit_or_build_email_message
from app.core.states.callbackdata_ids import EMAIL_PIPELINE_MESSAGE, EMAIL_SERVICE, MESSAGE_TO_REMOVE_ID, EMAIL, \
    PHOTO_TO_REMOVE_ID
from app.core.states.callbacks import EmailServiceCallbackFactory
from app.core.states.mail_authorization import EmailAuth
from app.dtos.email import EmailDTO
from app.services.database.dao.email import EmailDAO
from app.services.email.entities import get_service_by_id, EmailServices
from app.settings import paths
from app.settings.paths import get_imap_image_path


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
@new_email
async def handle_valid_email(m: Message, bot: Bot, state: FSMContext, i18n: TranslatorRunner, email: str):
    data = await state.get_data()

    await edit_or_build_email_message(
        bot=bot,
        m=m,
        text=_get_imap_params_message(i18n=i18n, email_service=data.get(EMAIL_SERVICE), email=email),
        markup=None,
        message_id=data.get(EMAIL_PIPELINE_MESSAGE),
        state=state
    )
    photo_message = await m.answer_photo(
        photo=FSInputFile(path=get_imap_image_path(data.get(EMAIL_SERVICE))),
        caption=enter_password_message(data.get(EMAIL_SERVICE), i18n),
        reply_markup=inline.return_to_email
    )

    await state.update_data({EMAIL: email})
    await state.update_data({PHOTO_TO_REMOVE_ID: photo_message.message_id})
    await state.set_state(EmailAuth.password)


@connection_success
async def handle_correct_password(m: Message, bot: Bot, state: FSMContext, session: AsyncSession,
                                  i18n: TranslatorRunner):
    data = await state.get_data()

    auth_key = str(m.text)
    text = i18n.auth.connection_success(
        email_service=data.get(EMAIL_SERVICE).value.title,
        email=data.get(EMAIL),
        password=auth_key
    )
    await edit_or_build_email_message(bot=bot, m=m, message_id=data.get(EMAIL_PIPELINE_MESSAGE), text=text, markup=None,
                                      state=state)

    await EmailDAO(session=session).add_email(
        email=EmailDTO.from_email(
            user_id=m.from_user.id,
            email_service=data.get(EMAIL_SERVICE).value,
            email_address=data.get(EMAIL),
            email_auth_key=auth_key
        )
    )
    await state.clear()

    await m.answer_photo(photo=FSInputFile(path=paths.ACTIVATE_TOPICS_IMAGE_PATH), caption=i18n.auth.create_group())
    await m.answer_photo(photo=FSInputFile(path=paths.GROUP_SETTINGS_IMAGE_PATH), caption=i18n.auth.add_to_chat(),
                         reply_markup=inline.add_to_chat)


def _get_imap_params_message(i18n: TranslatorRunner, email_service: EmailServices, email: str) -> str:
    match email_service:
        case EmailServices.yandex:
            return i18n.auth.set_imap_params.yandex(email_service=email_service.value.title, email=email)
        case EmailServices.gmail:
            return i18n.auth.set_imap_params.gmail(email_service=email_service.value.title, email=email)
        case EmailServices.mail_ru:
            return i18n.auth.set_imap_params.mail_ru(email_service=email_service.value.title, email=email)


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

    router.message.register(
        handle_correct_password,
        ChatTypeFilter(chat_type=ChatType.PRIVATE),
        EmailAuth.password
    )

    return router
