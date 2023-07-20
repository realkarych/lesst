from __future__ import annotations

from typing import Iterable

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.dtos import converters
from app.dtos.topic import TopicDTO
from app.services.database.dao.base import BaseDAO
from app.services.database.exception_mapper import exception_mapper
from app.services.database.models import Topic


class TopicDAO(BaseDAO[Topic]):

    def __init__(self, session: AsyncSession):
        super().__init__(Topic, session)

    @exception_mapper
    async def add_topic(self, topic: TopicDTO):
        await self._session.merge(topic.to_db_model())
        await self.commit()

    @exception_mapper
    async def is_topic_created(self, forum_id: int, email_address: str) -> bool:
        response = await self._session.execute(
            select(Topic).where(Topic.forum_id == forum_id, Topic.topic_name == email_address)
        )
        return bool(response.scalar_one_or_none())

    @exception_mapper
    async def get_topic(self, forum_id: int, email_address: str) -> TopicDTO:
        topic = await self._session.execute(
            select(Topic).where(Topic.forum_id == forum_id, Topic.topic_name == email_address)
        )
        return converters.db_topic_to_dto(topic.scalar_one())

    @exception_mapper
    async def add_topics(self, topics: Iterable[TopicDTO]):
        self._session.add_all([topic.to_db_model() for topic in topics])
        await self.commit()

    @exception_mapper
    async def get_topic_ids(self, forum_id: int) -> set[int]:
        result = await self._session.execute(
            select(Topic.topic_id).where(Topic.forum_id == forum_id)
        )
        return set(result.scalars())

    @exception_mapper
    async def get_topics(self, forum_id: int) -> list[TopicDTO]:
        result = await self._session.execute(
            select(Topic).where(Topic.forum_id == forum_id)
        )
        return [converters.db_topic_to_dto(topic) for topic in result.scalars()]
