"""FSM states for bot."""
from aiogram.fsm.state import State, StatesGroup


class VideoProcessing(StatesGroup):
    """States for video processing flow."""
    selecting_preset = State()
    waiting_for_video = State()
    selecting_options = State()
    selecting_language = State()
    confirming_preset = State()
    processing = State()


class Payment(StatesGroup):
    """States for payment flow."""
    waiting_for_payment = State()


class PresetEdit(StatesGroup):
    """States for preset editing workflows."""
    renaming = State()

