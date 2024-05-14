from aiogram.fsm.state import State, StatesGroup


class ChooseUnit(StatesGroup):
    unit = State()
    approve = State()