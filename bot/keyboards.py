"""Keyboard layouts for the bot."""
from aiogram.types import (
    ReplyKeyboardMarkup,
    KeyboardButton,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)
from aiogram.utils.keyboard import InlineKeyboardBuilder
from config.constants import UserTier
from bot.i18n import (
    tr,
    t,
    resolve_language,
    language_options,
)
from common.subtitle_styles import (
    SUBTITLE_STYLE_DEFINITIONS,
    get_style_display,
    get_style_description,
)


def get_main_menu(user=None) -> ReplyKeyboardMarkup:
    """Get main menu keyboard."""
    keyboard = [
        [KeyboardButton(text=t(user, "menu.upload"))],
        [
            KeyboardButton(text=t(user, "menu.options")),
            KeyboardButton(text=t(user, "menu.presets")),
        ],
        [
            KeyboardButton(text=t(user, "menu.plan")),
            KeyboardButton(text=t(user, "menu.history")),
        ],
        [
            KeyboardButton(text=t(user, "menu.help")),
            KeyboardButton(text=t(user, "menu.language")),
        ],
    ]
    return ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)


def get_processing_options(user, tier: UserTier) -> InlineKeyboardMarkup:
    """Get processing options keyboard based on user tier."""
    builder = InlineKeyboardBuilder()
    
    # All tiers can generate subtitles
    builder.button(text=tr(user, "✅ Субтитры", "✅ Subtitles"), callback_data="opt:subs:toggle")
    builder.button(text=tr(user, "↕️ Формат 9:16", "↕️ Format 9:16"), callback_data="opt:format:916")
    
    # PRO and CREATOR can translate
    if tier in [UserTier.PRO, UserTier.CREATOR]:
        builder.button(text=tr(user, "🌐 Перевод", "🌐 Translate"), callback_data="opt:translate:toggle")
    
    # Only CREATOR can use voiceover
    if tier == UserTier.CREATOR:
        builder.button(text=tr(user, "🗣️ Озвучка", "🗣️ Voiceover"), callback_data="opt:tts:toggle")
    
    # Extra controls row
    builder.button(text=tr(user, "⚙️ Ещё…", "⚙️ More…"), callback_data="opt:more")
    # Bottom controls: place Start rightmost
    builder.button(text=tr(user, "✖️ Отменить", "✖️ Cancel"), callback_data="job:cancel")
    builder.button(text=tr(user, "▶️ Запустить", "▶️ Start"), callback_data="job:start")
    
    builder.adjust(2, 2, 2)
    return builder.as_markup()


def get_language_selection(
    user=None,
    *,
    callback_prefix: str = "opt:lang:",
    include_back: bool = False,
    back_callback: str = "opt:back",
    current_code: str | None = None,
) -> InlineKeyboardMarkup:
    """Get language selection keyboard.

    callback_prefix: prefix for callback data, e.g. "opt:lang:" or "ui:lang:".
    include_back: append a back button with callback `back_callback`.
    current_code: if provided, highlight this language instead of interface language.
    """
    builder = InlineKeyboardBuilder()

    current_language = current_code or resolve_language(user)
    for code, name in language_options().items():
        mark = "✅ " if code == current_language else ""
        builder.button(text=f"{mark}{name}", callback_data=f"{callback_prefix}{code}")

    builder.adjust(3)

    if include_back:
        builder.row(
            InlineKeyboardButton(text=tr(user, "⬅️ Назад", "⬅️ Back"), callback_data=back_callback),
            width=1,
        )

    return builder.as_markup()


def get_pricing_keyboard(user=None) -> InlineKeyboardMarkup:
    """Get pricing keyboard."""
    builder = InlineKeyboardBuilder()
    
    builder.button(text=tr(user, "🔓 Активировать PRO", "🔓 Activate PRO"), callback_data="plan:buy:pro")
    builder.button(text=tr(user, "🔥 Взять CREATOR", "🔥 Get CREATOR"), callback_data="plan:buy:creator")
    builder.button(text=tr(user, "📅 Моя подписка", "📅 My Subscription"), callback_data="plan:status")
    builder.button(text=tr(user, "❓ Вопросы по оплате", "❓ Billing FAQ"), callback_data="plan:faq")
    
    builder.adjust(2, 2)
    return builder.as_markup()


def get_onetime_pricing_keyboard(user=None) -> InlineKeyboardMarkup:
    """Get one-time pricing keyboard."""
    builder = InlineKeyboardBuilder()
    
    builder.button(text=tr(user, "До 3 мин (29₽)", "Up to 3 min (29₽)"), callback_data="buy_onetime_short")
    builder.button(text=tr(user, "До 10 мин (49₽)", "Up to 10 min (49₽)"), callback_data="buy_onetime_medium")
    builder.button(text=tr(user, "До 30 мин (59₽)", "Up to 30 min (59₽)"), callback_data="buy_onetime_long")
    builder.button(text=tr(user, "◀️ Назад", "◀️ Back"), callback_data="back_to_pricing")
    
    builder.adjust(1)
    return builder.as_markup()


def get_admin_keyboard(user=None) -> InlineKeyboardMarkup:
    """Get admin keyboard."""
    builder = InlineKeyboardBuilder()
    
    builder.button(text=tr(user, "📡 Текущие задачи", "📡 Live Tasks"), callback_data="admin_tasks_live")
    builder.button(text=tr(user, "🚨 Ошибки", "🚨 Errors"), callback_data="admin_errors")
    builder.button(text=tr(user, "👤 Пользователь", "👤 User"), callback_data="admin_user")
    builder.button(text=tr(user, "💰 Платежи", "💰 Payments"), callback_data="admin_payments")
    builder.button(text=tr(user, "🧮 Метрики", "🧮 Metrics"), callback_data="admin_metrics")
    builder.button(text=tr(user, "🧰 Инструменты", "🧰 Tools"), callback_data="admin_tools")
    
    builder.adjust(2, 2, 2)
    return builder.as_markup()


def get_cancel_keyboard(user=None) -> InlineKeyboardMarkup:
    """Get cancel keyboard."""
    builder = InlineKeyboardBuilder()
    builder.button(text=tr(user, "❌ Отменить", "❌ Cancel"), callback_data="job:cancel")
    return builder.as_markup()


def get_onboarding_keyboard(user=None) -> InlineKeyboardMarkup:
    """Inline keyboard for onboarding quick actions."""
    # Deprecated: we no longer show duplicate quick-action buttons because the
    # persistent reply keyboard already covers these actions.
    return InlineKeyboardMarkup(inline_keyboard=[])


def get_advanced_options(user, tier: UserTier, watermark_forced: bool) -> InlineKeyboardMarkup:
    """Advanced options keyboard."""
    builder = InlineKeyboardBuilder()
    builder.button(text=tr(user, "🎚️ Стиль субтитров", "🎚️ Subtitle Style"), callback_data="opt:style:open")
    builder.button(text=tr(user, "🔤 Язык субтитров", "🔤 Subtitle Language"), callback_data="opt:lang:open")
    if tier == UserTier.CREATOR:
        builder.button(text=tr(user, "🗣️ Выбрать голос TTS", "🗣️ Choose TTS voice"), callback_data="opt:voice:open")
    builder.button(text=tr(user, "📍 Позиция субтитров", "📍 Subtitle Position"), callback_data="opt:position:open")
    builder.button(
        text=tr(
            user,
            f"🏷️ Водяной знак {'вкл' if watermark_forced else 'on/off'}",
            f"🏷️ Watermark {'on' if watermark_forced else 'on/off'}",
        ),
        callback_data="opt:watermark:info" if watermark_forced else "opt:watermark:toggle",
    )
    builder.button(text=tr(user, "💾 Сохранить пресет", "💾 Save Preset"), callback_data="opt:preset:save")
    builder.button(text=tr(user, "⬅️ Назад", "⬅️ Back"), callback_data="opt:back")
    builder.adjust(2, 2, 2)
    return builder.as_markup()


def get_options_menu(user=None) -> InlineKeyboardMarkup:
    """Options summary screen keyboard."""
    builder = InlineKeyboardBuilder()
    builder.button(text=tr(user, "🔄 Автодетект языка", "🔄 Auto-detect language"), callback_data="opt:lang:auto")
    builder.button(text=tr(user, "🌐 Выбрать язык перевода", "🌐 Choose translation language"), callback_data="opt:lang:open")
    builder.button(text=tr(user, "🗣️ Выбрать голос TTS", "🗣️ Choose TTS voice"), callback_data="opt:voice:open")
    builder.button(text=tr(user, "↕️ 9:16", "↕️ 9:16"), callback_data="opt:format:916")
    builder.button(text=tr(user, "🎚️ Стиль субтитров", "🎚️ Subtitle style"), callback_data="opt:style:open")
    builder.button(text=tr(user, "📍 Позиция субтитров", "📍 Subtitle position"), callback_data="opt:position:open")
    builder.button(text=tr(user, "💾 Сохранить пресет", "💾 Save preset"), callback_data="opt:preset:save")
    builder.button(text=tr(user, "⬅️ Назад", "⬅️ Back"), callback_data="opt:back")
    builder.adjust(2, 2, 2, 2)
    return builder.as_markup()


def get_style_presets_keyboard(user=None, callback_prefix="opt:style:preset:", back_callback="opt:back") -> InlineKeyboardMarkup:
    """Predefined subtitle style presets."""
    builder = InlineKeyboardBuilder()
    lang_code = resolve_language(user)
    for style_id, config in SUBTITLE_STYLE_DEFINITIONS.items():
        name = get_style_display(style_id, lang_code)
        builder.button(text=name, callback_data=f"{callback_prefix}{style_id}")
    builder.button(text=tr(user, "⬅️ Назад", "⬅️ Back"), callback_data=back_callback)
    builder.adjust(2, 2, 1)
    return builder.as_markup()


def style_help_text(user=None) -> str:
    """Human-friendly description of style presets for users."""
    lang_code = resolve_language(user)
    lines = [
        tr(
            user,
            "🎚️ Стиль субтитров\n",
            "🎚️ Subtitle style\n",
        )
    ]
    for style_id in SUBTITLE_STYLE_DEFINITIONS.keys():
        name = get_style_display(style_id, lang_code)
        description = get_style_description(style_id, lang_code)
        lines.append(f"{name} — {description}")
    lines.append(
        tr(
            user,
            "\nВыберите готовый пресет или откройте «Кастом…», чтобы настроить параметры вручную (скоро).",
            "\nPick a preset or tap “Custom…” to fine-tune parameters (coming soon).",
        )
    )
    return "\n".join(lines)


def get_voice_keyboard(user=None, callback_prefix="opt:voice:", back_callback="opt:back") -> InlineKeyboardMarkup:
    """Simple voice selection keyboard."""
    builder = InlineKeyboardBuilder()
    builder.button(text=tr(user, "🎤 Мужской", "🎤 Male"), callback_data=f"{callback_prefix}male")
    builder.button(text=tr(user, "🎤 Женский", "🎤 Female"), callback_data=f"{callback_prefix}female")
    builder.button(text=tr(user, "⬅️ Назад", "⬅️ Back"), callback_data=back_callback)
    builder.adjust(2)
    return builder.as_markup()


def get_subtitle_position_keyboard(user=None, callback_prefix="opt:position:", back_callback="opt:back") -> InlineKeyboardMarkup:
    """Subtitle placement selector."""
    builder = InlineKeyboardBuilder()
    builder.button(text=tr(user, "⬆️ Верх", "⬆️ Top"), callback_data=f"{callback_prefix}top")
    builder.button(text=tr(user, "⏺ Центр", "⏺ Middle"), callback_data=f"{callback_prefix}middle")
    builder.button(text=tr(user, "⬇️ Низ", "⬇️ Bottom"), callback_data=f"{callback_prefix}bottom")
    builder.button(text=tr(user, "⬅️ Назад", "⬅️ Back"), callback_data=back_callback)
    builder.adjust(3, 1)
    return builder.as_markup()


def get_preset_selection_keyboard(user=None, presets=None) -> InlineKeyboardMarkup:
    """Keyboard for selecting preset for upload."""
    builder = InlineKeyboardBuilder()
    
    if presets:
        for preset in presets:
            # Truncate long preset names for button display
            display_name = preset["name"][:25] + "..." if len(preset["name"]) > 25 else preset["name"]
            builder.button(
                text=f"🎯 {display_name}",
                callback_data=f"preset:select:{preset['id']}"
            )
    
    # Add cancel button
    builder.button(
        text=tr(user, "❌ Отменить", "❌ Cancel"),
        callback_data="preset:cancel"
    )
    
    builder.adjust(1)  # One preset per row
    return builder.as_markup()


def get_preset_creation_menu(user=None, opts=None) -> InlineKeyboardMarkup:
    """Menu for creating new presets with current state indicators."""
    builder = InlineKeyboardBuilder()
    
    if opts is None:
        # Default values if no options provided
        opts = {
            "subtitles": True,
            "translate": False,
            "voiceover": False,
            "vertical": False,
        }
    
    # Configuration options with state indicators
    subs_icon = "✅" if opts.get("subtitles", True) else "❌"
    translate_icon = "✅" if opts.get("translate", False) else "❌"
    tts_icon = "✅" if opts.get("voiceover", False) else "❌"
    format_icon = "✅" if opts.get("vertical", False) else "❌"
    
    builder.button(text=tr(user, f"{subs_icon} Субтитры", f"{subs_icon} Subtitles"), callback_data="create:subs:toggle")
    builder.button(text=tr(user, f"{translate_icon} Перевод", f"{translate_icon} Translate"), callback_data="create:translate:toggle")
    builder.button(text=tr(user, f"{tts_icon} Озвучка", f"{tts_icon} Voiceover"), callback_data="create:tts:toggle")
    builder.button(text=tr(user, f"{format_icon} Формат 9:16", f"{format_icon} Format 9:16"), callback_data="create:format:916")
    
    # Advanced options
    builder.button(text=tr(user, "🎚️ Стиль субтитров", "🎚️ Subtitle Style"), callback_data="create:style:open")
    builder.button(text=tr(user, "📍 Позиция субтитров", "📍 Subtitle Position"), callback_data="create:position:open")
    builder.button(text=tr(user, "🌐 Язык перевода", "🌐 Translation Language"), callback_data="create:lang:open")
    builder.button(text=tr(user, "🗣️ Голос TTS", "🗣️ TTS Voice"), callback_data="create:voice:open")
    
    # Save preset
    builder.button(text=tr(user, "💾 Сохранить пресет", "💾 Save Preset"), callback_data="create:save")
    
    builder.adjust(2, 2, 2, 2, 1)
    return builder.as_markup()


def get_preset_editing_menu(user=None, opts=None, preset_id=None) -> InlineKeyboardMarkup:
    """Menu for editing existing presets with current state indicators."""
    builder = InlineKeyboardBuilder()
    
    if opts is None:
        # Default values if no options provided
        opts = {
            "subtitles": True,
            "translate": False,
            "voiceover": False,
            "vertical": False,
        }
    
    # Configuration options with state indicators
    subs_icon = "✅" if opts.get("subtitles", True) else "❌"
    translate_icon = "✅" if opts.get("translate", False) else "❌"
    tts_icon = "✅" if opts.get("voiceover", False) else "❌"
    format_icon = "✅" if opts.get("vertical", False) else "❌"
    
    builder.button(text=tr(user, f"{subs_icon} Субтитры", f"{subs_icon} Subtitles"), callback_data="edit:subs:toggle")
    builder.button(text=tr(user, f"{translate_icon} Перевод", f"{translate_icon} Translate"), callback_data="edit:translate:toggle")
    builder.button(text=tr(user, f"{tts_icon} Озвучка", f"{tts_icon} Voiceover"), callback_data="edit:tts:toggle")
    builder.button(text=tr(user, f"{format_icon} Формат 9:16", f"{format_icon} Format 9:16"), callback_data="edit:format:916")
    
    # Advanced options
    builder.button(text=tr(user, "🎚️ Стиль субтитров", "🎚️ Subtitle Style"), callback_data="edit:style:open")
    builder.button(text=tr(user, "📍 Позиция субтитров", "📍 Subtitle Position"), callback_data="edit:position:open")
    builder.button(text=tr(user, "🌐 Язык перевода", "🌐 Translation Language"), callback_data="edit:lang:open")
    builder.button(text=tr(user, "🗣️ Голос TTS", "🗣️ TTS Voice"), callback_data="edit:voice:open")
    
    # Save changes and back
    builder.button(text=tr(user, "💾 Сохранить изменения", "💾 Save Changes"), callback_data=f"edit:save:{preset_id}")
    builder.button(text=tr(user, "⬅️ К списку пресетов", "⬅️ Back to presets"), callback_data="edit:back")
    
    builder.adjust(2, 2, 2, 2, 1, 1)
    return builder.as_markup()


def get_upsell_keyboard(user=None) -> InlineKeyboardMarkup:
    """Upsell buttons for PRO."""
    builder = InlineKeyboardBuilder()
    builder.button(text=tr(user, "🔓 Оформить PRO", "🔓 Upgrade to PRO"), callback_data="plan:buy:pro")
    builder.button(text=tr(user, "ℹ️ Подробнее", "ℹ️ Learn more"), callback_data="nav:plan")
    builder.adjust(2)
    return builder.as_markup()

