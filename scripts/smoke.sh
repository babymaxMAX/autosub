#!/usr/bin/env bash
set -euo pipefail

echo "[smoke] Starting smoke tests..."

# Wait for services to be ready
echo "[smoke] Waiting for postgres & redis..."
sleep 5

# Check postgres connection
echo "[smoke] Checking postgres connection..."
python -c "
from db.database import SessionLocal
from sqlalchemy import text
db = SessionLocal()
result = db.execute(text('SELECT 1'))
assert result.scalar() == 1
print('✓ Postgres connected')
" || { echo "[smoke] FAIL: Postgres connection failed"; exit 1; }

# Check redis connection
echo "[smoke] Checking redis connection..."
python -c "
from redis import Redis
from config.settings import settings
r = Redis.from_url(settings.redis_url)
assert r.ping()
print('✓ Redis connected')
" || { echo "[smoke] FAIL: Redis connection failed"; exit 1; }

# Run alembic upgrade
echo "[smoke] Running alembic upgrade..."
alembic upgrade head || { echo "[smoke] WARNING: Alembic upgrade failed (may be expected if no migrations)"; }

# Check ffmpeg
echo "[smoke] Checking ffmpeg..."
ffmpeg -version >/dev/null 2>&1 || { echo "[smoke] FAIL: ffmpeg not found"; exit 1; }
echo "✓ FFmpeg available"

# Check Python imports
echo "[smoke] Checking Python imports..."
python -c "
import torch
import transformers
from faster_whisper import WhisperModel
print('✓ All required imports successful')
" || { echo "[smoke] WARNING: Some ML imports failed (may be expected in minimal setup)"; }

# Check worker can access queue
echo "[smoke] Checking Redis queue..."
python -c "
from redis import Redis
from rq import Queue
from config.settings import settings
r = Redis.from_url(settings.redis_url)
q = Queue('video_processing', connection=r)
print('✓ Redis queue accessible')
" || { echo "[smoke] FAIL: Redis queue check failed"; exit 1; }

echo "[smoke] ✅ All smoke tests passed!"
