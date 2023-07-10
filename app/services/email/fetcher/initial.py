from app.services.email.cache import EmailCacheDirectory
from app.services.email.entities import EmailService, EmailFlagPattern
from app.services.email.fetcher.base import Mailbox
from app.settings.limits import INITIAL_FETCH_EMAILS_COUNT


class InitialMailboxFetcher(Mailbox):
    def __init__(self, email_service: EmailService, email_address: str, email_auth_key: str, user_id: int,
                 cache_dir: EmailCacheDirectory):
        super().__init__(email_service, email_address, email_auth_key, user_id, cache_dir)

    async def get_emails_ids(self, max_count: int = INITIAL_FETCH_EMAILS_COUNT,
                             flag: EmailFlagPattern = EmailFlagPattern.ALL,
                             order_from_new_to_old: bool = True) -> list[str]:
        status, data = await self._client.search(flag())
        ids = self._get_emails_ids_from_response(data)[:max_count]
        if order_from_new_to_old:
            ids.reverse()
            return ids
        return ids

    @staticmethod
    def _get_emails_ids_from_response(response_data: tuple) -> list[str]:
        data = str(response_data[0]).split()
        mail_ids = [''.join(filter(str.isdigit, _id)) for _id in data]
        mail_ids.reverse()
        return mail_ids
