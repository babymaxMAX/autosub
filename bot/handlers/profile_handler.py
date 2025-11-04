"""Profile handler."""
from datetime import datetime
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message
from db.models import User
from config.constants import TIER_LIMITS, UserTier

router = Router()


@router.message(Command("profile"))
@router.message(F.text == "👤 Профиль")
async def cmd_profile(message: Message, user: User, **kwargs):
    """Handle /profile command."""
    tier_info = TIER_LIMITS[user.tier]
    
    # Format tier expiration
    if user.tier_expires_at:
        expires = user.tier_expires_at.strftime("%d.%m.%Y")
        tier_status = f"до {expires}"
    else:
        tier_status = "бессрочно" if user.tier == UserTier.FREE else "не активна"
    
    profile_text = f"""
👤 <b>Ваш профиль</b>

<b>Тариф:</b> {user.tier.value.upper()} ({tier_status})
<b>Задач сегодня:</b> {user.tasks_today}/{tier_info['daily_tasks']}
<b>Всего обработано:</b> {user.tasks_total}

<b>Лимиты тарифа:</b>
• Макс. длительность: {tier_info['max_duration']}сек
• Качество: до {tier_info['max_quality']}
• Водяной знак: {'Да' if tier_info['watermark'] else 'Нет'}
• Задач в день: {tier_info['daily_tasks']}

💎 Используйте /pricing для улучшения тарифа
"""
    
    await message.answer(profile_text)

