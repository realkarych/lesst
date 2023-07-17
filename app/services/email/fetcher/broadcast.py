from __future__ import annotations

import asyncio
from contextlib import suppress

from aioimaplib import aioimaplib

from app.services.email.entities import EmailFlagPattern
from app.services.email.fetcher.base import Mailbox
from app.settings import settings


class BroadcastMailbox(Mailbox):

    async def __aenter__(self) -> BroadcastMailbox:
        while connection_attempts := 0 < settings.EMAIL_BROADCASTER_CONNECTIONS_ATTEMPTS_COUNT:
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

    async def get_not_sent_emails_ids(self, last_email_id: int) -> list[int] | None:
        status, data = await self._client.search(EmailFlagPattern.ALL.value)
        all_ids = self._get_emails_ids_from_response(data)
        ids: list[int] = list()
        for email_id in all_ids:
            if email_id > last_email_id:
                ids.append(int(email_id))
            else:
                break
        ids.reverse()
        return ids if ids else None

    async def get_initial_emails_ids(self) -> list[int] | None:
        status, data = await self._client.search(EmailFlagPattern.ALL.value)
        all_ids = self._get_emails_ids_from_response(data)
        all_ids = all_ids[:settings.INITIAL_FETCH_EMAILS_COUNT]
        return all_ids[::-1] if all_ids else None

    @staticmethod
    def _get_emails_ids_from_response(response_data: tuple) -> list[int]:
        data = str(response_data[0]).split()
        email_ids = [int(''.join(filter(str.isdigit, _id))) for _id in data]
        # Bug in API. Last Email id doesn't fetch.
        email_ids.append(max(email_ids)+1)
        email_ids.reverse()
        return email_ids
