"""Admin handler."""
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from sqlalchemy import select, func, and_
from datetime import datetime, timedelta
from db.models import User, Task, Payment, SystemLog
from db.database import AsyncSessionLocal
from config.settings import settings
from bot.keyboards import get_admin_keyboard

router = Router()


def is_admin(telegram_id: int) -> bool:
    """Check if user is admin."""
    return telegram_id in settings.admin_ids_list


@router.message(Command("admin"))
async def cmd_admin(message: Message, user: User, **kwargs):
    """Handle /admin command."""
    if not is_admin(message.from_user.id):
        await message.answer("❌ У вас нет доступа к этой команде")
        return
    
    await message.answer(
        "👑 <b>Панель администратора</b>\n\nВыберите раздел:",
        reply_markup=get_admin_keyboard(user)
    )


@router.callback_query(F.data == "admin_metrics")
async def show_stats(callback: CallbackQuery, user: User, **kwargs):
    """Show metrics digest."""
    if not is_admin(callback.from_user.id):
        await callback.answer("❌ Доступ запрещен")
        return
    
    async with AsyncSessionLocal() as db:
        # Users by tier
        total_users = await db.scalar(select(func.count(User.id)))
        free_users = await db.scalar(select(func.count(User.id)).where(User.tier == "free"))
        pro_users = await db.scalar(select(func.count(User.id)).where(User.tier == "pro"))
        creator_users = await db.scalar(select(func.count(User.id)).where(User.tier == "creator"))
        
        # Count tasks
        total_tasks = await db.scalar(select(func.count(Task.id)))
        completed_tasks = await db.scalar(select(func.count(Task.id)).where(Task.status == "completed"))
        failed_tasks = await db.scalar(select(func.count(Task.id)).where(Task.status == "failed"))
        since = datetime.utcnow() - timedelta(hours=24)
        tasks_24h = await db.scalar(select(func.count(Task.id)).where(Task.created_at >= since))
        completed_24h = await db.scalar(select(func.count(Task.id)).where(and_(Task.created_at >= since, Task.status == "completed")))
        success_rate = (completed_24h / tasks_24h * 100) if tasks_24h else 0.0
        
        # Count payments
        total_payments = await db.scalar(select(func.count(Payment.id)))
        total_revenue = await db.scalar(select(func.sum(Payment.amount)).where(Payment.status == "completed")) or 0
    
    stats_text = f"""
🧮 <b>Метрики</b>

Задач за 24ч: {tasks_24h} · успех {success_rate:.0f}%

ASR avg: —  (резерв)
Конверсия в оплату: — (резерв)

Пользователи: всего {total_users} · FREE {free_users} · PRO {pro_users} · CREATOR {creator_users}
"""
    
    await callback.message.edit_text(stats_text, reply_markup=get_admin_keyboard(user))
    await callback.answer()


@router.callback_query(F.data == "admin_users")
async def show_users(callback: CallbackQuery, user: User, **kwargs):
    """Show recent users."""
    if not is_admin(callback.from_user.id):
        await callback.answer("❌ Доступ запрещен")
        return
    
    async with AsyncSessionLocal() as db:
        result = await db.execute(
            select(User)
            .order_by(User.created_at.desc())
            .limit(10)
        )
        users = result.scalars().all()
    
    users_text = "👥 <b>Последние пользователи:</b>\n\n"
    for user in users:
        users_text += (
            f"ID: {user.id} | @{user.username or 'N/A'}\n"
            f"Тариф: {user.tier.value} | Задач: {user.tasks_total}\n\n"
        )
    
    await callback.message.edit_text(users_text, reply_markup=get_admin_keyboard(user))
    await callback.answer()


@router.callback_query(F.data == "admin_tasks_live")
async def show_tasks(callback: CallbackQuery, user: User, **kwargs):
    """Show recent tasks (live snapshot)."""
    if not is_admin(callback.from_user.id):
        await callback.answer("❌ Доступ запрещен")
        return
    
    async with AsyncSessionLocal() as db:
        result = await db.execute(
            select(Task).order_by(Task.created_at.desc()).limit(10)
        )
        tasks = result.scalars().all()
    
    tasks_text = "📡 <b>Текущие задачи:</b>\n\n"
    for task in tasks:
        tasks_text += (
            f"#{task.id} | User: {task.user_id}\n"
            f"Статус: {task.status.value} | Тип: {task.input_type}\n\n"
        )
    
    await callback.message.edit_text(tasks_text, reply_markup=get_admin_keyboard(user))
    await callback.answer()


@router.callback_query(F.data == "admin_payments")
async def show_payments(callback: CallbackQuery, user: User, **kwargs):
    """Show recent payments."""
    if not is_admin(callback.from_user.id):
        await callback.answer("❌ Доступ запрещен")
        return
    
    async with AsyncSessionLocal() as db:
        result = await db.execute(
            select(Payment)
            .order_by(Payment.created_at.desc())
            .limit(10)
        )
        payments = result.scalars().all()
    
    payments_text = "💰 <b>Последние платежи:</b>\n\n"
    for payment in payments:
        payments_text += (
            f"#{payment.id} | User: {payment.user_id}\n"
            f"Сумма: {payment.amount}₽ | Статус: {payment.status}\n"
            f"Тариф: {payment.tier.value if payment.tier else 'Разовый'}\n\n"
        )
    
    await callback.message.edit_text(payments_text, reply_markup=get_admin_keyboard(user))
    await callback.answer()


@router.callback_query(F.data == "admin_errors")
async def show_errors(callback: CallbackQuery, user: User, **kwargs):
    """Show error feed grouped by pattern for last 24h."""
    if not is_admin(callback.from_user.id):
        await callback.answer("❌ Доступ запрещен")
        return
    since = datetime.utcnow() - timedelta(hours=24)
    async with AsyncSessionLocal() as db:
        result = await db.execute(
            select(SystemLog.message).where(and_(SystemLog.level.in_(["ERROR", "CRITICAL"]), SystemLog.created_at >= since))
        )
        messages = [row[0] for row in result.all()]
    groups = {}
    for msg in messages:
        key = "ffmpeg exit" if "ffmpeg" in msg.lower() else ("yt-dlp blocked" if "blocked" in msg.lower() else "other")
        groups[key] = groups.get(key, 0) + 1
    text = "🚨 <b>Ошибки (24ч)</b>\n\n"
    for k, v in groups.items():
        text += f"{k} - {v} раз(а)\n"
    await callback.message.edit_text(text, reply_markup=get_admin_keyboard(user))
    await callback.answer()


@router.callback_query(F.data == "admin_user")
async def admin_user_prompt(callback: CallbackQuery, user: User, **kwargs):
    if not is_admin(callback.from_user.id):
        await callback.answer("❌ Доступ запрещен")
        return
    await callback.message.edit_text("Введи @username или tg_id (пока без интерактива).", reply_markup=get_admin_keyboard(user))
    await callback.answer()


@router.callback_query(F.data == "admin_tools")
async def admin_tools(callback: CallbackQuery, user: User, **kwargs):
    if not is_admin(callback.from_user.id):
        await callback.answer("❌ Доступ запрещен")
        return
    text = "🧰 Инструменты\n\n• 📣 Пуш всем Free с лимитом\n• 🧪 Тест ffmpeg\n• 🔗 Проверка Platega webhook"
    await callback.message.edit_text(text, reply_markup=get_admin_keyboard(user))
    await callback.answer()

