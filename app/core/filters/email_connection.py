from typing import Callable, Coroutine, Dict, Any

from aiogram import Bot
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, FSInputFile
from aioimaplib import aioimaplib
from fluentogram import TranslatorRunner
from sqlalchemy.ext.asyncio import AsyncSession

from app.core import urls
from app.core.keyboards import inline
from app.core.messages import remove_messages, enter_password_message
from app.core.responses import edit_or_build_email_message
from app.core.states.callbackdata_ids import EMAIL_PIPELINE_MESSAGE, EMAIL_SERVICE, EMAIL, PHOTO_TO_REMOVE_ID, \
    MESSAGE_GENERATE_KEY_ID, MESSAGE_TO_REMOVE_ID
from app.services.email.base.entities import EmailService, EmailServers
from app.services.email.imap.attachments import IncomingAttachmentsDirectory
from app.services.email.imap.fetcher.base import Mailbox
from app.settings.paths import get_imap_image_path


def connection_success(handler: callable) -> Callable[[Message], Coroutine]:
    async def wrapper(m: Message, bot: Bot, state: FSMContext, session: AsyncSession, i18n: TranslatorRunner):
        data = await state.get_data()
        await remove_messages(chat_id=m.from_user.id, bot=bot, ids=(
            m.message_id, data.get(MESSAGE_GENERATE_KEY_ID),
            data.get(PHOTO_TO_REMOVE_ID), data.get(MESSAGE_TO_REMOVE_ID)))
        password = str(m.text)
        if await is_connection_success(
                email_service=data.get(EMAIL_SERVICE).value,
                email=data.get(EMAIL),
                auth_key=password,
                user_id=m.from_user.id
        ):
            return await handler(m, bot, state, session, i18n)

        await edit_or_build_email_message(
            bot=bot, text=_get_connection_refused_message(data, i18n, password),
            message_id=data.get(EMAIL_PIPELINE_MESSAGE), markup=None, m=m, state=state)

        check_imap_params_photo = await m.answer_photo(
            photo=FSInputFile(path=get_imap_image_path(data.get(EMAIL_SERVICE))),
            reply_to_message_id=data.get(EMAIL_PIPELINE_MESSAGE)
        )
        password_message = await m.answer(
            enter_password_message(email_service=data.get(EMAIL_SERVICE), i18n=i18n),
            reply_markup=inline.return_to_email(i18n),
            disable_web_page_preview=True
        )

        await state.update_data({PHOTO_TO_REMOVE_ID: check_imap_params_photo.message_id})
        await state.update_data({MESSAGE_GENERATE_KEY_ID: password_message.message_id})

    return wrapper


def _get_connection_refused_message(data: Dict[str, Any], i18n: TranslatorRunner, auth_key: str):
    match data.get(EMAIL_SERVICE):
        case EmailServers.yandex:
            key_tutorial_url = urls.YANDEX_KEY_TUTORIAL_URL
            imap_tutorial_url = urls.YANDEX_IMAP_TUTORIAL_URL
        case EmailServers.gmail:
            key_tutorial_url = urls.GOOGLE_KEY_TUTORIAL_URL
            imap_tutorial_url = urls.GOOGLE_IMAP_TUTORIAL_URL
        case EmailServers.mail_ru:
            key_tutorial_url = urls.MAIL_RU_KEY_TUTORIAL_URL
            imap_tutorial_url = urls.MAIL_RU_IMAP_TUTORIAL_URL
        case _:
            key_tutorial_url = "https://google.com"
            imap_tutorial_url = "https://google.com"
    text = i18n.auth.connection_refused(
        email_service=data.get(EMAIL_SERVICE).value.title,
        email=data.get(EMAIL),
        password=auth_key,
        tutorial_url=key_tutorial_url,
        imap_tutorial_url=imap_tutorial_url
    )
    return text


async def is_connection_success(email_service: EmailService, email: str, auth_key: str, user_id: int) -> bool:
    with IncomingAttachmentsDirectory(user_id) as cache:
        mailbox = Mailbox(email_service=email_service, email_address=email, email_auth_key=auth_key, user_id=user_id,
                          cache_dir=cache)
        try:
            async with mailbox:
                can_create_connection = mailbox.can_connect()
                return can_create_connection
        except aioimaplib.Abort:
            return False
