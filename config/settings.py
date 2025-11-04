"""Application settings and configuration."""
from pydantic_settings import BaseSettings
from pydantic import Field, validator
from typing import List, Optional


class Settings(BaseSettings):
    """Application settings."""
    
    # Telegram Bot
    BOT_TOKEN: str = Field(..., description="Telegram Bot Token")
    ADMIN_IDS: str = Field(default="", description="Comma-separated admin IDs")
    
    # Database
    DB_HOST: str = Field(default="localhost", description="Database host")
    DB_PORT: int = Field(default=5432, description="Database port")
    DB_NAME: str = Field(default="autosub", description="Database name")
    DB_USER: str = Field(default="autosub", description="Database user")
    DB_PASSWORD: str = Field(default="autosub_password", description="Database password")
    
    # Redis
    REDIS_HOST: str = Field(default="localhost", description="Redis host")
    REDIS_PORT: int = Field(default=6379, description="Redis port")
    REDIS_DB: int = Field(default=0, description="Redis database")
    
    # Webhook / public base URL
    PUBLIC_BASE_URL: Optional[str] = Field(default=None, description="Public base URL for webhooks")
    WEBHOOK_SECRET: str = Field(default="secret", description="Webhook secret")
    
    # Platega
    PLATEGA_API_ID: str = Field(..., description="Platega API ID")
    PLATEGA_API_KEY: str = Field(..., description="Platega API Key")
    PLATEGA_PROJECT_ID: int = Field(..., description="Platega Project ID")
    PLATEGA_PROJECT_NAME: str = Field(..., description="Platega Project Name")
    PLATEGA_WEBHOOK_URL: str = Field(..., description="Platega Webhook URL")
    PLATEGA_SUCCESS_URL: str = Field(..., description="Payment Success URL")
    PLATEGA_FAIL_URL: str = Field(..., description="Payment Fail URL")
    PLATEGA_WEBHOOK_SECRET: Optional[str] = Field(default=None, description="Platega Webhook Secret")
    
    # Storage
    STORAGE_PATH: str = Field(default="./storage", description="Storage path")
    MAX_FILE_SIZE_MB: int = Field(default=500, description="Max file size in MB")
    CLEANUP_HOURS: int = Field(default=24, description="Cleanup files after hours")
    FREE_TTL_HOURS: int = Field(default=24, description="TTL for FREE tier files (hours)")
    PRO_TTL_HOURS: int = Field(default=168, description="TTL for PRO tier files (hours)")
    CREATOR_TTL_HOURS: int = Field(default=168, description="TTL for CREATOR tier files (hours)")
    
    # Processing
    MAX_WORKERS: int = Field(default=3, description="Max concurrent workers")
    MAX_VIDEO_DURATION_FREE: int = Field(default=60, description="Max video duration for free tier (seconds)")
    MAX_VIDEO_DURATION_PRO: int = Field(default=600, description="Max video duration for PRO tier (seconds)")
    MAX_VIDEO_DURATION_CREATOR: int = Field(default=1800, description="Max video duration for CREATOR tier (seconds)")
    
    # Whisper
    WHISPER_MODEL: str = Field(default="base", description="Whisper model size")
    WHISPER_DEVICE: str = Field(default="auto", description="Device for processing (cpu/cuda/auto)")
    WHISPER_CACHE_DIR: Optional[str] = Field(default=None, description="Whisper cache directory")
    TTS_CACHE_DIR: Optional[str] = Field(default=None, description="TTS cache directory")
    
    # Instagram
    INSTAGRAM_PROXY: Optional[str] = Field(default=None, description="Proxy for Instagram downloads")
    INSTAGRAM_COOKIES_FILE: Optional[str] = Field(default=None, description="Path to Instagram cookies file")
    INSTAGRAM_TIMEOUT: int = Field(default=60, description="Instagram download timeout in seconds")
    INSTAGRAM_RETRIES: int = Field(default=5, description="Instagram download retries")
    
    # Download settings
    DOWNLOAD_TIMEOUT: int = Field(default=60, description="Download timeout in seconds")
    DOWNLOAD_RETRIES: int = Field(default=3, description="Download retries")
    
    # FFmpeg
    FFMPEG_PATH: str = Field(default="/usr/bin/ffmpeg", description="FFmpeg binary path")
    
    # Misc
    LOG_LEVEL: str = Field(default="INFO", description="Logging level")
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True
    
    @validator("PUBLIC_BASE_URL")
    def validate_base_url(cls, v):
        if v and not v.startswith("http"):
            raise ValueError("PUBLIC_BASE_URL must start with http/https")
        return v
    
    @property
    def database_url(self) -> str:
        """Get database URL."""
        return f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
    
    @property
    def database_url_sync(self) -> str:
        """Get synchronous database URL."""
        return f"postgresql://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
    
    @property
    def redis_url(self) -> str:
        """Get Redis URL."""
        return f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"
    
    @property
    def admin_ids_list(self) -> List[int]:
        """Get list of admin IDs."""
        if not self.ADMIN_IDS:
            return []
        return [int(id.strip()) for id in self.ADMIN_IDS.split(",") if id.strip()]


# Global settings instance
settings = Settings()

