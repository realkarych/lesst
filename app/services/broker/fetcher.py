from __future__ import annotations

import logging

from nats.js import JetStreamContext
from ormsgpack import ormsgpack
from sqlalchemy.ext.asyncio import async_sessionmaker

from app.dtos.email import UserEmailDTO
from app.dtos.incoming_email import IncomingEmailMessageDTO
from app.services.broker import consts
from app.services.database.dao.email import EmailDAO
from app.services.email.base.entities import get_service_by_id
from app.services.email.imap.attachments import IncomingAttachmentsDirectory
from app.services.email.imap.fetcher.mailbox import BroadcastMailbox


async def fetch_incoming_emails(session_pool: async_sessionmaker, jetstream: JetStreamContext) -> None:
    async with session_pool() as session:
        email_dao = EmailDAO(session)
        emails_with_forums = await email_dao.get_emails_with_forums()

        for user_email in emails_with_forums:
            user_email: UserEmailDTO

            not_sent_email_ids = await _get_not_sent_email_ids(user_email=user_email)
            if not not_sent_email_ids:
                continue

            for email_id in not_sent_email_ids:
                try:
                    await jetstream.publish(
                        subject=consts.EMAILS_SUBJECT,
                        payload=ormsgpack.packb(
                            IncomingEmailMessageDTO(
                                forum_id=user_email.forum_id,
                                mailbox_email_id=email_id,
                                email_db_id=user_email.email_db_id,
                                user_id=user_email.user_id
                            )
                        )
                    )
                except Exception as e:
                    logging.error(e)

            # Update last "handled" email-id. "Handled" means: "added to nats queue"
            await email_dao.set_last_sent_email_id_by_email_id(
                email_db_id=user_email.email_db_id,
                last_email_id=max(not_sent_email_ids)
            )


async def _get_not_sent_email_ids(user_email: UserEmailDTO) -> list[int] | list[None]:
    with IncomingAttachmentsDirectory(user_id=user_email.user_id) as cache_dir:
        async with BroadcastMailbox(
                cache_dir=cache_dir,
                email_address=user_email.mail_address,
                email_service=get_service_by_id(service_id=user_email.mail_server).value,
                email_auth_key=user_email.mail_auth_key,
                user_id=user_email.user_id
        ) as mailbox:
            if mailbox.can_connect():
                if user_email.last_email_id == 0:  # No sent emails yet. Realize initial Emails fetching
                    emails_ids = await mailbox.get_initial_emails_ids()
                else:  # There are already sent emails. Trying it out to fetch new Emails
                    emails_ids = await mailbox.get_not_sent_emails_ids(last_email_id=user_email.last_email_id)
                return emails_ids or []
    return []
