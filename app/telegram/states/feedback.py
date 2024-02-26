from aiogram.fsm.state import StatesGroup, State


class GetFeedback(StatesGroup):
    feedback_text = State()
    approve = State()