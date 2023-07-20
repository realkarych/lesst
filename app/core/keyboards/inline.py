from aiogram.utils.keyboard import (
    InlineKeyboardMarkup, InlineKeyboardBuilder, InlineKeyboardButton
)
from fluentogram import TranslatorRunner

from app.core.states.callbacks import EmailServiceCallbackFactory, UserEmailCallbackFactory
from app.dtos.email import EmailDTO
from app.services.email.entities import EmailServices


def email_services() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for service in EmailServices:
        builder.button(
            text=service.value.title,
            callback_data=EmailServiceCallbackFactory(
                action="choose_email_service",
                service_id=service.value.id_)
        )
    builder.adjust(1)
    return builder.as_markup()


return_to_services = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="🔙 Вернуться к Email-сервисам", callback_data="return_to_services")]
])

return_to_email = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="🔙 Вернуться к Email", callback_data="return_to_email")]
])

add_to_chat = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="Добавить в чат", url="tg://resolve?domain=lesstrobot&startgroup")]
    ]
)


def remove_email(i18n: TranslatorRunner, email: EmailDTO) -> InlineKeyboardMarkup:
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
