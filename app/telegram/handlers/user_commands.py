from aiogram import Bot
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from db.database_manager import FeedbackRepository
from db.user_progress import initiate_user_progress
from db.chat_data import initiate_chat_data
from telegram.states.feedback import GetFeedback
from telegram.keyboards.feedback import approve_feedback_keyboard, cancel_feedback_keyboard
from telegram.keyboards.menu import main_menu


async def send_instructions(message: Message) -> None:
    """React to the Instruct command"""
    text = """
    🔎 <b>Поиск</b>: Найди нужное слово и его перевод.\n
    📚 <b>Выбор Юнита</b>: Выбери область обучения для Квиза и Правописания.\n
    🧠 <b>Квиз</b>: Проверь свои знания, выбирая правильный перевод слова на английском и русском. Твой прогресс сохраняется!\n
    ✍️ <b>Правописание</b>: Улучши свои навыки правописания слов на английском.\n
    📣 <b>Обратная связь</b>: Дай нам знать, как ты используешь бота!\n """
    await message.reply(text=text)


async def start(message: Message) -> None:
    """React to the Start command"""
    user_id = message.from_user.id
    chat_id = message.chat.id
    await initiate_user_progress(user_id=user_id)
    await initiate_chat_data(user_id=user_id, chat_id=chat_id)
    await message.answer(text="Добро пожаловать!", reply_markup=main_menu().as_markup(resize_keyboard=True))


async def init_feedback(message: Message, state: FSMContext) -> None:
    """Initialises the feedback"""
    initial_text = 'Спасибо, что решил оставить отзыв о работе бота. Напиши в ответном сообщении свои предложения по улучшениям'
    await message.answer(text=initial_text, reply_markup=cancel_feedback_keyboard().as_markup(resize_keyboard=True))
    await state.set_state(GetFeedback.feedback_text)


async def send_feedback(message: Message, state: FSMContext):
    await state.update_data(feedback_text=message.text)
    await message.answer(
        text='Подтверди отправку обратной связи',
        reply_markup=approve_feedback_keyboard().as_markup(resize_keyboard=True)
    )
    await state.set_state(GetFeedback.approve)


async def approve_feedback(message: Message, state: FSMContext):
    user_data = await state.get_data()
    await FeedbackRepository.add_data({'feedback': user_data['feedback_text']})
    await message.answer(
        text='Спасибо за обратную связь!',
        reply_markup=main_menu().as_markup(resize_keyboard=True)
    )

    await state.clear()


async def cancel_feedback(message: Message, state: FSMContext):
    await message.answer(text='<i>Обратно в меню</i>', reply_markup=main_menu().as_markup(resize_keyboard=True))

    await state.clear()

