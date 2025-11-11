# 🚀 Инструкция по установке и настройке AutoSub

## ✅ Текущий статус

**Проверено и работает:**
- ✅ Python 3.13.5 (требуется 3.11+)
- ✅ Файл .env с токеном бота `8181035994:AAGe8mQDBxRV1Zj0xFCCF-iuhZGk9s3HxRo`
- ✅ Токен бота действителен (@LsJAutoSub_bot)
- ✅ Конфигурация загружается корректно
- ✅ Валидация URL видео работает (YouTube, TikTok, Instagram)
- ✅ Базовые Python пакеты установлены

**Требует установки:**
- ❌ FFmpeg (для обработки видео)
- ❌ Redis (для очередей задач)
- ❌ PostgreSQL (база данных)
- ❌ Дополнительные Python пакеты

---

## 📦 Способы установки

### Вариант 1: Docker (Рекомендуется)

1. **Установите Docker Desktop:**
   ```bash
   # Скачайте с https://www.docker.com/products/docker-desktop
   # Или через Homebrew:
   brew install --cask docker
   ```

2. **Запустите проект:**
   ```bash
   cd /Users/musaabdullaev/Desktop/autosub
   docker-compose up -d
   ```

3. **Проверьте статус:**
   ```bash
   docker-compose ps
   docker-compose logs -f bot
   ```

### Вариант 2: Локальная установка

1. **Установите системные зависимости:**
   ```bash
   # Установите Homebrew (если не установлен)
   /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
   
   # Установите зависимости
   brew install ffmpeg redis postgresql
   ```

2. **Установите Python пакеты:**
   ```bash
   cd /Users/musaabdullaev/Desktop/autosub
   source venv/bin/activate
   pip install -r requirements.txt
   ```

3. **Настройте базу данных:**
   ```bash
   # Запустите PostgreSQL
   brew services start postgresql
   
   # Создайте базу данных
   createdb autosub
   
   # Создайте пользователя (опционально)
   psql -c "CREATE USER autosub WITH PASSWORD 'autosub_password_123';"
   psql -c "GRANT ALL PRIVILEGES ON DATABASE autosub TO autosub;"
   ```

4. **Запустите Redis:**
   ```bash
   brew services start redis
   ```

5. **Инициализируйте базу данных:**
   ```bash
   python -c "from db.database import init_db; import asyncio; asyncio.run(init_db())"
   ```

6. **Запустите компоненты:**
   ```bash
   # В отдельных терминалах:
   
   # Бот
   python -m bot.main
   
   # Worker
   python -m worker.main
   
   # Webhook (опционально)
   python -m webhook.main
   ```

---

## 🧪 Проверка работоспособности

Запустите скрипт проверки:
```bash
cd /Users/musaabdullaev/Desktop/autosub
source venv/bin/activate
python check_system.py
```

---

## 🤖 Тестирование бота

1. **Найдите бота в Telegram:** @LsJAutoSub_bot
2. **Отправьте команду:** `/start`
3. **Отправьте тестовое видео или ссылку:**
   - Файл видео (до 60 сек для FREE тарифа)
   - YouTube: `https://www.youtube.com/watch?v=dQw4w9WgXcQ`
   - TikTok: `https://www.tiktok.com/@username/video/123`
   - Instagram: `https://www.instagram.com/p/ABC123/`

---

## ⚙️ Настройка .env

Текущий файл `.env` уже настроен с вашим токеном:

```env
BOT_TOKEN=8181035994:AAGe8mQDBxRV1Zj0xFCCF-iuhZGk9s3HxRo
ADMIN_IDS=123456789  # Замените на ваш Telegram ID
DB_NAME=autosub
DB_USER=autosub
DB_PASSWORD=autosub_password_123
# ... остальные настройки
```

**Получите ваш Telegram ID:** Напишите @userinfobot в Telegram

---

## 🔧 Устранение проблем

### Проблема: "ModuleNotFoundError"
```bash
# Активируйте виртуальное окружение
source venv/bin/activate
pip install -r requirements.txt
```

### Проблема: "Connection refused" (Redis/PostgreSQL)
```bash
# Проверьте статус служб
brew services list | grep -E "(redis|postgresql)"

# Запустите службы
brew services start redis
brew services start postgresql
```

### Проблема: "FFmpeg not found"
```bash
# Установите FFmpeg
brew install ffmpeg

# Проверьте установку
ffmpeg -version
```

### Проблема: Бот не отвечает
1. Проверьте токен в `.env`
2. Проверьте логи: `python -m bot.main`
3. Убедитесь, что Redis и PostgreSQL запущены

---

## 📊 Мониторинг

### Проверка статуса служб
```bash
# Docker
docker-compose ps

# Локально
brew services list | grep -E "(redis|postgresql)"
ps aux | grep -E "(bot|worker)"
```

### Просмотр логов
```bash
# Docker
docker-compose logs -f bot
docker-compose logs -f worker

# Локально
tail -f logs/bot.log
tail -f logs/worker.log
```

---

## 🎯 Следующие шаги

1. ✅ **Установите недостающие зависимости** (Docker или локально)
2. ✅ **Запустите систему**
3. ✅ **Протестируйте бота**
4. ⚙️ **Настройте платежи** (при необходимости)
5. 🚀 **Разверните на сервере** (для продакшена)

---

## 💡 Рекомендации

- **Для разработки:** Используйте локальную установку
- **Для продакшена:** Используйте Docker
- **Для тестирования:** Достаточно текущей настройки с вашим токеном
- **Мониторинг:** Регулярно проверяйте `check_system.py`

---

**Статус:** Система готова к запуску после установки зависимостей! 🚀
