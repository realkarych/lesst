from __future__ import annotations

from dataclasses import dataclass

from app.dtos.dto import DTO
from app.services import cryptography
from app.services.database import models


@dataclass(frozen=True)
class EmailDTO(DTO):
    user_id: int
    forum_id: int
    mail_server: str
    mail_address: str
    mail_auth_key: str
    email_db_id: int | None = None

    def to_db_model(self) -> models.Email:
        return models.Email(
            user_id=self.user_id,
            forum_id=self.forum_id,
            mail_server=self.mail_server,
            mail_address=self.mail_address,
            mail_auth_key=cryptography.encrypt_key(self.mail_auth_key)
        )
