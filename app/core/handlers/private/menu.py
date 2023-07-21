from __future__ import annotations

from contextlib import suppress

from aiogram import types, Router, Bot
from aiogram.enums import ChatType
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import Command, Text
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from fluentogram import TranslatorRunner
from sqlalchemy.ext.asyncio import AsyncSession

from app.core import messages
from app.core.filters.chat_type import ChatTypeFilter
from app.core.filters.limiter import limits_not_reached
from app.core.keyboards import reply, inline
from app.core.navigations import reply as reply_callbacks
from app.core.navigations.command import Commands
from app.core.states import callbacks as inline_callbacks
from app.core.states.callbackdata_ids import MESSAGE_TO_REMOVE_ID
from app.core.states.mail_authorization import EmailAuth
from app.dtos.user import UserDTO
from app.services.database.dao.email import EmailDAO
from app.services.database.dao.user import UserDAO


async def cmd_start(m: Message, i18n: TranslatorRunner, session: AsyncSession, state: FSMContext):
    await state.clear()
    await _add_user_to_db(session=session, message=m)
    print(2 + 'v')
    with suppress(TelegramBadRequest):
        await m.answer(
            text=i18n.welcome.one(user_firstname=str(m.from_user.first_name)),  # type: ignore
            disable_web_page_preview=False
        )
    message = await m.answer(
        text=i18n.welcome.two(),
        reply_markup=reply.menu(i18n)
    )
    await state.set_data({MESSAGE_TO_REMOVE_ID: message.message_id})


async def cmd_cancel(m: Message, state: FSMContext, i18n: TranslatorRunner):
    await state.clear()
    await m.answer(text=i18n.cancel(), markup=reply.menu(i18n))


@limits_not_reached
async def btn_add_new_email(m: Message, bot: Bot, i18n: TranslatorRunner, state: FSMContext):
    data = await state.get_data()
    await m.delete()
    with suppress(TelegramBadRequest):
        if data.get(MESSAGE_TO_REMOVE_ID):
            await bot.delete_message(
                chat_id=m.from_user.id,  # type: ignore
                message_id=data.get(MESSAGE_TO_REMOVE_ID)
            )
    await m.answer(
        text=i18n.auth.choose_email_service(),
        reply_markup=inline.email_services()
    )
    await state.set_state(EmailAuth.service)


async def btn_my_emails(m: Message, session: AsyncSession, i18n: TranslatorRunner):
    emails_dao = EmailDAO(session)
    emails = await emails_dao.get_user_emails(m.from_user.id)  # type: ignore
    if not emails:
        await m.answer(
            text=i18n.auth.no_added_emails(),
            reply_markup=reply.menu(i18n)
        )
        return
    for email in emails:
        await m.answer(
            text=messages.get_email_info(email),
            reply_markup=inline.remove_email(i18n=i18n, email=email)
        )


async def cbq_remove_email(c: CallbackQuery, bot: Bot, session: AsyncSession,
                           callback_data: inline_callbacks.UserEmailCallbackFactory):
    emails_dao = EmailDAO(session)
    await emails_dao.remove_email(
        user_id=callback_data.user_id,
        email_address=callback_data.email_address
    )
    await bot.delete_message(chat_id=c.from_user.id, message_id=c.message.message_id)  # type: ignore


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
        Text(text=reply_callbacks.CONNECT_NEW_EMAIL)
    )

    router.message.register(
        btn_my_emails,
        ChatTypeFilter(chat_type=ChatType.PRIVATE),
        Text(text=reply_callbacks.MY_EMAILS)
    )

    router.callback_query.register(
        cbq_remove_email,
        ChatTypeFilter(chat_type=ChatType.PRIVATE),
        inline_callbacks.UserEmailCallbackFactory.filter()
    )

    return router


async def _add_user_to_db(session: AsyncSession, message: types.Message) -> None:
    dao = UserDAO(session)
    await dao.add_user(user=UserDTO.from_message(message))
