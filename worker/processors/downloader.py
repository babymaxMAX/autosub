"""Video downloader."""
import os
import logging
from pathlib import Path
from typing import Optional
import yt_dlp
from yt_dlp.utils import DownloadError as YTDLPError
from aiogram import Bot
from config.settings import settings

logger = logging.getLogger(__name__)

# Try to import instaloader for Instagram fallback
try:
    import instaloader
    INSTALOADER_AVAILABLE = True
except ImportError:
    INSTALOADER_AVAILABLE = False
    logger.warning("instaloader not available, Instagram fallback disabled")


def download_video(task, work_dir: Path) -> str:
    """Download video from URL or Telegram."""
    
    if task.input_type == "file":
        # Download from Telegram
        return download_from_telegram(task.input_file_id, work_dir)
    else:
        # Download from URL
        return download_from_url(task.input_url, work_dir, task.input_type)


def download_from_telegram(file_id: str, work_dir: Path) -> str:
    """Download video from Telegram."""
    bot = None
    try:
        import asyncio
        
        # Create bot with proper session management
        bot = Bot(token=settings.BOT_TOKEN)
        
        # Get file
        file = asyncio.run(bot.get_file(file_id))
        
        # Download file
        output_path = work_dir / f"input{Path(file.file_path).suffix}"
        asyncio.run(bot.download_file(file.file_path, output_path))
        
        logger.info(f"Downloaded from Telegram: {output_path}")
        return str(output_path)
    
    except Exception as e:
        logger.error(f"Error downloading from Telegram: {e}", exc_info=True)
        raise
    finally:
        # Properly close bot session to avoid conflicts
        if bot is not None:
            try:
                import asyncio
                asyncio.run(bot.session.close())
            except Exception as e:
                logger.warning(f"Error closing bot session: {e}")


def _get_instagram_headers() -> dict:
    """Get headers for Instagram downloads."""
    return {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:117.0) Gecko/20100101 Firefox/117.0',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
    }


def _get_platform_opts(source: str, url: str) -> dict:
    """Get platform-specific yt-dlp options."""
    base_opts = {
        'quiet': True,
        'no_warnings': True,
        'extract_flat': False,
        'writeinfojson': False,
        'writethumbnail': False,
        'noplaylist': True,
        'socket_timeout': settings.DOWNLOAD_TIMEOUT,
        'retries': settings.DOWNLOAD_RETRIES,
        'fragment_retries': settings.DOWNLOAD_RETRIES,
    }
    
    if source == "tiktok":
        return {
            **base_opts,
            'format': 'best',
            'extractor_args': {
                'tiktok': {
                    'webpage_download': True,
                }
            },
            'compat_opts': ['no-playlist'],
        }
    
    elif source == "instagram":
        opts = {
            **base_opts,
            'format': 'bestvideo+bestaudio/best',
            'socket_timeout': settings.INSTAGRAM_TIMEOUT,
            'retries': settings.INSTAGRAM_RETRIES,
            'fragment_retries': settings.INSTAGRAM_RETRIES,
            'http_headers': _get_instagram_headers(),
            'extractor_args': {
                'instagram': {
                    'post_format': 'video',
                }
            },
        }
        
        # Add proxy if configured
        if settings.INSTAGRAM_PROXY:
            opts['proxy'] = settings.INSTAGRAM_PROXY
            logger.info(f"Using proxy for Instagram: {settings.INSTAGRAM_PROXY}")
        
        # Add cookies if configured
        if settings.INSTAGRAM_COOKIES_FILE and os.path.exists(settings.INSTAGRAM_COOKIES_FILE):
            opts['cookiefile'] = settings.INSTAGRAM_COOKIES_FILE
            logger.info(f"Using cookies file: {settings.INSTAGRAM_COOKIES_FILE}")
        
        return opts
    
    elif source == "youtube":
        return {
            **base_opts,
            'format': 'bestvideo[height<=1080][ext=mp4]+bestaudio[ext=m4a]/best[height<=1080][ext=mp4]/best',
            'no_playlist': True,
        }
    
    # Default for unknown sources
    return {
        **base_opts,
        'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
    }


def _extract_instagram_shortcode(url: str) -> Optional[str]:
    """Extract Instagram shortcode from URL."""
    import re
    patterns = [
        r'instagram\.com/(?:p|reel|tv)/([A-Za-z0-9_-]+)',
        r'instagram\.com/p/([A-Za-z0-9_-]+)',
        r'instagram\.com/reel/([A-Za-z0-9_-]+)',
    ]
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    return None


def download_from_instagram_instaloader(url: str, work_dir: Path) -> str:
    """Download Instagram video using instaloader as fallback."""
    if not INSTALOADER_AVAILABLE:
        raise Exception("instaloader not available, cannot use fallback")
    
    shortcode = _extract_instagram_shortcode(url)
    if not shortcode:
        raise Exception("Could not extract Instagram shortcode from URL")
    
    try:
        logger.info(f"Trying instaloader fallback for Instagram shortcode: {shortcode}")
        
        # Create instaloader instance
        loader = instaloader.Instaloader(
            quiet=True,
            download_videos=True,
            download_video_thumbnails=False,
            download_geotags=False,
            download_comments=False,
            save_metadata=False,
            compress_json=False,
        )
        
        # Set download directory
        output_path = work_dir / "input.mp4"
        
        # Download post
        try:
            post = instaloader.Post.from_shortcode(loader.context, shortcode)
            
            if post.is_video:
                # Download video - instaloader saves as {shortcode}.mp4
                video_url = post.video_url
                if not video_url:
                    raise Exception("Video URL not found in post")
                
                # Download video file directly
                import requests
                response = requests.get(video_url, stream=True, timeout=settings.INSTAGRAM_TIMEOUT)
                response.raise_for_status()
                
                with open(output_path, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        if chunk:
                            f.write(chunk)
                
                if not output_path.exists() or output_path.stat().st_size == 0:
                    raise Exception("Downloaded video file is empty")
                
                logger.info(f"Downloaded via instaloader: {output_path} ({output_path.stat().st_size} bytes)")
                return str(output_path)
            else:
                raise Exception("Post is not a video")
                
        except instaloader.exceptions.LoginRequiredException:
            raise Exception("Instagram login required. Please configure INSTAGRAM_COOKIES_FILE or use proxy.")
        except instaloader.exceptions.PrivateProfileNotFollowedException:
            raise Exception("Instagram profile is private and not followed.")
        except Exception as e:
            logger.error(f"instaloader error: {e}", exc_info=True)
            raise Exception(f"Failed to download via instaloader: {str(e)}")
            
    except Exception as e:
        logger.error(f"Error downloading from Instagram via instaloader: {e}", exc_info=True)
        raise


def download_from_url(url: str, work_dir: Path, source: str = None) -> str:
    """Download video from URL using yt-dlp with enhanced support for TikTok, Instagram, etc."""
    output_template = str(work_dir / "input.%(ext)s")
    
    # Get platform-specific options
    ydl_opts = _get_platform_opts(source, url)
    ydl_opts['outtmpl'] = output_template
    
    # Try downloading with error handling and fallback
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # Extract info first to check if video is available
            logger.info(f"Extracting video info from {url} (source: {source})...")
            try:
                info = ydl.extract_info(url, download=False)
            except (YTDLPError, Exception) as e:
                error_msg = str(e).lower()
                if 'timeout' in error_msg or 'timed out' in error_msg:
                    raise Exception(f"Timeout while accessing {source or 'platform'}. Please try again later.")
                elif 'blocked' in error_msg or 'unable to download' in error_msg:
                    if source == "instagram":
                        raise Exception(f"Instagram video is not accessible. It may be private or require authentication. Please check the URL or try using a proxy.")
                    else:
                        raise Exception(f"Video is not accessible. Please check the URL.")
                else:
                    raise Exception(f"Failed to access video: {str(e)}")
            
            # Log video info
            logger.info(f"Video info - Title: {info.get('title', 'Unknown')}, "
                      f"Duration: {info.get('duration', 0)}s, "
                      f"Platform: {info.get('extractor', 'Unknown')}, "
                      f"Formats: {len(info.get('formats', []))}")
            
            # Download video
            logger.info(f"Starting download from {url}...")
            ydl.download([url])
            
            # Get downloaded filename
            filename = ydl.prepare_filename(info)
            
            # Check if file exists (sometimes extension differs)
            if not os.path.exists(filename):
                # Try to find the actual downloaded file
                logger.info(f"File not found at {filename}, searching in work_dir...")
                downloaded_files = list(work_dir.glob("input.*"))
                if downloaded_files:
                    filename = str(downloaded_files[0])
                    logger.info(f"Found downloaded file: {filename}")
                else:
                    raise Exception(f"Downloaded file not found: {filename}")
            
            # Verify file size
            file_size = os.path.getsize(filename)
            logger.info(f"Downloaded from URL ({source}): {filename} ({file_size} bytes)")
            
            if file_size == 0:
                raise Exception(f"Downloaded file is empty: {filename}")
            
            return filename
            
    except YTDLPError as e:
        logger.error(f"yt-dlp download error: {e}", exc_info=True)
        error_msg = str(e).lower()
        
        # Try fallback format for specific errors
        if 'format' in error_msg or 'codec' in error_msg:
            logger.info("Trying fallback format...")
            ydl_opts['format'] = 'best'
            try:
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    info = ydl.extract_info(url, download=True)
                    filename = ydl.prepare_filename(info)
                    if not os.path.exists(filename):
                        downloaded_files = list(work_dir.glob("input.*"))
                        if downloaded_files:
                            filename = str(downloaded_files[0])
                    file_size = os.path.getsize(filename) if os.path.exists(filename) else 0
                    if file_size == 0:
                        raise Exception(f"Downloaded file is empty: {filename}")
                    logger.info(f"Downloaded with fallback format: {filename} ({file_size} bytes)")
                    return filename
            except Exception as fallback_error:
                logger.error(f"Fallback download also failed: {fallback_error}", exc_info=True)
                raise Exception(f"Failed to download video after fallback: {str(fallback_error)}")
        else:
            # Re-raise with user-friendly message
            if 'timeout' in error_msg or 'timed out' in error_msg:
                raise Exception(f"Download timeout. {source or 'Platform'} may be slow or unavailable. Please try again later.")
            elif 'instagram' in error_msg and ('blocked' in error_msg or 'unable' in error_msg or 'unable to extract' in error_msg):
                # Try instaloader fallback for Instagram
                if source == "instagram" and INSTALOADER_AVAILABLE:
                    logger.info("yt-dlp failed for Instagram, trying instaloader fallback...")
                    try:
                        return download_from_instagram_instaloader(url, work_dir)
                    except Exception as insta_error:
                        logger.error(f"instaloader fallback also failed: {insta_error}", exc_info=True)
                        raise Exception(f"Instagram video is not accessible. yt-dlp and instaloader both failed. Error: {str(insta_error)}")
                else:
                    raise Exception(f"Instagram video is not accessible. It may be private or require authentication.")
            else:
                raise Exception(f"Failed to download video: {str(e)}")
    
    except Exception as e:
        logger.error(f"Error downloading from URL ({url}): {e}", exc_info=True)
        # For Instagram, try instaloader fallback if yt-dlp completely failed
        if source == "instagram" and INSTALOADER_AVAILABLE:
            error_msg = str(e).lower()
            if 'unable to extract' in error_msg or 'unable to download' in error_msg:
                logger.info("Primary download failed, trying instaloader fallback for Instagram...")
                try:
                    return download_from_instagram_instaloader(url, work_dir)
                except Exception as insta_error:
                    logger.error(f"instaloader fallback also failed: {insta_error}", exc_info=True)
                    # Re-raise original error
                    pass
        
        # Re-raise with context if it's not already a user-friendly message
        if isinstance(e, Exception) and not str(e).startswith(('Failed', 'Timeout', 'Instagram', 'Video')):
            raise Exception(f"Failed to download video: {str(e)}")
        raise

