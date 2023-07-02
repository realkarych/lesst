from contextlib import suppress
from typing import Iterable

from aiogram import Bot
from aiogram.exceptions import TelegramBadRequest
from fluentogram import TranslatorRunner

from app.core import urls
from app.services.email.entities import EmailServices


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
