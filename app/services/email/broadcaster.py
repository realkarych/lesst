from __future__ import annotations

from contextlib import suppress

from aiogram import Bot
from aiogram.exceptions import TelegramBadRequest
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.core.responses import send_topic_email
from app.dtos.email import EmailDTO
from app.dtos.incoming_email import IncomingEmailMessageDTO
from app.dtos.topic import TopicDTO
from app.services.database.dao.email import EmailDAO
from app.services.database.dao.incoming import IncomingEmailMessageDAO
from app.services.database.dao.topic import TopicDAO
from app.services.email.cache import EmailCacheDirectory
from app.services.email.entities import get_service_by_id, Email
from app.services.email.fetcher.broadcast import BroadcastMailbox


async def broadcast_incoming_emails(bot: Bot, session_pool: async_sessionmaker) -> None:
    async with session_pool() as session:
        incoming_dao = IncomingEmailMessageDAO(session)
        email_dao = EmailDAO(session)

        incoming_email_messages = await incoming_dao.get_email_messages()
        for incoming_email in incoming_email_messages:
            user_email_data = await email_dao.get_email(user_id=incoming_email.user_id,
                                                        forum_id=incoming_email.forum_id)

            with EmailCacheDirectory(user_id=user_email_data.user_id) as cache_dir:
                async with BroadcastMailbox(
                        cache_dir=cache_dir,
                        email_address=user_email_data.mail_address,
                        email_service=get_service_by_id(service_id=user_email_data.mail_server).value,
                        email_auth_key=user_email_data.mail_auth_key,
                        user_id=incoming_email.user_id
                ) as mailbox:
                    if mailbox.can_connect():
                        email = await mailbox.get_email(email_id=str(incoming_email.mailbox_email_id))
                        if email:
                            await _broadcast_email(bot=bot, session=session, email=email,
                                                   forum_id=incoming_email.forum_id)
                            await email_dao.set_last_email_id(
                                user_id=user_email_data.user_id,
                                email_address=user_email_data.mail_address,
                                last_email_id=incoming_email.mailbox_email_id
                            )

            await incoming_dao.remove_email_message(email_message=incoming_email)


async def fetch_incoming_emails(session_pool: async_sessionmaker) -> None:
    async with session_pool() as session:
        incoming_dao = IncomingEmailMessageDAO(session)
        email_dao = EmailDAO(session)
        for email in await email_dao.get_all_emails_with_forums():
            email: EmailDTO
            with EmailCacheDirectory(user_id=email.user_id) as cache_dir:
                async with BroadcastMailbox(
                        cache_dir=cache_dir,
                        email_address=email.mail_address,
                        email_service=get_service_by_id(service_id=email.mail_server).value,
                        email_auth_key=email.mail_auth_key,
                        user_id=email.user_id
                ) as mailbox:
                    if mailbox.can_connect():
                        not_sent_email_ids = await mailbox.get_not_sent_emails_ids(last_email_id=email.last_email_id)
                        email_messages: list[IncomingEmailMessageDTO] = list()
                        for email_id in not_sent_email_ids:
                            email_messages.append(
                                IncomingEmailMessageDTO(
                                    forum_id=email.forum_id,
                                    mailbox_email_id=email_id,
                                    user_email_db_id=email.email_db_id,
                                    user_id=email.user_id
                                )
                            )
                        await incoming_dao.add_email_messages(email_messages)
                        await email_dao.set_last_email_id(
                            user_id=email.user_id,
                            email_address=email.mail_address,
                            last_email_id=not_sent_email_ids[0])


async def _broadcast_email(bot: Bot, session: AsyncSession, email: Email, forum_id: int) -> None:
    topic_dao = TopicDAO(session)
    is_topic_created = await topic_dao.is_topic_created(forum_id=forum_id, email_address=email.from_address)
    if not is_topic_created:
        await _create_topic(bot=bot, topic_dao=topic_dao, forum_id=forum_id, email=email)

    topic = await topic_dao.get_topic(forum_id=forum_id, email_address=email.from_address)
    await send_topic_email(bot=bot, email=email, topic=topic)


async def _create_topic(bot: Bot, topic_dao: TopicDAO, forum_id: int, email: Email):
    with suppress(TelegramBadRequest):
        new_topic = await bot.create_forum_topic(chat_id=forum_id, name=email.from_address)
        await topic_dao.add_topic(
            TopicDTO(
                forum_id=forum_id,
                topic_id=new_topic.message_thread_id,
                topic_name=email.from_address
            )
        )
