"""Video downloader."""
import os
import logging
from pathlib import Path
import yt_dlp
from aiogram import Bot
from config.settings import settings

logger = logging.getLogger(__name__)


def download_video(task, work_dir: Path) -> str:
    """Download video from URL or Telegram."""
    
    if task.input_type == "file":
        # Download from Telegram
        return download_from_telegram(task.input_file_id, work_dir)
    else:
        # Download from URL
        return download_from_url(task.input_url, work_dir)


def download_from_telegram(file_id: str, work_dir: Path) -> str:
    """Download video from Telegram."""
    try:
        bot = Bot(token=settings.BOT_TOKEN)
        
        # Get file
        import asyncio
        file = asyncio.run(bot.get_file(file_id))
        
        # Download file
        output_path = work_dir / f"input{Path(file.file_path).suffix}"
        asyncio.run(bot.download_file(file.file_path, output_path))
        
        logger.info(f"Downloaded from Telegram: {output_path}")
        return str(output_path)
    
    except Exception as e:
        logger.error(f"Error downloading from Telegram: {e}")
        raise


def download_from_url(url: str, work_dir: Path) -> str:
    """Download video from URL using yt-dlp."""
    try:
        output_template = str(work_dir / "input.%(ext)s")
        
        ydl_opts = {
            'format': 'best[ext=mp4]/best',
            'outtmpl': output_template,
            'quiet': False,
            'no_warnings': False,
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)
        
        logger.info(f"Downloaded from URL: {filename}")
        return filename
    
    except Exception as e:
        logger.error(f"Error downloading from URL: {e}")
        raise

