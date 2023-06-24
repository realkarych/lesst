from __future__ import annotations

from typing import Iterable

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

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
        await self._session.commit()

    @exception_mapper
    async def get_topic_id(self, forum_id: int, email_address: str) -> int | None:
        topic_id = await self._session.execute(
            select(Topic.topic_id).where(Topic.forum_id == forum_id, Topic.topic_name == email_address)
        )
        return topic_id.scalar_one()

    @exception_mapper
    async def add_topics(self, topics: Iterable[TopicDTO]):
        self._session.add_all([topic.to_db_model() for topic in topics])
        await self._session.commit()

    @exception_mapper
    async def get_topic_ids(self, forum_id: int) -> set[str]:
        result = await self._session.execute(
            select(Topic.topic_id).where(Topic.forum_id == forum_id)
        )
        return set([topic_row[0] for topic_row in result])

    @exception_mapper
    async def get_topics(self, forum_id: int) -> list[Topic]:
        result = await self._session.execute(
            select(Topic).where(Topic.forum_id == forum_id)
        )
        return [topic[0].to_dto() for topic in result.all()]
