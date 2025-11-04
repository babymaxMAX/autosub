"""CRUD operations for database models."""
from datetime import datetime, timedelta
from typing import Optional, List
from sqlalchemy import select, update, and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session
from db.models import User, Task, Payment, SystemLog
from config.constants import UserTier, TaskStatus


# User CRUD
async def get_user_by_telegram_id(db: AsyncSession, telegram_id: int) -> Optional[User]:
    """Get user by Telegram ID."""
    result = await db.execute(select(User).where(User.telegram_id == telegram_id))
    return result.scalar_one_or_none()


async def create_user(
    db: AsyncSession,
    telegram_id: int,
    username: Optional[str] = None,
    first_name: Optional[str] = None,
    last_name: Optional[str] = None,
    language_code: str = "ru",
) -> User:
    """Create new user."""
    user = User(
        telegram_id=telegram_id,
        username=username,
        first_name=first_name,
        last_name=last_name,
        language_code=language_code,
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


async def update_user_tier(
    db: AsyncSession,
    user_id: int,
    tier: UserTier,
    expires_at: Optional[datetime] = None,
) -> User:
    """Update user subscription tier."""
    await db.execute(
        update(User)
        .where(User.id == user_id)
        .values(tier=tier, tier_expires_at=expires_at, updated_at=datetime.utcnow())
    )
    await db.commit()
    result = await db.execute(select(User).where(User.id == user_id))
    return result.scalar_one()


async def increment_user_tasks(db: AsyncSession, user_id: int) -> None:
    """Increment user's task counters."""
    user = await db.execute(select(User).where(User.id == user_id))
    user = user.scalar_one()
    
    # Reset daily counter if it's a new day
    today = datetime.utcnow().date()
    if user.last_task_date is None or user.last_task_date.date() < today:
        user.tasks_today = 0
    
    user.tasks_today += 1
    user.tasks_total += 1
    user.last_task_date = datetime.utcnow()
    
    await db.commit()


# Task CRUD
async def create_task(
    db: AsyncSession,
    user_id: int,
    input_type: str,
    priority: int = 3,
    **kwargs
) -> Task:
    """Create new processing task."""
    task = Task(
        user_id=user_id,
        input_type=input_type,
        priority=priority,
        **kwargs
    )
    db.add(task)
    await db.commit()
    await db.refresh(task)
    return task


async def get_task(db: AsyncSession, task_id: int) -> Optional[Task]:
    """Get task by ID."""
    result = await db.execute(select(Task).where(Task.id == task_id))
    return result.scalar_one_or_none()


async def update_task_status(
    db: AsyncSession,
    task_id: int,
    status: TaskStatus,
    **kwargs
) -> Task:
    """Update task status."""
    update_data = {"status": status, **kwargs}
    
    if status == TaskStatus.PROCESSING:
        update_data["started_at"] = datetime.utcnow()
    elif status in [TaskStatus.COMPLETED, TaskStatus.FAILED, TaskStatus.CANCELLED]:
        update_data["completed_at"] = datetime.utcnow()
    
    await db.execute(
        update(Task)
        .where(Task.id == task_id)
        .values(**update_data)
    )
    await db.commit()
    return await get_task(db, task_id)


async def get_user_tasks(
    db: AsyncSession,
    user_id: int,
    limit: int = 10,
    offset: int = 0
) -> List[Task]:
    """Get user's tasks."""
    result = await db.execute(
        select(Task)
        .where(Task.user_id == user_id)
        .order_by(Task.created_at.desc())
        .limit(limit)
        .offset(offset)
    )
    return result.scalars().all()


# Payment CRUD
async def create_payment(
    db: AsyncSession,
    user_id: int,
    amount: float,
    tier: Optional[UserTier] = None,
    **kwargs
) -> Payment:
    """Create new payment."""
    payment = Payment(
        user_id=user_id,
        amount=amount,
        tier=tier,
        **kwargs
    )
    db.add(payment)
    await db.commit()
    await db.refresh(payment)
    return payment


async def get_payment_by_external_id(db: AsyncSession, external_id: str) -> Optional[Payment]:
    """Get payment by external ID."""
    result = await db.execute(select(Payment).where(Payment.external_id == external_id))
    return result.scalar_one_or_none()


async def update_payment_status(
    db: AsyncSession,
    payment_id: int,
    status: str,
    **kwargs
) -> Payment:
    """Update payment status."""
    update_data = {"status": status, **kwargs}
    
    if status == "completed":
        update_data["completed_at"] = datetime.utcnow()
    
    await db.execute(
        update(Payment)
        .where(Payment.id == payment_id)
        .values(**update_data)
    )
    await db.commit()
    result = await db.execute(select(Payment).where(Payment.id == payment_id))
    return result.scalar_one()


# System Log CRUD
async def create_log(
    db: AsyncSession,
    level: str,
    message: str,
    module: Optional[str] = None,
    user_id: Optional[int] = None,
    task_id: Optional[int] = None,
    log_metadata: Optional[dict] = None,
) -> SystemLog:
    """Create system log entry."""
    log = SystemLog(
        level=level,
        message=message,
        module=module,
        user_id=user_id,
        task_id=task_id,
        log_metadata=log_metadata,
    )
    db.add(log)
    await db.commit()
    return log


# Sync versions for RQ workers
def get_task_sync(db: Session, task_id: int) -> Optional[Task]:
    """Get task by ID (sync)."""
    return db.query(Task).filter(Task.id == task_id).first()


def update_task_status_sync(
    db: Session,
    task_id: int,
    status: TaskStatus,
    **kwargs
) -> Task:
    """Update task status (sync)."""
    update_data = {"status": status, **kwargs}
    
    if status == TaskStatus.PROCESSING:
        update_data["started_at"] = datetime.utcnow()
    elif status in [TaskStatus.COMPLETED, TaskStatus.FAILED, TaskStatus.CANCELLED]:
        update_data["completed_at"] = datetime.utcnow()
    
    db.query(Task).filter(Task.id == task_id).update(update_data)
    db.commit()
    return get_task_sync(db, task_id)

