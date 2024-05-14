from aiogram.fsm.state import State, StatesGroup


class Quiz(StatesGroup):
    back_to_menu = State()