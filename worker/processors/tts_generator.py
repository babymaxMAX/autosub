"""TTS generation for voiceover."""
import logging
from pathlib import Path
from TTS.api import TTS

logger = logging.getLogger(__name__)

# TTS model cache
_tts_model = None


def get_tts_model():
    """Get or initialize TTS model."""
    global _tts_model
    if _tts_model is None:
        logger.info("Loading TTS model")
        # Using a lightweight model for now
        _tts_model = TTS(model_name="tts_models/en/ljspeech/tacotron2-DDC", progress_bar=False)
    return _tts_model


def generate_voiceover(srt_path: str, output_dir: Path, language: str = "en") -> str:
    """Generate voiceover from subtitles."""
    try:
        # Read subtitles
        with open(srt_path, "r", encoding="utf-8") as f:
            content = f.read()
        
        # Extract text from subtitles
        import re
        pattern = r'\d+\n\d{2}:\d{2}:\d{2},\d{3} --> \d{2}:\d{2}:\d{2},\d{3}\n(.*?)(?=\n\n|\Z)'
        texts = re.findall(pattern, content, re.DOTALL)
        full_text = " ".join([text.strip() for text in texts])
        
        if not full_text:
            logger.warning("No text found in subtitles")
            return None
        
        # Generate speech
        model = get_tts_model()
        output_path = output_dir / "voiceover.wav"
        
        logger.info(f"Generating voiceover for text: {full_text[:100]}...")
        model.tts_to_file(text=full_text, file_path=str(output_path))
        
        logger.info(f"Voiceover saved: {output_path}")
        return str(output_path)
    
    except Exception as e:
        logger.error(f"Error generating voiceover: {e}")
        return None

