#!/usr/bin/env python3
"""
Мониторинг бота через Telegram API без polling
"""
import asyncio
import logging
import sys
from datetime import datetime
from aiogram import Bot
from config.settings import settings

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('monitor.log', encoding='utf-8')
    ]
)
logger = logging.getLogger(__name__)

async def monitor_bot():
    """Мониторинг состояния бота"""
    bot = Bot(token=settings.BOT_TOKEN)
    
    try:
        logger.info("🔍 Запуск мониторинга бота...")
        
        # Получаем информацию о боте
        me = await bot.get_me()
        logger.info(f"✅ Бот активен: {me.first_name} (@{me.username})")
        logger.info(f"📱 ID: {me.id}")
        logger.info(f"🔗 Ссылка: https://t.me/{me.username}")
        
        # Получаем информацию о webhook
        webhook_info = await bot.get_webhook_info()
        logger.info(f"🌐 Webhook URL: {webhook_info.url or 'Не установлен'}")
        logger.info(f"📊 Ожидающих обновлений: {webhook_info.pending_update_count}")
        
        if webhook_info.last_error_date:
            logger.warning(f"⚠️ Последняя ошибка: {webhook_info.last_error_message}")
        
        # Проверяем, можем ли отправить сообщение админу
        admin_ids = settings.admin_ids_list
        if admin_ids:
            admin_id = admin_ids[0]
            try:
                await bot.send_message(
                    admin_id, 
                    f"🤖 Тест бота {datetime.now().strftime('%H:%M:%S')}\n"
                    f"Бот работает и готов к приему сообщений!"
                )
                logger.info(f"✅ Тестовое сообщение отправлено админу {admin_id}")
            except Exception as e:
                logger.warning(f"⚠️ Не удалось отправить сообщение админу: {e}")
        
        logger.info("📋 Статус: Бот готов к работе!")
        logger.info("📤 Отправьте сообщение боту для проверки...")
        
        # Показываем инструкции
        print("\n" + "="*60)
        print("🤖 БОТ ГОТОВ К ТЕСТИРОВАНИЮ!")
        print("="*60)
        print(f"📱 Найдите бота: @{me.username}")
        print("📤 Отправьте боту:")
        print("   • /start - для начала")
        print("   • Ссылку на YouTube/TikTok/Instagram")
        print("   • Видео файл")
        print("\n📊 Логи будут отображаться здесь...")
        print("⏹️  Нажмите Ctrl+C для остановки")
        print("="*60)
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Ошибка мониторинга: {e}")
        return False
    finally:
        await bot.session.close()

async def check_updates_periodically():
    """Периодическая проверка обновлений"""
    bot = Bot(token=settings.BOT_TOKEN)
    last_update_id = 0
    
    try:
        while True:
            try:
                # Получаем обновления
                updates = await bot.get_updates(offset=last_update_id + 1, limit=10, timeout=1)
                
                for update in updates:
                    last_update_id = update.update_id
                    
                    if update.message:
                        msg = update.message
                        user = msg.from_user
                        
                        logger.info(f"📨 Новое сообщение от @{user.username} (ID: {user.id})")
                        
                        if msg.text:
                            logger.info(f"💬 Текст: {msg.text[:100]}...")
                            
                            # Проверяем ссылки
                            text = msg.text.lower()
                            if any(platform in text for platform in ['youtube.com', 'youtu.be', 'tiktok.com', 'instagram.com']):
                                platform = 'YouTube' if 'youtube' in text or 'youtu.be' in text else \
                                          'TikTok' if 'tiktok' in text else 'Instagram'
                                logger.info(f"🔗 Обнаружена ссылка на {platform}!")
                                
                                # Отправляем ответ
                                await bot.send_message(
                                    msg.chat.id,
                                    f"✅ Получена ссылка на {platform}!\n\n"
                                    f"🔗 URL: {msg.text}\n\n"
                                    f"⚠️ Тестовый режим: обработка не выполняется.\n"
                                    f"📊 Логи сохранены для анализа."
                                )
                                logger.info(f"✅ Отправлен ответ пользователю")
                        
                        elif msg.video:
                            logger.info(f"🎬 Видео: {msg.video.duration}сек, {msg.video.file_size} байт")
                            await bot.send_message(
                                msg.chat.id,
                                f"📹 Видео получено!\n\n"
                                f"⏱️ Длительность: {msg.video.duration} сек\n"
                                f"📊 Размер: {msg.video.file_size} байт\n\n"
                                f"⚠️ Тестовый режим: обработка не выполняется."
                            )
                            logger.info(f"✅ Отправлен ответ о видео")
                        
                        elif msg.document:
                            logger.info(f"📄 Документ: {msg.document.file_name}")
                            await bot.send_message(
                                msg.chat.id,
                                f"📄 Файл получен: {msg.document.file_name}\n\n"
                                f"⚠️ Тестовый режим: обработка не выполняется."
                            )
                            logger.info(f"✅ Отправлен ответ о документе")
                
                await asyncio.sleep(2)  # Проверяем каждые 2 секунды
                
            except Exception as e:
                if "conflict" in str(e).lower():
                    logger.warning("⚠️ Конфликт с другим экземпляром бота")
                    await asyncio.sleep(5)
                else:
                    logger.error(f"❌ Ошибка получения обновлений: {e}")
                    await asyncio.sleep(3)
                    
    except KeyboardInterrupt:
        logger.info("⏹️ Мониторинг остановлен")
    finally:
        await bot.session.close()

async def main():
    """Основная функция"""
    # Сначала проверяем статус бота
    success = await monitor_bot()
    
    if success:
        # Затем начинаем мониторинг обновлений
        await check_updates_periodically()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n⏹️ Мониторинг остановлен пользователем")
    except Exception as e:
        logger.error(f"💥 Критическая ошибка: {e}")
        sys.exit(1)
