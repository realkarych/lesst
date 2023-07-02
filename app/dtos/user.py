from __future__ import annotations

import datetime
from dataclasses import dataclass

from aiogram.types import Message

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

    @classmethod
    def from_message(cls, message: Message) -> UserDTO:
        return cls(
            id=message.from_user.id,
            username=message.from_user.username,
            firstname=message.from_user.first_name,
            lastname=message.from_user.last_name,
            language_code=message.from_user.language_code
        )

    def to_db_model(self) -> User:
        return User(
            id=self.id,
            username=self.username,
            firstname=self.firstname,
            lastname=self.lastname,
            language_code=self.language_code
        )
