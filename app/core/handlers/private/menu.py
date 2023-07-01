from __future__ import annotations

from aiogram import types, Router, Bot
from aiogram.enums import ChatType
from aiogram.filters import Command, Text
from aiogram.fsm.context import FSMContext
from fluentogram import TranslatorRunner
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.filters.chat_type import ChatTypeFilter
from app.core.keyboards import reply, inline
from app.core.navigations.command import Commands
from app.core.responses import send_response
from app.core.states.callbackdata_ids import MESSAGE_TO_REMOVE_ID
from app.core.states.mail_authorization import EmailAuth
from app.dtos.user import UserDTO
from app.services.database.dao.user import UserDAO


async def cmd_start(m: types.Message, bot: Bot, i18n: TranslatorRunner, session: AsyncSession, state: FSMContext):
    await state.clear()
    await _add_user_to_db(session=session, message=m)
    await send_response(m, bot, text=i18n.welcome.one(user_firstname=m.from_user.first_name), web_preview=True)
    message = await send_response(m, bot, text=i18n.welcome.two(), markup=reply.menu(i18n))
    await state.set_data({MESSAGE_TO_REMOVE_ID: message.message_id})


async def cmd_cancel(m: types.Message, bot: Bot, state: FSMContext, i18n: TranslatorRunner):
    await state.clear()
    await send_response(m, bot, text=i18n.cancel(), markup=reply.menu(i18n))


async def btn_add_new_email(m: types.Message, bot: Bot, i18n: TranslatorRunner,
                            state: FSMContext):
    data = await state.get_data()
    await m.delete()
    await bot.delete_message(chat_id=m.from_user.id, message_id=data.get(MESSAGE_TO_REMOVE_ID))
    await send_response(m, bot, text=i18n.auth.choose_email_service(), markup=inline.email_services())
    await state.set_state(EmailAuth.service)


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
        Command(str(Commands.cancel)),

    )

    router.message.register(
        btn_add_new_email,
        ChatTypeFilter(chat_type=ChatType.PRIVATE),
        Text(text=["➕ Подключить новую почту", "➕ Connect new Email"])
    )

    return router


async def _add_user_to_db(session: AsyncSession, message: types.Message) -> None:
    dao = UserDAO(session)
    await dao.add_user(user=UserDTO.from_message(message))
