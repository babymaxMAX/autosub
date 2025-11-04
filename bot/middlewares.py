"""Bot middlewares."""
import logging
from typing import Callable, Dict, Any, Awaitable
from aiogram import BaseMiddleware
from aiogram.types import Message, CallbackQuery
from db.database import AsyncSessionLocal
from db.crud import get_user_by_telegram_id, create_user

logger = logging.getLogger(__name__)


class UserMiddleware(BaseMiddleware):
    """Middleware to get or create user in database."""
    
    async def __call__(
        self,
        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
        event: Message | CallbackQuery,
        data: Dict[str, Any]
    ) -> Any:
        """Process event."""
        # Get user from event
        if isinstance(event, Message):
            telegram_user = event.from_user
        else:
            telegram_user = event.from_user
        
        if not telegram_user:
            return await handler(event, data)
        
        # Get or create user in database
        async with AsyncSessionLocal() as db:
            user = await get_user_by_telegram_id(db, telegram_user.id)
            
            if not user:
                user = await create_user(
                    db,
                    telegram_id=telegram_user.id,
                    username=telegram_user.username,
                    first_name=telegram_user.first_name,
                    last_name=telegram_user.last_name,
                    language_code=telegram_user.language_code or "ru",
                )
                logger.info(f"New user created: {user.telegram_id}")
            
            # Add user to data
            data["user"] = user
            data["db"] = db
        
        return await handler(event, data)


class LoggingMiddleware(BaseMiddleware):
    """Middleware for logging all messages."""
    
    async def __call__(
        self,
        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
        event: Message,
        data: Dict[str, Any]
    ) -> Any:
        """Process event."""
        user = event.from_user
        logger.info(
            f"Message from {user.id} (@{user.username}): {event.text[:50] if event.text else 'Media'}"
        )
        return await handler(event, data)

