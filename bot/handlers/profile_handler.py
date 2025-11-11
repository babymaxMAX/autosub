"""Profile handler."""
from datetime import datetime
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message
from db.models import User
from config.constants import TIER_LIMITS, UserTier
from bot.i18n import t, all_translations_for_key

router = Router()
PROFILE_BUTTONS = list(all_translations_for_key("profile.button"))


@router.message(Command("profile"))
@router.message(F.text.in_(PROFILE_BUTTONS))
async def cmd_profile(message: Message, user: User, **kwargs):
    """Handle /profile command."""
    tier_info = TIER_LIMITS[user.tier]

    if user.tier_expires_at:
        expires = user.tier_expires_at.strftime("%d.%m.%Y")
        tier_status = t(user, "profile.status_until", date=expires)
    else:
        tier_status = (
            t(user, "profile.status_permanent")
            if user.tier == UserTier.FREE
            else t(user, "profile.status_inactive")
        )

    watermark_text = (
        t(user, "profile.boolean_yes")
        if tier_info["watermark"]
        else t(user, "profile.boolean_no")
    )

    profile_text = t(
        user,
        "profile.summary",
        tier=user.tier.value.upper(),
        status=tier_status,
        today=user.tasks_today,
        daily=tier_info["daily_tasks"],
        total=user.tasks_total,
        max_duration=tier_info["max_duration"],
        max_quality=tier_info["max_quality"],
        watermark=watermark_text,
    )

    await message.answer(profile_text)

