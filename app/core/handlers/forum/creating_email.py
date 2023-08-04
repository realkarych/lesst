from aiogram import Router, Bot
from aiogram.types import Message
from fluentogram import TranslatorRunner


async def cmd_create_email(m: Message, bot: Bot, i18n: TranslatorRunner):
    """Stub"""


def register() -> Router:
    router = Router()

    router.message.register(
        cmd_create_email
    )

    return router
