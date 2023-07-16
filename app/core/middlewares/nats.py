from typing import Callable, Dict, Any, Awaitable

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject
from nats.js import JetStreamContext


class JetStreamContextMiddleware(BaseMiddleware):
    def __init__(self, context: JetStreamContext):
        super().__init__()
        self.context = context

    async def __call__(
            self,
            handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
            event: TelegramObject,
            data: Dict[str, Any],
    ) -> Any:
        data["nats"] = self.context
        return await handler(event, data)
