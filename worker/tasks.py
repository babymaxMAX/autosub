"""Worker tasks for video processing."""
import os
import logging
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
        
        # Update status to processing
        update_task_status_sync(db, task_id, TaskStatus.PROCESSING)
        
        # Create working directory
        work_dir = Path(settings.STORAGE_PATH) / f"task_{task_id}"
        work_dir.mkdir(parents=True, exist_ok=True)
        
        # Step 1: Download video
        logger.info(f"Task #{task_id}: Downloading video")
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
            subtitles_path = transcribe_audio(
                input_video_path,
                work_dir,
                language=task.source_language
            )
            # Get detected language from transcription result
            # Note: transcriber returns detected language in logs, we'll pass source_language
            detected_language = task.source_language
        else:
            subtitles_path = None
        
        # Step 3: Translate subtitles
        if task.translate and subtitles_path:
            logger.info(f"Task #{task_id}: Translating subtitles")
            subtitles_path = translate_subtitles(
                subtitles_path,
                work_dir,
                target_language=task.target_language,
                source_language=detected_language
            )
        
        # Step 4: Generate voiceover
        voiceover_path = None
        if task.voiceover and subtitles_path:
            logger.info(f"Task #{task_id}: Generating voiceover")
            voiceover_path = generate_voiceover(
                subtitles_path,
                work_dir,
                language=task.target_language or task.source_language
            )
        
        # Step 5: Process video (hardsub, vertical format, watermark)
        logger.info(f"Task #{task_id}: Processing video")
        output_video_path = process_video_with_subtitles(
            input_video_path=input_video_path,
            subtitles_path=subtitles_path,
            voiceover_path=voiceover_path,
            output_dir=work_dir,
            vertical_format=task.vertical_format,
            add_watermark=task.add_watermark,
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

