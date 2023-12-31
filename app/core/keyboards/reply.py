from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from fluentogram import TranslatorRunner


class ResizedReplyKeyboard(ReplyKeyboardMarkup):
    """
    I prefer override default ReplyKeyboardMarkup to avoid passing the resizer parameter
    every time.
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.resize_keyboard = True


def menu(i18n: TranslatorRunner) -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text=i18n.menu.connect_email())
            ],
            [
                KeyboardButton(text=i18n.menu.emails()),
                KeyboardButton(text=i18n.menu.subscription())
            ]
        ],
        resize_keyboard=True
    )


def cancel(i18n: TranslatorRunner) -> ResizedReplyKeyboard:
    return ResizedReplyKeyboard(
        keyboard=[
            [
                KeyboardButton(text=i18n.menu.back()),
                KeyboardButton(text=i18n.menu.cancel())
            ]
        ]
    )
