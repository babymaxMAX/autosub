"""Application settings and configuration."""
from pydantic_settings import BaseSettings
from pydantic import Field
from typing import List


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
    
    # Platega
    PLATEGA_API_ID: str = Field(..., description="Platega API ID")
    PLATEGA_API_KEY: str = Field(..., description="Platega API Key")
    PLATEGA_PROJECT_ID: int = Field(..., description="Platega Project ID")
    PLATEGA_PROJECT_NAME: str = Field(..., description="Platega Project Name")
    PLATEGA_WEBHOOK_URL: str = Field(..., description="Platega Webhook URL")
    PLATEGA_SUCCESS_URL: str = Field(..., description="Payment Success URL")
    PLATEGA_FAIL_URL: str = Field(..., description="Payment Fail URL")
    
    # Storage
    STORAGE_PATH: str = Field(default="./storage", description="Storage path")
    MAX_FILE_SIZE_MB: int = Field(default=500, description="Max file size in MB")
    CLEANUP_HOURS: int = Field(default=24, description="Cleanup files after hours")
    
    # Processing
    MAX_WORKERS: int = Field(default=3, description="Max concurrent workers")
    MAX_VIDEO_DURATION_FREE: int = Field(default=60, description="Max video duration for free tier (seconds)")
    MAX_VIDEO_DURATION_PRO: int = Field(default=600, description="Max video duration for PRO tier (seconds)")
    MAX_VIDEO_DURATION_CREATOR: int = Field(default=1800, description="Max video duration for CREATOR tier (seconds)")
    
    # Whisper
    WHISPER_MODEL: str = Field(default="base", description="Whisper model size")
    WHISPER_DEVICE: str = Field(default="cpu", description="Device for processing")
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True
    
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

