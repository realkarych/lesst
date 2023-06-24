from __future__ import annotations

import datetime
from dataclasses import dataclass

from app.dtos.dto import DTO
from app.services.database.models import User


@dataclass(frozen=True)
class UserDTO(DTO):
    id: int  # Telegram unique id
    username: str | None = None
    firstname: str | None = None
    lastname: str | None = None
    language_code: str | None = None
    registered_time: datetime.datetime | None = None

    def to_db_model(self) -> User:
        return User(
            id=self.id,
            username=self.username,
            firstname=self.firstname,
            lastname=self.lastname,
            language_code=self.language_code
        )
