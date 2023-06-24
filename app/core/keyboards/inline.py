from aiogram.utils.keyboard import (
    InlineKeyboardMarkup, InlineKeyboardBuilder, InlineKeyboardButton
)

from app.services.email import EmailServices, EmailServiceCallbackFactory


def email_services() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for service in EmailServices:
        builder.button(
            text=service().title,
            callback_data=EmailServiceCallbackFactory(
                action="choose_email_service",
                service_id=service().id_)
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
        [InlineKeyboardButton(text="Добавить в чат",
                              url="tg://resolve?domain=mail_inbot&startgroup")]
    ]
)
