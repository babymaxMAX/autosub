"""TTS generation for voiceover."""
import os
import logging
import re
from pathlib import Path
from TTS.api import TTS
from config.settings import settings

logger = logging.getLogger(__name__)

# TTS model cache
_tts_models = {}


def get_tts_model(language: str = "en"):
    """Get or initialize TTS model for specific language."""
    global _tts_models
    
    # Normalize language code
    lang_code = language.lower()[:2] if language != "auto" else "en"
    
    # Language to model mapping
    language_models = {
        "en": "tts_models/en/ljspeech/tacotron2-DDC",
        "ru": "tts_models/ru/mai_female/glow-tts",  # Russian female voice
        "es": "tts_models/es/mai_female/glow-tts",  # Spanish
        "fr": "tts_models/fr/mai_female/vits",
        "de": "tts_models/de/thorsten/tacotron2-DDC",
        "it": "tts_models/it/mai_female/vits",
        "pt": "tts_models/pt/cv/vits",
        "pl": "tts_models/pl/mai_female/vits",
        "tr": "tts_models/tr/common-voice/glow-tts",
        "uk": "tts_models/uk/mai_female/vits",  # Ukrainian
        "zh": "tts_models/zh-CN/baker/tacotron2-DDC-GST",
        "ja": "tts_models/ja/kokoro/tacotron2-DDC",
        "ko": "tts_models/ko/korean/jets",
    }
    
    # Get model name
    model_name = language_models.get(lang_code, language_models["en"])
    
    # Return cached model if exists
    if model_name in _tts_models:
        return _tts_models[model_name]
    
    # Determine cache directory
    cache_dir = None
    if settings.TTS_CACHE_DIR:
        cache_dir = Path(settings.TTS_CACHE_DIR)
        cache_dir.mkdir(parents=True, exist_ok=True)
    elif settings.STORAGE_PATH:
        # Use storage/.models/tts as default cache
        cache_dir = Path(settings.STORAGE_PATH) / ".models" / "tts"
        cache_dir.mkdir(parents=True, exist_ok=True)
    
    # Load model
    try:
        logger.info(f"Loading TTS model for language {lang_code}: {model_name} (cache: {cache_dir})")
        
        # Set TTS cache directory if available
        if cache_dir:
            os.environ["TTS_HOME"] = str(cache_dir)
        
        model = TTS(model_name=model_name, progress_bar=False, gpu=False)
        _tts_models[model_name] = model
        logger.info(f"TTS model loaded successfully")
        return model
    except Exception as e:
        logger.warning(f"Failed to load model {model_name}, using English default: {e}")
        # Fallback to English
        if language_models["en"] not in _tts_models:
            fallback_model_name = language_models["en"]
            if cache_dir:
                os.environ["TTS_HOME"] = str(cache_dir)
            model = TTS(model_name=fallback_model_name, progress_bar=False, gpu=False)
            _tts_models[fallback_model_name] = model
        return _tts_models[language_models["en"]]


def parse_srt_to_segments(srt_content: str) -> list:
    """Parse SRT content to segments with timing."""
    segments = []
    pattern = r'(\d+)\n(\d{2}:\d{2}:\d{2},\d{3}) --> (\d{2}:\d{2}:\d{2},\d{3})\n(.*?)(?=\n\n|\Z)'
    
    matches = re.findall(pattern, srt_content, re.DOTALL)
    
    for match in matches:
        index, start, end, text = match
        # Clean text
        text = re.sub(r'<[^>]+>', '', text)  # Remove HTML tags
        text = text.strip().replace('\n', ' ')
        
        if text:
            segments.append({
                'index': int(index),
                'start': start,
                'end': end,
                'text': text
            })
    
    return segments


def generate_voiceover(srt_path: str, output_dir: Path, language: str = "en") -> str:
    """Generate voiceover from SRT subtitles."""
    try:
        # Read subtitles
        with open(srt_path, "r", encoding="utf-8") as f:
            content = f.read()
        
        # Parse subtitles
        segments = parse_srt_to_segments(content)
        
        if not segments:
            logger.warning("No text found in subtitles")
            return None
        
        # Extract full text
        full_text = " ".join([seg['text'] for seg in segments])
        
        if not full_text.strip():
            logger.warning("Empty text in subtitles")
            return None
        
        # Get appropriate TTS model
        model = get_tts_model(language)
        
        # Generate speech
        output_path = output_dir / "voiceover.wav"
        
        logger.info(f"Generating voiceover for {len(segments)} segments, "
                   f"language: {language}, text preview: {full_text[:100]}...")
        
        # Generate TTS
        model.tts_to_file(text=full_text, file_path=str(output_path))
        
        # Verify file was created
        if not output_path.exists():
            raise Exception("Voiceover file was not created")
        
        logger.info(f"Voiceover saved: {output_path} ({output_path.stat().st_size} bytes)")
        return str(output_path)
    
    except Exception as e:
        logger.error(f"Error generating voiceover: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return None

