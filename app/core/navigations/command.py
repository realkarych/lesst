from dataclasses import dataclass
from enum import Enum, unique

from aiogram import Bot
from aiogram.types import BotCommand, BotCommandScopeAllPrivateChats, BotCommandScopeAllGroupChats


@dataclass
class Command:
    """
    Command object is dto for organize the same interface to access /command
    data in handlers & in commands-factory & in registrator.
    """

    name: str
    description: str

    def to_bot_command(self) -> BotCommand:
        """Map Command object to BotCommand object"""

        return BotCommand(command=self.name, description=self.description)


@unique
class BaseCommandList(Enum):
    """Base list of commands."""

    def __str__(self) -> str:
        return self.value.name

    def __call__(self, *args, **kwargs) -> Command:
        return self.value


class PrivateChatCommands(BaseCommandList):
    """
    List of commands with public access & submission to Telegram menu list.
    Do not implement here admin commands because of submission to menu.
    """

    start = Command(name="start", description="Перезапустить бота")
    cancel = Command(name="cancel", description="Отменить действие")


class ForumCommands(BaseCommandList):
    create = Command(name="create", description="Создать Email")


async def set_bot_commands(bot: Bot) -> None:
    """
    Creates a commands' lists (shortcuts) in Telegram app menu.
    """

    private_chat_commands: list[BotCommand] = [command().to_bot_command() for command in PrivateChatCommands]
    await bot.set_my_commands(
        commands=private_chat_commands,
        scope=BotCommandScopeAllPrivateChats()  # pyright: ignore
    )

    forum_commands: list[BotCommand] = [command().to_bot_command() for command in ForumCommands]
    await bot.set_my_commands(
        commands=forum_commands,
        scope=BotCommandScopeAllGroupChats()  # pyright: ignore
    )
