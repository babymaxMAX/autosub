"""Centralized subtitle style definitions shared between bot and worker."""
from __future__ import annotations

from typing import Dict, Any, Optional

DEFAULT_SUBTITLE_STYLE = "modern_bold"

FONT_LANGUAGE_MAP = {
    "zh": "Noto Sans CJK SC",
    "ja": "Noto Sans CJK JP",
    "ko": "Noto Sans CJK KR",
    "ar": "Noto Naskh Arabic",
    "he": "Noto Sans Hebrew",
    "hi": "Noto Sans Devanagari",
    "bn": "Noto Sans Bengali",
    "th": "Noto Sans Thai",
}

SUBTITLE_STYLE_DEFINITIONS: Dict[str, Dict[str, Any]] = {
    "modern_bold": {
        "name": {
            "ru": "🔥 Современный жирный",
            "en": "🔥 Modern Bold",
        },
        "description": {
            "ru": "Трендовый жирный шрифт с яркой обводкой — идеально для TikTok и YouTube Shorts",
            "en": "Trendy bold font with bright outline — perfect for TikTok and YouTube Shorts",
        },
        "ffmpeg": {
            "FontName": "Arial Black",
            "FontSize": 34,
            "Bold": 1,
            "Italic": 0,
            "Spacing": 0.3,
            "MarginL": 40,
            "MarginR": 40,
            "Outline": 3,
            "Shadow": 2,
            "BorderStyle": 1,
            "PrimaryColour": "&H00FFFFFF",
            "OutlineColour": "&H00FF6B35",
            "BackColour": "&H80000000",
        },
    },
    "neon_glow": {
        "name": {
            "ru": "✨ Неоновое свечение",
            "en": "✨ Neon Glow",
        },
        "description": {
            "ru": "Светящийся эффект с неоновой подсветкой — для ярких и динамичных видео",
            "en": "Glowing effect with neon backlight — for bright and dynamic videos",
        },
        "ffmpeg": {
            "FontName": "Arial",
            "FontSize": 30,
            "Bold": 1,
            "Italic": 0,
            "Spacing": 0.2,
            "MarginL": 40,
            "MarginR": 40,
            "Outline": 4,
            "Shadow": 0,
            "BorderStyle": 1,
            "PrimaryColour": "&H00FFFFFF",
            "OutlineColour": "&H00FF00FF",
            "BackColour": "&H00000000",
        },
    },
    "clean_minimal": {
        "name": {
            "ru": "🎯 Чистый минимализм",
            "en": "🎯 Clean Minimal",
        },
        "description": {
            "ru": "Элегантный минималистичный стиль без лишних элементов — для профессиональных видео",
            "en": "Elegant minimalist style without extra elements — for professional videos",
        },
        "ffmpeg": {
            "FontName": "Arial",
            "FontSize": 28,
            "Bold": 0,
            "Italic": 0,
            "Spacing": 0.1,
            "MarginL": 50,
            "MarginR": 50,
            "Outline": 2,
            "Shadow": 1,
            "BorderStyle": 1,
            "PrimaryColour": "&H00FFFFFF",
            "OutlineColour": "&H00000000",
            "BackColour": "&H80000000",
        },
    },
    "gaming_style": {
        "name": {
            "ru": "🎮 Игровой стиль",
            "en": "🎮 Gaming Style",
        },
        "description": {
            "ru": "Агрессивный стиль с контрастной обводкой — идеально для игровых видео",
            "en": "Aggressive style with contrasting outline — perfect for gaming videos",
        },
        "ffmpeg": {
            "FontName": "Impact",
            "FontSize": 36,
            "Bold": 1,
            "Italic": 0,
            "Spacing": 0.4,
            "MarginL": 35,
            "MarginR": 35,
            "Outline": 4,
            "Shadow": 3,
            "BorderStyle": 1,
            "PrimaryColour": "&H0000FFFF",
            "OutlineColour": "&H00000000",
            "BackColour": "&H80FF0000",
        },
    },
    "elegant_serif": {
        "name": {
            "ru": "📚 Элегантная классика",
            "en": "📚 Elegant Classic",
        },
        "description": {
            "ru": "Классический шрифт с засечками — для образовательных и культурных видео",
            "en": "Classic serif font — for educational and cultural videos",
        },
        "ffmpeg": {
            "FontName": "Times New Roman",
            "FontSize": 28,
            "Bold": 0,
            "Italic": 0,
            "Spacing": 0.0,
            "MarginL": 60,
            "MarginR": 60,
            "Outline": 2,
            "Shadow": 1,
            "BorderStyle": 1,
            "PrimaryColour": "&H00F0F0F0",
            "OutlineColour": "&H00404040",
            "BackColour": "&H90000000",
        },
    },
    "retro_wave": {
        "name": {
            "ru": "🌈 Ретро волна",
            "en": "🌈 Retro Wave",
        },
        "description": {
            "ru": "Стиль в духе 80-х с градиентными цветами — для креативных и ностальгических видео",
            "en": "80s-inspired style with gradient colors — for creative and nostalgic videos",
        },
        "ffmpeg": {
            "FontName": "Courier New",
            "FontSize": 32,
            "Bold": 1,
            "Italic": 0,
            "Spacing": 0.5,
            "MarginL": 45,
            "MarginR": 45,
            "Outline": 3,
            "Shadow": 2,
            "BorderStyle": 1,
            "PrimaryColour": "&H00FF80FF",
            "OutlineColour": "&H0080FFFF",
            "BackColour": "&H80000040",
        },
    },
    "social_media": {
        "name": {
            "ru": "📱 Соцсети",
            "en": "📱 Social Media",
        },
        "description": {
            "ru": "Оптимизированный стиль для Instagram, TikTok и других соцсетей",
            "en": "Optimized style for Instagram, TikTok and other social media",
        },
        "ffmpeg": {
            "FontName": "Arial",
            "FontSize": 30,
            "Bold": 1,
            "Italic": 0,
            "Spacing": 0.2,
            "MarginL": 30,
            "MarginR": 30,
            "Outline": 3,
            "Shadow": 2,
            "BorderStyle": 1,
            "PrimaryColour": "&H00FFFFFF",
            "OutlineColour": "&H00000000",
            "BackColour": "&H80000000",
        },
    },
    "cinematic": {
        "name": {
            "ru": "🎬 Кинематограф",
            "en": "🎬 Cinematic",
        },
        "description": {
            "ru": "Кинематографический стиль с мягкими тенями — для художественных видео",
            "en": "Cinematic style with soft shadows — for artistic videos",
        },
        "ffmpeg": {
            "FontName": "Arial",
            "FontSize": 26,
            "Bold": 0,
            "Italic": 0,
            "Spacing": 0.1,
            "MarginL": 80,
            "MarginR": 80,
            "Outline": 1,
            "Shadow": 3,
            "BorderStyle": 1,
            "PrimaryColour": "&H00F5F5F5",
            "OutlineColour": "&H00202020",
            "BackColour": "&H60000000",
        },
    },
}

# Position presets for subtitle placement
POSITION_PRESETS: Dict[str, Dict[str, Any]] = {
    "top": {"Alignment": 8, "MarginV": 120},
    "middle": {"Alignment": 5, "MarginV": 60},
    "bottom": {"Alignment": 2, "MarginV": 90},
}


def get_style_display(style_id: str, lang_code: str = "en") -> str:
    """Get display name for a style."""
    style = SUBTITLE_STYLE_DEFINITIONS.get(style_id)
    if not style:
        return style_id
    
    name = style.get("name", {})
    return name.get(lang_code, name.get("en", style_id))


def get_style_description(style_id: str, lang_code: str = "en") -> str:
    """Get description for a style."""
    style = SUBTITLE_STYLE_DEFINITIONS.get(style_id)
    if not style:
        return ""
    
    description = style.get("description", {})
    return description.get(lang_code, description.get("en", ""))


def build_ffmpeg_style(
    style_id: str,
    position: str = "bottom",
    target_language: Optional[str] = None,
) -> Dict[str, Any]:
    """Build complete FFmpeg style parameters."""
    style = SUBTITLE_STYLE_DEFINITIONS.get(style_id, SUBTITLE_STYLE_DEFINITIONS[DEFAULT_SUBTITLE_STYLE])
    ffmpeg_params = style["ffmpeg"].copy()
    
    # Apply position settings
    position_params = POSITION_PRESETS.get(position, POSITION_PRESETS["bottom"])
    ffmpeg_params.update(position_params)
    
    # Apply language-specific font if needed
    if target_language and target_language in FONT_LANGUAGE_MAP:
        ffmpeg_params["FontName"] = FONT_LANGUAGE_MAP[target_language]
    
    return ffmpeg_params


def get_available_styles() -> Dict[str, Dict[str, Any]]:
    """Get all available subtitle styles."""
    return SUBTITLE_STYLE_DEFINITIONS.copy()


def validate_style(style_id: str) -> bool:
    """Check if style exists."""
    return style_id in SUBTITLE_STYLE_DEFINITIONS


def get_default_style() -> str:
    """Get default style ID."""
    return DEFAULT_SUBTITLE_STYLE