#!/usr/bin/env python3
"""
Скрипт проверки работоспособности AutoSub
"""
import os
import sys
import subprocess
import asyncio
from pathlib import Path

# Добавляем текущую директорию в PYTHONPATH
sys.path.insert(0, str(Path(__file__).parent))

def check_python_version():
    """Проверка версии Python"""
    version = sys.version_info
    print(f"Python версия: {version.major}.{version.minor}.{version.micro}")
    if version.major >= 3 and version.minor >= 11:
        print("✅ Версия Python подходит (требуется 3.11+)")
        return True
    else:
        print("❌ Требуется Python 3.11 или выше")
        return False

def check_env_file():
    """Проверка .env файла"""
    env_path = Path(".env")
    if env_path.exists():
        print("✅ Файл .env найден")
        
        # Проверяем основные переменные
        with open(env_path, 'r') as f:
            content = f.read()
            
        required_vars = ['BOT_TOKEN', 'DB_NAME', 'DB_USER', 'DB_PASSWORD']
        missing = []
        
        for var in required_vars:
            if var not in content or f"{var}=" not in content:
                missing.append(var)
        
        if missing:
            print(f"❌ Отсутствуют переменные: {', '.join(missing)}")
            return False
        else:
            print("✅ Основные переменные окружения настроены")
            return True
    else:
        print("❌ Файл .env не найден")
        return False

def check_system_dependencies():
    """Проверка системных зависимостей"""
    deps = {
        'ffmpeg': 'FFmpeg (для обработки видео)',
        'redis-server': 'Redis (для очередей задач)',
        'psql': 'PostgreSQL (база данных)',
        'docker': 'Docker (альтернативный способ запуска)'
    }
    
    available = {}
    for cmd, desc in deps.items():
        try:
            result = subprocess.run([cmd, '--version'], 
                                  capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                print(f"✅ {desc}")
                available[cmd] = True
            else:
                print(f"❌ {desc}")
                available[cmd] = False
        except (subprocess.TimeoutExpired, FileNotFoundError):
            print(f"❌ {desc}")
            available[cmd] = False
    
    return available

def check_python_dependencies():
    """Проверка Python зависимостей"""
    required_packages = [
        'pydantic',
        'pydantic_settings', 
        'python_dotenv',
        'aiogram',
        'aiohttp',
        'sqlalchemy',
        'redis',
        'rq'
    ]
    
    missing = []
    for package in required_packages:
        try:
            __import__(package)
            print(f"✅ {package}")
        except ImportError:
            print(f"❌ {package}")
            missing.append(package)
    
    return len(missing) == 0, missing

async def check_bot_token():
    """Проверка токена бота"""
    try:
        from config.settings import settings
        from aiogram import Bot
        
        bot = Bot(token=settings.BOT_TOKEN)
        try:
            me = await bot.get_me()
            print(f"✅ Токен бота действителен (@{me.username})")
            return True
        except Exception as e:
            print(f"❌ Ошибка токена бота: {e}")
            return False
        finally:
            await bot.session.close()
    except Exception as e:
        print(f"❌ Не удалось проверить токен: {e}")
        return False

def check_config_loading():
    """Проверка загрузки конфигурации"""
    try:
        from config.settings import settings
        from config.constants import TIER_LIMITS, UserTier
        
        print(f"✅ Конфигурация загружена")
        print(f"   BOT_TOKEN: {settings.BOT_TOKEN[:10]}...")
        print(f"   DB_NAME: {settings.DB_NAME}")
        print(f"   Тарифов: {len(TIER_LIMITS)}")
        return True
    except Exception as e:
        print(f"❌ Ошибка загрузки конфигурации: {e}")
        return False

def check_video_service():
    """Проверка сервиса валидации видео"""
    try:
        import re
        
        def validate_video_url(url: str):
            youtube_pattern = r'(youtube\.com|youtu\.be)'
            tiktok_pattern = r'tiktok\.com'
            instagram_pattern = r'instagram\.com'
            
            if re.search(youtube_pattern, url):
                return True, 'youtube'
            elif re.search(tiktok_pattern, url):
                return True, 'tiktok'
            elif re.search(instagram_pattern, url):
                return True, 'instagram'
            else:
                return False, None
        
        # Тест
        test_urls = [
            ('https://www.youtube.com/watch?v=test', True, 'youtube'),
            ('https://www.tiktok.com/@user/video/123', True, 'tiktok'),
            ('https://www.instagram.com/p/ABC/', True, 'instagram'),
            ('https://example.com/video.mp4', False, None)
        ]
        
        all_passed = True
        for url, expected_valid, expected_source in test_urls:
            is_valid, source = validate_video_url(url)
            if is_valid == expected_valid and source == expected_source:
                print(f"✅ {url[:30]}... -> {source}")
            else:
                print(f"❌ {url[:30]}... -> Expected: {expected_source}, Got: {source}")
                all_passed = False
        
        return all_passed
    except Exception as e:
        print(f"❌ Ошибка проверки видео сервиса: {e}")
        return False

def main():
    """Основная функция проверки"""
    print("=" * 60)
    print("ПРОВЕРКА РАБОТОСПОСОБНОСТИ AUTOSUB")
    print("=" * 60)
    
    results = {}
    
    print("\n1. Проверка версии Python:")
    results['python'] = check_python_version()
    
    print("\n2. Проверка .env файла:")
    results['env'] = check_env_file()
    
    print("\n3. Проверка системных зависимостей:")
    sys_deps = check_system_dependencies()
    results['system'] = any(sys_deps.values())
    
    print("\n4. Проверка Python пакетов:")
    py_deps_ok, missing_packages = check_python_dependencies()
    results['packages'] = py_deps_ok
    
    print("\n5. Проверка загрузки конфигурации:")
    results['config'] = check_config_loading()
    
    print("\n6. Проверка токена бота:")
    try:
        results['bot_token'] = asyncio.run(check_bot_token())
    except Exception as e:
        print(f"❌ Ошибка проверки токена: {e}")
        results['bot_token'] = False
    
    print("\n7. Проверка валидации видео URL:")
    results['video_service'] = check_video_service()
    
    # Итоговый отчет
    print("\n" + "=" * 60)
    print("ИТОГОВЫЙ ОТЧЕТ")
    print("=" * 60)
    
    passed = sum(results.values())
    total = len(results)
    
    for check, status in results.items():
        status_icon = "✅" if status else "❌"
        print(f"{status_icon} {check.replace('_', ' ').title()}")
    
    print(f"\nПройдено: {passed}/{total} проверок")
    
    if passed == total:
        print("\n🎉 ВСЕ ПРОВЕРКИ ПРОЙДЕНЫ! Система готова к работе.")
        return True
    else:
        print(f"\n⚠️  ТРЕБУЕТСЯ ДОПОЛНИТЕЛЬНАЯ НАСТРОЙКА")
        
        # Рекомендации
        print("\nРекомендации:")
        
        if not results['system']:
            print("📦 Установите системные зависимости:")
            if not sys_deps.get('docker', False):
                print("   - Установите Docker Desktop для macOS")
                print("   - Или установите через Homebrew:")
                print("     brew install ffmpeg redis postgresql")
        
        if not results['packages']:
            print("🐍 Установите Python пакеты:")
            print("   pip install -r requirements.txt")
        
        if not results['env']:
            print("⚙️  Настройте .env файл с правильными параметрами")
        
        if not results['bot_token']:
            print("🤖 Проверьте токен бота в .env файле")
        
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
