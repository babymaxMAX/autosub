"""Tests for plan quota and TTL settings."""
import pytest
from config.settings import settings


def test_plan_ttl_defaults():
    """Test that plan TTL defaults are set correctly."""
    assert settings.FREE_TTL_HOURS > 0
    assert settings.PRO_TTL_HOURS >= settings.FREE_TTL_HOURS
    assert settings.CREATOR_TTL_HOURS >= settings.PRO_TTL_HOURS


def test_plan_ttl_values():
    """Test specific TTL values."""
    # FREE tier should have shortest TTL
    assert settings.FREE_TTL_HOURS == 24
    
    # PRO and CREATOR should have longer TTL
    assert settings.PRO_TTL_HOURS == 168  # 7 days
    assert settings.CREATOR_TTL_HOURS == 168  # 7 days
