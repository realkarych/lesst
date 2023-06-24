from __future__ import annotations
from aiogram import types, Router, Bot
from aiogram.enums import ChatType
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from fluentogram import TranslatorRunner
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.filters.chat_type import ChatTypeFilter
from app.core.navigations.command import Commands


async def cmd_start(m: types.Message, bot: Bot, i18n: TranslatorRunner, session: AsyncSession, state: FSMContext):
    await state.clear()
    await m.answer(i18n.welcome(user_firstname=m.from_user.first_name))


def register() -> Router:
    router = Router()

    router.message.register(
        cmd_start,
        ChatTypeFilter(chat_type=ChatType.PRIVATE),
        Command(str(Commands.start))
    )

    return router


