from __future__ import annotations

import asyncio
from contextlib import suppress

from aioimaplib import aioimaplib
from bs4 import BeautifulSoup
from mailparser import mailparser

from app.services.email import parser
from app.services.email.cache import EmailCacheDirectory
from app.services.email.entities import EmailService, EmailConnectionType, Email
from app.settings.limits import EMAIL_CONNECTIONS_ATTEMPTS_COUNT


class Mailbox:

    def __init__(self, email_service: EmailService, email_address: str, email_auth_key: str,
                 user_id: int, cache_dir: EmailCacheDirectory) -> None:
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

    async def get_email(self, email_id: str) -> Email | None:
        response = await self._get_response(email_id)
        if not response:
            return None
        response_200, mail_bytes = response
        if not response_200:
            return None

        email = mailparser.parse_from_bytes(mail_bytes)
        soup = BeautifulSoup(" ".join(email.text_html), "html.parser")

        text = None
        subject = None

        if soup.text:
            text = parser.form_mail_text_nodes(soup.get_text())
        if email.subject:
            subject = email.subject

        attachments_paths = self._cache_dir.save_attachments(email=email, email_id=int(email_id))

        return Email(
            id_=email_id,
            from_name=email.from_[0][0],
            from_address=email.from_[0][1],
            to_=self._email_address,
            date=email.date,
            subject=subject,
            text=text,
            attachments_paths=attachments_paths
        )
