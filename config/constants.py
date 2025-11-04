"""Application constants."""
from enum import Enum


class UserTier(str, Enum):
    """User subscription tier."""
    FREE = "free"
    PRO = "pro"
    CREATOR = "creator"


class TaskStatus(str, Enum):
    """Task processing status."""
    CREATED = "created"
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class ProcessingOption(str, Enum):
    """Video processing options."""
    SUBTITLES = "subtitles"
    TRANSLATION = "translation"
    VOICEOVER = "voiceover"
    VERTICAL_FORMAT = "vertical_format"


# Tier limits
TIER_LIMITS = {
    UserTier.FREE: {
        "max_duration": 60,  # seconds
        "max_quality": "720p",
        "daily_tasks": 3,
        "watermark": True,
        "priority": 3,
        "features": [ProcessingOption.SUBTITLES, ProcessingOption.VERTICAL_FORMAT],
    },
    UserTier.PRO: {
        "max_duration": 600,  # 10 minutes
        "max_quality": "1080p",
        "daily_tasks": 50,
        "watermark": False,
        "priority": 2,
        "features": [
            ProcessingOption.SUBTITLES,
            ProcessingOption.TRANSLATION,
            ProcessingOption.VERTICAL_FORMAT,
        ],
    },
    UserTier.CREATOR: {
        "max_duration": 1800,  # 30 minutes
        "max_quality": "1080p",
        "daily_tasks": 200,
        "watermark": False,
        "priority": 1,
        "features": [
            ProcessingOption.SUBTITLES,
            ProcessingOption.TRANSLATION,
            ProcessingOption.VOICEOVER,
            ProcessingOption.VERTICAL_FORMAT,
        ],
    },
}

# Pricing (in rubles)
PRICING = {
    "one_time_short": 29,  # up to 3 minutes
    "one_time_medium": 49,  # up to 10 minutes
    "one_time_long": 59,  # up to 30 minutes
    UserTier.PRO: {
        "monthly": 299,
        "yearly": 2990,
    },
    UserTier.CREATOR: {
        "monthly": 599,
        "yearly": 5990,
    },
}

# Supported languages
SUPPORTED_LANGUAGES = {
    "ru": "Русский",
    "en": "English",
    "es": "Español",
    "fr": "Français",
    "de": "Deutsch",
    "it": "Italiano",
    "pt": "Português",
    "pl": "Polski",
    "tr": "Türkçe",
    "uk": "Українська",
    "ar": "العربية",
    "zh": "中文",
    "ja": "日本語",
    "ko": "한국어",
    "hi": "हिन्दी",
}

# Video formats
SUPPORTED_VIDEO_FORMATS = [
    "video/mp4",
    "video/mpeg",
    "video/quicktime",
    "video/x-msvideo",
    "video/x-matroska",
]

SUPPORTED_AUDIO_FORMATS = [
    "audio/mpeg",
    "audio/mp4",
    "audio/wav",
    "audio/x-wav",
    "audio/ogg",
]

# Text constants
WELCOME_MESSAGE = """
👋 Добро пожаловать в AutoSub!

Я помогу вам добавить субтитры, перевод и озвучку к вашим видео.

🎬 Что я умею:
• Распознавание речи и создание субтитров
• Перевод на 50+ языков
• Озвучка текста
• Встраивание субтитров в видео
• Конвертация в вертикальный формат 9:16

📤 Отправьте мне видео или ссылку на YouTube/TikTok/Instagram

Используйте /help для подробной информации
"""

HELP_MESSAGE = """
📖 Инструкция по использованию AutoSub

🎥 Как отправить видео:
1. Загрузите видеофайл напрямую в чат
2. Отправьте ссылку на YouTube, TikTok или Instagram
3. Выберите нужные опции обработки
4. Дождитесь результата!

💎 Тарифы:
• FREE - до 60 сек, 3 видео/день, с водяным знаком
• PRO - до 10 мин, 50 видео/день, без водяного знака
• CREATOR - до 30 мин, озвучка, стили субтитров

📋 Команды:
/start - Начать работу
/help - Справка
/profile - Мой профиль
/pricing - Тарифы и цены
/cancel - Отменить текущую операцию

❓ Поддержка: @support
"""

