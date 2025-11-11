"""Video service for handling video operations."""
import re
from datetime import datetime
from typing import Tuple, Optional
import json
from redis import Redis
from rq import Queue
from config.settings import settings
from config.constants import TIER_LIMITS, TaskStatus
from db.models import User
from db.crud import create_task, increment_user_tasks
import yt_dlp
from typing import Dict


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


def extract_url_preview(url: str) -> Dict[str, Optional[str]]:
    """Extract preview metadata from URL without downloading."""
    try:
        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'skip_download': True,
            'noplaylist': True,
            'extract_flat': False,
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            return {
                "title": info.get("title"),
                "duration": info.get("duration"),
                "uploader": info.get("uploader") or info.get("channel") or info.get("uploader_id"),
                "thumbnail": info.get("thumbnail"),
            }
    except Exception:
        return {"title": None, "duration": None, "uploader": None, "thumbnail": None}


async def check_user_limits(db, user: User) -> Tuple[bool, Optional[str]]:
    """Check if user can process video based on their tier limits."""
    # Allow disabling all limits for testing via .env
    if getattr(settings, "DISABLE_LIMITS", False):
        return True, None
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
    
    options = data.get("options", {})
    target_language = options.get("target_language", data.get("target_language", "auto"))
    extra_options = {
        "style": options.get("style", "sub36o1"),
        "voice": options.get("voice", "female"),
        "position": options.get("position", "bottom"),
    }
    
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
        "target_language": target_language,
        "source_language": "auto",
    }
    
    # Create task in database
    task = await create_task(db, user.id, **task_data)
    
    # Increment user task counters
    await increment_user_tasks(db, user.id)
    
    # Enqueue to Redis queue
    redis_conn = Redis.from_url(settings.redis_url)
    queue = Queue("video_processing", connection=redis_conn)
    # Persist extended options for worker consumption
    try:
        redis_conn.setex(f"task:{task.id}:options", 60 * 60 * 24, json.dumps(extra_options, ensure_ascii=False))
    except Exception:
        pass
    queue.enqueue(
        "worker.tasks.process_video_task",
        task_id=task.id,
        job_timeout="30m",
        result_ttl=3600,
    )
    
    return task

