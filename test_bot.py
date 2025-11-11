#!/usr/bin/env python3
"""
Тестовая версия бота для проверки работы с логами
"""
import asyncio
import logging
import sys
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message
from aiogram.filters import Command
from config.settings import settings

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('bot_test.log', encoding='utf-8')
    ]
)
logger = logging.getLogger(__name__)

# Создаем бота и диспетчер
bot = Bot(token=settings.BOT_TOKEN)
dp = Dispatcher()

@dp.message(Command("start"))
async def cmd_start(message: Message):
    """Обработчик команды /start"""
    logger.info(f"Получена команда /start от пользователя {message.from_user.id} (@{message.from_user.username})")
    
    welcome_text = """
👋 Добро пожаловать в AutoSub!

🎬 Я помогу вам добавить субтитры к видео.

📤 Отправьте мне:
• Видео файл
• Ссылку на YouTube
• Ссылку на TikTok  
• Ссылку на Instagram

⚠️ ТЕСТОВЫЙ РЕЖИМ: База данных не подключена
"""
    
    await message.answer(welcome_text)
    logger.info(f"Отправлено приветствие пользователю {message.from_user.id}")

@dp.message(Command("help"))
async def cmd_help(message: Message):
    """Обработчик команды /help"""
    logger.info(f"Получена команда /help от пользователя {message.from_user.id}")
    
    help_text = """
📖 Помощь по AutoSub

🎥 Поддерживаемые форматы:
• YouTube: youtube.com/watch?v=...
• TikTok: tiktok.com/@user/video/...
• Instagram: instagram.com/p/... или /reel/...
• Видео файлы: MP4, AVI, MOV

⚠️ Сейчас бот работает в тестовом режиме
"""
    
    await message.answer(help_text)

@dp.message(F.text)
async def handle_text(message: Message):
    """Обработчик текстовых сообщений (ссылок)"""
    text = message.text.strip()
    logger.info(f"Получено текстовое сообщение от {message.from_user.id}: {text[:50]}...")
    
    # Простая валидация URL
    if any(platform in text.lower() for platform in ['youtube.com', 'youtu.be', 'tiktok.com', 'instagram.com']):
        logger.info(f"Обнаружена ссылка на видео: {text}")
        
        platform = None
        if 'youtube.com' in text or 'youtu.be' in text:
            platform = 'YouTube'
        elif 'tiktok.com' in text:
            platform = 'TikTok'
        elif 'instagram.com' in text:
            platform = 'Instagram'
        
        response = f"""
✅ Ссылка распознана как {platform}!

🔗 URL: {text}

⚠️ В тестовом режиме обработка не выполняется.
Для полной работы требуется:
• Redis (очереди задач)
• PostgreSQL (база данных) 
• FFmpeg (обработка видео)
• Worker процесс

📦 Используйте: docker-compose up -d
"""
        await message.answer(response)
        logger.info(f"Отправлен ответ о распознанной ссылке {platform}")
    else:
        logger.info(f"Получено обычное текстовое сообщение: {text[:30]}...")
        await message.answer("🤔 Отправьте ссылку на видео или используйте /help для справки")

@dp.message(F.video | F.document)
async def handle_media(message: Message):
    """Обработчик медиа файлов"""
    logger.info(f"Получен медиа файл от {message.from_user.id}")
    
    if message.video:
        file_info = f"Видео: {message.video.duration}сек, {message.video.file_size} байт"
        logger.info(f"Детали видео: {file_info}")
    elif message.document:
        file_info = f"Документ: {message.document.file_name}, {message.document.file_size} байт"
        logger.info(f"Детали документа: {file_info}")
    
    response = f"""
📹 Файл получен!

📊 Информация: {file_info}

⚠️ В тестовом режиме обработка не выполняется.
Файл сохранен в логах для отладки.

🚀 Для обработки запустите полную систему:
docker-compose up -d
"""
    
    await message.answer(response)
    logger.info(f"Отправлен ответ о полученном медиа файле")

@dp.message()
async def handle_other(message: Message):
    """Обработчик всех остальных сообщений"""
    logger.info(f"Получено неизвестное сообщение от {message.from_user.id}: {message.content_type}")
    await message.answer("🤷‍♂️ Не понимаю этот тип сообщения. Отправьте видео или ссылку.")

async def main():
    """Основная функция"""
    logger.info("🚀 Запуск тестового бота AutoSub...")
    logger.info(f"🤖 Токен: {settings.BOT_TOKEN[:10]}...")
    
    try:
        # Получаем информацию о боте
        me = await bot.get_me()
        logger.info(f"✅ Бот подключен: {me.first_name} (@{me.username})")
        logger.info(f"📱 ID бота: {me.id}")
        
        # Запускаем polling
        logger.info("🔄 Начинаем получение обновлений...")
        await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())
        
    except Exception as e:
        logger.error(f"❌ Ошибка запуска бота: {e}")
        raise
    finally:
        await bot.session.close()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("⏹️ Бот остановлен пользователем")
    except Exception as e:
        logger.error(f"💥 Критическая ошибка: {e}")
        sys.exit(1)
