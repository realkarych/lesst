from __future__ import annotations

import asyncio
from contextlib import suppress

import dataclass_factory
from aiogram import Bot
from aiogram.exceptions import TelegramBadRequest, TelegramRetryAfter
from nats.js import JetStreamContext
from ormsgpack import ormsgpack
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.core.responses import send_topic_email
from app.dtos.email import EmailDTO
from app.dtos.incoming_email import IncomingEmailMessageDTO
from app.dtos.topic import TopicDTO
from app.services.broker import consts
from app.services.database.dao.email import EmailDAO
from app.services.database.dao.topic import TopicDAO
from app.services.email.cache import EmailCacheDirectory
from app.services.email.entities import get_service_by_id, Email
from app.services.email.fetcher.broadcast import BroadcastMailbox
from app.settings import settings


async def broadcast_incoming_emails(
        bot: Bot,
        session_pool: async_sessionmaker,
        jetstream: JetStreamContext
) -> None:
    async with session_pool() as session:
        email_dao = EmailDAO(session)

        subscriber = await jetstream.pull_subscribe(stream=consts.STREAM, subject=consts.ANY_SUBJECT,
                                                    durable=consts.DURABLE)
        factory = dataclass_factory.Factory()

        try:
            pulled_email_messages = await subscriber.fetch(settings.BROADCAST_BATCH_SIZE)
        except TimeoutError:
            return

        for pulled_email_message in pulled_email_messages:
            email_message = factory.load(ormsgpack.unpackb(pulled_email_message.data), IncomingEmailMessageDTO)
            user_mailbox = await email_dao.get_email(user_id=email_message.user_id, forum_id=email_message.forum_id)

            await email_dao.set_last_email_id(
                user_id=user_mailbox.user_id,
                email_address=user_mailbox.mail_address,
                last_email_id=email_message.mailbox_email_id
            )

            with EmailCacheDirectory(user_id=user_mailbox.user_id) as cache_dir:
                async with BroadcastMailbox(
                        cache_dir=cache_dir,
                        email_address=user_mailbox.mail_address,
                        email_service=get_service_by_id(service_id=user_mailbox.mail_server).value,
                        email_auth_key=user_mailbox.mail_auth_key,
                        user_id=email_message.user_id
                ) as mailbox:
                    if mailbox.can_connect():
                        email = await mailbox.get_email(email_id=str(email_message.mailbox_email_id))
                        if email:
                            await _broadcast_email(bot=bot, session=session, email=email,
                                                   forum_id=email_message.forum_id)

            await pulled_email_message.ack()


async def fetch_incoming_emails(
        session_pool: async_sessionmaker,
        jetstream: JetStreamContext
) -> None:
    async with session_pool() as session:
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
                        if not not_sent_email_ids:
                            return

                        await email_dao.set_last_email_id(
                            user_id=email.user_id,
                            email_address=email.mail_address,
                            last_email_id=max(not_sent_email_ids)
                        )

                        for email_id in not_sent_email_ids:
                            email_message = IncomingEmailMessageDTO(
                                forum_id=email.forum_id,
                                mailbox_email_id=email_id,
                                user_email_db_id=email.email_db_id,
                                user_id=email.user_id
                            )
                            await jetstream.publish(subject=consts.STREAM, payload=ormsgpack.packb(email_message))


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
