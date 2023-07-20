from contextlib import suppress
from typing import Iterable

from aiogram import Bot
from aiogram.exceptions import TelegramBadRequest
from fluentogram import TranslatorRunner

from app.core import urls
from app.dtos.email import EmailDTO
from app.services.email.entities import EmailServices, Email, get_service_by_id


async def remove_messages(chat_id: int, bot: Bot, ids: Iterable[int]) -> None:
    for message_id in ids:
        if message_id:
            with suppress(TelegramBadRequest):
                await bot.delete_message(chat_id, message_id)


def enter_password_message(email_service: EmailServices, i18n: TranslatorRunner) -> str:
    match email_service.value:
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


def get_imap_params_message(i18n: TranslatorRunner, email_service: EmailServices, email: str) -> str:
    match email_service:
        case EmailServices.yandex:
            return i18n.auth.set_imap_params.yandex(email_service=email_service.value.title, email=email)
        case EmailServices.gmail:
            return i18n.auth.set_imap_params.gmail(email_service=email_service.value.title, email=email)
        case EmailServices.mail_ru:
            return i18n.auth.set_imap_params.mail_ru(email_service=email_service.value.title, email=email)


def first_email_message(email: Email) -> str:
    return f"{email.from_name}: {email.subject}\n\n{email.text[0]}"


def last_email_message(email: Email) -> str:
    return f"{email.text[-1]}\n\n{email.date}"


def email_message_without_text(email: Email) -> str:
    return f"{email.from_name}: {email.subject}\n\n{email.date}"


def get_email_info(email: EmailDTO) -> str:
    return f"<b>Сервер:</b> <code>{get_service_by_id(email.mail_server).value.title}</code>\n" \
           f"<b>Email:</b> <code>{email.mail_address}</code>\n" \
           f"<b>Ключ доступа:</b> <span class=\"tg-spoiler\">{email.mail_auth_key}</span>\n" \
           f"<b>ID Форума:</b> <code>{email.forum_id}</code>"
