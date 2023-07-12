"""App launcher"""

import asyncio
import logging

import tzlocal
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from sqlalchemy.ext.asyncio import async_sessionmaker

from app.core.handlers import factory
from app.core.handlers.forum import forum_updates
from app.core.handlers.private import menu, email_adding_pipeline
from app.core.middlewares.db import DbSessionMiddleware
from app.core.middlewares.i18n import TranslatorRunnerMiddleware
from app.core.navigations.command import set_bot_commands
from app.core.templates import build_translator_hub
from app.services.database.connector import setup_get_pool
from app.services.email.broadcaster import broadcast_incoming_emails, fetch_incoming_emails
from app.settings.config import Config, load_config


async def main() -> None:
    """Starts app & polling."""

    _configure_logger()
    config: Config = load_config()

    bot = Bot(config.bot.token, parse_mode=config.bot.parse_mode)
    await set_bot_commands(bot=bot)
    dp = Dispatcher(bot=bot, storage=MemoryStorage())
    
    sessionmaker = await setup_get_pool(db_uri=config.db.get_uri())

    _set_middlewares(dp=dp, sessionmaker=sessionmaker)

    scheduler = _init_scheduler()
    await _set_schedulers(scheduler=scheduler, bot=bot, session_pool=sessionmaker)

    # Provide your default handler-modules into register() func.
    factory.register(dp, menu, email_adding_pipeline, forum_updates)

    try:
        await dp.start_polling(bot, _translator_hub=build_translator_hub(),
                               allowed_updates=dp.resolve_used_update_types())
    finally:
        scheduler.shutdown()
        await dp.storage.close()
        await bot.session.close()


def _configure_logger() -> None:
    # On prod, set log-level to WARNING; add `filename=` arg and write your logs to
    # file instead of stdout.
    # Example: filename=f"{ROOT_DIR}/error.log".
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(name)s - %(message)s"
    )


def _init_scheduler() -> AsyncIOScheduler:
    """
    Initialize & start scheduler.
    :return scheduler:
    """
    scheduler = AsyncIOScheduler(timezone=str(tzlocal.get_localzone()))
    scheduler.start()
    return scheduler


def _set_middlewares(dp: Dispatcher, sessionmaker: async_sessionmaker) -> None:
    dp.my_chat_member.outer_middleware(DbSessionMiddleware(sessionmaker))
    dp.my_chat_member.middleware(TranslatorRunnerMiddleware())
    dp.message.outer_middleware(DbSessionMiddleware(sessionmaker))
    dp.edited_message.outer_middleware(DbSessionMiddleware(sessionmaker))
    dp.message.middleware(TranslatorRunnerMiddleware())
    dp.callback_query.middleware(TranslatorRunnerMiddleware())


async def _set_schedulers(scheduler: AsyncIOScheduler, bot: Bot, session_pool: async_sessionmaker) -> None:
    scheduler.add_job(broadcast_incoming_emails, IntervalTrigger(seconds=10), (bot, session_pool))
    scheduler.add_job(fetch_incoming_emails, IntervalTrigger(minutes=1), (session_pool, ))


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        # Logging this is pointless
        pass
