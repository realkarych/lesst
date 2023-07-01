from aiogram.fsm.state import StatesGroup, State


class EmailAuth(StatesGroup):
    service = State()
    email = State()
    password = State()
