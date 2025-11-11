"""Start command handler."""
from aiogram import Router, F
from aiogram.filters import Command, CommandStart, StateFilter
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from bot.keyboards import (
    get_main_menu,
    get_language_selection,
    get_options_menu,
    get_style_presets_keyboard,
    get_voice_keyboard,
    get_subtitle_position_keyboard,
)
from db.crud import update_user_language
from aiogram import F as AF
from config.constants import SUPPORTED_LANGUAGES
from bot.i18n import t, tr, all_translations_for_key, resolve_language, language_options
from bot.services.options_service import get_default_options, update_default_options
from bot.services.preset_service import save_preset, list_presets
from common.subtitle_styles import get_style_display


OPTIONS_BUTTONS = list(all_translations_for_key("menu.options"))
PRESETS_BUTTONS = list(all_translations_for_key("menu.presets"))
PLAN_BUTTONS = list(all_translations_for_key("menu.plan"))
HELP_BUTTONS = list(all_translations_for_key("menu.help"))
LANGUAGE_BUTTONS = list(all_translations_for_key("menu.language"))

router = Router()


@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext, user, **kwargs):
    """Handle /start command."""
    await state.clear()
    await message.answer(t(user, "onboarding.welcome"), reply_markup=get_main_menu(user))
    await message.answer(t(user, "language.prompt"), reply_markup=get_language_selection(user, callback_prefix="ui:lang:"))


@router.message(Command("help"))
@router.message(AF.text.in_(HELP_BUTTONS))
async def cmd_help(message: Message, user, **kwargs):
    """Handle /help command with detailed instructions."""
    from bot.keyboards import get_main_menu
    
    await message.answer(
        t(user, "help.detailed"),
        reply_markup=get_main_menu(user)
    )


@router.message(Command("settings"))
@router.message(AF.text.in_(OPTIONS_BUTTONS))
async def cmd_create_preset(message: Message, user, **kwargs):
    """Open preset creation screen."""
    from bot.keyboards import get_preset_creation_menu
    
    opts = await get_default_options(user.id)
    lang_code = resolve_language(user)
    def fmt_on(v: bool) -> str:
        return tr(user, "вкл", "on") if v else tr(user, "выкл", "off")
    style_name = get_style_display(opts.get("style", "sub36o1"), lang_code)
    position_label = {
        "top": tr(user, "верх", "top"),
        "middle": tr(user, "центр", "middle"),
        "bottom": tr(user, "низ", "bottom"),
    }.get(opts.get("position", "bottom"), tr(user, "низ", "bottom"))
    voice_label = tr(user, "женский", "female") if opts.get("voice", "female") == "female" else tr(user, "мужской", "male")
    lang_map = language_options()
    target = opts.get("target_language", "auto")
    if target == "auto":
        target_label = tr(user, "авто", "auto")
    else:
        target_label = lang_map.get(target, target)
    translate_line = (
        tr(user, f"{fmt_on(True)} → {target_label}", f"{fmt_on(True)} → {target_label}")
        if opts.get("translate", False)
        else fmt_on(False)
    )
    voice_line = (
        tr(user, f"{fmt_on(True)} · {voice_label}", f"{fmt_on(True)} · {voice_label}")
        if opts.get("voiceover", False)
        else fmt_on(False)
    )
    format_ru = "9:16" if opts.get("vertical") else "исходный"
    format_en = "9:16" if opts.get("vertical") else "original"
    text = tr(
        user,
        "✨ Создание пресета\n\n"
        f"📋 Текущие настройки:\n"
        f"• Субтитры: {fmt_on(opts.get('subtitles', True))}\n"
        f"• Перевод: {translate_line}\n"
        f"• Озвучка: {voice_line}\n"
        f"• Формат: {format_ru}\n"
        f"• Стиль: {style_name}\n"
        f"• Позиция: {position_label}\n\n"
        f"Настройте параметры и сохраните как пресет:",
        "✨ Creating preset\n\n"
        f"📋 Current settings:\n"
        f"• Subtitles: {fmt_on(opts.get('subtitles', True))}\n"
        f"• Translate: {translate_line}\n"
        f"• Voiceover: {voice_line}\n"
        f"• Format: {format_en}\n"
        f"• Style: {style_name}\n"
        f"• Position: {position_label}\n\n"
        f"Configure parameters and save as preset:",
    )
    await message.answer(text, reply_markup=get_preset_creation_menu(user, opts))


@router.message(Command("preset"))
@router.message(AF.text.in_(PRESETS_BUTTONS))
async def cmd_preset(message: Message, user, **kwargs):
    """Open presets list."""
    from bot.handlers.preset_handler import cmd_presets
    await cmd_presets(message, user)


@router.message(Command("plan"))
@router.message(AF.text.in_(PLAN_BUTTONS))
async def cmd_plan(message: Message, user, **kwargs):
    """Alias to pricing screen."""
    # Lazy import to avoid circular
    from bot.handlers.pricing_handler import cmd_pricing
    await cmd_pricing(message, user=user)


@router.message(Command("language"))
@router.message(AF.text.in_(LANGUAGE_BUTTONS))
async def cmd_language(message: Message, user, **kwargs):
    """Open language selection."""
    await message.answer(t(user, "language.prompt"), reply_markup=get_language_selection(user, callback_prefix="ui:lang:"))


@router.message(Command("cancel"))
async def cmd_cancel(message: Message, state: FSMContext, user, **kwargs):
    """Handle /cancel command."""
    await state.clear()
    await message.answer(
        tr(user, "❌ Операция отменена.", "❌ Operation cancelled."),
        reply_markup=get_main_menu(user)
    )


@router.callback_query(AF.data == "nav:upload")
async def nav_upload(callback: CallbackQuery, user, **kwargs):
    """Navigate to upload flow."""
    await callback.message.answer(tr(user, "📥 Загрузить: отправь видео/аудио или ссылку.", "📥 Upload: send a video/audio or link."))
    await callback.answer()


@router.callback_query(AF.data == "nav:options")
async def nav_options(callback: CallbackQuery, user, **kwargs):
    """Navigate to options."""
    await cmd_settings(callback.message, user)
    await callback.answer()


@router.callback_query(AF.data == "nav:plan")
async def nav_plan(callback: CallbackQuery, user, **kwargs):
    """Navigate to plan screen."""
    await cmd_plan(callback.message, user)
    await callback.answer()


@router.callback_query(AF.data.startswith("ui:lang:"))
async def set_interface_language(callback: CallbackQuery, user, db, **kwargs):
    """Set interface language from onboarding."""
    lang = callback.data.split(":")[-1]
    if lang not in SUPPORTED_LANGUAGES:
        await callback.answer(t(user, "language.invalid"), show_alert=True)
        return
    await update_user_language(db, user.id, lang)
    user.language_code = lang
    await callback.answer(t(user, "language.saved"))
    try:
        await callback.message.edit_reply_markup()
    except Exception:
        pass
    await callback.message.answer(t(user, "language.ready"), reply_markup=get_main_menu(user))


# -------- Interactive defaults management (outside processing flow) --------

def _options_summary_text(user, opts):
    def fmt_on(v: bool) -> str:
        return tr(user, "вкл", "on") if v else tr(user, "выкл", "off")
    lang_code = resolve_language(user)
    style_name = get_style_display(opts.get("style", "sub36o1"), lang_code)
    position_label = {
        "top": tr(user, "верх", "top"),
        "middle": tr(user, "центр", "middle"),
        "bottom": tr(user, "низ", "bottom"),
    }.get(opts.get("position", "bottom"), tr(user, "низ", "bottom"))
    voice_label = tr(user, "женский", "female") if opts.get("voice", "female") == "female" else tr(user, "мужской", "male")
    lang_map = language_options()
    target = opts.get("target_language", "auto")
    if target == "auto":
        target_label = tr(user, "авто", "auto")
    else:
        target_label = lang_map.get(target, target)
    translate_line = (
        tr(user, f"{fmt_on(True)} → {target_label}", f"{fmt_on(True)} → {target_label}")
        if opts.get("translate", False)
        else fmt_on(False)
    )
    voice_line = (
        tr(user, f"{fmt_on(True)} · {voice_label}", f"{fmt_on(True)} · {voice_label}")
        if opts.get("voiceover", False)
        else fmt_on(False)
    )
    return tr(
        user,
        "🎛️ Опции\n"
        f"- Субтитры: {fmt_on(opts.get('subtitles', True))}\n"
        f"- Перевод: {translate_line}\n"
        f"- Озвучка: {voice_line}\n"
        f"- Формат: {'9:16' if opts.get('vertical') else 'исходный'}\n"
        f"- Стиль: {style_name}\n"
        f"- Позиция: {position_label}\n",
        "🎛️ Options\n"
        f"- Subtitles: {fmt_on(opts.get('subtitles', True))}\n"
        f"- Translate: {translate_line}\n"
        f"- Voiceover: {voice_line}\n"
        f"- Format: {'9:16' if opts.get('vertical') else 'original'}\n"
        f"- Style: {style_name}\n"
        f"- Position: {position_label}\n",
    )


@router.callback_query(StateFilter(None), AF.data.startswith("opt:"))
async def settings_opt_handler(callback: CallbackQuery, user, **kwargs):
    """Handle option updates in Settings (global defaults)."""
    parts = callback.data.split(":")[1:]
    if not parts:
        await callback.answer()
        return
    key = parts[0]
    val = parts[1] if len(parts) > 1 else None

    opts = await get_default_options(user.id)

    # Open sub-menus
    if key == "style" and val == "open":
        from bot.keyboards import style_help_text
        await callback.message.edit_text(style_help_text(user), reply_markup=get_style_presets_keyboard(user))
        await callback.answer()
        return
    if key == "voice" and val == "open":
        await callback.message.edit_text(tr(user, "🗣️ Выберите голос", "🗣️ Choose voice"), reply_markup=get_voice_keyboard(user))
        await callback.answer()
        return
    if key == "lang" and val == "open":
        await callback.message.edit_text(
            tr(user, "🌐 Язык перевода", "🌐 Translation language"),
            reply_markup=get_language_selection(
                user,
                callback_prefix="opt:lang:",
                include_back=True,
                back_callback="opt:back",
                current_code=opts.get("target_language", "auto"),
            ),
        )
        await callback.answer()
        return
    if key == "position" and val == "open":
        await callback.message.edit_text(
            tr(user, "📍 Расположение субтитров", "📍 Subtitle placement"),
            reply_markup=get_subtitle_position_keyboard(user),
        )
        await callback.answer()
        return

    if key == "subs":
        opts = await update_default_options(user.id, {"subtitles": not opts.get("subtitles", True)})
    elif key in ("translate", "translation"):
        opts = await update_default_options(user.id, {"translate": not opts.get("translate", False)})
    elif key == "tts":
        opts = await update_default_options(user.id, {"voiceover": not opts.get("voiceover", False)})
    elif key == "format":
        if val in ("916", "src"):
            new_vertical = (val == "916")
        else:
            new_vertical = not opts.get("vertical", False)
        opts = await update_default_options(user.id, {"vertical": new_vertical})
    elif key == "style" and val == "preset":
        preset_id = parts[2] if len(parts) > 2 else "sub36o1"
        opts = await update_default_options(user.id, {"style": preset_id})
        await callback.answer(tr(user, "Стиль сохранён", "Style saved"))
    elif key == "style" and val == "custom":
        opts = await update_default_options(user.id, {"style": "custom"})
    elif key == "voice" and val:
        opts = await update_default_options(user.id, {"voice": val, "voiceover": True})
        await callback.answer(tr(user, f"Голос: {val} · озвучка вкл", f"Voice: {val} · TTS on"))
    elif key == "lang" and val:
        # Set translation target language default and enable translation
        opts = await update_default_options(user.id, {"target_language": val, "translate": True})
        target_label = tr(user, "авто", "auto") if val == "auto" else language_options().get(val, val)
        await callback.answer(tr(user, f"Перевод → {target_label}", f"Translate → {target_label}"))
    elif key == "position" and val:
        if val in {"top", "middle", "bottom"}:
            opts = await update_default_options(user.id, {"position": val})
            label = {
                "top": tr(user, "верх", "top"),
                "middle": tr(user, "центр", "middle"),
                "bottom": tr(user, "низ", "bottom"),
            }[val]
            await callback.answer(tr(user, f"Позиция: {label}", f"Position: {label}"))
    elif key == "preset" and val == "save":
        options_for_preset = {
            "subtitles": opts.get("subtitles", True),
            "translate": opts.get("translate", False),
            "voiceover": opts.get("voiceover", False),
            "vertical": opts.get("vertical", False),
            "style": opts.get("style", "sub36o1"),
            "voice": opts.get("voice", "female"),
            "target_language": opts.get("target_language", "auto"),
            "position": opts.get("position", "bottom"),
        }
        presets = await list_presets(user.id)
        name = f"Preset {len(presets) + 1}"
        await save_preset(user.id, name, options_for_preset)
        await callback.answer(tr(user, "Пресет сохранён", "Preset saved"))
    elif key == "back":
        # Just fall through to summary redraw
        pass
    else:
        # Unknown / noop
        await callback.answer()

    # Redraw summary
    opts = await get_default_options(user.id)
    await callback.message.edit_text(_options_summary_text(user, opts), reply_markup=get_options_menu(user))
    await callback.answer()


# -------- Preset creation handlers --------

@router.callback_query(F.data.startswith("create:") & ~F.data.startswith("create:set:"))
async def handle_preset_creation(callback: CallbackQuery, user, **kwargs):
    """Handle preset creation callbacks."""
    from bot.keyboards import get_preset_creation_menu, get_language_selection, get_style_presets_keyboard, get_voice_keyboard, get_subtitle_position_keyboard
    
    parts = callback.data.split(":")
    if len(parts) < 2:
        await callback.answer()
        return
    
    action = parts[1]
    value = parts[2] if len(parts) > 2 else None
    
    if action == "set":
        # These callbacks are handled by more specific handlers (create:set:...)
        return
    opts = await get_default_options(user.id)
    
    if action == "subs" and value == "toggle":
        # Toggle subtitles
        new_value = not opts.get("subtitles", True)
        opts = await update_default_options(user.id, {"subtitles": new_value})
        status = tr(user, "включены", "enabled") if new_value else tr(user, "выключены", "disabled")
        await callback.answer(tr(user, f"Субтитры {status}", f"Subtitles {status}"))
        
    elif action == "translate" and value == "toggle":
        # Toggle translation
        new_value = not opts.get("translate", False)
        opts = await update_default_options(user.id, {"translate": new_value})
        status = tr(user, "включен", "enabled") if new_value else tr(user, "выключен", "disabled")
        await callback.answer(tr(user, f"Перевод {status}", f"Translation {status}"))
        
    elif action == "tts" and value == "toggle":
        # Toggle voiceover
        new_value = not opts.get("voiceover", False)
        opts = await update_default_options(user.id, {"voiceover": new_value})
        status = tr(user, "включена", "enabled") if new_value else tr(user, "выключена", "disabled")
        await callback.answer(tr(user, f"Озвучка {status}", f"Voiceover {status}"))
        
    elif action == "format" and value == "916":
        # Toggle vertical format
        new_value = not opts.get("vertical", False)
        opts = await update_default_options(user.id, {"vertical": new_value})
        format_text = "9:16" if new_value else tr(user, "исходный", "original")
        await callback.answer(tr(user, f"Формат: {format_text}", f"Format: {format_text}"))
        
    elif action == "style" and value == "open":
        # Open style selection
        await callback.message.edit_text(
            tr(user, "🎚️ Выберите стиль субтитров:", "🎚️ Choose subtitle style:"),
            reply_markup=get_style_presets_keyboard(user, callback_prefix="create:set:style:", back_callback="create:back")
        )
        await callback.answer()
        return
        
    elif action == "position" and value == "open":
        # Open position selection
        await callback.message.edit_text(
            tr(user, "📍 Выберите позицию субтитров:", "📍 Choose subtitle position:"),
            reply_markup=get_subtitle_position_keyboard(user, callback_prefix="create:set:position:", back_callback="create:back")
        )
        await callback.answer()
        return
        
    elif action == "lang" and value == "open":
        # Open language selection
        current_code = opts.get("target_language", "auto")
        if current_code not in language_options():
            current_code = resolve_language(user)
        await callback.message.edit_text(
            tr(user, "🌐 Выберите язык перевода:", "🌐 Choose translation language:"),
            reply_markup=get_language_selection(
                user,
                callback_prefix="create:lang:",
                include_back=True,
                back_callback="create:back",
                current_code=current_code,
            ),
        )
        await callback.answer()
        return
    
    elif action == "lang" and value:
        # Handle language selection directly
        lang_map = language_options()
        if value != "auto" and value not in lang_map:
            await callback.answer(tr(user, "❌ Недоступный язык", "❌ Unsupported language"), show_alert=True)
            return
        
        opts = await update_default_options(user.id, {"target_language": value, "translate": True})
        if value == "auto":
            label = tr(user, "авто", "auto")
        else:
            label = lang_map.get(value, value)
        
        # Re-render language selection with updated checkmark
        current_code = opts.get("target_language", value)
        if current_code not in lang_map:
            current_code = resolve_language(user)
        await callback.message.edit_text(
            tr(user, "🌐 Выберите язык перевода:", "🌐 Choose translation language:"),
            reply_markup=get_language_selection(
                user,
                callback_prefix="create:lang:",
                include_back=True,
                back_callback="create:back",
                current_code=current_code,
            ),
        )
        await callback.answer(tr(user, f"Язык перевода: {label}", f"Translation language: {label}"))
        return
        
    elif action == "voice" and value == "open":
        # Open voice selection
        await callback.message.edit_text(
            tr(user, "🗣️ Выберите голос для озвучки:", "🗣️ Choose voice for TTS:"),
            reply_markup=get_voice_keyboard(user, callback_prefix="create:set:voice:", back_callback="create:back")
        )
        await callback.answer()
        return
        
    elif action == "save":
        # Save preset
        from bot.services.preset_service import save_preset, list_presets
        
        options_for_preset = {
            "subtitles": opts.get("subtitles", True),
            "translate": opts.get("translate", False),
            "voiceover": opts.get("voiceover", False),
            "vertical": opts.get("vertical", False),
            "style": opts.get("style", "sub36o1"),
            "voice": opts.get("voice", "female"),
            "target_language": opts.get("target_language", "auto"),
            "position": opts.get("position", "bottom"),
        }
        presets = await list_presets(user.id)
        name = f"Пресет {len(presets) + 1}"
        await save_preset(user.id, name, options_for_preset)
        await callback.answer(tr(user, "✅ Пресет сохранён!", "✅ Preset saved!"))
        
        # Return to main menu
        from bot.keyboards import get_main_menu
        await callback.message.edit_text(
            tr(user, "✅ Пресет успешно сохранён!\n\nТеперь вы можете использовать его для обработки видео.", "✅ Preset saved successfully!\n\nNow you can use it to process videos."),
            reply_markup=get_main_menu(user)
        )
        return
        
    elif action == "back":
        # Return to preset creation menu with current options
        await _update_preset_creation_interface(callback.message, user, opts)
        return
    else:
        await callback.answer()
        return
    
    # Update the preset creation interface
    await _update_preset_creation_interface(callback.message, user, opts)


async def _update_preset_creation_interface(message, user, opts):
    """Update preset creation interface with current settings."""
    from bot.keyboards import get_preset_creation_menu
    
    lang_code = resolve_language(user)
    def fmt_on(v: bool) -> str:
        return tr(user, "вкл", "on") if v else tr(user, "выкл", "off")
    style_name = get_style_display(opts.get("style", "sub36o1"), lang_code)
    position_label = {
        "top": tr(user, "верх", "top"),
        "middle": tr(user, "центр", "middle"),
        "bottom": tr(user, "низ", "bottom"),
    }.get(opts.get("position", "bottom"), tr(user, "низ", "bottom"))
    voice_label = tr(user, "женский", "female") if opts.get("voice", "female") == "female" else tr(user, "мужской", "male")
    lang_map = language_options()
    target = opts.get("target_language", "auto")
    if target == "auto":
        target_label = tr(user, "авто", "auto")
    else:
        target_label = lang_map.get(target, target)
    translate_line = (
        tr(user, f"{fmt_on(True)} → {target_label}", f"{fmt_on(True)} → {target_label}")
        if opts.get("translate", False)
        else fmt_on(False)
    )
    voice_line = (
        tr(user, f"{fmt_on(True)} · {voice_label}", f"{fmt_on(True)} · {voice_label}")
        if opts.get("voiceover", False)
        else fmt_on(False)
    )
    format_ru = "9:16" if opts.get("vertical") else "исходный"
    format_en = "9:16" if opts.get("vertical") else "original"
    text = tr(
        user,
        "✨ Создание пресета\n\n"
        f"📋 Текущие настройки:\n"
        f"• Субтитры: {fmt_on(opts.get('subtitles', True))}\n"
        f"• Перевод: {translate_line}\n"
        f"• Озвучка: {voice_line}\n"
        f"• Формат: {format_ru}\n"
        f"• Стиль: {style_name}\n"
        f"• Позиция: {position_label}\n\n"
        f"Настройте параметры и сохраните как пресет:",
        "✨ Creating preset\n\n"
        f"📋 Current settings:\n"
        f"• Subtitles: {fmt_on(opts.get('subtitles', True))}\n"
        f"• Translate: {translate_line}\n"
        f"• Voiceover: {voice_line}\n"
        f"• Format: {format_en}\n"
        f"• Style: {style_name}\n"
        f"• Position: {position_label}\n\n"
        f"Configure parameters and save as preset:",
    )
    
    try:
        await message.edit_text(text, reply_markup=get_preset_creation_menu(user, opts))
    except Exception:
        # If edit fails, send new message
        await message.answer(text, reply_markup=get_preset_creation_menu(user, opts))


# Handle additional preset creation callbacks (style, position, voice)
@router.callback_query(F.data.startswith("create:set:style:"))
async def handle_preset_style_selection(callback: CallbackQuery, user, **kwargs):
    """Handle style selection in preset creation."""
    style_id = callback.data.split(":")[-1]
    
    opts = await update_default_options(user.id, {"style": style_id})
    
    lang_code = resolve_language(user)
    style_name = get_style_display(style_id, lang_code)
    await callback.answer(tr(user, f"Стиль: {style_name}", f"Style: {style_name}"))
    await _update_preset_creation_interface(callback.message, user, opts)


@router.callback_query(F.data.startswith("create:set:position:"))
async def handle_preset_position_selection(callback: CallbackQuery, user, **kwargs):
    """Handle position selection in preset creation."""
    position = callback.data.split(":")[-1]
    
    if position in {"top", "middle", "bottom"}:
        opts = await update_default_options(user.id, {"position": position})
        
        labels = {
            "top": tr(user, "верх", "top"),
            "middle": tr(user, "центр", "middle"),
            "bottom": tr(user, "низ", "bottom"),
        }
        await callback.answer(tr(user, f"Позиция: {labels[position]}", f"Position: {labels[position]}"))
        await _update_preset_creation_interface(callback.message, user, opts)


@router.callback_query(F.data.startswith("create:set:voice:"))
async def handle_preset_voice_selection(callback: CallbackQuery, user, **kwargs):
    """Handle voice selection in preset creation."""
    voice = callback.data.split(":")[-1]
    
    if voice in {"male", "female"}:
        opts = await update_default_options(user.id, {"voice": voice, "voiceover": True})
        
        voice_label = tr(user, "мужской", "male") if voice == "male" else tr(user, "женский", "female")
        await callback.answer(tr(user, f"Голос: {voice_label}", f"Voice: {voice_label}"))
        await _update_preset_creation_interface(callback.message, user, opts)


@router.callback_query(F.data == "create:back")
async def handle_preset_creation_back(callback: CallbackQuery, user, **kwargs):
    """Handle back button in preset creation."""
    opts = await get_default_options(user.id)
    await _update_preset_creation_interface(callback.message, user, opts)

