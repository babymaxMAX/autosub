"""Video service for handling video operations."""
import re
from datetime import datetime
from typing import Tuple, Optional
from redis import Redis
from rq import Queue
from config.settings import settings
from config.constants import TIER_LIMITS, TaskStatus
from db.models import User
from db.crud import create_task, increment_user_tasks


def validate_video_url(url: str) -> Tuple[bool, Optional[str]]:
    """Validate video URL and return source."""
    youtube_pattern = r'(youtube\.com|youtu\.be)'
    tiktok_pattern = r'tiktok\.com'
    instagram_pattern = r'instagram\.com'
    
    if re.search(youtube_pattern, url):
        return True, "youtube"
    elif re.search(tiktok_pattern, url):
        return True, "tiktok"
    elif re.search(instagram_pattern, url):
        return True, "instagram"
    else:
        return False, None


async def check_user_limits(db, user: User) -> Tuple[bool, Optional[str]]:
    """Check if user can process video based on their tier limits."""
    tier_limits = TIER_LIMITS[user.tier]
    
    # Check if it's a new day
    today = datetime.utcnow().date()
    if user.last_task_date and user.last_task_date.date() < today:
        user.tasks_today = 0
    
    # Check daily limit
    if user.tasks_today >= tier_limits["daily_tasks"]:
        return False, f"Вы достигли дневного лимита ({tier_limits['daily_tasks']} задач). Попробуйте завтра или улучшите тариф."
    
    # Check if subscription is active
    if user.tier_expires_at and user.tier_expires_at < datetime.utcnow():
        return False, "Ваша подписка истекла. Продлите подписку для продолжения."
    
    return True, None


async def enqueue_video_task(db, user: User, data: dict):
    """Enqueue video processing task."""
    # Get tier limits
    tier_limits = TIER_LIMITS[user.tier]
    
    # Prepare task data
    task_data = {
        "input_type": data.get("input_type"),
        "input_url": data.get("input_url"),
        "input_file_id": data.get("file_id"),
        "duration": data.get("duration"),
        "priority": tier_limits["priority"],
        "generate_subtitles": data.get("options", {}).get("subtitles", True),
        "translate": data.get("options", {}).get("translate", False),
        "voiceover": data.get("options", {}).get("voiceover", False),
        "vertical_format": data.get("options", {}).get("vertical", False),
        "add_watermark": tier_limits["watermark"],
        "target_language": data.get("target_language", "auto"),
        "source_language": "auto",
    }
    
    # Create task in database
    task = await create_task(db, user.id, **task_data)
    
    # Increment user task counters
    await increment_user_tasks(db, user.id)
    
    # Enqueue to Redis queue
    redis_conn = Redis.from_url(settings.redis_url)
    queue = Queue("video_processing", connection=redis_conn)
    queue.enqueue(
        "worker.tasks.process_video_task",
        task_id=task.id,
        job_timeout="30m",
        result_ttl=3600,
    )
    
    return task

