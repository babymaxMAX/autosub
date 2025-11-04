"""Video processing handler."""
import logging
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from bot.keyboards import (
    get_processing_options,
    get_language_selection,
    get_cancel_keyboard,
    get_main_menu,
)
from bot.states import VideoProcessing
from bot.services.video_service import (
    validate_video_url,
    enqueue_video_task,
    check_user_limits,
)
from db.models import User
from config.constants import TIER_LIMITS

router = Router()
logger = logging.getLogger(__name__)


@router.message(F.text == "🎬 Обработать видео")
async def start_video_processing(message: Message, state: FSMContext, **kwargs):
    """Start video processing flow."""
    await state.set_state(VideoProcessing.waiting_for_video)
    await message.answer(
        "📤 Отправьте мне:\n"
        "• Видео файл\n"
        "• Аудио файл\n"
        "• Ссылку на YouTube/TikTok/Instagram\n\n"
        "Или нажмите /cancel для отмены",
        reply_markup=get_cancel_keyboard()
    )


@router.message(VideoProcessing.waiting_for_video, F.video | F.document | F.audio)
async def handle_video_file(message: Message, state: FSMContext, user: User, db, **kwargs):
    """Handle video file upload."""
    # Check user limits
    can_process, error_msg = await check_user_limits(db, user)
    if not can_process:
        await message.answer(f"❌ {error_msg}")
        await state.clear()
        return
    
    # Get file info
    if message.video:
        file_id = message.video.file_id
        file_size = message.video.file_size
        duration = message.video.duration
    elif message.document:
        file_id = message.document.file_id
        file_size = message.document.file_size
        duration = None
    elif message.audio:
        file_id = message.audio.file_id
        file_size = message.audio.file_size
        duration = message.audio.duration
    else:
        await message.answer("❌ Неподдерживаемый тип файла")
        return
    
    # Check duration limit
    tier_limits = TIER_LIMITS[user.tier]
    if duration and duration > tier_limits["max_duration"]:
        await message.answer(
            f"❌ Длительность видео ({duration}сек) превышает лимит для вашего тарифа ({tier_limits['max_duration']}сек)\n\n"
            f"💎 Используйте /pricing для улучшения тарифа"
        )
        await state.clear()
        return
    
    # Save to state
    await state.update_data(
        input_type="file",
        file_id=file_id,
        file_size=file_size,
        duration=duration,
    )
    
    # Show processing options
    await message.answer(
        "✅ Файл получен!\n\n"
        "Выберите опции обработки:",
        reply_markup=get_processing_options(user.tier)
    )
    await state.set_state(VideoProcessing.selecting_options)


@router.message(VideoProcessing.waiting_for_video, F.text)
async def handle_video_url(message: Message, state: FSMContext, user: User, db, **kwargs):
    """Handle video URL."""
    # Check user limits
    can_process, error_msg = await check_user_limits(db, user)
    if not can_process:
        await message.answer(f"❌ {error_msg}")
        await state.clear()
        return
    
    url = message.text.strip()
    
    # Validate URL
    is_valid, source = validate_video_url(url)
    if not is_valid:
        await message.answer(
            "❌ Неверная ссылка. Поддерживаются:\n"
            "• YouTube\n"
            "• TikTok\n"
            "• Instagram"
        )
        return
    
    # Save to state
    await state.update_data(
        input_type=source,
        input_url=url,
    )
    
    # Show processing options
    await message.answer(
        f"✅ Ссылка на {source} получена!\n\n"
        "Выберите опции обработки:",
        reply_markup=get_processing_options(user.tier)
    )
    await state.set_state(VideoProcessing.selecting_options)


@router.callback_query(VideoProcessing.selecting_options, F.data.startswith("opt_"))
async def toggle_option(callback: CallbackQuery, state: FSMContext, user: User, **kwargs):
    """Toggle processing option."""
    option = callback.data.replace("opt_", "")
    
    # Get current state data
    data = await state.get_data()
    options = data.get("options", {})
    
    # Toggle option
    options[option] = not options.get(option, False)
    await state.update_data(options=options)
    
    # Update keyboard
    await callback.answer(f"{'Включено' if options[option] else 'Отключено'}: {option}")


@router.callback_query(VideoProcessing.selecting_options, F.data == "start_processing")
async def start_processing(callback: CallbackQuery, state: FSMContext, user: User, db, **kwargs):
    """Start video processing."""
    data = await state.get_data()
    options = data.get("options", {})
    
    # Check if translation is enabled
    if options.get("translate", False):
        await callback.message.edit_text(
            "🌐 Выберите язык перевода:",
            reply_markup=get_language_selection()
        )
        await state.set_state(VideoProcessing.selecting_language)
        await callback.answer()
        return
    
    # Enqueue task
    try:
        task = await enqueue_video_task(db, user, data)
        
        await callback.message.edit_text(
            f"✅ Задача #{task.id} поставлена в очередь!\n\n"
            f"⏳ Обработка может занять несколько минут.\n"
            f"Мы отправим вам результат, когда обработка завершится.",
            reply_markup=None
        )
        
        await state.clear()
    except Exception as e:
        logger.error(f"Error enqueueing task: {e}")
        await callback.message.edit_text(
            f"❌ Ошибка при создании задачи: {str(e)}\n\n"
            f"Попробуйте позже или обратитесь в поддержку."
        )
        await state.clear()
    
    await callback.answer()


@router.callback_query(VideoProcessing.selecting_language, F.data.startswith("lang_"))
async def select_language(callback: CallbackQuery, state: FSMContext, user: User, db, **kwargs):
    """Select target language."""
    language = callback.data.replace("lang_", "")
    
    # Update state
    await state.update_data(target_language=language)
    
    # Get all data
    data = await state.get_data()
    
    # Enqueue task
    try:
        task = await enqueue_video_task(db, user, data)
        
        await callback.message.edit_text(
            f"✅ Задача #{task.id} поставлена в очередь!\n\n"
            f"⏳ Обработка может занять несколько минут.\n"
            f"Мы отправим вам результат, когда обработка завершится.",
            reply_markup=None
        )
        
        await state.clear()
    except Exception as e:
        logger.error(f"Error enqueueing task: {e}")
        await callback.message.edit_text(
            f"❌ Ошибка при создании задачи: {str(e)}\n\n"
            f"Попробуйте позже или обратитесь в поддержку."
        )
        await state.clear()
    
    await callback.answer()


@router.callback_query(F.data == "cancel")
async def cancel_processing(callback: CallbackQuery, state: FSMContext, **kwargs):
    """Cancel processing."""
    await state.clear()
    await callback.message.edit_text("❌ Операция отменена.")
    await callback.answer()

