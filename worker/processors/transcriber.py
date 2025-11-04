"""Audio transcription using Faster-Whisper."""
import os
import logging
from pathlib import Path
from faster_whisper import WhisperModel
from config.settings import settings

logger = logging.getLogger(__name__)

# Initialize Whisper model (lazy loading)
_whisper_model = None


def get_whisper_model():
    """Get or initialize Whisper model with caching."""
    global _whisper_model
    if _whisper_model is None:
        # Determine cache directory
        cache_dir = None
        if settings.WHISPER_CACHE_DIR:
            cache_dir = Path(settings.WHISPER_CACHE_DIR)
            cache_dir.mkdir(parents=True, exist_ok=True)
        elif settings.STORAGE_PATH:
            # Use storage/.models/whisper as default cache
            cache_dir = Path(settings.STORAGE_PATH) / ".models" / "whisper"
            cache_dir.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"Loading Whisper model: {settings.WHISPER_MODEL} (cache: {cache_dir})")
        
        model_kwargs = {
            "device": settings.WHISPER_DEVICE,
            "compute_type": "int8" if settings.WHISPER_DEVICE == "cpu" else "float16"
        }
        
        # Set cache directory if available
        if cache_dir:
            # Faster-Whisper uses HF_HOME or local cache
            os.environ["HF_HOME"] = str(cache_dir)
            model_kwargs["download_root"] = str(cache_dir)
        
        _whisper_model = WhisperModel(
            settings.WHISPER_MODEL,
            **model_kwargs
        )
        logger.info("Whisper model loaded successfully")
    return _whisper_model


def transcribe_audio(video_path: str, output_dir: Path, language: str = "auto") -> str:
    """Transcribe audio from video."""
    try:
        model = get_whisper_model()
        
        # Transcribe
        logger.info(f"Transcribing: {video_path}")
        segments, info = model.transcribe(
            video_path,
            language=None if language == "auto" else language,
            beam_size=5,
            vad_filter=True,
        )
        
        detected_language = info.language
        logger.info(f"Detected language: {detected_language}")
        
        # Save as SRT
        output_path = output_dir / "subtitles.srt"
        with open(output_path, "w", encoding="utf-8") as f:
            for i, segment in enumerate(segments, start=1):
                start_time = format_timestamp(segment.start)
                end_time = format_timestamp(segment.end)
                text = segment.text.strip()
                
                f.write(f"{i}\n")
                f.write(f"{start_time} --> {end_time}\n")
                f.write(f"{text}\n\n")
        
        logger.info(f"Subtitles saved: {output_path}")
        return str(output_path)
    
    except Exception as e:
        logger.error(f"Error transcribing audio: {e}")
        raise


def format_timestamp(seconds: float) -> str:
    """Format timestamp for SRT format."""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    millis = int((seconds % 1) * 1000)
    return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"

