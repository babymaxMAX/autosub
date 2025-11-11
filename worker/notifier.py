"""Notification service to send results to users."""
import asyncio
import logging
from pathlib import Path
from aiogram import Bot
from aiogram.types import FSInputFile
from config.settings import settings
from redis.asyncio import Redis
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

        telegram_id = task.user.telegram_id

        # Create a dedicated event loop to avoid "Event loop is closed" issues in RQ worker context
        loop = asyncio.new_event_loop()
        try:
            asyncio.set_event_loop(loop)
            loop.run_until_complete(_send_notification(telegram_id, task))
        finally:
            try:
                loop.stop()
            except Exception:
                pass
            loop.close()
        db.close()
    except Exception as e:
        logger.error(f"Error sending notification: {e}", exc_info=True)


async def _send_notification(telegram_id: int, task):
    """Send notification to user (async)."""
    # Use context manager to ensure session lifecycle is tied to running loop
    async with Bot(token=settings.BOT_TOKEN) as bot:
        try:
            if task.status == TaskStatus.COMPLETED:
                try:
                    await bot.send_message(
                        telegram_id,
                        f"✅ Задача #{task.id} завершена!\n\nОтправляем вам результат..."
                    )
                except Exception as e:
                    logger.error(f"Error sending completion message: {e}", exc_info=True)

                if task.output_file_path and Path(task.output_file_path).exists():
                    try:
                        video_file = FSInputFile(task.output_file_path)
                        await bot.send_video(telegram_id, video_file, caption=f"🎬 Обработанное видео #task{task.id}")
                    except Exception as e:
                        logger.error(f"Error sending video: {e}", exc_info=True)

                if task.subtitles_file_path and Path(task.subtitles_file_path).exists():
                    try:
                        srt_file = FSInputFile(task.subtitles_file_path)
                        await bot.send_document(telegram_id, srt_file, caption="📝 Файл субтитров (SRT)")
                    except Exception as e:
                        logger.error(f"Error sending subtitles: {e}", exc_info=True)

            elif task.status == TaskStatus.FAILED:
                try:
                    await bot.send_message(
                        telegram_id,
                        f"❌ Задача #{task.id} завершилась с ошибкой\n\nПричина: {task.error_message or 'Неизвестная ошибка'}\n\nПопробуйте еще раз или обратитесь в поддержку."
                    )
                except Exception as e:
                    logger.error(f"Error sending error message: {e}", exc_info=True)
        except Exception as e:
            logger.error(f"Unexpected error in _send_notification: {e}", exc_info=True)


async def send_status_update(task_id: int, text: str):
    """Edit unified status message stored in Redis mapping."""
    try:
        r = Redis.from_url(settings.redis_url)
        mapping = await r.hgetall(f"task:{task_id}:status_msg")
        if not mapping or b"chat_id" not in mapping or b"message_id" not in mapping:
            return
        chat_id = int(mapping[b"chat_id"].decode())
        message_id = int(mapping[b"message_id"].decode())
        async with Bot(token=settings.BOT_TOKEN) as bot:
            try:
                await bot.edit_message_text(text, chat_id=chat_id, message_id=message_id, disable_web_page_preview=True)
            except Exception as e:
                logger.warning(f"Failed to edit status message: {e}")
    except Exception as e:
        logger.error(f"send_status_update error: {e}", exc_info=True)

