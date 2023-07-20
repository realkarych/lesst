from aiogram.filters.callback_data import CallbackData


class EmailServiceCallbackFactory(CallbackData, prefix="email_service"):
    action: str
    service_id: str


class UserEmailCallbackFactory(CallbackData, prefix="user_email"):
    user_id: int
    email_address: str
