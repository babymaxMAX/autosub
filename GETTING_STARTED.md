# Руководство по началу работы с AutoSub

## Предварительная подготовка

Перед началом работы убедитесь, что у вас есть:

1. **Токен Telegram бота** - получите у [@BotFather](https://t.me/BotFather)
2. **Аккаунт Platega** - для приёма платежей (опционально)
3. **Сервер или VPS** - для развертывания (минимум 2GB RAM, 2 CPU)

## Шаг 1: Установка на сервер

### Ubuntu/Debian

```bash
# Обновите систему
sudo apt update && sudo apt upgrade -y

# Установите Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Установите Docker Compose
sudo apt install docker-compose -y

# Клонируйте проект
git clone <your-repository-url>
cd AutoSub
```

### Windows

1. Установите [Docker Desktop](https://www.docker.com/products/docker-desktop)
2. Установите [Git](https://git-scm.com/download/win)
3. Клонируйте проект через Git Bash или PowerShell

## Шаг 2: Настройка переменных окружения

Создайте файл `.env` в корне проекта:

```bash
cp .env.example .env
nano .env  # или используйте любой другой редактор
```

Обязательные параметры:

```env
# Токен вашего бота от BotFather
BOT_TOKEN=8181035994:AAGe8mQDBxRV1Zj0xFCCF-iuhZGk9s3HxRo

# Ваш Telegram ID (получите у @userinfobot)
ADMIN_IDS=123456789

# Данные Platega (если используете платежи)
PLATEGA_API_ID=your_api_id
PLATEGA_API_KEY=your_api_key
PLATEGA_PROJECT_ID=16699
```

## Шаг 3: Запуск проекта

```bash
# Соберите и запустите контейнеры
docker-compose up -d

# Проверьте статус
docker-compose ps

# Посмотрите логи
docker-compose logs -f
```

Вы должны увидеть:
```
autosub_bot      | Bot started successfully!
autosub_worker   | Worker started successfully!
autosub_postgres | database system is ready to accept connections
autosub_redis    | Ready to accept connections
```

## Шаг 4: Проверка работы

1. Откройте Telegram и найдите вашего бота
2. Отправьте команду `/start`
3. Бот должен ответить приветственным сообщением

## Шаг 5: Тестирование обработки видео

1. Отправьте боту короткое видео (до 60 сек для бесплатного тарифа)
2. Выберите опции обработки
3. Дождитесь результата

## Настройка платежей (опционально)

### Platega

1. Зарегистрируйтесь на [Platega](https://platega.com)
2. Создайте проект
3. Получите API ключи
4. Настройте webhook:
   ```
   URL: https://your-domain.com/webhook/payment
   Method: POST
   Signature: SHA256
   ```
5. Добавьте данные в `.env`:
   ```env
   PLATEGA_API_ID=your_api_id
   PLATEGA_API_KEY=your_api_key
   PLATEGA_PROJECT_ID=your_project_id
   ```

## Настройка домена и SSL (для webhook)

### Использование Nginx

```bash
# Установите Nginx
sudo apt install nginx -y

# Создайте конфигурацию
sudo nano /etc/nginx/sites-available/autosub
```

Содержимое конфигурации:

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location /webhook/ {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

```bash
# Активируйте конфигурацию
sudo ln -s /etc/nginx/sites-available/autosub /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx

# Установите Certbot для SSL
sudo apt install certbot python3-certbot-nginx -y
sudo certbot --nginx -d your-domain.com
```

## Оптимизация производительности

### Для серверов с GPU

Если у вас есть GPU, можно ускорить обработку:

```env
# В .env файле
WHISPER_DEVICE=cuda
```

И обновите `docker-compose.yml`:

```yaml
worker:
  deploy:
    resources:
      reservations:
        devices:
          - driver: nvidia
            count: 1
            capabilities: [gpu]
```

### Увеличение количества workers

```yaml
worker:
  deploy:
    replicas: 3  # Запустить 3 worker процесса
```

## Мониторинг

### Просмотр логов

```bash
# Все логи
docker-compose logs -f

# Только бот
docker-compose logs -f bot

# Только worker
docker-compose logs -f worker
```

### Проверка использования ресурсов

```bash
docker stats
```

### Подключение к базе данных

```bash
docker-compose exec postgres psql -U autosub -d autosub
```

## Резервное копирование

### Автоматическое резервное копирование БД

Создайте скрипт `backup.sh`:

```bash
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
docker-compose exec -T postgres pg_dump -U autosub autosub > backup_$DATE.sql
# Удалить старые бэкапы (старше 7 дней)
find . -name "backup_*.sql" -mtime +7 -delete
```

Добавьте в cron:
```bash
crontab -e
# Добавьте строку:
0 2 * * * /path/to/backup.sh
```

## Обновление проекта

```bash
# Остановите контейнеры
docker-compose down

# Получите обновления
git pull

# Пересоберите и запустите
docker-compose up -d --build

# Проверьте логи
docker-compose logs -f
```

## Устранение проблем

### Бот не запускается

```bash
# Проверьте токен бота
docker-compose logs bot | grep -i error

# Проверьте подключение к БД
docker-compose exec postgres psql -U autosub -c "SELECT 1;"
```

### Worker не обрабатывает задачи

```bash
# Проверьте Redis
docker-compose exec redis redis-cli ping

# Проверьте очередь
docker-compose exec redis redis-cli LLEN rq:queue:video_processing
```

### Ошибки при обработке видео

```bash
# Проверьте FFmpeg
docker-compose exec worker ffmpeg -version

# Проверьте свободное место
df -h
```

## Производственное развертывание

### Systemd service (для автозапуска)

Создайте `/etc/systemd/system/autosub.service`:

```ini
[Unit]
Description=AutoSub Bot
Requires=docker.service
After=docker.service

[Service]
Type=oneshot
RemainAfterExit=yes
WorkingDirectory=/path/to/AutoSub
ExecStart=/usr/bin/docker-compose up -d
ExecStop=/usr/bin/docker-compose down
TimeoutStartSec=0

[Install]
WantedBy=multi-user.target
```

Активируйте:
```bash
sudo systemctl enable autosub
sudo systemctl start autosub
```

## Контакты и поддержка

- 📧 Email: support@example.com
- 💬 Telegram: @support
- 🐛 Issues: [GitHub Issues](https://github.com/your-repo/issues)

---

Готово! Ваш бот AutoSub настроен и готов к работе! 🎉

