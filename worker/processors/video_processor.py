"""Video processing with ffmpeg."""
import logging
import subprocess
import json
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)


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
            return json.loads(result.stdout)
        else:
            logger.error(f"ffprobe error: {result.stderr}")
            return {}
    
    except Exception as e:
        logger.error(f"Error getting video info: {e}")
        return {}


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
        
        # Get video info for proper handling
        video_info = get_video_info(input_video_path)
        width = None
        height = None
        
        # Extract dimensions from video info
        if video_info and 'streams' in video_info:
            for stream in video_info['streams']:
                if stream.get('codec_type') == 'video':
                    width = stream.get('width')
                    height = stream.get('height')
                    break
        
        # Build ffmpeg command
        cmd = ["ffmpeg", "-i", input_video_path]
        
        # Add voiceover if exists
        if voiceover_path:
            cmd.extend(["-i", voiceover_path])
        
        # Build filter complex for video processing
        video_filters = []
        
        # Convert to vertical format (9:16)
        if vertical_format:
            if width and height:
                # Calculate crop and scale based on aspect ratio
                video_aspect = width / height
                target_aspect = 9 / 16  # 0.5625
                
                if video_aspect > target_aspect:
                    # Video is wider than 9:16, crop width
                    new_width = int(height * target_aspect)
                    crop_x = (width - new_width) // 2
                    video_filters.append(f"crop={new_width}:{height}:{crop_x}:0")
                elif video_aspect < target_aspect:
                    # Video is taller than 9:16, crop height
                    new_height = int(width / target_aspect)
                    crop_y = (height - new_height) // 2
                    video_filters.append(f"crop={width}:{new_height}:0:{crop_y}")
                
                # Scale to 1080x1920 (9:16)
                video_filters.append("scale=1080:1920:force_original_aspect_ratio=decrease")
                # Add padding if needed to maintain 9:16
                video_filters.append("pad=1080:1920:(ow-iw)/2:(oh-ih)/2:color=black")
            else:
                # Fallback if we can't get dimensions
                video_filters.append("crop=ih*9/16:ih:(iw-oh*9/16)/2:0")
                video_filters.append("scale=1080:1920")
        
        # Burn subtitles (hardsub)
        if subtitles_path:
            # Escape path for ffmpeg (works on both Windows and Linux)
            srt_path_escaped = str(subtitles_path).replace("\\", "/").replace(":", "\\:")
            # Add subtitle styling
            video_filters.append(
                f"subtitles='{srt_path_escaped}':"
                "force_style='FontName=Arial,FontSize=20,"
                "PrimaryColour=&Hffffff,OutlineColour=&H000000,"
                "Outline=2,Shadow=1,MarginV=30'"
            )
        
        # Add watermark
        if add_watermark:
            watermark_text = "AutoSub"
            video_filters.append(
                f"drawtext=text='{watermark_text}':"
                "fontfile=/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf:"
                "fontsize=24:fontcolor=white@0.5:"
                "x=(w-text_w)-10:y=(h-text_h)-10"
            )
        
        # Build audio filter complex if needed
        audio_filters = []
        audio_map = None
        
        if voiceover_path:
            # Mix original audio with voiceover
            audio_filters.append("[0:a][1:a]amix=inputs=2:duration=first:dropout_transition=2[aout]")
            audio_map = "[aout]"
        else:
            audio_map = "[0:a]"
        
        # Build complete filter_complex
        filter_complex_parts = []
        
        # Video filters
        if video_filters:
            video_filter_str = ",".join(video_filters)
            filter_complex_parts.append(f"[0:v]{video_filter_str}[vout]")
        else:
            filter_complex_parts.append("[0:v]copy[vout]")
        
        # Audio filters
        if audio_filters:
            filter_complex_parts.extend(audio_filters)
        else:
            filter_complex_parts.append("[0:a]copy[aout]")
            audio_map = "[aout]"
        
        if filter_complex_parts:
            cmd.extend(["-filter_complex", ";".join(filter_complex_parts)])
            cmd.extend(["-map", "[vout]", "-map", audio_map])
        else:
            cmd.extend(["-c:v", "copy", "-c:a", "copy"])
        
        # Output settings
        output_cmd = [
            "-c:v", "libx264",
            "-preset", "medium",
            "-crf", "23",
            "-c:a", "aac",
            "-b:a", "128k",
            "-movflags", "+faststart",
            "-pix_fmt", "yuv420p",  # Ensure compatibility
            "-y",  # Overwrite output
            str(output_path)
        ]
        
        cmd.extend(output_cmd)
        
        logger.info(f"Running ffmpeg command: {' '.join(cmd)}")
        
        # Run ffmpeg
        result = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        
        if result.returncode != 0:
            logger.error(f"ffmpeg error: {result.stderr}")
            raise Exception(f"ffmpeg failed with code {result.returncode}: {result.stderr[:500]}")
        
        # Verify output file exists
        if not output_path.exists():
            raise Exception(f"Output file was not created: {output_path}")
        
        logger.info(f"Video processed successfully: {output_path}")
        return str(output_path)
    
    except Exception as e:
        logger.error(f"Error processing video: {e}")
        raise

