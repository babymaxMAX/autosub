"""Subtitle translation using Argos Translate."""
import logging
import re
from pathlib import Path
from typing import Optional
import argostranslate.package
import argostranslate.translate
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


def ensure_language_package(from_code: str, to_code: str):
    """Ensure translation package is installed."""
    global _installed_languages
    
    package_key = f"{from_code}_{to_code}"
    if package_key in _installed_languages:
        return
    
    # Update package index
    argostranslate.package.update_package_index()
    available_packages = argostranslate.package.get_available_packages()
    
    # Find and install package
    package_to_install = None
    for package in available_packages:
        if package.from_code == from_code and package.to_code == to_code:
            package_to_install = package
            break
    
    if package_to_install:
        logger.info(f"Installing translation package: {from_code} -> {to_code}")
        argostranslate.package.install_from_path(package_to_install.download())
        _installed_languages.add(package_key)
    else:
        logger.warning(f"Translation package not found: {from_code} -> {to_code}")


def translate_text(text: str, from_lang: str, to_lang: str) -> str:
    """Translate text."""
    try:
        ensure_language_package(from_lang, to_lang)
        translated = argostranslate.translate.translate(text, from_lang, to_lang)
        return translated
    except Exception as e:
        logger.error(f"Translation error: {e}")
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
    # Map common codes to Argos Translate codes
    lang_map = {
        "en": "en",
        "ru": "ru",
        "es": "es",
        "fr": "fr",
        "de": "de",
        "it": "it",
        "pt": "pt",
        "pl": "pl",
        "tr": "tr",
        "uk": "uk",
        "zh": "zh",
        "ja": "ja",
        "ko": "ko",
    }
    lang_lower = lang.lower()[:2]
    return lang_map.get(lang_lower, "en")


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
        for i, subtitle in enumerate(subtitles):
            try:
                subtitle["text"] = translate_text(
                    subtitle["text"],
                    from_lang=source_language,
                    to_lang=target_language
                )
            except Exception as e:
                logger.warning(f"Failed to translate subtitle {i+1}: {e}, keeping original")
                # Keep original text on translation failure
        
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

