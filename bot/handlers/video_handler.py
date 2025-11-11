"""Video processing handler."""
import logging
from aiogram import Router, F
from aiogram.filters import StateFilter
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from bot.keyboards import (
    get_processing_options,
    get_language_selection,
    get_cancel_keyboard,
    get_advanced_options,
    get_upsell_keyboard,
    get_subtitle_position_keyboard,
)
from bot.states import VideoProcessing
from bot.services.video_service import (
    validate_video_url,
    enqueue_video_task,
    check_user_limits,
    extract_url_preview,
)
from bot.services.options_service import get_default_options
from db.models import User
from config.constants import TIER_LIMITS
from config.settings import settings
from config.constants import UserTier
from redis.asyncio import Redis
from bot.i18n import t, tr, all_translations_for_key, language_options, resolve_language
from common.subtitle_styles import get_style_display
from common.subtitle_styles import get_style_display

UPLOAD_BUTTONS = list(all_translations_for_key("menu.upload"))

router = Router()
logger = logging.getLogger(__name__)


def _build_task_card_text(user: User, data: dict) -> str:
    """Build unified task card text including selected options."""
    input_type = data.get("input_type") or "file"
    title = "file" if input_type == "file" else data.get("input_url") or input_type
    duration = data.get("duration")
    dur_str = ""
    if duration:
        mm = duration // 60
        ss = duration % 60
        dur_str = f"{int(mm):02d}:{int(ss):02d}"
    tier_name = user.tier.value.upper()
    plan_line = tr(user, f"План: {tier_name}", f"Plan: {tier_name}")
    options = data.get("options", {})
    subs = "✅" if options.get("subtitles", True) else "❌"
    trn = "✅" if options.get("translate", False) else "❌"
    tts = "✅" if options.get("voiceover", False) else "❌"
    fmt = "9:16" if options.get("vertical", False) else tr(user, "исходный", "original")
    lang_code = resolve_language(user)
    style_name = get_style_display(options.get("style", "sub36o1"), lang_code)
    position_labels = {
        "top": tr(user, "верх", "top"),
        "middle": tr(user, "центр", "middle"),
        "bottom": tr(user, "низ", "bottom"),
    }
    position_label = position_labels.get(options.get("position", "bottom"), position_labels["bottom"])
    target_code = options.get("target_language", data.get("target_language", "auto"))
    if target_code == "auto":
        target_label = tr(user, "авто", "auto")
    else:
        target_label = language_options().get(target_code, target_code.upper())
    voice_label = tr(user, "женский", "female") if options.get("voice", "female") == "female" else tr(user, "мужской", "male")
    extra_ru = f"Стиль: {style_name} · Позиция: {position_label} · Язык: {target_label} · Голос: {voice_label}"
    extra_en = f"Style: {style_name} · Position: {position_label} · Language: {target_label} · Voice: {voice_label}"
    return tr(
        user,
        f"🎬 Источник: {('файл' if input_type=='file' else title)} · {dur_str or '—'}\n\n"
        f"Опции: субтитры {subs} · перевод {trn} · озвучка {tts} · формат {fmt}\n"
        f"{extra_ru}\n\n"
        f"{plan_line}",
        f"🎬 Source: {('file' if input_type=='file' else title)} · {dur_str or '—'}\n\n"
        f"Options: subtitles {subs} · translate {trn} · voiceover {tts} · format {fmt}\n"
        f"{extra_en}\n\n"
        f"{plan_line}",
    )

# Auto-capture media outside of the explicit flow: user can just drop a video/audio/document
@router.message(StateFilter(None), F.video | F.document | F.audio)
async def auto_handle_media(message: Message, state: FSMContext, user: User, db, **kwargs):
    """Automatically accept user-uploaded media and start processing with default options.

    Default options: subtitles ON, translate OFF, voiceover OFF, vertical OFF.
    """
    # Check user limits (respects DISABLE_LIMITS)
    can_process, error_msg = await check_user_limits(db, user)
    if not can_process:
        await message.answer(f"{t(user,'limits.daily')}\n\n{t(user,'upsell.free')}", reply_markup=get_upsell_keyboard(user))
        return

    # Extract file info
    if message.video:
        file_id = message.video.file_id
        duration = message.video.duration
        file_size = message.video.file_size
    elif message.document:
        file_id = message.document.file_id
        duration = None
        file_size = message.document.file_size
    elif message.audio:
        file_id = message.audio.file_id
        duration = message.audio.duration
        file_size = message.audio.file_size
    else:
        await message.answer(tr(user, "❌ Неподдерживаемый тип файла", "❌ Unsupported file type"))
        return

    # Prepare data similar to FSM flow, with sane defaults
    data = {
        "input_type": "file",
        "file_id": file_id,
        "duration": duration,
        "options": await get_default_options(user.id),
        "target_language": (await get_default_options(user.id)).get("target_language", "auto"),
    }
    opts = data["options"]
    lang_code = resolve_language(user)
    style_name = get_style_display(opts.get("style", "sub36o1"), lang_code)
    position_label = {
        "top": tr(user, "верх", "top"),
        "middle": tr(user, "центр", "middle"),
        "bottom": tr(user, "низ", "bottom"),
    }.get(opts.get("position", "bottom"), tr(user, "низ", "bottom"))
    subs_text = tr(user, "субтитры вкл", "subtitles on") if opts.get("subtitles", True) else tr(user, "субтитры выкл", "subtitles off")
    if opts.get("translate", False):
        target_code = opts.get("target_language", "auto")
        target_label = tr(user, "авто", "auto") if target_code == "auto" else language_options().get(target_code, target_code)
        translate_text = tr(user, f"перевод → {target_label}", f"translate → {target_label}")
    else:
        translate_text = tr(user, "перевод выкл", "translate off")
    if opts.get("voiceover", False):
        voice = opts.get("voice", "female")
        voice_label = tr(user, "женский", "female") if voice == "female" else tr(user, "мужской", "male")
        voice_text = tr(user, f"озвучка → {voice_label}", f"voiceover → {voice_label}")
    else:
        voice_text = tr(user, "озвучка выкл", "voiceover off")
    format_text = tr(user, "формат 9:16" if opts.get("vertical") else "формат исходный", "format 9:16" if opts.get("vertical") else "format original")

    try:
        task = await enqueue_video_task(db, user, data)
        await message.answer(
            tr(
                user,
                "✅ Файл получен и поставлен в очередь!\n\n"
                f"Задача #{task.id}. ⏳ Обработка началась.\n"
                f"{subs_text} · {translate_text} · {voice_text} · {format_text}\n"
                f"Стиль: {style_name} · Позиция: {position_label}",
                "✅ File received and queued!\n\n"
                f"Task #{task.id}. ⏳ Processing started.\n"
                f"{subs_text} · {translate_text} · {voice_text} · {format_text}\n"
                f"Style: {style_name} · Position: {position_label}",
            )
        )
    except Exception as e:
        logger.error(f"Error enqueueing task from auto media: {e}")
        await message.answer(
            tr(
                user,
                f"❌ Ошибка при создании задачи: {str(e)}\n\nПопробуйте позже или обратитесь в поддержку.",
                f"❌ Failed to create task: {str(e)}\n\nPlease try again later or contact support.",
            )
        )

@router.message(F.text.in_(UPLOAD_BUTTONS))
async def start_preset_upload(message: Message, state: FSMContext, user: User, **kwargs):
    """Start preset-based upload flow."""
    from bot.services.preset_service import list_presets
    from bot.keyboards import get_preset_selection_keyboard
    
    # Get user's presets
    presets = await list_presets(user.id)
    
    if not presets:
        # No presets available, suggest creating one
        await message.answer(
            tr(
                user,
                "📋 У вас пока нет сохраненных пресетов.\n\nИспользуйте кнопку \"✨ Создать пресет\" для создания первого пресета с вашими настройками.",
                "📋 You don't have any saved presets yet.\n\nUse the \"✨ Create preset\" button to create your first preset with your settings.",
            )
        )
        return
    
    # Show preset selection with instructions
    await state.set_state(VideoProcessing.selecting_preset)
    await message.answer(
        t(user, "preset.upload.instruction"),
        reply_markup=get_preset_selection_keyboard(user, presets)
    )


@router.message(VideoProcessing.waiting_for_video, F.video | F.document | F.audio)
async def handle_video_file(message: Message, state: FSMContext, user: User, db, **kwargs):
    """Handle video file upload."""
    # Check user limits
    can_process, error_msg = await check_user_limits(db, user)
    if not can_process:
        await message.answer(f"{t(user,'limits.daily')}\n\n{t(user,'upsell.free')}", reply_markup=get_upsell_keyboard(user))
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
        await message.answer(tr(user, "❌ Неподдерживаемый тип файла", "❌ Unsupported file type"))
        return
    
    # Check duration limit
    tier_limits = TIER_LIMITS[user.tier]
    if not getattr(settings, "DISABLE_LIMITS", False):
        if duration and duration > tier_limits["max_duration"]:
            await message.answer(
                tr(
                    user,
                    "Этот ролик длиннее лимита Free. Оформи PRO для до 10 мин без водяного знака.",
                    "This video exceeds the Free limit. Upgrade to PRO for up to 10 minutes without watermark.",
                ),
                reply_markup=get_upsell_keyboard(user),
            )
            await state.clear()
            return
    
    # Get options from selected preset or defaults
    data = await state.get_data()
    selected_preset = data.get("selected_preset")
    
    if selected_preset:
        # Use preset options
        options = selected_preset.get("options", {})
        target_language = options.get("target_language", "auto")
    else:
        # Use default options
        options = await get_default_options(user.id)
        target_language = options.get("target_language", "auto")
    
    # Save to state
    await state.update_data(
        input_type="file",
        file_id=file_id,
        file_size=file_size,
        duration=duration,
        options=options,
        target_language=target_language,
    )
    
    # Show task card
    tier_name = user.tier.value.upper()
    plan_line = tr(user, f"План: {tier_name}", f"Plan: {tier_name}")
    dur_str = ""
    if duration:
        mm = duration // 60
        ss = duration % 60
        dur_str = f"{int(mm):02d}:{int(ss):02d}"
    card = _build_task_card_text(user, await state.get_data())
    
    if selected_preset:
        # For preset upload - show preset info and start/cancel buttons only
        preset_name = selected_preset.get("name", "Unnamed")
        preset_options = selected_preset.get("options", {})
        
        # Build preset info text
        preset_info = f"🎯 Пресет: {preset_name}\n\n"
        preset_info += f"• Субтитры: {'✅' if preset_options.get('subtitles', True) else '❌'}\n"
        preset_info += f"• Перевод: {'✅' if preset_options.get('translate', False) else '❌'}\n"
        preset_info += f"• Озвучка: {'✅' if preset_options.get('voiceover', False) else '❌'}\n"
        preset_info += f"• Формат: {'9:16' if preset_options.get('vertical', False) else 'исходный'}\n"
        
        if preset_options.get('translate'):
            lang_map = language_options()
            target_lang = preset_options.get('target_language', 'auto')
            lang_label = lang_map.get(target_lang, target_lang) if target_lang != 'auto' else tr(user, "авто", "auto")
            preset_info += f"• Язык: {lang_label}\n"
        
        if preset_options.get('voiceover'):
            voice_label = tr(user, "мужской", "male") if preset_options.get('voice') == 'male' else tr(user, "женский", "female")
            preset_info += f"• Голос: {voice_label}\n"
        
        preset_info += f"\n{card}"
        
        # Show simple start/cancel keyboard
        from bot.keyboards import InlineKeyboardBuilder
        builder = InlineKeyboardBuilder()
        builder.button(text="▶️ Запустить", callback_data="start_processing")
        builder.button(text="❌ Отменить", callback_data="cancel_processing")
        builder.adjust(2)
        
        await message.answer(preset_info, reply_markup=builder.as_markup())
        await state.set_state(VideoProcessing.confirming_preset)
    else:
        # For regular upload - show options interface
        await message.answer(card, reply_markup=get_processing_options(user, user.tier))
        await state.set_state(VideoProcessing.selecting_options)


@router.message(VideoProcessing.waiting_for_video, F.text)
async def handle_video_url(message: Message, state: FSMContext, user: User, db, **kwargs):
    """Handle video URL."""
    # Check user limits
    can_process, error_msg = await check_user_limits(db, user)
    if not can_process:
        await message.answer(f"{t(user,'limits.daily')}\n\n{t(user,'upsell.free')}", reply_markup=get_upsell_keyboard(user))
        await state.clear()
        return
    
    url = message.text.strip()
    
    # Validate URL
    is_valid, source = validate_video_url(url)
    if not is_valid:
        await message.answer(
            tr(
                user,
                "❌ Неверная ссылка. Поддерживаются:\n• YouTube\n• TikTok\n• Instagram",
                "❌ Invalid link. Supported:\n• YouTube\n• TikTok\n• Instagram",
            )
        )
        return
    
    # Extract preview
    preview = extract_url_preview(url)
    title = preview.get("title") or source
    duration = preview.get("duration")
    
    # Save to state
    await state.update_data(
        input_type=source,
        input_url=url,
        duration=duration,
        options=await get_default_options(user.id),
    )
    
    # Show task card with preview
    dur_str = ""
    if duration:
        mm = duration // 60
        ss = duration % 60
        dur_str = f"{int(mm):02d}:{int(ss):02d}"
    tier_name = user.tier.value.upper()
    plan_line = tr(user, f"План: {tier_name}", f"Plan: {tier_name}")
    card = _build_task_card_text(user, await state.get_data())
    await message.answer(card, reply_markup=get_processing_options(user, user.tier))
    await state.set_state(VideoProcessing.selecting_options)


@router.callback_query(VideoProcessing.selecting_options, F.data.startswith("opt:"))
async def toggle_option(callback: CallbackQuery, state: FSMContext, user: User, **kwargs):
    """Toggle processing option."""
    data = await state.get_data()
    options = data.get("options", {})
    
    payload = callback.data.split(":")[1:]
    # General schema: opt:<key>[:<val>[:<extra>]]
    if len(payload) >= 1:
        key = payload[0]
        val = payload[1] if len(payload) > 1 else None
        if key == "subs":
            options["subtitles"] = not options.get("subtitles", True)
            await callback.answer(tr(user, f"{'Вкл' if options['subtitles'] else 'Выкл'}: субтитры", f"{'On' if options['subtitles'] else 'Off'}: subtitles"))
        elif key in ("translate", "translation"):
            options["translate"] = not options.get("translate", False)
            await callback.answer(tr(user, f"{'Вкл' if options['translate'] else 'Выкл'}: перевод", f"{'On' if options['translate'] else 'Off'}: translate"))
        elif key == "tts":
            options["voiceover"] = not options.get("voiceover", False)
            await callback.answer(tr(user, f"{'Вкл' if options['voiceover'] else 'Выкл'}: озвучка", f"{'On' if options['voiceover'] else 'Off'}: voiceover"))
        elif key == "format":
            options["vertical"] = (val == "916") if val in ("916", "src") else not options.get("vertical", False)
            await callback.answer(tr(user, f"Формат: {'9:16' if options['vertical'] else 'исходный'}", f"Format: {'9:16' if options['vertical'] else 'original'}"))
        elif key == "more":
            watermark_forced = TIER_LIMITS[user.tier]["watermark"]
            await callback.message.edit_text(tr(user, "⚙️ Расширенные опции", "⚙️ Advanced options"), reply_markup=get_advanced_options(user, user.tier, watermark_forced))
            await callback.answer()
            return
        elif key == "style":
            if val == "open":
                from bot.keyboards import get_style_presets_keyboard, style_help_text
                await callback.message.edit_text(style_help_text(user), reply_markup=get_style_presets_keyboard(user))
                await callback.answer()
                return
            elif val == "preset":
                preset_id = payload[2] if len(payload) > 2 else "sub36o1"
                options["style"] = preset_id
                await callback.answer(tr(user, "Стиль применён", "Style applied"))
            elif val == "custom":
                options["style"] = "custom"
                await callback.answer(tr(user, "Кастомный стиль выбран", "Custom style selected"))
        elif key == "voice":
            if val == "open":
                from bot.keyboards import get_voice_keyboard
                await callback.message.edit_text(tr(user, "🗣️ Выберите голос", "🗣️ Choose voice"), reply_markup=get_voice_keyboard(user))
                await callback.answer()
                return
            else:
                options["voice"] = val
                options["voiceover"] = True
                voice_names = {
                    "male": tr(user, "мужской", "male"),
                    "female": tr(user, "женский", "female"),
                }
                label = voice_names.get(val, val)
                await callback.answer(tr(user, f"Голос: {label} · озвучка вкл", f"Voice: {label} · TTS on"))
        elif key == "position":
            if val == "open":
                await callback.message.edit_text(
                    tr(user, "📍 Расположение субтитров", "📍 Subtitle placement"),
                    reply_markup=get_subtitle_position_keyboard(user),
                )
                await callback.answer()
                return
            elif val in {"top", "middle", "bottom"}:
                labels = {
                    "top": tr(user, "верх", "top"),
                    "middle": tr(user, "центр", "middle"),
                    "bottom": tr(user, "низ", "bottom"),
                }
                options["position"] = val
                await callback.answer(tr(user, f"Позиция: {labels[val]}", f"Position: {labels[val]}"))
        elif key == "lang":
            if val == "open":
                current_code = options.get("target_language", "auto")
                await callback.message.edit_text(
                    tr(user, "🌐 Язык перевода", "🌐 Translation language"),
                    reply_markup=get_language_selection(
                        user,
                        callback_prefix="opt:lang:",
                        include_back=True,
                        back_callback="opt:back",
                        current_code=current_code,
                    ),
                )
                await callback.answer()
                return
            elif val:
                if val == "auto":
                    label = tr(user, "Автоопределение", "Auto-detect")
                else:
                    label = language_options().get(val, val.upper())
                options["target_language"] = val
                options["translate"] = True
                await state.update_data(options=options, target_language=val)
                await callback.message.edit_text(
                    tr(user, "🌐 Язык перевода", "🌐 Translation language"),
                    reply_markup=get_language_selection(
                        user,
                        callback_prefix="opt:lang:",
                        include_back=True,
                        back_callback="opt:back",
                        current_code=val,
                    ),
                )
                await callback.answer(tr(user, f"Язык: {label} · перевод включён", f"Language: {label} · translate on"))
                return
        elif key == "watermark":
            await callback.answer(
                tr(
                    user,
                    "Водяной знак доступен только в Free" if TIER_LIMITS[user.tier]["watermark"] else "Тумблер недоступен",
                    "Watermark is fixed in Free plan" if TIER_LIMITS[user.tier]["watermark"] else "Toggle unavailable",
                )
            )
            return
        elif key == "back":
            current_text = callback.message.text or ""
            if current_text.startswith(("🎚️", "🗣️", "🌐")):
                watermark_forced = TIER_LIMITS[user.tier]["watermark"]
                await callback.message.edit_text(
                    tr(user, "⚙️ Расширенные опции", "⚙️ Advanced options"),
                    reply_markup=get_advanced_options(user, user.tier, watermark_forced),
                )
            elif current_text.startswith("⚙️"):
                card = _build_task_card_text(user, data)
                await callback.message.edit_text(card, reply_markup=get_processing_options(user, user.tier))
            else:
                card = _build_task_card_text(user, data)
                await callback.message.edit_text(card, reply_markup=get_processing_options(user, user.tier))
            await callback.answer()
            return
        elif key == "preset" and val == "save":
            # Save current options as preset with auto-name
            from bot.services.preset_service import save_preset, list_presets
            options_for_preset = {
                "subtitles": options.get("subtitles", True),
                "translate": options.get("translate", False),
                "voiceover": options.get("voiceover", False),
                "vertical": options.get("vertical", False),
                "style": options.get("style", "sub36o1"),
                "voice": options.get("voice", "female"),
                "position": options.get("position", "bottom"),
                "target_language": options.get("target_language", data.get("target_language", "auto")),
            }
            presets = await list_presets(user.id)
            name = f"Preset {len(presets) + 1}"
            await save_preset(user.id, name, options_for_preset)
            await callback.answer(tr(user, "Пресет сохранён", "Preset saved"))
    await state.update_data(
        options=options,
        target_language=options.get("target_language", data.get("target_language", "auto")),
    )
    # Refresh card to reflect changes
    try:
        card = _build_task_card_text(user, await state.get_data())
        await callback.message.edit_text(card, reply_markup=get_processing_options(user, user.tier))
    except Exception:
        pass


@router.callback_query(VideoProcessing.selecting_options, F.data == "job:start")
async def start_processing(callback: CallbackQuery, state: FSMContext, user: User, db, **kwargs):
    """Start video processing."""
    data = await state.get_data()
    options = data.get("options", {})
    data["options"] = options
    data["target_language"] = options.get("target_language", data.get("target_language", "auto"))
    await state.update_data(target_language=data["target_language"])
    lang_code = resolve_language(user)
    style_name = get_style_display(options.get("style", "sub36o1"), lang_code)
    position_label = {
        "top": tr(user, "верх", "top"),
        "middle": tr(user, "центр", "middle"),
        "bottom": tr(user, "низ", "bottom"),
    }.get(options.get("position", "bottom"), tr(user, "низ", "bottom"))
    subs_text = tr(user, "субтитры ✅", "subtitles ✅") if options.get("subtitles") else tr(user, "субтитры ❌", "subtitles ❌")
    if options.get("translate"):
        tgt_code = options.get("target_language", "auto")
        tgt_label = tr(user, "авто", "auto") if tgt_code == "auto" else language_options().get(tgt_code, tgt_code)
        translate_text = tr(user, f"перевод → {tgt_label}", f"translate → {tgt_label}")
    else:
        translate_text = tr(user, "перевод выкл", "translate off")
    if options.get("voiceover"):
        voice = options.get("voice", "female")
        voice_label = tr(user, "женский", "female") if voice == "female" else tr(user, "мужской", "male")
        voice_text = tr(user, f"озвучка → {voice_label}", f"voiceover → {voice_label}")
    else:
        voice_text = tr(user, "озвучка выкл", "voiceover off")
    format_text = tr(user, "формат 9:16" if options.get("vertical") else "формат исходный", "format 9:16" if options.get("vertical") else "format original")
    
    # Enqueue task
    try:
        task = await enqueue_video_task(db, user, data)
        # Create unified status message and store mapping in Redis
        status_text = tr(
            user,
            f"🚀 Задача #{task.id} создана\n\n"
            f"{subs_text} · {translate_text} · {voice_text} · {format_text}\n"
            f"Стиль: {style_name} · Позиция: {position_label}\n\n"
            "Оценка времени: ~1–2 мин",
            f"🚀 Task #{task.id} created\n\n"
            f"{subs_text} · {translate_text} · {voice_text} · {format_text}\n"
            f"Style: {style_name} · Position: {position_label}\n\n"
            "Estimated time: ~1–2 min",
        )
        sent = await callback.message.edit_text(status_text)
        try:
            r = Redis.from_url(settings.redis_url)
            await r.hset(f"task:{task.id}:status_msg", mapping={"chat_id": sent.chat.id, "message_id": sent.message_id})
            await r.expire(f"task:{task.id}:status_msg", 60 * 60 * 24)
        except Exception:
            pass
        
        await state.clear()
    except Exception as e:
        logger.error(f"Error enqueueing task: {e}")
        await callback.message.edit_text(
            f"❌ Ошибка при создании задачи: {str(e)}\n\n"
            f"Попробуйте позже или обратитесь в поддержку."
        )
        await state.clear()
    
    await callback.answer()


@router.callback_query(VideoProcessing.selecting_language, F.data.startswith("opt:lang:"))
async def select_language(callback: CallbackQuery, state: FSMContext, user: User, db, **kwargs):
    """Select target language."""
    language = callback.data.split(":")[-1]
    
    # Update options in state
    data = await state.get_data()
    options = data.get("options", {})
    options["target_language"] = language
    options["translate"] = True
    await state.update_data(options=options, target_language=language)
    data = await state.get_data()
    
    # Enqueue task
    try:
        task = await enqueue_video_task(db, user, data)
        
        await callback.message.edit_text(
            tr(
                user,
            f"✅ Задача #{task.id} поставлена в очередь!\n\n"
                "⏳ Обработка может занять несколько минут.\n"
                "Мы отправим вам результат, когда обработка завершится.",
                f"✅ Task #{task.id} queued!\n\n"
                "⏳ Processing may take a few minutes.\n"
                "We will send the result when it’s done.",
            ),
            reply_markup=None
        )
        
        await state.clear()
    except Exception as e:
        logger.error(f"Error enqueueing task: {e}")
        await callback.message.edit_text(
            tr(
                user,
            f"❌ Ошибка при создании задачи: {str(e)}\n\n"
                "Попробуйте позже или обратитесь в поддержку.",
                f"❌ Failed to create task: {str(e)}\n\n"
                "Try again later or contact support.",
            )
        )
        await state.clear()
    
    await callback.answer()


@router.callback_query(F.data == "job:cancel")
async def cancel_processing(callback: CallbackQuery, state: FSMContext, user: User, **kwargs):
    """Cancel processing."""
    await state.clear()
    await callback.message.edit_text(tr(user, "❌ Операция отменена.", "❌ Operation cancelled."))
    await callback.answer()


@router.callback_query(F.data == "opt:back")
async def generic_back(callback: CallbackQuery, state: FSMContext, user: User, **kwargs):
    """Handle back button from any options sub-screen."""
    try:
        data = await state.get_data()
        if not data:
            from bot.services.options_service import get_default_options
            defaults = await get_default_options(user.id)
            data = {"input_type": "file", "options": defaults}
        card = _build_task_card_text(user, data)
        await callback.message.edit_text(card, reply_markup=get_processing_options(user, user.tier))
    except Exception:
        pass
    finally:
        await callback.answer()


# -------- Preset selection handlers --------

@router.callback_query(VideoProcessing.selecting_preset, F.data.startswith("preset:select:"))
async def handle_preset_selection(callback: CallbackQuery, state: FSMContext, user: User, **kwargs):
    """Handle preset selection for upload."""
    from bot.services.preset_service import get_preset
    
    preset_id = int(callback.data.split(":")[-1])
    preset = await get_preset(user.id, preset_id)
    
    if not preset:
        await callback.answer(tr(user, "Пресет не найден", "Preset not found"))
        return
    
    # Store selected preset in state
    await state.update_data(selected_preset=preset)
    await state.set_state(VideoProcessing.waiting_for_video)
    
    # Show upload instructions with selected preset info
    preset_name = preset.get("name", "Unnamed")
    await callback.message.edit_text(
        tr(
            user,
            f"🎯 Выбран пресет: {preset_name}\n\n📤 Теперь отправьте:\n• Видео файл\n• Аудио файл\n• Ссылку на YouTube/TikTok/Instagram\n\nВидео будет обработано с настройками выбранного пресета.",
            f"🎯 Selected preset: {preset_name}\n\n📤 Now send:\n• Video file\n• Audio file\n• YouTube/TikTok/Instagram link\n\nVideo will be processed with the selected preset settings.",
        ),
        reply_markup=get_cancel_keyboard(user)
    )
    await callback.answer()


@router.callback_query(VideoProcessing.selecting_preset, F.data == "preset:cancel")
async def handle_preset_cancel(callback: CallbackQuery, state: FSMContext, user: User, **kwargs):
    """Cancel preset selection."""
    await state.clear()
    await callback.message.edit_text(
        tr(user, "❌ Выбор пресета отменён.", "❌ Preset selection cancelled."),
        reply_markup=None
    )
    await callback.answer()


# -------- Preset confirmation handlers --------

@router.callback_query(VideoProcessing.confirming_preset, F.data == "start_processing")
async def handle_start_preset_processing(callback: CallbackQuery, state: FSMContext, user: User, db, **kwargs):
    """Start processing with selected preset."""
    from datetime import datetime
    
    data = await state.get_data()
    
    # Enqueue video task
    await enqueue_video_task(db, user, data)
    
    # Update user stats
    user.tasks_today += 1
    user.last_task_date = datetime.utcnow()
    await db.commit()
    
    await callback.message.edit_text(
        tr(user, "✅ Задача добавлена в очередь обработки!", "✅ Task added to processing queue!")
    )
    await state.clear()
    await callback.answer()


@router.callback_query(VideoProcessing.confirming_preset, F.data == "cancel_processing")
async def handle_cancel_preset_processing(callback: CallbackQuery, state: FSMContext, user: User, **kwargs):
    """Cancel processing with preset."""
    await state.clear()
    await callback.message.edit_text(
        tr(user, "❌ Обработка отменена", "❌ Processing cancelled")
    )
    await callback.answer()
