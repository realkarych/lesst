from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from fluentogram import TranslatorRunner

from app.core.states.callbacks import EmailServiceCallbackFactory, UserEmailCallbackFactory
from app.dtos.email import UserEmailDTO
from app.services.email.base.entities import EmailServers


def email_services() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for service in EmailServers:
        builder.button(
            text=service.value.title,
            callback_data=EmailServiceCallbackFactory(
                action="choose_email_service",
                service_id=service.value.id_)
        )
    builder.adjust(1)
    return builder.as_markup()


def return_to_services(i18n: TranslatorRunner) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=i18n.button.back_to_email_services(), callback_data="return_to_services")]
    ])


def return_to_email(i18n: TranslatorRunner) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=i18n.button.back_to_email_address(), callback_data="return_to_email")]
    ])


def add_to_chat(i18n: TranslatorRunner) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=i18n.button.add_to_chat(), url="https://t.me/lesstrobot?startgroup=true")]
        ]
    )


def remove_email(i18n: TranslatorRunner, email: UserEmailDTO) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(
        text=str(i18n.button.remove_email()),
        callback_data=UserEmailCallbackFactory(
            user_id=email.user_id,
            email_address=email.mail_address
        )
    )
    builder.adjust(1)
    return builder.as_markup()
