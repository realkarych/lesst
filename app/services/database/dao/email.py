from __future__ import annotations

from typing import AsyncGenerator

from sqlalchemy import update, select
from sqlalchemy.exc import NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession

from app.dtos import dto
from app.dtos.database import Topic
from app.services.database.dao import mapper
from app.services.database.dao.base import BaseDAO


class TopicDAO(BaseDAO[Topic]):
    """ORM queries for users table"""

    def __init__(self, session: AsyncSession):
        super().__init__(Topic, session)

    async def add_topic(self, topic: dto.Topic):
        await self._session.merge(mapper.map_to_db_topic(topic))
        await self._session.commit()

    async def get_topic_id(self, forum_id: int, email_address: str) -> int | None:
        topic_id = await self._session.execute(
            select(Topic.topic_id).where(Topic.forum_id == forum_id, Topic.topic_name == email_address)
        )
        return topic_id.scalar_one()

    async def add_topics(self, topics: list[dto.Topic]):
        self._session.add_all([mapper.map_to_db_topic(topic) for topic in topics])
        await self._session.commit()

    async def get_topic_ids(self, forum_id: int) -> set[str]:
        result = await self._session.execute(
            select(Topic.topic_id).where(Topic.forum_id == forum_id)
        )
        return set([row[0] for row in result])

    async def get_topics(self, forum_id: int) -> list[Topic]:
        result = await self._session.execute(
            select(Topic).where(Topic.forum_id == forum_id)
        )
        return [dto.Topic.from_db(topic[0]) for topic in result.all()]
