"""Worker tasks for video processing."""
import os
import logging
import json
from pathlib import Path
from config.settings import settings
from config.constants import TaskStatus
from db.database import SessionLocal
from db.crud import get_task_sync, update_task_status_sync
from worker.processors.downloader import download_video
from worker.processors.transcriber import transcribe_audio
from worker.processors.translator import translate_subtitles
from worker.processors.tts_generator import generate_voiceover
from worker.processors.video_processor import process_video_with_subtitles
from worker.notifier import send_status_update
from redis import Redis

logger = logging.getLogger(__name__)


def process_video_task(task_id: int):
    """Process video task."""
    logger.info(f"Processing task #{task_id}")
    
    db = SessionLocal()
    
    try:
        # Get task
        task = get_task_sync(db, task_id)
        if not task:
            logger.error(f"Task #{task_id} not found")
            return
        # Fetch extra appearance options
        subtitle_options = {
            "style": "sub36o1",
            "position": "bottom",
            "voice": "female",
        }
        try:
            redis_conn = Redis.from_url(settings.redis_url)
            raw_opts = redis_conn.get(f"task:{task_id}:options")
            if raw_opts:
                subtitle_options.update(json.loads(raw_opts))
                redis_conn.delete(f"task:{task_id}:options")
        except Exception:
            logger.warning(f"Task #{task_id}: failed to load extra options from Redis, using defaults.")
        
        # Update status to processing
        update_task_status_sync(db, task_id, TaskStatus.PROCESSING)
        
        # Create working directory
        work_dir = Path(settings.STORAGE_PATH) / f"task_{task_id}"
        work_dir.mkdir(parents=True, exist_ok=True)
        
        # Step 1: Download video
        logger.info(f"Task #{task_id}: Downloading video")
        try:
            import asyncio
            asyncio.run(send_status_update(task_id, f"⏳ #{task_id} · загрузка…"))
        except Exception:
            pass
        input_video_path = download_video(task, work_dir)
        
        if not input_video_path or not os.path.exists(input_video_path):
            raise Exception("Failed to download video")
        
        # Update task with input file path
        update_task_status_sync(
            db,
            task_id,
            TaskStatus.PROCESSING,
            input_file_path=input_video_path
        )
        
        # Step 2: Transcribe audio
        detected_language = None
        if task.generate_subtitles:
            logger.info(f"Task #{task_id}: Transcribing audio")
             # status update
            try:
                import asyncio
                asyncio.run(send_status_update(task_id, f"⏳ #{task_id}\nASR: выполняется…\nПеревод: {'ожидает' if task.translate else 'пропущен'}\nОзвучка: {'ожидает' if task.voiceover else 'пропущена'}\nХардсаб: ожидает"))
            except Exception:
                pass
            subtitles_path, detected_language = transcribe_audio(
                input_video_path,
                work_dir,
                language=task.source_language
            )
            if detected_language and detected_language != task.source_language:
                update_task_status_sync(
                    db,
                    task_id,
                    TaskStatus.PROCESSING,
                    source_language=detected_language
                )
        else:
            subtitles_path = None
            detected_language = task.source_language if task.source_language not in (None, "", "auto") else None
        
        # Step 3: Translate subtitles
        if task.translate and subtitles_path:
            logger.info(f"Task #{task_id}: Translating subtitles")
            try:
                import asyncio
                asyncio.run(send_status_update(task_id, f"⏳ #{task_id}\nASR: готово\nПеревод: выполняется…\nОзвучка: {'ожидает' if task.voiceover else 'пропущена'}\nХардсаб: ожидает"))
            except Exception:
                pass
            source_lang = detected_language or task.source_language or "auto"
            subtitles_path = translate_subtitles(
                subtitles_path,
                work_dir,
                target_language=task.target_language,
                source_language=source_lang
            )
        
        # Step 4: Generate voiceover
        voiceover_path = None
        if task.voiceover and subtitles_path:
            logger.info(f"Task #{task_id}: Generating voiceover")
            try:
                import asyncio
                asyncio.run(send_status_update(task_id, f"⏳ #{task_id}\nASR: готово\nПеревод: {'готово' if task.translate else 'пропущен'}\nОзвучка: выполняется…\nХардсаб: ожидает"))
            except Exception:
                pass
            voice_lang = None
            if task.translate and task.target_language and task.target_language != "auto":
                voice_lang = task.target_language
            else:
                voice_lang = detected_language or task.source_language
            if not voice_lang or voice_lang == "auto":
                voice_lang = "en"
            voiceover_path = generate_voiceover(
                subtitles_path,
                work_dir,
                language=voice_lang,
                voice=subtitle_options.get("voice", "female"),
            )
        
        # Step 5: Process video (hardsub, vertical format, watermark)
        logger.info(f"Task #{task_id}: Processing video")
        try:
            import asyncio
            asyncio.run(send_status_update(task_id, f"⏳ #{task_id}\nASR: {'готово' if task.generate_subtitles else 'пропущен'}\nПеревод: {'готово' if task.translate else 'пропущен'}\nОзвучка: {'готово' if task.voiceover else 'пропущена'}\nХардсаб: выполняется…"))
        except Exception:
            pass
        subtitle_lang = None
        if task.translate and task.target_language and task.target_language != "auto":
            subtitle_lang = task.target_language
        else:
            subtitle_lang = detected_language or task.source_language
        if subtitle_lang in (None, "", "auto"):
            subtitle_lang = None
        
        output_video_path = process_video_with_subtitles(
            input_video_path=input_video_path,
            subtitles_path=subtitles_path,
            voiceover_path=voiceover_path,
            output_dir=work_dir,
            vertical_format=task.vertical_format,
            add_watermark=task.add_watermark,
            subtitle_style=subtitle_options.get("style", "sub36o1"),
            subtitle_position=subtitle_options.get("position", "bottom"),
            subtitle_language=subtitle_lang,
        )
        
        # Update task with output
        update_task_status_sync(
            db,
            task_id,
            TaskStatus.COMPLETED,
            output_file_path=output_video_path,
            subtitles_file_path=subtitles_path,
        )
        
        logger.info(f"Task #{task_id}: Completed successfully")
        
        # Send result to user (will be handled by a separate notification service)
        from worker.notifier import send_result_to_user
        send_result_to_user(task_id)
        
    except Exception as e:
        logger.error(f"Task #{task_id}: Error - {str(e)}", exc_info=True)
        error_message = str(e)
        
        # Update task status to failed
        update_task_status_sync(
            db,
            task_id,
            TaskStatus.FAILED,
            error_message=error_message
        )
        
        # Send error notification to user
        try:
            from worker.notifier import send_result_to_user
            send_result_to_user(task_id)
        except Exception as notify_error:
            logger.error(f"Task #{task_id}: Failed to send error notification: {notify_error}", exc_info=True)
    finally:
        db.close()

