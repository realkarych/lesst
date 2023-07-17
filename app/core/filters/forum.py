from contextlib import suppress
from typing import Callable, Coroutine

from aiogram import Bot
from aiogram.exceptions import TelegramBadRequest
from aiogram.types import ChatMemberUpdated, ChatMemberOwner
from fluentogram import TranslatorRunner
from sqlalchemy.ext.asyncio import AsyncSession


def is_forum(handler: callable) -> Callable[[ChatMemberUpdated], Coroutine]:
    async def wrapper(event: ChatMemberUpdated, session: AsyncSession, bot: Bot, i18n: TranslatorRunner):
        if event.chat.is_forum:
            return await handler(event, session, bot, i18n)

        with suppress(TelegramBadRequest):
            await bot.send_message(chat_id=await _get_owner_id(event, bot), text=i18n.forum.not_forum)
        return

    return wrapper


async def _get_owner_id(event: ChatMemberUpdated, bot: Bot) -> int:
    chat_admins = await bot.get_chat_administrators(chat_id=event.chat.id)
    for admin in chat_admins:
        if isinstance(admin, ChatMemberOwner) and not admin.user.is_bot:
            return admin.user.id
