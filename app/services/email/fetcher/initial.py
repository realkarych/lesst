from typing import AsyncGenerator

from app.services.email.cache import EmailCacheDirectory
from app.services.email.entities import EmailService, Email, EmailFlagPattern
from app.services.email.fetcher.base import Mailbox
from app.settings.limits import INITIAL_FETCH_EMAILS_COUNT


class InitialMailboxFetcher(Mailbox):

    def __init__(self, email_service: EmailService, email_address: str, email_auth_key: str, user_id: int,
                 cache_dir: EmailCacheDirectory) -> None:
        super().__init__(email_service, email_address, email_auth_key, user_id, cache_dir)

    async def fetch(self) -> AsyncGenerator[list[Email]]:
        emails: list[Email] = list()
        batch_size = 10
        email_count = 0
        for email_id in await self._get_email_ids():
            email = await self.get_email(email_id)
            if email:
                emails.append(email)
                email_count += 1
                if email_count >= batch_size:
                    email_count = 0
                    yield emails
                    emails.clear()

    async def _get_email_ids(self) -> list[str]:
        status, data = await self._client.search(EmailFlagPattern.ALL)
        ids = self._get_email_ids_from_response(data)[:INITIAL_FETCH_EMAILS_COUNT]
        ids.reverse()
        return ids

    @staticmethod
    def _get_email_ids_from_response(response_data: tuple) -> list[str]:
        data = str(response_data[0]).split()
        mail_ids = [''.join(filter(str.isdigit, _id)) for _id in data]
        return mail_ids
