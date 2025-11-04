"""Admin handler."""
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from sqlalchemy import select, func
from db.models import User, Task, Payment
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
        "👑 <b>Панель администратора</b>\n\n"
        "Выберите действие:",
        reply_markup=get_admin_keyboard()
    )


@router.callback_query(F.data == "admin_stats")
async def show_stats(callback: CallbackQuery, **kwargs):
    """Show statistics."""
    if not is_admin(callback.from_user.id):
        await callback.answer("❌ Доступ запрещен")
        return
    
    async with AsyncSessionLocal() as db:
        # Count users
        total_users = await db.scalar(select(func.count(User.id)))
        free_users = await db.scalar(select(func.count(User.id)).where(User.tier == "free"))
        pro_users = await db.scalar(select(func.count(User.id)).where(User.tier == "pro"))
        creator_users = await db.scalar(select(func.count(User.id)).where(User.tier == "creator"))
        
        # Count tasks
        total_tasks = await db.scalar(select(func.count(Task.id)))
        completed_tasks = await db.scalar(select(func.count(Task.id)).where(Task.status == "completed"))
        failed_tasks = await db.scalar(select(func.count(Task.id)).where(Task.status == "failed"))
        
        # Count payments
        total_payments = await db.scalar(select(func.count(Payment.id)))
        total_revenue = await db.scalar(select(func.sum(Payment.amount)).where(Payment.status == "completed")) or 0
    
    stats_text = f"""
📊 <b>Статистика системы</b>

<b>Пользователи:</b>
• Всего: {total_users}
• FREE: {free_users}
• PRO: {pro_users}
• CREATOR: {creator_users}

<b>Задачи:</b>
• Всего: {total_tasks}
• Завершено: {completed_tasks}
• Ошибок: {failed_tasks}

<b>Платежи:</b>
• Всего: {total_payments}
• Выручка: {total_revenue:.2f}₽
"""
    
    await callback.message.edit_text(stats_text, reply_markup=get_admin_keyboard())
    await callback.answer()


@router.callback_query(F.data == "admin_users")
async def show_users(callback: CallbackQuery, **kwargs):
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
    
    await callback.message.edit_text(users_text, reply_markup=get_admin_keyboard())
    await callback.answer()


@router.callback_query(F.data == "admin_tasks")
async def show_tasks(callback: CallbackQuery, **kwargs):
    """Show recent tasks."""
    if not is_admin(callback.from_user.id):
        await callback.answer("❌ Доступ запрещен")
        return
    
    async with AsyncSessionLocal() as db:
        result = await db.execute(
            select(Task)
            .order_by(Task.created_at.desc())
            .limit(10)
        )
        tasks = result.scalars().all()
    
    tasks_text = "📋 <b>Последние задачи:</b>\n\n"
    for task in tasks:
        tasks_text += (
            f"#{task.id} | User: {task.user_id}\n"
            f"Статус: {task.status.value} | Тип: {task.input_type}\n\n"
        )
    
    await callback.message.edit_text(tasks_text, reply_markup=get_admin_keyboard())
    await callback.answer()


@router.callback_query(F.data == "admin_payments")
async def show_payments(callback: CallbackQuery, **kwargs):
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
    
    await callback.message.edit_text(payments_text, reply_markup=get_admin_keyboard())
    await callback.answer()

