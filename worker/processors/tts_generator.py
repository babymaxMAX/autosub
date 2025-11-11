"""TTS generation for voiceover."""
import logging
import os
import re
from pathlib import Path
from typing import Any, Dict, Optional, Tuple

import requests
import torch
import torchaudio
from TTS.api import TTS
from config.settings import settings
from torch.package import PackageImporter

logger = logging.getLogger(__name__)


class TTSLanguageUnsupported(Exception):
    """Raised when a requested language does not have a configured TTS model."""

    def __init__(self, language: str):
        self.language = language
        super().__init__(f"TTS language '{language}' is not available in the TTS catalog")


class TTSModelLoadError(Exception):
    """Raised when a TTS backend model fails to load."""

    def __init__(self, model_name: str, cause: Exception):
        self.model_name = model_name
        super().__init__(f"Failed to load TTS model '{model_name}': {cause}")
        self.__cause__ = cause


# TTS model cache
_tts_models: Dict[str, TTS] = {}
_silero_models: Dict[str, Any] = {}

MODEL_CATALOG: Dict[str, Dict[str, Dict[str, Any]]] = {
    "en": {
        "female": {
            "backend": "coqui",
            "model": "tts_models/en/ljspeech/tacotron2-DDC",
            "speaker": None,
        },
        "male": {
            "backend": "coqui",
            "model": "tts_models/en/vctk/vits",
            "speaker": None,
            # Try multiple male speakers; fall back gracefully if unavailable
            "speaker_candidates": ["p258", "p270", "p362", "p248", "p292", "p306", "p254", "p278"],
        },
    },
    "ru": {
        "female": {
            "backend": "coqui",
            "model": "tts_models/ru/mai_female/glow-tts",
            "speaker": None,
        },
        "male": {
            "backend": "coqui",
            "model": "tts_models/ru/ruslan/vits",
            "speaker": None,
        },
    },
    "es": {
        "female": {
            "backend": "coqui",
            "model": "tts_models/es/mai/tacotron2-DDC",
            "speaker": None,
        },
        "male": {
            "backend": "coqui",
            "model": "tts_models/es/css10/vits",
            "speaker": None,
        },
    },
    "fr": {
        "female": {
            "backend": "coqui",
            "model": "tts_models/fr/mai/tacotron2-DDC",
            "speaker": None,
        },
        "male": {
            "backend": "coqui",
            "model": "tts_models/fr/css10/vits",
            "speaker": None,
        },
    },
    "de": {
        "female": {
            "backend": "coqui",
            "model": "tts_models/de/thorsten/tacotron2-DDC",
            "speaker": None,
        },
        "male": {
            "backend": "coqui",
            "model": "tts_models/de/thorsten/tacotron2-DDC",
            "speaker": None,
        },
    },
    "it": {
        "female": {
            "backend": "coqui",
            "model": "tts_models/it/mai_female/vits",
            "speaker": None,
        },
        "male": {
            "backend": "coqui",
            "model": "tts_models/it/css10/vits",
            "speaker": None,
        },
    },
}

# Languages we can serve via gTTS fallback if Coqui models are unavailable
_GTTS_LANG_CACHE: Optional[Dict[str, str]] = None
# Map internal two-letter codes to preferred gTTS codes
GTT_LANGUAGE_ALIASES = {
    "en": "en",
    "ru": "ru",
    "es": "es",
    "fr": "fr",
    "de": "de",
    "it": "it",
}


def _get_tts_cache_dir() -> Optional[Path]:
    """Return cache directory used for TTS models."""
    cache_dir: Optional[Path] = None
    if settings.TTS_CACHE_DIR:
        cache_dir = Path(settings.TTS_CACHE_DIR)
    elif settings.STORAGE_PATH:
        cache_dir = Path(settings.STORAGE_PATH) / ".models" / "tts"
    if cache_dir:
        cache_dir.mkdir(parents=True, exist_ok=True)
    return cache_dir


def _resolve_lang_key(language: str) -> str:
    """Normalize language value to a two-letter Coqui catalog key."""
    if not language:
        return "en"
    lang = language.lower()
    if len(lang) >= 2:
        return lang[:2]
    return "en"


def _select_model_config(language: str, voice: str) -> Tuple[Dict[str, Any], str]:
    """Return backend configuration for language/voice or raise if unsupported."""
    lang_key = _resolve_lang_key(language)
    logger.info(f"TTS: Selecting model for language={language} (resolved={lang_key}), voice={voice}")
    
    catalog = MODEL_CATALOG.get(lang_key)
    if not catalog:
        logger.error(f"TTS: No catalog found for language {lang_key}")
        raise TTSLanguageUnsupported(language)
    
    logger.info(f"TTS: Available voices for {lang_key}: {list(catalog.keys())}")
    
    if voice not in catalog:
        cfg = catalog.get("female") or next(iter(catalog.values()))
        logger.warning(
            "TTS voice '%s' not available for language %s, falling back to default voice.",
            voice,
            language,
        )
        return cfg, lang_key
    
    cfg = catalog[voice]
    logger.info(f"TTS: Selected config for {voice}: {cfg}")
    return cfg, lang_key


def _get_coqui_model(model_name: str, language: str, voice: str) -> TTS:
    """Get or initialize a Coqui TTS model by name."""
    global _tts_models

    if model_name in _tts_models:
        return _tts_models[model_name]

    cache_dir = _get_tts_cache_dir()

    try:
        logger.info(
            "Loading Coqui TTS model %s for language=%s, voice=%s (cache: %s)",
            model_name,
            language,
            voice,
            cache_dir,
        )
        if cache_dir:
            os.environ["TTS_HOME"] = str(cache_dir)
        model = TTS(model_name=model_name, progress_bar=False, gpu=False)
        _tts_models[model_name] = model
        logger.info("Coqui TTS model loaded successfully")
        return model
    except Exception as e:
        raise TTSModelLoadError(model_name, e) from e


def _ensure_silero_model_file(model_name: str, model_url: str) -> Path:
    """Ensure Silero model file is downloaded and return its path."""
    cache_root = _get_tts_cache_dir() or (Path.home() / ".cache" / "autosub" / "tts")
    model_dir = cache_root / "silero"
    model_dir.mkdir(parents=True, exist_ok=True)
    model_path = model_dir / model_name
    if model_path.exists():
        return model_path

    logger.info("Downloading Silero TTS model %s from %s", model_name, model_url)
    tmp_path = model_path.with_suffix(".tmp")
    try:
        with requests.get(model_url, stream=True, timeout=60) as response:
            response.raise_for_status()
            with open(tmp_path, "wb") as f:
                for chunk in response.iter_content(chunk_size=65536):
                    if chunk:
                        f.write(chunk)
        tmp_path.replace(model_path)
        logger.info("Silero model downloaded: %s", model_path)
    except Exception as exc:
        if tmp_path.exists():
            tmp_path.unlink(missing_ok=True)
        raise TTSModelLoadError(model_name, exc) from exc

    return model_path


def _get_silero_model(model_name: str, model_url: str) -> Tuple[Any, torch.device]:
    """Load and cache Silero TTS model."""
    if model_name in _silero_models:
        return _silero_models[model_name]

    model_path = _ensure_silero_model_file(model_name, model_url)
    try:
        importer = PackageImporter(str(model_path))
        model = importer.load_pickle("tts_models", "model")
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        if hasattr(model, "to"):
            model.to(device)
        if hasattr(model, "eval"):
            model.eval()
        _silero_models[model_name] = (model, device)
        logger.info(
            "Silero TTS model loaded successfully (%s) on device=%s", model_name, device
        )
        return _silero_models[model_name]
    except Exception as exc:
        raise TTSModelLoadError(model_name, exc) from exc


def _turkish_safe_lower(text: str) -> str:
    """Lowercase text using Turkish-specific casing rules."""
    mapping = str.maketrans({"I": "ı", "İ": "i"})
    return text.translate(mapping).lower()


def _prepare_text_for_backend(language: str, config: Dict[str, Any], text: str) -> str:
    """Apply language/backend specific text normalisation before synthesis."""
    filter_type = config.get("text_filter")
    if filter_type == "lowercase" and language == "tr":
        return _turkish_safe_lower(text)
    return text


def _synthesize_with_coqui(
    config: Dict[str, Any],
    language: str,
    voice: str,
    text: str,
    output_path: Path,
) -> str:
    """Generate speech using Coqui TTS backend."""
    model_name = config["model"]
    speaker = config.get("speaker")
    model = _get_coqui_model(model_name, language, voice)

    logger.info(
        "Generating voiceover with Coqui (model=%s, speaker=%s)", model_name, speaker
    )
    
    # Check available speakers
    available_speakers = list(getattr(model, "speakers", []) or [])
    logger.info(f"TTS: Available speakers for model {model_name}: {available_speakers}")
    
    speaker_candidates = config.get("speaker_candidates", [])
    chosen_speaker = None
    if speaker and available_speakers and speaker in available_speakers:
        chosen_speaker = speaker
    elif speaker_candidates and available_speakers:
        for candidate in speaker_candidates:
            if candidate in available_speakers:
                chosen_speaker = candidate
                break
        if chosen_speaker:
            logger.info(f"TTS: Selected candidate speaker {chosen_speaker}")
        else:
            logger.warning(
                "TTS: None of the candidate speakers %s present in model %s; using default voice",
                speaker_candidates,
                model_name,
            )
    elif speaker and available_speakers:
        logger.warning(f"TTS: Speaker {speaker} not found in available speakers, using default")
    elif speaker and not available_speakers:
        logger.warning(f"TTS: Model {model_name} does not expose speakers; ignoring speaker='{speaker}'")
    
    tts_kwargs = {"text": text, "file_path": str(output_path)}
    if chosen_speaker:
        tts_kwargs["speaker"] = chosen_speaker
    
    logger.info(f"TTS: Calling tts_to_file with kwargs: {tts_kwargs}")
    model.tts_to_file(**tts_kwargs)

    if not output_path.exists():
        raise RuntimeError("Coqui voiceover file was not created")

    logger.info(
        "Voiceover saved: %s (%d bytes)", output_path, output_path.stat().st_size
    )
    return str(output_path)


def _synthesize_with_silero(
    config: Dict[str, Any],
    language: str,
    text: str,
    output_path: Path,
) -> str:
    """Generate speech using Silero TTS backend."""
    model_name = config["model"]
    model_url = config.get("model_url")
    if not model_url:
        raise ValueError(f"Silero model URL missing for {language}")
    speaker = config.get("speaker")
    sample_rate = int(config.get("sample_rate", 48000))

    silero_model, device = _get_silero_model(model_name, model_url)
    logger.info(
        "Generating voiceover with Silero (model=%s, speaker=%s, sample_rate=%s, device=%s)",
        model_name,
        speaker,
        sample_rate,
        device,
    )

    audio = silero_model.apply_tts(
        text=text,
        speaker=speaker,
        sample_rate=sample_rate,
    )

    audio_tensor = torch.tensor(audio, dtype=torch.float32)
    if audio_tensor.dim() == 1:
        audio_tensor = audio_tensor.unsqueeze(0)
    elif audio_tensor.dim() > 2:
        raise RuntimeError(
            f"Unexpected audio tensor shape from Silero: {audio_tensor.shape}"
        )

    torchaudio.save(str(output_path), audio_tensor.cpu(), sample_rate)

    if not output_path.exists():
        raise RuntimeError("Silero voiceover file was not created")

    logger.info(
        "Voiceover saved: %s (%d bytes)", output_path, output_path.stat().st_size
    )
    return str(output_path)


def _load_gtts_languages() -> Dict[str, str]:
    """Load and memoize gTTS available languages."""
    global _GTTS_LANG_CACHE
    if _GTTS_LANG_CACHE is not None:
        return _GTTS_LANG_CACHE
    try:
        from gtts.lang import tts_langs
    except ImportError:
        logger.error(
            "gTTS package is not installed. Install `gTTS` to enable multilingual voiceover fallback."
        )
        _GTTS_LANG_CACHE = {}
        return _GTTS_LANG_CACHE
    try:
        _GTTS_LANG_CACHE = tts_langs()
    except Exception as e:
        logger.error(f"Failed to load gTTS languages: {e}")
        _GTTS_LANG_CACHE = {}
    return _GTTS_LANG_CACHE


def _resolve_gtts_language(language: str) -> Optional[str]:
    """Resolve requested language to a gTTS language code."""
    langs = _load_gtts_languages()
    if not langs:
        return None
    
    if not language:
        return "en" if "en" in langs else None
    
    lang_lower = language.lower()
    candidates = [
        GTT_LANGUAGE_ALIASES.get(lang_lower),
        lang_lower,
        lang_lower.replace("_", "-"),
        lang_lower.replace("-", "_"),
        GTT_LANGUAGE_ALIASES.get(lang_lower[:2]),
        lang_lower[:2],
    ]
    
    for candidate in candidates:
        if candidate and candidate in langs:
            return candidate
    
    prefix = lang_lower[:2]
    for code in langs.keys():
        if code.startswith(prefix):
            return code
    return None


def _generate_voiceover_gtts(text: str, language: str, output_path: Path) -> Optional[str]:
    """Generate voiceover using gTTS as a fallback."""
    gtts_lang = _resolve_gtts_language(language)
    if not gtts_lang:
        logger.error(f"gTTS fallback unavailable for language '{language}'")
        return None
    
    try:
        from gtts import gTTS
    except ImportError:
        logger.error("gTTS package is not installed. Unable to synthesize fallback voiceover.")
        return None
    
    try:
        logger.info(f"Using gTTS fallback for language '{language}' resolved as '{gtts_lang}'")
        tts = gTTS(text=text, lang=gtts_lang)
        tts.save(str(output_path))
        logger.info(f"gTTS voiceover saved: {output_path}")
        return str(output_path)
    except Exception as e:
        logger.error(f"gTTS synthesis failed for language '{language}': {e}", exc_info=True)
        return None


def parse_srt_to_segments(srt_content: str) -> list:
    """Parse SRT content to segments with timing."""
    segments = []
    pattern = r'(\d+)\n(\d{2}:\d{2}:\d{2},\d{3}) --> (\d{2}:\d{2}:\d{2},\d{3})\n(.*?)(?=\n\n|\Z)'
    
    matches = re.findall(pattern, srt_content, re.DOTALL)
    
    def srt_time_to_seconds(time_str: str) -> float:
        """Convert SRT time format to seconds."""
        h, m, s_ms = time_str.split(':')
        s, ms = s_ms.split(',')
        return int(h) * 3600 + int(m) * 60 + int(s) + int(ms) / 1000
    
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
                'start_time': srt_time_to_seconds(start),
                'end_time': srt_time_to_seconds(end),
                'text': text
            })
    
    return segments


def generate_voiceover_synchronized(srt_path: str, output_dir: Path, language: str = "en", voice: str = "female") -> str:
    """Generate synchronized voiceover from SRT subtitles with timing."""
    try:
        # Read subtitles
        with open(srt_path, "r", encoding="utf-8") as f:
            content = f.read()
        
        # Parse subtitles
        segments = parse_srt_to_segments(content)
        
        if not segments:
            logger.warning("No text found in subtitles")
            return None
        
        # Get TTS backend configuration
        try:
            backend_config, resolved_lang = _select_model_config(language, voice)
        except TTSLanguageUnsupported as exc:
            logger.info(
                "No local TTS backend for language '%s': %s. Using simple voiceover fallback.",
                language,
                exc,
            )
            # Fallback to simple voiceover for unsupported languages
            return generate_voiceover_simple(srt_path, output_dir, language, voice)

        backend = backend_config.get("backend", "coqui")
        
        # Generate individual segment audio files
        segment_files = []
        temp_dir = output_dir / "tts_segments"
        temp_dir.mkdir(exist_ok=True)
        
        for i, segment in enumerate(segments):
            text = segment['text'].strip()
            if not text:
                continue
                
            segment_output = temp_dir / f"segment_{i:04d}.wav"
            normalized_text = _prepare_text_for_backend(resolved_lang, backend_config, text)
            
            try:
                if backend == "coqui":
                    _synthesize_with_coqui(
                        backend_config,
                        resolved_lang,
                        voice,
                        normalized_text,
                        segment_output
                    )
                elif backend == "silero":
                    _synthesize_with_silero(
                        backend_config,
                        resolved_lang,
                        voice,
                        normalized_text,
                        segment_output
                    )
                
                if segment_output.exists():
                    segment_files.append({
                        'file': segment_output,
                        'start_time': segment['start_time'],
                        'end_time': segment['end_time'],
                        'duration': segment['end_time'] - segment['start_time']
                    })
                    
            except Exception as e:
                logger.warning(f"Failed to generate TTS for segment {i}: {e}")
                continue
        
        if not segment_files:
            logger.error("No TTS segments generated successfully")
            return None
        
        # Create synchronized audio track using FFmpeg
        output_path = output_dir / "voiceover.wav"
        return _create_synchronized_audio_track(segment_files, output_path)
        
    except Exception as e:
        logger.error(f"Error generating synchronized voiceover: {e}")
        return None


def generate_voiceover_simple(srt_path: str, output_dir: Path, language: str = "en", voice: str = "female") -> str:
    """Generate simple voiceover from SRT subtitles (legacy method)."""
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
        
        output_path = output_dir / "voiceover.wav"

        try:
            backend_config, resolved_lang = _select_model_config(language, voice)
        except TTSLanguageUnsupported as exc:
            logger.info(
                "No local TTS backend for language '%s': %s. Trying gTTS fallback.",
                language,
                exc,
            )
            fallback_path = _generate_voiceover_gtts(full_text, language, output_path)
            if fallback_path:
                return fallback_path
            logger.error(
                "Failed to generate voiceover: language '%s' unsupported and gTTS unavailable.",
                language,
            )
            return None

        backend = backend_config.get("backend", "coqui")
        normalized_text = _prepare_text_for_backend(resolved_lang, backend_config, full_text)
        primary_error: Optional[Exception] = None

        try:
            if backend == "coqui":
                return _synthesize_with_coqui(
                    backend_config,
                    resolved_lang,
                    voice,
                    normalized_text,
                    output_path,
                )
            if backend == "silero":
                return _synthesize_with_silero(
                    backend_config,
                    resolved_lang,
                    normalized_text,
                    output_path,
                )
            if backend == "mms":
                raise NotImplementedError(
                    "MMS TTS backend is not yet implemented in the worker"
                )
            raise ValueError(f"Unsupported TTS backend '{backend}'")
        except Exception as exc:
            primary_error = exc
            logger.warning(
                "Primary TTS backend '%s' failed for language '%s': %s. Attempting gTTS fallback.",
                backend,
                language,
                exc,
                exc_info=True,
            )

        fallback_path = _generate_voiceover_gtts(full_text, language, output_path)
        if fallback_path:
            return fallback_path
        
        logger.error(
            "Failed to generate voiceover with backend '%s' and gTTS fallback.",
            backend,
        )
        if primary_error:
            logger.error("Primary backend error: %s", primary_error, exc_info=True)
        return None
    
    except Exception as e:
        logger.error(f"Error generating voiceover: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return None


def _create_synchronized_audio_track(segment_files: list, output_path: Path) -> str:
    """Create synchronized audio track from individual TTS segments using FFmpeg."""
    import subprocess
    
    TARGET_SAMPLE_RATE = 44100
    
    try:
        # Calculate total duration from the last segment
        if not segment_files:
            return None
            
        total_duration = max(seg['end_time'] for seg in segment_files)
        
        # Create FFmpeg filter complex for synchronized audio
        filter_parts = []
        input_files = []
        
        # Add silence as base track
        filter_parts.append(f"anullsrc=channel_layout=stereo:sample_rate={TARGET_SAMPLE_RATE}:duration={total_duration}[silence]")
        
        # Process each segment
        for i, segment in enumerate(segment_files):
            input_files.extend(["-i", str(segment['file'])])
            
            # Add delay to position audio at correct time
            delay_ms = int(segment['start_time'] * 1000)
            duration = max(segment['duration'], 0.01)
            filter_parts.append(
                f"[{i}:a]aresample={TARGET_SAMPLE_RATE},atrim=0:{duration},asetpts=PTS-STARTPTS,"
                f"adelay={delay_ms}|{delay_ms}[seg{i}]"
            )
        
        # Mix all delayed segments with silence
        mix_inputs = "[silence]" + "".join(f"[seg{i}]" for i in range(len(segment_files)))
        
        filter_parts.append(
            f"{mix_inputs}amix=inputs={len(segment_files)+1}:duration=first:dropout_transition=0,"
            f"aresample={TARGET_SAMPLE_RATE}[out]"
        )
        
        # Build FFmpeg command
        cmd = ["ffmpeg", "-y"]  # -y to overwrite output
        
        # Add input files
        cmd.extend(input_files)
        
        # Add filter complex
        filter_complex = ";".join(filter_parts)
        cmd.extend(["-filter_complex", filter_complex])
        
        # Map output and set codec
        cmd.extend(["-map", "[out]", "-c:a", "pcm_s16le", str(output_path)])
        
        logger.info(f"Creating synchronized audio with {len(segment_files)} segments")
        logger.debug(f"FFmpeg command: {' '.join(cmd)}")
        
        # Run FFmpeg
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
        
        if result.returncode != 0:
            logger.error(f"FFmpeg failed: {result.stderr}")
            return None
        
        if output_path.exists():
            logger.info(f"Synchronized voiceover created: {output_path}")
            return str(output_path)
        else:
            logger.error("Output file was not created")
            return None
            
    except Exception as e:
        logger.error(f"Error creating synchronized audio track: {e}")
        return None


# Alias for backward compatibility
def generate_voiceover(srt_path: str, output_dir: Path, language: str = "en", voice: str = "female") -> str:
    """Generate voiceover - uses synchronized method by default."""
    return generate_voiceover_synchronized(srt_path, output_dir, language, voice)

