from aiogram.fsm.state import State, StatesGroup


class GetFeedback(StatesGroup):
    feedback_text = State()
    approve = State()