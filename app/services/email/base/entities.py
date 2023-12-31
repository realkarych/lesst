from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import Enum


@dataclass(frozen=True)
class IncomingEmail:
    id_: str
    from_name: str
    from_address: str
    to_: str
    date: datetime | None = None
    subject: str | None = None
    text: list[str] | None = None
    attachments_paths: tuple[str] | None = None


@dataclass(frozen=True)
class OutgoingEmail:
    send_to: list[str]
    subject: str | None = None
    text: str | None = None
    attachments_paths: tuple[str] | None = None


class EmailConnectionType(str, Enum):
    STARTED = "STARTED"
    NONAUTH = "NONAUTH"
    AUTH = "AUTH"
    SELECTED = "SELECTED"

    def __call__(self, *args, **kwargs) -> str:
        return self.value


class EmailFlagPattern(str, Enum):
    ALL = "ALL"
    SEEN = "Seen"
    UNSEEN = "Unseen"
    ANSWERED = "Answered"
    FLAGGED = "Flagged"
    DELETED = "Deleted"
    JUNK = "Junk"
    NON_JUNK = "NonJunk"

    def __call__(self, *args, **kwargs) -> str:
        return self.value


@dataclass(frozen=True)
class IMAP:
    server: str
    port: int


@dataclass(frozen=True)
class SMTP:
    server: str
    port: int


@dataclass(frozen=True)
class EmailService:
    id_: str
    title: str
    imap: IMAP
    smtp: SMTP


class EmailServers(Enum):
    gmail = EmailService(
        id_="gmail",
        title="Gmail",
        imap=IMAP(server="imap.gmail.com", port=993),
        smtp=SMTP(server="smtp.gmail.com", port=465)
    )
    mail_ru = EmailService(
        id_="vk",
        title="Mail.ru",
        imap=IMAP(server="imap.mail.ru", port=993),
        smtp=SMTP(server="smtp.mail.ru", port=465)
    )
    yandex = EmailService(
        id_="yandex",
        title="Яндекс",
        imap=IMAP(server="imap.yandex.ru", port=993),
        smtp=SMTP(server="smtp.yandex.ru", port=465)
    )


def get_service_by_id(service_id: str) -> EmailServers:
    for service in EmailServers:
        if service.value.id_ == service_id:
            return service
    raise ValueError(f"Wrong service id submitted! {service_id}")
