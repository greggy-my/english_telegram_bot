from aiogram.fsm.state import StatesGroup, State


class ChooseUnit(StatesGroup):
    unit = State()
    approve = State()