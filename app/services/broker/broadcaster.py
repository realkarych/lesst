from __future__ import annotations

import logging
from contextlib import suppress

import dataclass_factory
from aiogram import Bot
from aiogram.exceptions import TelegramBadRequest, TelegramForbiddenError
from nats.aio.msg import Msg
from nats.errors import ConnectionClosedError
from nats.js import JetStreamContext
from ormsgpack import ormsgpack
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.core.responses import send_topic_email
from app.dtos.email import UserEmailDTO
from app.dtos.incoming_email import IncomingEmailMessageDTO
from app.dtos.topic import TopicDTO
from app.services.broker import consts
from app.services.database.dao.email import EmailDAO
from app.services.database.dao.topic import TopicDAO
from app.services.email.base.entities import get_service_by_id, IncomingEmail
from app.services.email.imap.attachments import IncomingAttachmentsDirectory
from app.services.email.imap.fetcher.mailbox import BroadcastMailbox
from app.settings import settings


async def broadcast_incoming_emails(bot: Bot, session_pool: async_sessionmaker, jetstream: JetStreamContext) -> None:
    async with session_pool() as session:
        email_dao = EmailDAO(session)
        subscriber = await jetstream.pull_subscribe(stream=consts.STREAM, subject=consts.ANY_SUBJECT,
                                                    durable=consts.DURABLE)
        try:
            pulled_email_messages = await subscriber.fetch(settings.BROADCAST_BATCH_SIZE)
        except (TimeoutError, ConnectionClosedError):
            return

        for pulled_email_message in pulled_email_messages:
            email_message = _unpack_email_message(pulled_email_message)
            user_email = await email_dao.get_email(user_id=email_message.user_id, forum_id=email_message.forum_id)
            if not user_email:
                await pulled_email_message.ack()
                continue

            await email_dao.set_last_sent_email_id(
                user_id=user_email.user_id,
                email_address=user_email.mail_address,
                last_email_id=email_message.mailbox_email_id
            )

            await _broadcast(bot=bot, session=session, user_email=user_email, email_message=email_message)
            await pulled_email_message.ack()


def _unpack_email_message(pulled_email_message: Msg) -> IncomingEmailMessageDTO:
    factory = dataclass_factory.Factory()
    message = factory.load(ormsgpack.unpackb(pulled_email_message.data), IncomingEmailMessageDTO)
    return message


async def _broadcast(
        user_email: UserEmailDTO, bot: Bot, session: AsyncSession, email_message: IncomingEmailMessageDTO
):
    with IncomingAttachmentsDirectory(user_id=user_email.user_id) as cache_dir:
        async with BroadcastMailbox(
                cache_dir=cache_dir,
                email_address=user_email.mail_address,
                email_service=get_service_by_id(service_id=user_email.mail_server).value,
                email_auth_key=user_email.mail_auth_key,
                user_id=user_email.user_id
        ) as mailbox:
            if mailbox.can_connect():
                email = await mailbox.get_email(email_id=str(email_message.mailbox_email_id))
                if email:
                    try:
                        await _send_email(bot=bot, session=session, email=email, forum_id=email_message.forum_id)
                    except (TelegramBadRequest, TelegramForbiddenError):
                        pass
                    except Exception as e:
                        logging.error(e)


async def _send_email(bot: Bot, session: AsyncSession, email: IncomingEmail, forum_id: int) -> None:
    topic_dao = TopicDAO(session)
    is_topic_created = await topic_dao.is_topic_created(forum_id=forum_id, email_address=email.from_address)
    if not is_topic_created:
        await _create_topic(bot=bot, topic_dao=topic_dao, forum_id=forum_id, email=email)

    topic = await topic_dao.get_topic(forum_id=forum_id, email_address=email.from_address)

    try:
        await send_topic_email(bot=bot, email=email, topic=topic)
    except Exception as e:
        logging.error(e)


async def _create_topic(bot: Bot, topic_dao: TopicDAO, forum_id: int, email: IncomingEmail):
    with suppress(TelegramBadRequest):
        new_topic = await bot.create_forum_topic(chat_id=forum_id, name=email.from_address)
        await topic_dao.add_topic(
            TopicDTO(
                forum_id=forum_id,
                topic_id=new_topic.message_thread_id,
                topic_name=email.from_address
            )
        )
