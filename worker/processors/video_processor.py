"""Video processing with ffmpeg."""
import logging
import subprocess
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)


def process_video_with_subtitles(
    input_video_path: str,
    subtitles_path: Optional[str],
    voiceover_path: Optional[str],
    output_dir: Path,
    vertical_format: bool = False,
    add_watermark: bool = False,
) -> str:
    """Process video with subtitles, voiceover, and format conversion."""
    try:
        output_path = output_dir / "output.mp4"
        
        # Build ffmpeg command
        cmd = ["ffmpeg", "-i", input_video_path]
        
        # Add voiceover if exists
        if voiceover_path:
            cmd.extend(["-i", voiceover_path])
        
        # Filter complex for video processing
        filters = []
        
        # Convert to vertical format (9:16)
        if vertical_format:
            filters.append(
                "crop=ih*9/16:ih,"  # Crop to 9:16 aspect ratio
                "scale=1080:1920"    # Scale to 1080x1920
            )
        
        # Add watermark
        if add_watermark:
            watermark_text = "AutoSub"
            filters.append(
                f"drawtext=text='{watermark_text}':"
                "fontsize=24:fontcolor=white@0.5:"
                "x=(w-text_w)-10:y=(h-text_h)-10"
            )
        
        # Burn subtitles
        if subtitles_path:
            # Escape path for ffmpeg
            srt_path_escaped = subtitles_path.replace("\\", "/").replace(":", "\\\\:")
            filters.append(f"subtitles='{srt_path_escaped}'")
        
        # Apply filters
        if filters:
            cmd.extend(["-vf", ",".join(filters)])
        
        # Audio mapping
        if voiceover_path:
            # Mix original audio with voiceover
            cmd.extend([
                "-filter_complex",
                "[0:a][1:a]amix=inputs=2:duration=first[aout]",
                "-map", "0:v",
                "-map", "[aout]",
            ])
        
        # Output settings
        cmd.extend([
            "-c:v", "libx264",
            "-preset", "medium",
            "-crf", "23",
            "-c:a", "aac",
            "-b:a", "128k",
            "-movflags", "+faststart",
            "-y",  # Overwrite output
            str(output_path)
        ])
        
        logger.info(f"Running ffmpeg: {' '.join(cmd)}")
        
        # Run ffmpeg
        result = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        
        if result.returncode != 0:
            logger.error(f"ffmpeg error: {result.stderr}")
            raise Exception(f"ffmpeg failed with code {result.returncode}")
        
        logger.info(f"Video processed successfully: {output_path}")
        return str(output_path)
    
    except Exception as e:
        logger.error(f"Error processing video: {e}")
        raise


def get_video_info(video_path: str) -> dict:
    """Get video information using ffprobe."""
    try:
        cmd = [
            "ffprobe",
            "-v", "quiet",
            "-print_format", "json",
            "-show_format",
            "-show_streams",
            video_path
        ]
        
        result = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        
        if result.returncode == 0:
            import json
            return json.loads(result.stdout)
        else:
            logger.error(f"ffprobe error: {result.stderr}")
            return {}
    
    except Exception as e:
        logger.error(f"Error getting video info: {e}")
        return {}

