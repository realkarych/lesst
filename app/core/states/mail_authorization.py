from aiogram.fsm.state import StatesGroup, State


class MailAuth(StatesGroup):
    service = State()
    mail = State()
    password = State()
