"""Pricing and subscription handler."""
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from bot.keyboards import get_pricing_keyboard, get_onetime_pricing_keyboard
from bot.services.payment_service import create_payment_link
from bot.states import Payment
from db.models import User
from config.constants import UserTier, PRICING

router = Router()


@router.message(Command("pricing"))
@router.message(F.text == "💎 Тарифы")
async def cmd_pricing(message: Message, **kwargs):
    """Handle /pricing command."""
    pricing_text = """
💎 <b>Доступные тарифы</b>

<b>🆓 FREE (текущий)</b>
• Видео до 60 секунд
• До 720p
• 3 задачи в день
• С водяным знаком

<b>💎 PRO</b>
• Видео до 10 минут
• До 1080p
• 50 задач в день
• Без водяного знака
• Приоритетная обработка
• Перевод на 50+ языков
<b>299₽/месяц</b> или <b>2990₽/год</b>

<b>⭐ CREATOR</b>
• Видео до 30 минут
• До 1080p
• 200 задач в день
• Озвучка субтитров
• Стили субтитров
• Приоритетная обработка
<b>599₽/месяц</b> или <b>5990₽/год</b>

<b>🎬 Разовая обработка</b>
• Без подписки
• 29-59₽ за видео

Выберите подходящий тариф:
"""
    await message.answer(pricing_text, reply_markup=get_pricing_keyboard())


@router.callback_query(F.data == "buy_onetime")
async def buy_onetime(callback: CallbackQuery, **kwargs):
    """Handle one-time purchase."""
    await callback.message.edit_text(
        """
🎬 <b>Разовая обработка</b>

Выберите длительность видео:
• До 3 минут - 29₽
• До 10 минут - 49₽
• До 30 минут - 59₽

После оплаты вы сможете обработать одно видео выбранной длительности.
""",
        reply_markup=get_onetime_pricing_keyboard()
    )
    await callback.answer()


@router.callback_query(F.data == "back_to_pricing")
async def back_to_pricing(callback: CallbackQuery, **kwargs):
    """Go back to pricing menu."""
    await cmd_pricing(callback.message)
    await callback.answer()


@router.callback_query(F.data.startswith("buy_"))
async def process_purchase(callback: CallbackQuery, state: FSMContext, user: User, **kwargs):
    """Process purchase."""
    data = callback.data
    
    # Parse purchase type
    if data == "buy_pro_monthly":
        tier = UserTier.PRO
        period = "monthly"
        amount = PRICING[UserTier.PRO]["monthly"]
        description = "PRO подписка на 1 месяц"
    elif data == "buy_pro_yearly":
        tier = UserTier.PRO
        period = "yearly"
        amount = PRICING[UserTier.PRO]["yearly"]
        description = "PRO подписка на 1 год"
    elif data == "buy_creator_monthly":
        tier = UserTier.CREATOR
        period = "monthly"
        amount = PRICING[UserTier.CREATOR]["monthly"]
        description = "CREATOR подписка на 1 месяц"
    elif data == "buy_creator_yearly":
        tier = UserTier.CREATOR
        period = "yearly"
        amount = PRICING[UserTier.CREATOR]["yearly"]
        description = "CREATOR подписка на 1 год"
    elif data == "buy_onetime_short":
        tier = None
        period = "onetime"
        amount = PRICING["one_time_short"]
        description = "Разовая обработка (до 3 мин)"
    elif data == "buy_onetime_medium":
        tier = None
        period = "onetime"
        amount = PRICING["one_time_medium"]
        description = "Разовая обработка (до 10 мин)"
    elif data == "buy_onetime_long":
        tier = None
        period = "onetime"
        amount = PRICING["one_time_long"]
        description = "Разовая обработка (до 30 мин)"
    else:
        await callback.answer("Неизвестный тип покупки")
        return
    
    # Create payment link
    try:
        payment_url = await create_payment_link(
            user_id=user.id,
            amount=amount,
            description=description,
            tier=tier,
            period=period,
        )
        
        await callback.message.answer(
            f"💳 <b>Оплата: {description}</b>\n\n"
            f"Сумма: {amount}₽\n\n"
            f"Перейдите по ссылке для оплаты:\n{payment_url}\n\n"
            f"После успешной оплаты ваш тариф будет автоматически активирован."
        )
        
        await state.set_state(Payment.waiting_for_payment)
    except Exception as e:
        await callback.message.answer(
            f"❌ Ошибка при создании платежа: {str(e)}\n\n"
            f"Попробуйте позже или обратитесь в поддержку."
        )
    
    await callback.answer()

