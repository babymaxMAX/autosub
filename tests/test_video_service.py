"""Tests for video service."""
import pytest
from bot.services.video_service import validate_video_url


def test_validate_youtube_url():
    """Test YouTube URL validation."""
    is_valid, source = validate_video_url("https://www.youtube.com/watch?v=dQw4w9WgXcQ")
    assert is_valid is True
    assert source == "youtube"


def test_validate_tiktok_url():
    """Test TikTok URL validation."""
    is_valid, source = validate_video_url("https://www.tiktok.com/@user/video/1234567890")
    assert is_valid is True
    assert source == "tiktok"


def test_validate_instagram_url():
    """Test Instagram URL validation."""
    is_valid, source = validate_video_url("https://www.instagram.com/p/ABC123/")
    assert is_valid is True
    assert source == "instagram"


def test_validate_invalid_url():
    """Test invalid URL."""
    is_valid, source = validate_video_url("https://example.com/video.mp4")
    assert is_valid is False
    assert source is None

