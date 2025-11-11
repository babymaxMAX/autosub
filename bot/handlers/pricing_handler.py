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
from bot.i18n import tr, all_translations_for_key

router = Router()
PLAN_BUTTONS = list(all_translations_for_key("menu.plan"))


@router.message(Command("pricing"))
@router.message(Command("plan"))
@router.message(F.text.in_(PLAN_BUTTONS))
async def cmd_pricing(message: Message, user: User, **kwargs):
    """Handle /pricing command."""
    pricing_text = tr(
        user,
        "💳 Тариф\n\nFree - до 60 сек, 720p, 3 задачи/день, водяной знак\nPRO 199 ₽/мес - до 10 мин, 1080p, без водяного знака, приоритет\nCREATOR 499 ₽/мес - до 30 мин, стили пресетов, озвучка",
        "💳 Plan\n\nFree - up to 60 sec, 720p, 3 tasks/day, watermark\nPRO 199 ₽/mo - up to 10 min, 1080p, no watermark, priority\nCREATOR 499 ₽/mo - up to 30 min, presets & voiceover",
    )
    await message.answer(pricing_text, reply_markup=get_pricing_keyboard(user))


@router.callback_query(F.data == "buy_onetime")
async def buy_onetime(callback: CallbackQuery, user: User, **kwargs):
    """Handle one-time purchase."""
    await callback.message.edit_text(
        tr(
            user,
            "🎬 <b>Разовая обработка</b>\n\nВыберите длительность видео:\n• До 3 минут - 29₽\n• До 10 минут - 49₽\n• До 30 минут - 59₽\n\nПосле оплаты вы сможете обработать одно видео выбранной длительности.",
            "🎬 <b>One-time processing</b>\n\nChoose video length:\n• Up to 3 min - 29₽\n• Up to 10 min - 49₽\n• Up to 30 min - 59₽\n\nAfter payment you can process one video with the selected duration.",
        ),
        reply_markup=get_onetime_pricing_keyboard(user)
    )
    await callback.answer()


@router.callback_query(F.data == "back_to_pricing")
async def back_to_pricing(callback: CallbackQuery, user: User, **kwargs):
    """Go back to pricing menu."""
    await cmd_pricing(callback.message, user=user)
    await callback.answer()


@router.callback_query(F.data == "plan:buy:pro")
async def plan_buy_pro(callback: CallbackQuery, state: FSMContext, user: User, **kwargs):
    """Create PRO monthly invoice quickly."""
    from config.constants import PRICING
    amount = PRICING[UserTier.PRO]["monthly"]
    description = "PRO подписка на 1 месяц"
    try:
        payment_url = await create_payment_link(
            user_id=user.id,
            amount=amount,
            description=description,
            tier=UserTier.PRO,
            period="monthly",
        )
        await callback.message.answer(
            tr(
                user,
                f"💳 Оплата PRO (199₽/мес)\nСсылка для оплаты:\n{payment_url}\n\nОжидаем оплату… Нажмите «🔄 Проверить статус» после оплаты.",
                f"💳 PRO payment (199₽/mo)\nPayment link:\n{payment_url}\n\nAwaiting payment… Press “🔄 Check status” after paying.",
            )
        )
        await state.set_state(Payment.waiting_for_payment)
    except Exception as e:
        await callback.message.answer(tr(user, f"❌ Ошибка при создании платежа: {str(e)}", f"❌ Failed to create payment: {str(e)}"))
    await callback.answer()


@router.callback_query(F.data == "plan:buy:creator")
async def plan_buy_creator(callback: CallbackQuery, state: FSMContext, user: User, **kwargs):
    """Create CREATOR monthly invoice quickly."""
    from config.constants import PRICING
    amount = PRICING[UserTier.CREATOR]["monthly"]
    description = "CREATOR подписка на 1 месяц"
    try:
        payment_url = await create_payment_link(
            user_id=user.id,
            amount=amount,
            description=description,
            tier=UserTier.CREATOR,
            period="monthly",
        )
        await callback.message.answer(
            tr(
                user,
                f"💳 Оплата CREATOR (499₽/мес)\nСсылка для оплаты:\n{payment_url}\n\nОжидаем оплату… Нажмите «🔄 Проверить статус» после оплаты.",
                f"💳 CREATOR payment (499₽/mo)\nPayment link:\n{payment_url}\n\nAwaiting payment… Press “🔄 Check status” after paying.",
            )
        )
        await state.set_state(Payment.waiting_for_payment)
    except Exception as e:
        await callback.message.answer(tr(user, f"❌ Ошибка при создании платежа: {str(e)}", f"❌ Failed to create payment: {str(e)}"))
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
        await callback.answer(tr(user, "Неизвестный тип покупки", "Unknown purchase type"))
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
            tr(
                user,
                f"💳 <b>Оплата: {description}</b>\n\n"
                f"Сумма: {amount}₽\n\n"
                f"Перейдите по ссылке для оплаты:\n{payment_url}\n\n"
                "После успешной оплаты ваш тариф будет автоматически активирован.",
                f"💳 <b>Payment: {description}</b>\n\n"
                f"Amount: {amount}₽\n\n"
                f"Open the link to pay:\n{payment_url}\n\n"
                "After successful payment your plan will activate automatically.",
            )
        )
        
        await state.set_state(Payment.waiting_for_payment)
    except Exception as e:
        await callback.message.answer(
            tr(
                user,
                f"❌ Ошибка при создании платежа: {str(e)}\n\nПопробуйте позже или обратитесь в поддержку.",
                f"❌ Failed to create payment: {str(e)}\n\nTry again later or contact support.",
            )
        )
    
    await callback.answer()

