"""Presets management handler."""
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import InlineKeyboardBuilder

from bot.services.preset_service import (
    list_presets,
    delete_preset,
    get_preset,
    update_preset,
)
from bot.services.options_service import get_default_options
from bot.states import VideoProcessing, PresetEdit
from bot.i18n import tr, all_translations_for_key, resolve_language, language_options
from common.subtitle_styles import get_style_display

router = Router()

PRESETS_BUTTONS = list(all_translations_for_key("menu.presets"))


def _build_presets_keyboard(presets, user):
    kb = InlineKeyboardBuilder()
    for p in presets:
        pid = p["id"]
        kb.button(text=f"🎯 {p['name']}", callback_data=f"preset:apply:{pid}")
        kb.button(text="✏️", callback_data=f"preset:edit:{pid}")
        kb.button(text="🗑️", callback_data=f"preset:delete:{pid}")
    # Removed "New" button - presets are created in "Create preset" section
    kb.adjust(3)
    return kb.as_markup()


def _build_edit_keyboard(preset_id: int, user):
    kb = InlineKeyboardBuilder()
    kb.button(text=tr(user, "🔄 Обновить опции", "🔄 Update options"), callback_data=f"preset:update:{preset_id}")
    kb.button(text=tr(user, "✏️ Переименовать", "✏️ Rename"), callback_data=f"preset:rename:{preset_id}")
    kb.button(text=tr(user, "⬅️ К списку", "⬅️ Back to list"), callback_data="preset:back")
    kb.adjust(1)
    return kb.as_markup()


def _format_preset_line(user, preset, lang_code: str) -> str:
    opts = preset.get("options", {})
    fmt = tr(user, "9:16", "9:16") if opts.get("vertical") else tr(user, "оригинал", "original")
    style_label = get_style_display(opts.get("style", "sub36o1"), lang_code)
    voice = opts.get("voice", "female")
    voice_label = tr(user, "TTS выкл", "TTS off") if not opts.get("voiceover") else tr(
        user,
        f"TTS { 'муж' if voice == 'male' else 'жен' }",
        f"TTS {voice}",
    )
    lang_map = language_options()
    target = opts.get("target_language", "auto")
    if opts.get("translate"):
        if target == "auto":
            translate_label = tr(user, "перевод → авто", "translate → auto")
        else:
            translate_label = tr(
                user,
                f"перевод → {lang_map.get(target, target)}",
                f"translate → {lang_map.get(target, target)}",
            )
    else:
        translate_label = tr(user, "без перевода", "no translate")
    return f"{preset['id']}) {preset['name']} · {fmt} · {style_label} · {voice_label} · {translate_label}"


@router.message(Command("preset"))
@router.message(F.text.in_(PRESETS_BUTTONS))
async def cmd_presets(message: Message, user, **kwargs):
    """Show presets list."""
    presets = await list_presets(user.id)
    text = tr(user, "🧩 Мои пресеты", "🧩 My presets")
    if presets:
        lang_code = resolve_language(user)
        lines = [_format_preset_line(user, preset, lang_code) for preset in presets]
        text += f" ({len(presets)})\n\n" + "\n".join(lines)
    else:
        text += tr(user, "\nПока пусто.", "\nNo presets yet.")
    await message.answer(text, reply_markup=_build_presets_keyboard(presets, user))


@router.callback_query(F.data.startswith("preset:delete:"))
async def cb_preset_delete(callback: CallbackQuery, user, **kwargs):
    preset_id = int(callback.data.split(":")[-1])
    ok = await delete_preset(user.id, preset_id)
    await callback.answer(tr(user, "Удалено", "Deleted") if ok else tr(user, "Не найдено", "Not found"))
    await cmd_presets(callback.message, user)


@router.callback_query(F.data.startswith("preset:apply:"))
async def cb_preset_apply(callback: CallbackQuery, state: FSMContext, user, **kwargs):
    pid = int(callback.data.split(":")[-1])
    preset = await get_preset(user.id, pid)
    if not preset:
        await callback.answer(tr(user, "Пресет не найден", "Preset not found"))
        return
    data = await state.get_data()
    options = preset.get("options", {})
    # Persist as new defaults so auto-upload and fresh sessions use this preset
    from bot.services.options_service import update_default_options
    await update_default_options(user.id, options)
    if data and await state.get_state() == VideoProcessing.selecting_options.state:
        await state.update_data(
            options=options,
            target_language=options.get("target_language", "auto"),
        )
        await callback.answer(tr(user, "Пресет применён", "Preset applied"))
    else:
        await callback.message.answer(tr(user, "Пресет применён. Отправьте видео или ссылку, чтобы обработать с этими опциями.", "Preset applied. Send a video or link to process with these options."))
        await callback.answer()


@router.callback_query(F.data.startswith("preset:edit:"))
async def cb_preset_edit(callback: CallbackQuery, user, **kwargs):
    preset_id = int(callback.data.split(":")[-1])
    preset = await get_preset(user.id, preset_id)
    if not preset:
        await callback.answer(tr(user, "Пресет не найден", "Preset not found"))
        return
    lang_code = resolve_language(user)
    summary = _format_preset_line(user, preset, lang_code)
    await callback.message.answer(
        tr(user, f"✏️ Редактирование: {summary}", f"✏️ Editing: {summary}"),
        reply_markup=_build_edit_keyboard(preset_id, user),
    )
    await callback.answer()


@router.callback_query(F.data.startswith("preset:update:"))
async def cb_preset_update(callback: CallbackQuery, state: FSMContext, user, **kwargs):
    """Open preset editing interface."""
    preset_id = int(callback.data.split(":")[-1])
    preset = await get_preset(user.id, preset_id)
    if not preset:
        await callback.answer(tr(user, "Пресет не найден", "Preset not found"))
        return
    
    # Set preset options as current defaults for editing
    from bot.services.options_service import update_default_options
    preset_options = preset.get("options", {})
    await update_default_options(user.id, preset_options)
    
    # Store preset ID in state for saving later
    await state.update_data(editing_preset_id=preset_id, current_preset_options=preset_options)
    
    # Show preset editing interface
    await _show_preset_editing_interface(callback.message, user, preset_options, preset_id, state)
    await callback.answer()


async def _show_preset_editing_interface(message, user, opts, preset_id, state: FSMContext | None = None):
    """Show preset editing interface with current settings."""
    from bot.keyboards import get_preset_editing_menu
    
    if state:
        await state.update_data(editing_preset_id=preset_id, current_preset_options=opts)
    
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
    
    preset_name = ""
    try:
        preset = await get_preset(user.id, preset_id)
        preset_name = preset.get("name", "Unnamed") if preset else "Unnamed"
    except:
        preset_name = "Unnamed"
    
    text = tr(
        user,
        f"✏️ Редактирование пресета: {preset_name}\n\n"
        f"📋 Текущие настройки:\n"
        f"• Субтитры: {fmt_on(opts.get('subtitles', True))}\n"
        f"• Перевод: {translate_line}\n"
        f"• Озвучка: {voice_line}\n"
        f"• Формат: {format_ru}\n"
        f"• Стиль: {style_name}\n"
        f"• Позиция: {position_label}\n\n"
        f"Измените параметры и сохраните:",
        f"✏️ Editing preset: {preset_name}\n\n"
        f"📋 Current settings:\n"
        f"• Subtitles: {fmt_on(opts.get('subtitles', True))}\n"
        f"• Translate: {translate_line}\n"
        f"• Voiceover: {voice_line}\n"
        f"• Format: {format_en}\n"
        f"• Style: {style_name}\n"
        f"• Position: {position_label}\n\n"
        f"Change parameters and save:",
    )
    
    try:
        await message.edit_text(text, reply_markup=get_preset_editing_menu(user, opts, preset_id))
    except Exception:
        # If edit fails, send new message
        await message.answer(text, reply_markup=get_preset_editing_menu(user, opts, preset_id))


# -------- Preset editing handlers --------

@router.callback_query(F.data.startswith("edit:"))
async def handle_preset_editing(callback: CallbackQuery, state: FSMContext, user, **kwargs):
    """Handle preset editing callbacks."""
    from bot.keyboards import get_preset_editing_menu, get_language_selection, get_style_presets_keyboard, get_voice_keyboard, get_subtitle_position_keyboard
    
    parts = callback.data.split(":")
    if len(parts) < 2:
        await callback.answer()
        return
    
    action = parts[1]
    value = parts[2] if len(parts) > 2 else None
    
    # Get current state data
    data = await state.get_data()
    editing_preset_id = data.get("editing_preset_id")
    
    if not editing_preset_id:
        await callback.answer(tr(user, "Ошибка: пресет не найден", "Error: preset not found"))
        return
    
    current_opts = data.get("current_preset_options")
    if not current_opts:
        current_opts = await get_default_options(user.id)
        await state.update_data(current_preset_options=current_opts)
    
    if action == "subs" and value == "toggle":
        # Toggle subtitles
        new_value = not current_opts.get("subtitles", True)
        current_opts["subtitles"] = new_value
        await state.update_data(current_preset_options=current_opts)
        status = tr(user, "включены", "enabled") if new_value else tr(user, "выключены", "disabled")
        await callback.answer(tr(user, f"Субтитры {status}", f"Subtitles {status}"))
        await _show_preset_editing_interface(callback.message, user, current_opts, editing_preset_id, state)
        return
    elif action == "translate" and value == "toggle":
        # Toggle translation
        new_value = not current_opts.get("translate", False)
        current_opts["translate"] = new_value
        if not new_value:
            current_opts["target_language"] = "auto"
        await state.update_data(current_preset_options=current_opts)
        status = tr(user, "включен", "enabled") if new_value else tr(user, "выключен", "disabled")
        await callback.answer(tr(user, f"Перевод {status}", f"Translation {status}"))
        await _show_preset_editing_interface(callback.message, user, current_opts, editing_preset_id, state)
        return
    elif action == "tts" and value == "toggle":
        # Toggle voiceover
        new_value = not current_opts.get("voiceover", False)
        current_opts["voiceover"] = new_value
        await state.update_data(current_preset_options=current_opts)
        status = tr(user, "включена", "enabled") if new_value else tr(user, "выключена", "disabled")
        await callback.answer(tr(user, f"Озвучка {status}", f"Voiceover {status}"))
        await _show_preset_editing_interface(callback.message, user, current_opts, editing_preset_id, state)
        return
    elif action == "format" and value == "916":
        # Toggle vertical format
        new_value = not current_opts.get("vertical", False)
        current_opts["vertical"] = new_value
        await state.update_data(current_preset_options=current_opts)
        format_text = "9:16" if new_value else tr(user, "исходный", "original")
        await callback.answer(tr(user, f"Формат: {format_text}", f"Format: {format_text}"))
        await _show_preset_editing_interface(callback.message, user, current_opts, editing_preset_id, state)
        return
    elif action == "style" and value == "open":
        # Open style selection
        await callback.message.edit_text(
            tr(user, "🎚️ Выберите стиль субтитров:", "🎚️ Choose subtitle style:"),
            reply_markup=get_style_presets_keyboard(user, callback_prefix="edit:style:", back_callback="edit:back")
        )
        await callback.answer()
        return
        
    elif action == "position" and value == "open":
        # Open position selection
        await callback.message.edit_text(
            tr(user, "📍 Выберите позицию субтитров:", "📍 Choose subtitle position:"),
            reply_markup=get_subtitle_position_keyboard(user, callback_prefix="edit:position:", back_callback="edit:back")
        )
        await callback.answer()
        return
        
    elif action == "lang" and value == "open":
        # Open language selection
        await callback.message.edit_text(
            tr(user, "🌐 Выберите язык перевода:", "🌐 Choose translation language:"),
            reply_markup=get_language_selection(user, callback_prefix="edit:lang:", include_back=True, back_callback="edit:back")
        )
        await callback.answer()
        return
        
    elif action == "voice" and value == "open":
        # Open voice selection
        await callback.message.edit_text(
            tr(user, "🗣️ Выберите голос для озвучки:", "🗣️ Choose voice for TTS:"),
            reply_markup=get_voice_keyboard(user, callback_prefix="edit:voice:", back_callback="edit:back")
        )
        await callback.answer()
        return
        
    elif action == "save":
        # Save preset changes
        preset_id = int(value) if value else editing_preset_id
        
        options_for_preset = {
            "subtitles": current_opts.get("subtitles", True),
            "translate": current_opts.get("translate", False),
            "voiceover": current_opts.get("voiceover", False),
            "vertical": current_opts.get("vertical", False),
            "style": current_opts.get("style", "sub36o1"),
            "voice": current_opts.get("voice", "female"),
            "target_language": current_opts.get("target_language", "auto"),
            "position": current_opts.get("position", "bottom"),
        }
        
        await update_preset(user.id, preset_id, options=options_for_preset)
        await callback.answer(tr(user, "✅ Изменения сохранены!", "✅ Changes saved!"))
        
        # Clear editing state and return to presets list
        await state.clear()
        await cmd_presets(callback.message, user)
        return
        
    elif action == "back":
        # Return to preset editing menu - get current options from state
        data = await state.get_data()
        current_opts = data.get("current_preset_options", current_opts)
        await _show_preset_editing_interface(callback.message, user, current_opts, editing_preset_id, state)
        return
    else:
        await callback.answer()
        return
    
    # Update the preset editing interface
    await _show_preset_editing_interface(callback.message, user, current_opts, editing_preset_id, state)


# Handle additional preset editing callbacks (style, position, voice, language)
@router.callback_query(F.data.startswith("edit:lang:"))
async def handle_preset_edit_language_selection(callback: CallbackQuery, state: FSMContext, user, **kwargs):
    """Handle language selection in preset editing."""
    language = callback.data.split(":")[-1]
    
    # Get current editing preset ID and options from state
    data = await state.get_data()
    editing_preset_id = data.get("editing_preset_id")
    current_opts = data.get("current_preset_options", {})
    
    if not editing_preset_id:
        await callback.answer("❌ Ошибка: пресет не найден")
        return
    
    # Update the options in state, not global defaults
    current_opts["target_language"] = language
    current_opts["translate"] = True
    await state.update_data(current_preset_options=current_opts)
    
    lang_map = language_options()
    if language == "auto":
        label = tr(user, "авто", "auto")
    else:
        label = lang_map.get(language, language)
    
    await callback.answer(tr(user, f"Язык перевода: {label}", f"Translation language: {label}"))
    await _show_preset_editing_interface(callback.message, user, current_opts, editing_preset_id, state)


@router.callback_query(F.data.startswith("edit:position:"))
async def handle_preset_edit_position_selection(callback: CallbackQuery, state: FSMContext, user, **kwargs):
    """Handle position selection in preset editing."""
    position = callback.data.split(":")[-1]
    
    # Get current editing preset ID and options from state
    data = await state.get_data()
    editing_preset_id = data.get("editing_preset_id")
    current_opts = data.get("current_preset_options", {})
    
    if not editing_preset_id:
        await callback.answer("❌ Ошибка: пресет не найден")
        return
    
    if position in {"top", "middle", "bottom"}:
        # Update the options in state
        current_opts["position"] = position
        await state.update_data(current_preset_options=current_opts)
        
        labels = {
            "top": tr(user, "верх", "top"),
            "middle": tr(user, "центр", "middle"),
            "bottom": tr(user, "низ", "bottom"),
        }
        await callback.answer(tr(user, f"Позиция: {labels[position]}", f"Position: {labels[position]}"))
        await _show_preset_editing_interface(callback.message, user, current_opts, editing_preset_id, state)


@router.callback_query(F.data.startswith("edit:style:"))
async def handle_preset_edit_style_selection(callback: CallbackQuery, state: FSMContext, user, **kwargs):
    """Handle style selection in preset editing."""
    style_id = callback.data.split(":")[-1]
    
    # Get current editing preset ID and options from state
    data = await state.get_data()
    editing_preset_id = data.get("editing_preset_id")
    current_opts = data.get("current_preset_options", {})
    
    if not editing_preset_id:
        await callback.answer("❌ Ошибка: пресет не найден")
        return
    
    # Update the options in state
    current_opts["style"] = style_id
    await state.update_data(current_preset_options=current_opts)
    
    lang_code = resolve_language(user)
    style_name = get_style_display(style_id, lang_code)
    await callback.answer(tr(user, f"Стиль: {style_name}", f"Style: {style_name}"))
    await _show_preset_editing_interface(callback.message, user, current_opts, editing_preset_id, state)


@router.callback_query(F.data.startswith("edit:voice:"))
async def handle_preset_edit_voice_selection(callback: CallbackQuery, state: FSMContext, user, **kwargs):
    """Handle voice selection in preset editing."""
    voice = callback.data.split(":")[-1]
    
    # Get current editing preset ID and options from state
    data = await state.get_data()
    editing_preset_id = data.get("editing_preset_id")
    current_opts = data.get("current_preset_options", {})
    
    if not editing_preset_id:
        await callback.answer("❌ Ошибка: пресет не найден")
        return
    
    if voice in {"male", "female"}:
        # Update the options in state
        current_opts["voice"] = voice
        await state.update_data(current_preset_options=current_opts)
        
        labels = {
            "male": tr(user, "мужской", "male"),
            "female": tr(user, "женский", "female"),
        }
        await callback.answer(tr(user, f"Голос: {labels[voice]}", f"Voice: {labels[voice]}"))
        await _show_preset_editing_interface(callback.message, user, current_opts, editing_preset_id, state)


@router.callback_query(F.data == "edit:back")
async def handle_preset_edit_back(callback: CallbackQuery, state: FSMContext, user, **kwargs):
    """Handle back button in preset editing."""
    data = await state.get_data()
    editing_preset_id = data.get("editing_preset_id")
    if editing_preset_id:
        current_opts = data.get("current_preset_options", {})
        await _show_preset_editing_interface(callback.message, user, current_opts, editing_preset_id, state)


@router.callback_query(F.data.startswith("preset:rename:"))
async def cb_preset_rename(callback: CallbackQuery, state: FSMContext, user, **kwargs):
    preset_id = int(callback.data.split(":")[-1])
    preset = await get_preset(user.id, preset_id)
    if not preset:
        await callback.answer(tr(user, "Пресет не найден", "Preset not found"))
        return
    previous_state = await state.get_state()
    await state.update_data(preset_rename_id=preset_id, preset_previous_state=previous_state)
    await state.set_state(PresetEdit.renaming)
    await callback.message.answer(tr(user, "Введите новое название пресета:", "Send a new preset name:"))
    await callback.answer()


@router.message(PresetEdit.renaming)
async def preset_rename_input(message: Message, state: FSMContext, user, **kwargs):
    new_name = message.text.strip()
    if not new_name:
        await message.answer(tr(user, "Название не может быть пустым. Попробуйте ещё раз.", "Name cannot be empty. Try again."))
        return
    data = await state.get_data()
    preset_id = data.get("preset_rename_id")
    if preset_id is None:
        await message.answer(tr(user, "Что-то пошло не так. Повторите попытку.", "Something went wrong. Please try again."))
    else:
        await update_preset(user.id, preset_id, name=new_name)
        await message.answer(tr(user, "Название обновлено.", "Name updated."))
    prev_state = data.get("preset_previous_state")
    await state.update_data(preset_rename_id=None, preset_previous_state=None)
    if prev_state:
        await state.set_state(prev_state)
    else:
        await state.clear()
    await cmd_presets(message, user)


@router.callback_query(F.data == "preset:back")
async def cb_preset_back(callback: CallbackQuery, user, **kwargs):
    await callback.answer()
    await cmd_presets(callback.message, user)


@router.callback_query(F.data == "preset:new")
async def cb_preset_new(callback: CallbackQuery, user, **kwargs):
    await callback.answer(tr(user, "Создайте новый пресет через кнопку «Сохранить пресет» в опциях.", "Use “Save preset” inside the options screen to create a new preset."))
