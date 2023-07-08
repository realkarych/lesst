from __future__ import annotations

from dataclasses import dataclass

from app.dtos.dto import DTO
from app.services import cryptography
from app.services.database import models
from app.services.email.entities import EmailService


@dataclass(frozen=True)
class EmailDTO(DTO):
    user_id: int
    mail_server: str
    mail_address: str
    mail_auth_key: str
    forum_id: int | None = None
    email_db_id: int | None = None

    def to_db_model(self) -> models.Email:
        return models.Email(
            user_id=self.user_id,
            forum_id=self.forum_id,
            mail_server=self.mail_server,
            mail_address=self.mail_address,
            mail_auth_key=cryptography.encrypt_key(self.mail_auth_key)
        )

    @classmethod
    def from_email(cls, email_service: EmailService, email_address: str, email_auth_key: str, user_id: int,
                   forum_id: int | None = None):
        return cls(
            user_id=user_id,
            mail_server=email_service.id_,
            mail_address=email_address,
            mail_auth_key=email_auth_key,
            forum_id=forum_id
        )
