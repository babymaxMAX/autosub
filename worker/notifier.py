"""Notification service to send results to users."""
import asyncio
import logging
from pathlib import Path
from aiogram import Bot
from aiogram.types import FSInputFile
from config.settings import settings
from db.database import SessionLocal
from db.crud import get_task_sync
from config.constants import TaskStatus

logger = logging.getLogger(__name__)


def send_result_to_user(task_id: int):
    """Send processing result to user."""
    try:
        db = SessionLocal()
        task = get_task_sync(db, task_id)
        
        if not task:
            logger.error(f"Task #{task_id} not found")
            return
        
        # Get user's telegram_id
        telegram_id = task.user.telegram_id
        
        # Send notification
        asyncio.run(_send_notification(telegram_id, task))
        
        db.close()
    
    except Exception as e:
        logger.error(f"Error sending notification: {e}")


async def _send_notification(telegram_id: int, task):
    """Send notification to user (async)."""
    bot = Bot(token=settings.BOT_TOKEN)
    
    try:
        if task.status == TaskStatus.COMPLETED:
            # Send success message
            try:
                await bot.send_message(
                    telegram_id,
                    f"✅ Задача #{task.id} завершена!\n\n"
                    f"Отправляем вам результат..."
                )
            except Exception as e:
                logger.error(f"Error sending completion message: {e}", exc_info=True)
            
            # Send video
            if task.output_file_path and Path(task.output_file_path).exists():
                try:
                    video_file = FSInputFile(task.output_file_path)
                    await bot.send_video(
                        telegram_id,
                        video_file,
                        caption=f"🎬 Обработанное видео #task{task.id}"
                    )
                except Exception as e:
                    logger.error(f"Error sending video: {e}", exc_info=True)
            
            # Send subtitles
            if task.subtitles_file_path and Path(task.subtitles_file_path).exists():
                try:
                    srt_file = FSInputFile(task.subtitles_file_path)
                    await bot.send_document(
                        telegram_id,
                        srt_file,
                        caption="📝 Файл субтитров (SRT)"
                    )
                except Exception as e:
                    logger.error(f"Error sending subtitles: {e}", exc_info=True)
        
        elif task.status == TaskStatus.FAILED:
            # Send error message
            try:
                await bot.send_message(
                    telegram_id,
                    f"❌ Задача #{task.id} завершилась с ошибкой\n\n"
                    f"Причина: {task.error_message or 'Неизвестная ошибка'}\n\n"
                    f"Попробуйте еще раз или обратитесь в поддержку."
                )
            except Exception as e:
                logger.error(f"Error sending error message: {e}", exc_info=True)
    
    except Exception as e:
        logger.error(f"Unexpected error in _send_notification: {e}", exc_info=True)
    finally:
        # Properly close bot session to avoid conflicts
        try:
            await bot.session.close()
        except Exception as e:
            logger.warning(f"Error closing bot session: {e}")

