from __future__ import annotations

from dataclasses import dataclass

from app.dtos.dto import DTO


@dataclass(frozen=True)
class IncomingEmailMessageDTO(DTO):
    user_id: int
    mailbox_email_id: int
    forum_id: int
    email_db_id: int | None = None

    def to_db_model(self):
        pass
