from __future__ import annotations

from typing import Union

from aiogram.filters import BaseFilter
from aiogram.types import Message, CallbackQuery


class ChatTypeFilter(BaseFilter):
    def __init__(self, chat_type: Union[str, list]):
        self.chat_type = chat_type

    async def __call__(self, message: Message | CallbackQuery) -> bool:
        if isinstance(message, CallbackQuery):
            message = message.message
        if isinstance(self.chat_type, str):
            return message.chat.type == self.chat_type
        else:
            return message.chat.type in self.chat_type
