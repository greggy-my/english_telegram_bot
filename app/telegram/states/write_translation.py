from aiogram.fsm.state import State, StatesGroup


class WriteTranslation(StatesGroup):
    back_to_menu = State()
