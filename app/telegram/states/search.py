from aiogram.fsm.state import State, StatesGroup


class Search(StatesGroup):
    back_to_menu = State()