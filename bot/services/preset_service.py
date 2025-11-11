"""Simple Preset storage using Redis."""
from typing import List, Optional, Dict, Any
from redis.asyncio import Redis
from config.settings import settings
import json


def _redis() -> Redis:
    return Redis.from_url(settings.redis_url)


def _key_list(user_id: int) -> str:
    return f"user:{user_id}:presets:list"


def _key_next(user_id: int) -> str:
    return f"user:{user_id}:presets:next_id"


async def list_presets(user_id: int) -> List[Dict[str, Any]]:
    r = _redis()
    raw = await r.lrange(_key_list(user_id), 0, -1)
    return [json.loads(x) for x in raw]


async def save_preset(user_id: int, name: str, options: Dict[str, Any]) -> Dict[str, Any]:
    r = _redis()
    preset_id = await r.incr(_key_next(user_id))
    preset = {"id": int(preset_id), "name": name, "options": options}
    await r.rpush(_key_list(user_id), json.dumps(preset, ensure_ascii=False))
    return preset


async def update_preset(user_id: int, preset_id: int, *, name: str | None = None, options: Dict[str, Any] | None = None) -> Optional[Dict[str, Any]]:
    """Update preset name and/or options."""
    r = _redis()
    key = _key_list(user_id)
    items = await r.lrange(key, 0, -1)
    for idx, item in enumerate(items):
        preset = json.loads(item)
        if int(preset.get("id")) == int(preset_id):
            if name is not None:
                preset["name"] = name
            if options is not None:
                preset["options"] = options
            await r.lset(key, idx, json.dumps(preset, ensure_ascii=False))
            return preset
    return None


async def delete_preset(user_id: int, preset_id: int) -> bool:
    r = _redis()
    key = _key_list(user_id)
    items = await r.lrange(key, 0, -1)
    for item in items:
        p = json.loads(item)
        if int(p.get("id")) == int(preset_id):
            await r.lrem(key, 1, item)
            return True
    return False


async def get_preset(user_id: int, preset_id: int) -> Optional[Dict[str, Any]]:
    r = _redis()
    items = await r.lrange(_key_list(user_id), 0, -1)
    for item in items:
        p = json.loads(item)
        if int(p.get("id")) == int(preset_id):
            return p
    return None


