from aiogram.fsm.state import StatesGroup, State


class Search(StatesGroup):
    back_to_menu = State()