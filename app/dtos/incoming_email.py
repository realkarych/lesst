from __future__ import annotations

from dataclasses import dataclass

from app.dtos.dto import DTO
from app.services.database import models


@dataclass(frozen=True)
class IncomingEmailMessageDTO(DTO):
    destination_topic_id: int
    email_id: int
    incoming_email_id: int
    email_message_db_id: int | None = None

    def to_db_model(self) -> models.IncomingEmailMessage:
        return models.IncomingEmailMessage(
            destination_topic_id=self.destination_topic_id,
            email_id=self.email_id,
            incoming_email_id=self.incoming_email_id
        )
