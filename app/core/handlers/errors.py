import logging

from aiogram import Router
from aiogram.types import ErrorEvent


async def handle_errors(event: ErrorEvent) -> None:
    logging.error(event)


def register() -> Router:
    router = Router()

    router.errors.register(handle_errors)

    return router
