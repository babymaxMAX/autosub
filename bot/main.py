"""Main bot entry point."""
import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.redis import RedisStorage
from redis.asyncio import Redis
from config.settings import settings
from db.database import init_db
from bot.handlers import (
    start_handler,
    profile_handler,
    pricing_handler,
    video_handler,
    admin_handler,
)
from bot.middlewares import UserMiddleware, LoggingMiddleware

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def main():
    """Main function to start the bot."""
    logger.info("Starting AutoSub Bot...")
    
    # Initialize database
    await init_db()
    logger.info("Database initialized")
    
    # Initialize Redis storage
    redis = Redis.from_url(settings.redis_url)
    storage = RedisStorage(redis=redis)
    
    # Initialize bot and dispatcher
    bot = Bot(token=settings.BOT_TOKEN)
    dp = Dispatcher(storage=storage)
    
    # Register middlewares
    dp.message.middleware(UserMiddleware())
    dp.callback_query.middleware(UserMiddleware())
    dp.message.middleware(LoggingMiddleware())
    
    # Register handlers
    dp.include_router(start_handler.router)
    dp.include_router(profile_handler.router)
    dp.include_router(pricing_handler.router)
    dp.include_router(video_handler.router)
    dp.include_router(admin_handler.router)
    
    # Start polling
    logger.info("Bot started successfully!")
    await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.info("Bot stopped")
