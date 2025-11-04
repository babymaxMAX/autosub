"""Subtitle translation using Argos Translate."""
import logging
import re
from pathlib import Path
import argostranslate.package
import argostranslate.translate

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


def translate_subtitles(srt_path: str, output_dir: Path, target_language: str = "en") -> str:
    """Translate SRT subtitles."""
    try:
        # Read SRT file
        with open(srt_path, "r", encoding="utf-8") as f:
            content = f.read()
        
        # Parse SRT
        subtitles = parse_srt(content)
        
        # Detect source language (assuming first subtitle)
        if subtitles:
            # Simple language detection - you may want to use a proper library
            source_language = "auto"  # For now, we'll use English as source
            
            # Translate each subtitle
            for subtitle in subtitles:
                subtitle["text"] = translate_text(
                    subtitle["text"],
                    from_lang="en",  # You should detect this properly
                    to_lang=target_language
                )
        
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

