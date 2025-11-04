"""Start command handler."""
from aiogram import Router, F
from aiogram.filters import Command, CommandStart
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from config.constants import WELCOME_MESSAGE, HELP_MESSAGE
from bot.keyboards import get_main_menu

router = Router()


@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext, **kwargs):
    """Handle /start command."""
    await state.clear()
    await message.answer(
        WELCOME_MESSAGE,
        reply_markup=get_main_menu()
    )


@router.message(Command("help"))
@router.message(F.text == "📖 Помощь")
async def cmd_help(message: Message, **kwargs):
    """Handle /help command."""
    await message.answer(HELP_MESSAGE)


@router.message(Command("cancel"))
async def cmd_cancel(message: Message, state: FSMContext, **kwargs):
    """Handle /cancel command."""
    await state.clear()
    await message.answer(
        "❌ Операция отменена.",
        reply_markup=get_main_menu()
    )

