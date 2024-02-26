from aiogram.fsm.state import StatesGroup, State


class Quiz(StatesGroup):
    back_to_menu = State()