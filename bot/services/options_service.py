"""User default options storage backed by Redis."""
from __future__ import annotations

from typing import Dict, Any
from redis.asyncio import Redis
from config.settings import settings
import json


def _redis() -> Redis:
    return Redis.from_url(settings.redis_url)


def _key_defaults(user_id: int) -> str:
    return f"user:{user_id}:options:defaults"


DEFAULTS: Dict[str, Any] = {
    "subtitles": True,
    "translate": False,
    "voiceover": False,
    "vertical": False,
    "style": "modern_bold",
    "voice": "female",
    "target_language": "auto",
    "position": "bottom",
}


async def get_default_options(user_id: int) -> Dict[str, Any]:
    """Return user's default options, falling back to sensible defaults."""
    try:
        r = _redis()
        raw = await r.get(_key_defaults(user_id))
    except Exception:
        return dict(DEFAULTS)
    
    if not raw:
        return dict(DEFAULTS)
    
    try:
        data = json.loads(raw)
        # Ensure all defaults exist
        merged = dict(DEFAULTS)
        merged.update(data or {})
        return merged
    except Exception:
        return dict(DEFAULTS)


async def update_default_options(user_id: int, updates: Dict[str, Any]) -> Dict[str, Any]:
    """Update defaults with provided updates and return resulting map."""
    current = await get_default_options(user_id)
    current.update(updates)
    
    try:
        r = _redis()
        await r.set(_key_defaults(user_id), json.dumps(current, ensure_ascii=False))
    except Exception:
        # Silently ignore persistence issues; caller already has merged defaults.
        pass
    
    return current


