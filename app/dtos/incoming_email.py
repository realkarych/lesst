from __future__ import annotations

from dataclasses import dataclass

from app.dtos.dto import DTO
from app.services.database import models


@dataclass(frozen=True)
class IncomingEmailMessageDTO(DTO):
    user_id: int
    forum_id: int
    user_email_db_id: int
    mailbox_email_id: int
    email_db_id: int | None = None

    def to_db_model(self) -> models.IncomingEmailMessage:
        return models.IncomingEmailMessage(
            user_id=self.user_id,
            forum_id=self.forum_id,
            user_email_db_id=self.user_email_db_id,
            mailbox_email_id=self.mailbox_email_id
        )
