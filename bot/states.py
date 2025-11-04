"""FSM states for bot."""
from aiogram.fsm.state import State, StatesGroup


class VideoProcessing(StatesGroup):
    """States for video processing flow."""
    waiting_for_video = State()
    selecting_options = State()
    selecting_language = State()
    processing = State()


class Payment(StatesGroup):
    """States for payment flow."""
    waiting_for_payment = State()

