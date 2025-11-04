# API Документация AutoSub

## Webhook API

### Payment Webhook

Endpoint для получения уведомлений о платежах от Platega.

**Endpoint:** `POST /webhook/payment`

**Request Body:**
```json
{
  "order_id": "12345",
  "amount": 299.00,
  "status": "success",
  "signature": "sha256_hash",
  "external_id": "ext_12345"
}
```

**Response:**
```json
{
  "status": "ok"
}
```

**Status Codes:**
- `200` - Success
- `400` - Invalid signature
- `404` - Payment not found
- `500` - Internal error

### Health Check

**Endpoint:** `GET /health`

**Response:**
```json
{
  "status": "healthy"
}
```

---

## Bot Commands

### User Commands

#### /start
Начало работы с ботом. Показывает приветственное сообщение и главное меню.

#### /help
Показывает справку по использованию бота.

#### /profile
Показывает информацию о пользователе:
- Текущий тариф
- Лимиты
- Статистику использования

#### /pricing
Показывает доступные тарифы и цены.

#### /cancel
Отменяет текущую операцию.

### Admin Commands

#### /admin
Открывает панель администратора (только для админов).

**Доступные разделы:**
- 📊 Статистика системы
- 👥 Пользователи
- 📋 Задачи
- 💰 Платежи

---

## Database Models

### User

```python
{
  "id": int,
  "telegram_id": int,
  "username": str,
  "first_name": str,
  "last_name": str,
  "language_code": str,
  "tier": "free" | "pro" | "creator",
  "tier_expires_at": datetime,
  "tasks_today": int,
  "tasks_total": int,
  "created_at": datetime,
  "updated_at": datetime
}
```

### Task

```python
{
  "id": int,
  "user_id": int,
  "status": "created" | "pending" | "processing" | "completed" | "failed",
  "priority": int,
  "input_type": "file" | "youtube" | "tiktok" | "instagram",
  "input_url": str,
  "input_file_id": str,
  "duration": float,
  "generate_subtitles": bool,
  "translate": bool,
  "voiceover": bool,
  "vertical_format": bool,
  "add_watermark": bool,
  "source_language": str,
  "target_language": str,
  "output_file_path": str,
  "subtitles_file_path": str,
  "error_message": str,
  "processing_time": float,
  "created_at": datetime,
  "completed_at": datetime
}
```

### Payment

```python
{
  "id": int,
  "user_id": int,
  "external_id": str,
  "amount": float,
  "currency": "RUB",
  "tier": "free" | "pro" | "creator",
  "subscription_period": "monthly" | "yearly" | "onetime",
  "status": "pending" | "completed" | "failed" | "refunded",
  "payment_method": str,
  "metadata": dict,
  "created_at": datetime,
  "completed_at": datetime
}
```

---

## Internal API (для разработчиков)

### CRUD Operations

#### get_user_by_telegram_id
```python
async def get_user_by_telegram_id(db: AsyncSession, telegram_id: int) -> Optional[User]
```

#### create_user
```python
async def create_user(
    db: AsyncSession,
    telegram_id: int,
    username: Optional[str] = None,
    first_name: Optional[str] = None,
    last_name: Optional[str] = None,
    language_code: str = "ru",
) -> User
```

#### update_user_tier
```python
async def update_user_tier(
    db: AsyncSession,
    user_id: int,
    tier: UserTier,
    expires_at: Optional[datetime] = None,
) -> User
```

#### create_task
```python
async def create_task(
    db: AsyncSession,
    user_id: int,
    input_type: str,
    priority: int = 3,
    **kwargs
) -> Task
```

#### update_task_status
```python
async def update_task_status(
    db: AsyncSession,
    task_id: int,
    status: TaskStatus,
    **kwargs
) -> Task
```

### Video Processing

#### validate_video_url
```python
def validate_video_url(url: str) -> Tuple[bool, Optional[str]]
```
Валидирует URL и определяет источник (youtube, tiktok, instagram).

#### check_user_limits
```python
async def check_user_limits(db, user: User) -> Tuple[bool, Optional[str]]
```
Проверяет, может ли пользователь обработать видео согласно лимитам тарифа.

#### enqueue_video_task
```python
async def enqueue_video_task(db, user: User, data: dict) -> Task
```
Создает задачу и помещает её в очередь обработки.

### Payment Service

#### create_payment_link
```python
async def create_payment_link(
    user_id: int,
    amount: float,
    description: str,
    tier: Optional[UserTier] = None,
    period: Optional[str] = None,
) -> str
```
Создает платежную ссылку через Platega.

#### verify_payment_signature
```python
async def verify_payment_signature(
    order_id: str,
    amount: float,
    status: str,
    signature: str,
) -> bool
```
Проверяет подпись платежного уведомления.

---

## Worker Tasks

### process_video_task
```python
def process_video_task(task_id: int)
```

Основная функция обработки видео:

1. Загрузка видео
2. Транскрибация (ASR)
3. Перевод (опционально)
4. Генерация озвучки (опционально)
5. Обработка видео (hardsub, формат, watermark)
6. Сохранение результата
7. Отправка пользователю

### Processors

#### download_video
```python
def download_video(task, work_dir: Path) -> str
```

#### transcribe_audio
```python
def transcribe_audio(video_path: str, output_dir: Path, language: str = "auto") -> str
```

#### translate_subtitles
```python
def translate_subtitles(srt_path: str, output_dir: Path, target_language: str = "en") -> str
```

#### generate_voiceover
```python
def generate_voiceover(srt_path: str, output_dir: Path, language: str = "en") -> str
```

#### process_video_with_subtitles
```python
def process_video_with_subtitles(
    input_video_path: str,
    subtitles_path: Optional[str],
    voiceover_path: Optional[str],
    output_dir: Path,
    vertical_format: bool = False,
    add_watermark: bool = False,
) -> str
```

---

## Константы

### UserTier
```python
class UserTier(str, Enum):
    FREE = "free"
    PRO = "pro"
    CREATOR = "creator"
```

### TaskStatus
```python
class TaskStatus(str, Enum):
    CREATED = "created"
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
```

### ProcessingOption
```python
class ProcessingOption(str, Enum):
    SUBTITLES = "subtitles"
    TRANSLATION = "translation"
    VOICEOVER = "voiceover"
    VERTICAL_FORMAT = "vertical_format"
```

### Tier Limits
```python
TIER_LIMITS = {
    UserTier.FREE: {
        "max_duration": 60,
        "max_quality": "720p",
        "daily_tasks": 3,
        "watermark": True,
        "priority": 3,
    },
    UserTier.PRO: {
        "max_duration": 600,
        "max_quality": "1080p",
        "daily_tasks": 50,
        "watermark": False,
        "priority": 2,
    },
    UserTier.CREATOR: {
        "max_duration": 1800,
        "max_quality": "1080p",
        "daily_tasks": 200,
        "watermark": False,
        "priority": 1,
    },
}
```

---

## Rate Limiting

Лимиты реализованы на уровне БД:
- `tasks_today` - счетчик задач за сегодня
- `last_task_date` - дата последней задачи
- Автоматический сброс счетчика при смене даты

---

## Error Handling

### Error Codes

- `USER_LIMIT_EXCEEDED` - Превышен дневной лимит задач
- `VIDEO_TOO_LONG` - Видео слишком длинное для тарифа
- `SUBSCRIPTION_EXPIRED` - Подписка истекла
- `DOWNLOAD_FAILED` - Не удалось загрузить видео
- `TRANSCRIPTION_FAILED` - Ошибка транскрибации
- `PROCESSING_FAILED` - Ошибка обработки видео

### Error Response Format

```python
{
    "error": "ERROR_CODE",
    "message": "Human readable message",
    "details": {...}  # Optional
}
```

---

## Webhooks

### Настройка Webhook (Platega)

1. URL: `https://your-domain.com/webhook/payment`
2. Method: `POST`
3. Signature Algorithm: `SHA256`
4. Format: JSON

### Signature Verification

```python
signature = sha256(f"{order_id}{amount}{status}{api_key}".encode()).hexdigest()
```

---

## Environment Variables

См. `.env.example` для полного списка.

**Обязательные:**
- `BOT_TOKEN` - Telegram bot token
- `DB_*` - Database credentials
- `REDIS_*` - Redis connection
- `PLATEGA_*` - Payment system credentials (если используется)

**Опциональные:**
- `WHISPER_MODEL` - Whisper model size (tiny/base/small/medium/large)
- `WHISPER_DEVICE` - Processing device (cpu/cuda)
- `MAX_WORKERS` - Maximum concurrent workers
- `CLEANUP_HOURS` - Hours before cleaning up files

---

## Testing API

### Примеры запросов

#### Health Check
```bash
curl http://localhost:8000/health
```

#### Payment Webhook (тестовый)
```bash
curl -X POST http://localhost:8000/webhook/payment \
  -H "Content-Type: application/json" \
  -d '{
    "order_id": "12345",
    "amount": 299.00,
    "status": "success",
    "signature": "test_signature",
    "external_id": "ext_12345"
  }'
```

---

## Расширение API

Для добавления новых endpoints в webhook сервис:

```python
# webhook/main.py

@app.post("/api/v1/your-endpoint")
async def your_endpoint(data: YourModel):
    # Your logic
    return {"status": "ok"}
```

---

**Вопросы по API?** Создайте [issue](https://github.com/your-repo/issues)

