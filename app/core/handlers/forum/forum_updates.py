from __future__ import annotations

from contextlib import suppress

from aiogram import Router, Bot
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import ChatMemberUpdatedFilter, ADMINISTRATOR, IS_NOT_MEMBER, MEMBER, KICKED
from aiogram.types import ChatMemberUpdated, ChatMemberOwner, FSInputFile
from fluentogram import TranslatorRunner
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.filters.forum import is_forum
from app.dtos.email import EmailDTO
from app.dtos.incoming_email import IncomingEmailMessageDTO
from app.services.database.dao.email import EmailDAO
from app.services.database.dao.incoming import IncomingEmailMessageDAO
from app.services.email.cache import EmailCacheDirectory
from app.services.email.entities import get_service_by_id
from app.services.email.fetcher.initial import InitialMailboxFetcher
from app.settings import paths


@is_forum
async def handle_adding_to_forum(event: ChatMemberUpdated, session: AsyncSession, bot: Bot,
                                 i18n: TranslatorRunner) -> None:
    email_dao = EmailDAO(session=session)
    user_email = await _get_user_email(event=event, bot=bot, email_dao=email_dao, forum_id=event.chat.id)
    await email_dao.set_forum(user_id=user_email.user_id, forum_id=event.chat.id,
                              mail_address=user_email.mail_address)
    user_email = await email_dao.get_email(user_id=user_email.user_id, forum_id=event.chat.id)

    await _update_forum_settings(event, bot, i18n)

    if not user_email:
        await bot.send_message(chat_id=event.chat.id, text=i18n.forum.email_not_added())
        return
    try:
        await bot.send_message(chat_id=event.chat.id, text=i18n.forum.group_added())
    except TelegramBadRequest:
        with suppress(TelegramBadRequest):
            await bot.send_message(chat_id=user_email.user_id, text=i18n.forum.no_permissions())
        return

    incoming_dao = IncomingEmailMessageDAO(session=session)
    await incoming_dao.add_email_messages(await _get_email_messages(event=event, user_email=user_email))


async def _get_email_messages(event: ChatMemberUpdated, user_email: EmailDTO) -> list[IncomingEmailMessageDTO]:
    with EmailCacheDirectory(user_id=user_email.user_id) as cache_dir:
        async with InitialMailboxFetcher(
                cache_dir=cache_dir,
                email_address=user_email.mail_address,
                email_service=get_service_by_id(service_id=user_email.mail_server).value,
                email_auth_key=user_email.mail_auth_key,
                user_id=user_email.user_id
        ) as mailbox:
            if mailbox.can_connect():
                emails_ids = await mailbox.get_emails_ids()
                email_messages: list[IncomingEmailMessageDTO] = list()
                for email_id in emails_ids:
                    email_messages.append(IncomingEmailMessageDTO(
                        forum_id=event.chat.id,
                        mailbox_email_id=int(email_id),
                        user_email_db_id=user_email.email_db_id,
                        user_id=user_email.user_id
                    ))
                return email_messages


async def _update_forum_settings(event: ChatMemberUpdated, bot: Bot, i18n: TranslatorRunner) -> None:
    with suppress(TelegramBadRequest):
        await bot.set_chat_photo(chat_id=event.chat.id, photo=FSInputFile(path=paths.BOT_LOGO_IMAGE_PATH))

    with suppress(TelegramBadRequest):
        await bot.edit_general_forum_topic(chat_id=event.chat.id, name=i18n.forum.general_topic_name())


async def _get_user_email(event: ChatMemberUpdated, bot: Bot, email_dao: EmailDAO, forum_id: int) -> EmailDTO | None:
    chat_admins = await bot.get_chat_administrators(chat_id=event.chat.id)
    chat_owner_id = None
    for admin in chat_admins:
        if isinstance(admin, ChatMemberOwner) and not admin.user.is_bot:
            chat_owner_id = admin.user.id
            break
    if chat_owner_id:
        user_email = await email_dao.get_email_without_forum(user_id=chat_owner_id)
        if not user_email:
            user_email = await email_dao.get_email(user_id=chat_owner_id, forum_id=forum_id)
        return user_email


def register() -> Router:
    router = Router()
    router.my_chat_member.register(
        handle_adding_to_forum,
        ChatMemberUpdatedFilter(member_status_changed=(IS_NOT_MEMBER | MEMBER | KICKED) >> ADMINISTRATOR)
    )
    return router
