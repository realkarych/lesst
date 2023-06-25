from aiogram.filters.callback_data import CallbackData


class EmailServiceCallbackFactory(CallbackData, prefix="email_service"):
    action: str
    service_id: str
