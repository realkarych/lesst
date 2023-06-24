from __future__ import annotations

from dataclasses import dataclass

from app.dtos.dto import DTO
from app.services.database.models import Topic


@dataclass(frozen=True)
class TopicDTO(DTO):
    forum_id: int  # Unique Telegram forum-group id
    topic_id: int  # Unique topic id for forum
    topic_name: str  # address@domain — unique for forum
    topic_db_id: int | None = None  # Database unique topic id

    def to_db_model(self) -> Topic:
        return Topic(
            forum_id=self.forum_id,
            topic_id=self.topic_id,
            topic_name=self.topic_name
        )
