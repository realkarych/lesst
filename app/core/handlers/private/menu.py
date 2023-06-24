from __future__ import annotations

from aiogram import types, Router, Bot
from aiogram.enums import ChatType
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from fluentogram import TranslatorRunner
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.filters.chat_type import ChatTypeFilter
from app.core.navigations.command import Commands
from app.core.responses import send_response
from app.dtos.user import UserDTO
from app.services.database.dao.user import UserDAO


async def cmd_start(m: types.Message, bot: Bot, i18n: TranslatorRunner, session: AsyncSession, state: FSMContext):
    await state.clear()
    dao = UserDAO(session)
    await dao.add_user(user=UserDTO.from_message(m))
    await send_response(message=m, bot=bot, text=i18n.welcome(user_firstname=m.from_user.first_name))


async def cmd_cancel(m: types.Message, bot: Bot, state: FSMContext, i18n: TranslatorRunner):
    await state.clear()
    await send_response(message=m, bot=bot, text=i18n.cancel())


def register() -> Router:
    router = Router()

    router.message.register(
        cmd_start,
        ChatTypeFilter(chat_type=ChatType.PRIVATE),
        Command(str(Commands.start))
    )

    router.message.register(
        cmd_cancel,
        ChatTypeFilter(chat_type=ChatType.PRIVATE),
        Command(str(Commands.cancel))
    )

    return router
