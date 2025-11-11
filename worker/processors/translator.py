"""Subtitle translation using Argos Translate and MarianMT backends."""
import logging
import os
import re
from functools import lru_cache
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Sequence, Tuple

import argostranslate.package
import argostranslate.translate
import torch
from config.settings import settings
from transformers import MarianMTModel, MarianTokenizer
try:
    from langdetect import detect, DetectorFactory
    # Set seed for consistent results
    DetectorFactory.seed = 0
    LANGDETECT_AVAILABLE = True
except ImportError:
    LANGDETECT_AVAILABLE = False
    logger = logging.getLogger(__name__)
    logger.warning("langdetect not available, using fallback language detection")

logger = logging.getLogger(__name__)

# Installed language packages cache
_installed_languages = set()
_package_index_loaded = False
_languages_loaded = False

# Pivot language used when direct translation is unavailable
PIVOT_LANGUAGE = "en"

# Map UI language codes and aliases to Argos Translate codes
LANGUAGE_ALIASES = {
    "en": "en",
    "ru": "ru",
    "es": "es",
    "fr": "fr",
    "de": "de",
    "it": "it",
}

MARIAN_MODELS: Dict[Tuple[str, str], str] = {}
MARIAN_BATCH_SIZE = 8

# Ensure HF auth token is available for transformers downloads (if provided)
if settings.HUGGINGFACE_TOKEN:
    os.environ.setdefault("HF_TOKEN", settings.HUGGINGFACE_TOKEN)
    os.environ.setdefault("HUGGINGFACEHUB_API_TOKEN", settings.HUGGINGFACE_TOKEN)
    os.environ.setdefault("HUGGINGFACE_HUB_TOKEN", settings.HUGGINGFACE_TOKEN)


def _load_languages(force: bool = False):
    """Ensure Argos Translate cache of installed languages is ready."""
    global _languages_loaded
    if force or not _languages_loaded:
        try:
            argostranslate.translate.load_installed_languages()
            _languages_loaded = True
        except Exception as e:
            logger.error(f"Failed to load Argos languages: {e}")
            _languages_loaded = False


def ensure_language_package(from_code: str, to_code: str) -> bool:
    """Ensure translation package is installed. Returns True if available."""
    global _installed_languages, _package_index_loaded
    if (from_code, to_code) in MARIAN_MODELS:
        return True
    
    package_key = f"{from_code}_{to_code}"
    if package_key in _installed_languages:
        _load_languages()
        return True
    
    # Update package index (cached on subsequent calls)
    if not _package_index_loaded:
        try:
            argostranslate.package.update_package_index()
            _package_index_loaded = True
        except Exception as e:
            logger.warning(f"Failed to refresh Argos package index: {e}")

    try:
        available_packages = argostranslate.package.get_available_packages()
    except Exception as e:
        logger.error(f"Failed to list Argos packages: {e}")
        return False
    
    # Find and install package
    package_to_install = None
    for package in available_packages:
        if package.from_code == from_code and package.to_code == to_code:
            package_to_install = package
            break
    
    if package_to_install:
        try:
            logger.info(f"Installing translation package: {from_code} -> {to_code}")
            argostranslate.package.install_from_path(package_to_install.download())
            _installed_languages.add(package_key)
            _load_languages(force=True)
            return True
        except Exception as e:
            logger.error(f"Failed to install package {from_code}->{to_code}: {e}")
            return False
    
    logger.warning(f"Translation package not found: {from_code} -> {to_code}")
    return False


def _get_translation_cache_dir() -> Optional[Path]:
    """Return cache directory for Marian translation models."""
    cache_dir = None
    if settings.TRANSLATION_CACHE_DIR:
        cache_dir = Path(settings.TRANSLATION_CACHE_DIR)
    elif settings.STORAGE_PATH:
        cache_dir = Path(settings.STORAGE_PATH) / ".models" / "translation"
    if cache_dir:
        cache_dir.mkdir(parents=True, exist_ok=True)
    return cache_dir


class MarianTranslationModel:
    """Wrapper around MarianMT model and tokenizer."""

    def __init__(self, model_name: str):
        cache_dir = _get_translation_cache_dir()
        extra_kwargs: Dict[str, str] = {}
        if cache_dir:
            extra_kwargs["cache_dir"] = str(cache_dir)
        if settings.HUGGINGFACE_TOKEN:
            extra_kwargs["token"] = settings.HUGGINGFACE_TOKEN

        logger.info(
            "Loading MarianMT model %s (cache: %s)",
            model_name,
            cache_dir,
        )

        self.tokenizer = MarianTokenizer.from_pretrained(model_name, **extra_kwargs)
        self.model = MarianMTModel.from_pretrained(model_name, **extra_kwargs)
        self.model.eval()

        device_preference = settings.TRANSLATION_DEVICE.lower()
        if device_preference == "cuda" or (
            device_preference == "auto" and torch.cuda.is_available()
        ):
            device_name = "cuda"
        else:
            device_name = "cpu"
        self.device = torch.device(device_name)
        self.model.to(self.device)

    def translate(self, texts: Sequence[str]) -> List[str]:
        outputs: List[str] = []
        with torch.no_grad():
            for start in range(0, len(texts), MARIAN_BATCH_SIZE):
                batch = texts[start : start + MARIAN_BATCH_SIZE]
                if not batch:
                    continue
                inputs = self.tokenizer(
                    batch,
                    return_tensors="pt",
                    padding=True,
                    truncation=True,
                ).to(self.device)
                generated_tokens = self.model.generate(
                    **inputs, max_new_tokens=512, num_beams=4
                )
                decoded = self.tokenizer.batch_decode(
                    generated_tokens, skip_special_tokens=True
                )
                outputs.extend(decoded)
        return outputs


@lru_cache(maxsize=len(MARIAN_MODELS))
def _get_marian_model(model_name: str) -> MarianTranslationModel:
    return MarianTranslationModel(model_name)


def _translate_with_marian(
    texts: Sequence[str], source_language: str, target_language: str
) -> Optional[List[str]]:
    model_name = MARIAN_MODELS.get((source_language, target_language))
    if not model_name:
        return None
    try:
        model = _get_marian_model(model_name)
        logger.info(
            "Translating batch with MarianMT %s (%d items)",
            model_name,
            len(texts),
        )
        return model.translate(texts)
    except Exception as exc:
        logger.error(
            "Marian translation failed (%s -> %s) with model '%s': %s",
            source_language,
            target_language,
            model_name,
            exc,
            exc_info=True,
        )
        if (
            "401" in str(exc)
            and "Invalid username or password" in str(exc)
            and not settings.HUGGINGFACE_TOKEN
        ):
            logger.error(
                "HuggingFace now requires authentication for %s. "
                "Set HUGGINGFACE_TOKEN in your environment with a read access token.",
                model_name,
            )
        return None


def translate_text(text: str, from_lang: str, to_lang: str) -> str:
    """Translate text."""
    try:
        marian_result = _translate_with_marian([text], from_lang, to_lang)
        if marian_result is not None:
            return marian_result[0]

        if not ensure_language_package(from_lang, to_lang):
            logger.warning(f"No translation model for {from_lang}->{to_lang}")
            return text
        _load_languages()
        translated = argostranslate.translate.translate(text, from_lang, to_lang)
        return translated
    except Exception as e:
        logger.error(f"Translation error ({from_lang}->{to_lang}): {e}")
        return text


def detect_language(text: str) -> str:
    """Detect language from text."""
    if not LANGDETECT_AVAILABLE:
        # Fallback: simple heuristic
        return "en"
    
    try:
        # Combine first few subtitles for better detection
        detected = detect(text)
        logger.info(f"Detected language: {detected}")
        return detected
    except Exception as e:
        logger.warning(f"Language detection failed: {e}, using 'en' as fallback")
        return "en"


def _normalize_lang_code(lang: str) -> str:
    """Normalize language code for Argos Translate."""
    if not lang:
        return "en"
    
    lang_lower = lang.lower()
    if lang_lower in LANGUAGE_ALIASES:
        return LANGUAGE_ALIASES[lang_lower]
    
    # Try by first two letters as last resort
    lang_short = lang_lower[:2]
    return LANGUAGE_ALIASES.get(lang_short, "en")


def _translate_batch(texts: Iterable[str], source_language: str, target_language: str) -> Optional[List[str]]:
    """Translate a batch of strings. Returns None if translation is unavailable."""
    if source_language == target_language:
        return list(texts)
    
    texts = list(texts)
    if not texts:
        return []
    
    marian_translated = _translate_with_marian(
        texts, source_language, target_language
    )
    if marian_translated is not None:
        return marian_translated

    if not ensure_language_package(source_language, target_language):
        return None
    
    _load_languages()
    
    results: List[str] = []
    for idx, text in enumerate(texts, start=1):
        if not text.strip():
            results.append(text)
            continue
        try:
            translated = argostranslate.translate.translate(text, source_language, target_language)
            results.append(translated)
        except Exception as e:
            logger.warning(
                f"Failed to translate text #{idx} ({source_language}->{target_language}): {e}"
            )
            return None
    return results


# Load languages cache on module import (safe no-op if already loaded)
_load_languages()


def translate_subtitles(srt_path: str, output_dir: Path, target_language: str = "en", source_language: Optional[str] = None) -> str:
    """Translate SRT subtitles."""
    try:
        # Read SRT file
        with open(srt_path, "r", encoding="utf-8") as f:
            content = f.read()
        
        # Parse SRT
        subtitles = parse_srt(content)
        
        if not subtitles:
            logger.warning("No subtitles found in file")
            return srt_path
        
        # Detect source language if not provided
        if source_language is None or source_language == "auto":
            # Combine text from first few subtitles for detection
            sample_text = " ".join([s["text"] for s in subtitles[:5]])
            detected_lang = detect_language(sample_text)
            source_language = _normalize_lang_code(detected_lang)
            logger.info(f"Detected source language: {detected_lang} (normalized: {source_language})")
        
        # Normalize target language
        target_language = _normalize_lang_code(target_language)
        
        # If source and target are the same, return original
        if source_language == target_language:
            logger.info("Source and target languages are the same, skipping translation")
            return srt_path
        
        # Translate each subtitle
        logger.info(f"Translating from {source_language} to {target_language}")
        texts = [s["text"] for s in subtitles]
        translated_texts = _translate_batch(texts, source_language, target_language)
        
        # Attempt pivot translation if direct path unavailable
        if translated_texts is None and source_language != PIVOT_LANGUAGE and target_language != PIVOT_LANGUAGE:
            logger.info(
                f"No direct translation path for {source_language}->{target_language}, "
                f"trying pivot via {PIVOT_LANGUAGE}"
            )
            pivot_texts = _translate_batch(texts, source_language, PIVOT_LANGUAGE)
            if pivot_texts is not None:
                translated_texts = _translate_batch(pivot_texts, PIVOT_LANGUAGE, target_language)
        
        if translated_texts is None:
            logger.warning(
                f"Failed to translate subtitles from {source_language} to {target_language}. "
                "Keeping original text."
            )
            return srt_path
        
        for subtitle, new_text in zip(subtitles, translated_texts):
            subtitle["text"] = new_text
        
        # Save translated SRT
        output_path = output_dir / f"subtitles_{target_language}.srt"
        with open(output_path, "w", encoding="utf-8") as f:
            for i, subtitle in enumerate(subtitles, start=1):
                f.write(f"{i}\n")
                f.write(f"{subtitle['start']} --> {subtitle['end']}\n")
                f.write(f"{subtitle['text']}\n\n")
        
        logger.info(f"Translated subtitles saved: {output_path}")
        return str(output_path)
    
    except Exception as e:
        logger.error(f"Error translating subtitles: {e}")
        # Return original if translation fails
        return srt_path


def parse_srt(content: str) -> list:
    """Parse SRT content."""
    subtitles = []
    pattern = r'(\d+)\n(\d{2}:\d{2}:\d{2},\d{3}) --> (\d{2}:\d{2}:\d{2},\d{3})\n(.*?)(?=\n\n|\Z)'
    
    matches = re.findall(pattern, content, re.DOTALL)
    for match in matches:
        subtitles.append({
            "index": int(match[0]),
            "start": match[1],
            "end": match[2],
            "text": match[3].strip(),
        })
    
    return subtitles

