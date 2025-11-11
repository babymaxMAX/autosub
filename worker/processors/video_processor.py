"""Video processing with ffmpeg."""
import logging
import subprocess
import json
import re
from pathlib import Path
from typing import Optional, Dict, Any

from common.subtitle_styles import build_ffmpeg_style

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


def _build_subtitle_style(style_id: str, position: str, language: Optional[str]) -> Dict[str, Any]:
    """Compose subtitle style parameters."""
    style = build_ffmpeg_style(style_id, position, target_language=language)
    # Ensure defaults for ASS conversion
    defaults = {
        "FontName": "Arial",
        "FontSize": 36,
        "Bold": 0,
        "Italic": 0,
        "Spacing": 0,
        "MarginL": 40,
        "MarginR": 40,
        "MarginV": 40,
        "Alignment": 2,
        "Outline": 2,
        "Shadow": 0,
        "BorderStyle": 1,
        "PrimaryColour": "&H00FFFFFF",
        "OutlineColour": "&H00000000",
        "BackColour": "&H80000000",
    }
    defaults.update(style)
    # ASS expects Bold/Italic as -1/0
    defaults["Bold"] = -1 if defaults.get("Bold") else 0
    defaults["Italic"] = -1 if defaults.get("Italic") else 0
    defaults.setdefault("SecondaryColour", defaults["PrimaryColour"])
    defaults.setdefault("Underline", 0)
    defaults.setdefault("StrikeOut", 0)
    defaults.setdefault("ScaleX", 100)
    defaults.setdefault("ScaleY", 100)
    defaults.setdefault("Angle", 0)
    defaults.setdefault("Encoding", 1)
    return defaults


def _srt_to_ass(
    srt_path: str,
    output_dir: Path,
    style: Dict[str, Any],
    play_res_x: int = 1920,
    play_res_y: int = 1080,
) -> Path:
    """Convert SRT subtitles to ASS with provided style."""
    output_path = output_dir / (Path(srt_path).stem + ".ass")
    
    def _time_to_ass(ts: str) -> str:
        h, m, rest = ts.split(":")
        s, ms = rest.split(",")
        centiseconds = int(int(ms) / 10)
        return f"{int(h)}:{int(m):02d}:{int(s):02d}.{centiseconds:02d}"
    
    def _escape_text(text: str) -> str:
        return (
            text.replace("\\", r"\\")
            .replace("{", r"\{")
            .replace("}", r"\}")
            .replace("\n", r"\N")
        )
    
    with open(srt_path, "r", encoding="utf-8") as src, open(output_path, "w", encoding="utf-8") as dst:
        dst.write("[Script Info]\n")
        dst.write("ScriptType: v4.00+\n")
        dst.write("PlayResX: {}\n".format(play_res_x))
        dst.write("PlayResY: {}\n".format(play_res_y))
        dst.write("ScaledBorderAndShadow: yes\n")
        dst.write("\n[V4+ Styles]\n")
        dst.write(
            "Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, "
            "OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, "
            "ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, "
            "MarginL, MarginR, MarginV, Encoding\n"
        )
        dst.write(
            "Style: Default,{FontName},{FontSize},{PrimaryColour},{SecondaryColour},"
            "{OutlineColour},{BackColour},{Bold},{Italic},{Underline},{StrikeOut},"
            "{ScaleX},{ScaleY},{Spacing},{Angle},{BorderStyle},{Outline},{Shadow},"
            "{Alignment},{MarginL},{MarginR},{MarginV},{Encoding}\n".format(**style)
        )
        dst.write("\n[Events]\n")
        dst.write("Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text\n")
        
        entry_pattern = re.compile(
            r"(\d+)\n(\d{2}:\d{2}:\d{2},\d{3}) --> (\d{2}:\d{2}:\d{2},\d{3})\n(.*?)(?=\n\n|\Z)",
            re.DOTALL,
        )
        content = src.read()
        for match in entry_pattern.finditer(content):
            start = _time_to_ass(match.group(2))
            end = _time_to_ass(match.group(3))
            text = _escape_text(match.group(4).strip())
            if not text:
                continue
            dst.write(f"Dialogue: 0,{start},{end},Default,,0,0,0,,{text}\n")
    
    return output_path


def process_video_with_subtitles(
    input_video_path: str,
    subtitles_path: Optional[str],
    voiceover_path: Optional[str],
    output_dir: Path,
    vertical_format: bool = False,
    add_watermark: bool = False,
    subtitle_style: str = "sub36o1",
    subtitle_position: str = "bottom",
    subtitle_language: Optional[str] = None,
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
            style_dict = _build_subtitle_style(subtitle_style, subtitle_position, subtitle_language)
            ass_path = _srt_to_ass(subtitles_path, Path(subtitles_path).parent, style_dict)
            ass_path_escaped = str(ass_path).replace("\\", "/").replace(":", "\\:")
            video_filters.append(f"ass='{ass_path_escaped}'")
        
        # Add watermark
        if add_watermark:
            watermark_text = "AutoSub"
            video_filters.append(
                f"drawtext=text='{watermark_text}':"
                "fontfile=/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf:"
                "fontsize=36:fontcolor=white@0.35:"
                "x=(w-text_w)-30:y=(h-text_h)-40"
            )
        
        # Build audio filter complex if needed
        audio_filters = []
        audio_map = None
        
        if voiceover_path:
            # Mix original audio with voiceover - better balance
            audio_filters.extend([
                "[0:a]volume=0.2[orig_low]",  # Reduce original audio more
                "[1:a]volume=0.8[voice_clear]",  # Slightly reduce voiceover for clarity
                "[orig_low][voice_clear]amix=inputs=2:duration=first:dropout_transition=2,volume=1.2[aout]"  # Boost final output
            ])
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
            # 'copy' is not a filter; use 'null' in filtergraph to pass-through
            filter_complex_parts.append("[0:v]null[vout]")
        
        # Audio filters
        if audio_filters:
            filter_complex_parts.extend(audio_filters)
        else:
            # 'copy' is not a filter; use 'anull' in filtergraph to pass-through
            filter_complex_parts.append("[0:a]anull[aout]")
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

