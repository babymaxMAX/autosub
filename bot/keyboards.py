"""Keyboard layouts for the bot."""
from aiogram.types import (
    ReplyKeyboardMarkup,
    KeyboardButton,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)
from aiogram.utils.keyboard import InlineKeyboardBuilder
from config.constants import SUPPORTED_LANGUAGES, UserTier


def get_main_menu() -> ReplyKeyboardMarkup:
    """Get main menu keyboard."""
    keyboard = [
        [KeyboardButton(text="🎬 Обработать видео")],
        [KeyboardButton(text="👤 Профиль"), KeyboardButton(text="💎 Тарифы")],
        [KeyboardButton(text="📖 Помощь")],
    ]
    return ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)


def get_processing_options(tier: UserTier) -> InlineKeyboardMarkup:
    """Get processing options keyboard based on user tier."""
    builder = InlineKeyboardBuilder()
    
    # All tiers can generate subtitles
    builder.button(text="✅ Субтитры", callback_data="opt_subtitles")
    builder.button(text="🎬 Вертикальный формат", callback_data="opt_vertical")
    
    # PRO and CREATOR can translate
    if tier in [UserTier.PRO, UserTier.CREATOR]:
        builder.button(text="🌐 Перевод", callback_data="opt_translate")
    
    # Only CREATOR can use voiceover
    if tier == UserTier.CREATOR:
        builder.button(text="🎤 Озвучка", callback_data="opt_voiceover")
    
    builder.button(text="▶️ Начать обработку", callback_data="start_processing")
    builder.button(text="❌ Отмена", callback_data="cancel")
    
    builder.adjust(2)
    return builder.as_markup()


def get_language_selection() -> InlineKeyboardMarkup:
    """Get language selection keyboard."""
    builder = InlineKeyboardBuilder()
    
    for code, name in list(SUPPORTED_LANGUAGES.items())[:15]:  # First 15 languages
        builder.button(text=name, callback_data=f"lang_{code}")
    
    builder.button(text="🔍 Автоопределение", callback_data="lang_auto")
    builder.adjust(3)
    return builder.as_markup()


def get_pricing_keyboard() -> InlineKeyboardMarkup:
    """Get pricing keyboard."""
    builder = InlineKeyboardBuilder()
    
    builder.button(text="💎 PRO (299₽/мес)", callback_data="buy_pro_monthly")
    builder.button(text="💎 PRO (2990₽/год)", callback_data="buy_pro_yearly")
    builder.button(text="⭐ CREATOR (599₽/мес)", callback_data="buy_creator_monthly")
    builder.button(text="⭐ CREATOR (5990₽/год)", callback_data="buy_creator_yearly")
    
    builder.button(text="🎬 Разовая обработка", callback_data="buy_onetime")
    
    builder.adjust(2)
    return builder.as_markup()


def get_onetime_pricing_keyboard() -> InlineKeyboardMarkup:
    """Get one-time pricing keyboard."""
    builder = InlineKeyboardBuilder()
    
    builder.button(text="До 3 мин (29₽)", callback_data="buy_onetime_short")
    builder.button(text="До 10 мин (49₽)", callback_data="buy_onetime_medium")
    builder.button(text="До 30 мин (59₽)", callback_data="buy_onetime_long")
    builder.button(text="◀️ Назад", callback_data="back_to_pricing")
    
    builder.adjust(1)
    return builder.as_markup()


def get_admin_keyboard() -> InlineKeyboardMarkup:
    """Get admin keyboard."""
    builder = InlineKeyboardBuilder()
    
    builder.button(text="📊 Статистика", callback_data="admin_stats")
    builder.button(text="👥 Пользователи", callback_data="admin_users")
    builder.button(text="📋 Задачи", callback_data="admin_tasks")
    builder.button(text="💰 Платежи", callback_data="admin_payments")
    
    builder.adjust(2)
    return builder.as_markup()


def get_cancel_keyboard() -> InlineKeyboardMarkup:
    """Get cancel keyboard."""
    builder = InlineKeyboardBuilder()
    builder.button(text="❌ Отменить", callback_data="cancel")
    return builder.as_markup()

