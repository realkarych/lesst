from __future__ import annotations

import asyncio
import email
from contextlib import suppress

from aioimaplib import aioimaplib
from mailparser import mailparser

from app.services.email.base.entities import EmailService, EmailConnectionType, IncomingEmail
from app.services.email.imap import parser
from app.services.email.imap.attachments import IncomingAttachmentsDirectory
from app.services.email.imap.parser import get_email_text
from app.settings.settings import EMAIL_CONNECTIONS_ATTEMPTS_COUNT


class Mailbox:

    def __init__(self, email_service: EmailService, email_address: str, email_auth_key: str,
                 user_id: int, cache_dir: IncomingAttachmentsDirectory) -> None:
        self._email_service = email_service
        self._email_address = email_address
        self._email_auth_key = email_auth_key
        self._user_id = user_id
        self._cache_dir = cache_dir

    async def __aenter__(self) -> Mailbox:
        while connection_attempts := 0 < EMAIL_CONNECTIONS_ATTEMPTS_COUNT:
            with suppress(TimeoutError):
                self._client = aioimaplib.IMAP4_SSL(
                    host=self._email_service.imap.server,
                    port=self._email_service.imap.port
                )
                await self._client.wait_hello_from_server()
                await self._client.login(self._email_address, self._email_auth_key)
                await self._client.select("inbox")
                break

            await asyncio.sleep(0.1)
            connection_attempts += 1
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self._client.logout()

    def can_connect(self) -> bool:
        connection_state = self._client.get_state()
        if connection_state in (EmailConnectionType.AUTH, EmailConnectionType.SELECTED):
            return True
        return False

    async def _get_response(self, email_id: str) -> tuple[bool, bytes] | None:
        status, data = await self._client.uid("fetch", email_id, "(RFC822)")
        try:
            return status == "OK", data[1]
        except IndexError:
            return None

    async def get_email(self, email_id: str) -> IncomingEmail | None:
        response = await self._get_response(email_id)
        if not response:
            return None
        response_200, mail_bytes = response
        if not response_200:
            return None

        letter = mailparser.parse_from_bytes(mail_bytes)

        subject = None

        all_text = get_email_text(email.message_from_bytes(mail_bytes))
        if all_text:
            text_nodes = parser.form_mail_text_nodes(all_text)
        else:
            text_nodes = None

        if letter.subject:
            subject = letter.subject

        attachments_paths = self._cache_dir.save_attachments(email=letter, email_id=int(email_id))

        return IncomingEmail(
            id_=str(email_id),
            from_name=str(letter.from_[0][0]),
            from_address=str(letter.from_[0][1]),
            to_=str(self._email_address),
            date=letter.date,
            subject=str(subject),
            text=text_nodes,
            attachments_paths=attachments_paths
        )
