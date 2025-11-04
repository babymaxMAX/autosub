#!/usr/bin/env python3
"""Скрипт для проверки статуса задачи."""
import os
import sys
from datetime import datetime
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session
from db.models import Task, User
from config.settings import settings

def check_task_status(task_id: int):
    """Проверить статус задачи."""
    try:
        # Создать подключение к БД
        engine = create_engine(settings.database_url_sync)
        
        with Session(engine) as db:
            # Получить задачу
            task = db.query(Task).filter(Task.id == task_id).first()
            
            if not task:
                print(f"❌ Задача #{task_id} не найдена в базе данных.")
                return
            
            # Получить пользователя
            user = db.query(User).filter(User.id == task.user_id).first()
            
            print(f"\n{'='*60}")
            print(f"📋 Статус задачи #{task.id}")
            print(f"{'='*60}")
            print(f"👤 Пользователь: {user.telegram_id} (@{user.username or 'N/A'})")
            print(f"📊 Статус: {task.status.value}")
            print(f"📁 Тип: {task.input_type}")
            print(f"🔗 URL: {task.input_url or 'N/A'}")
            print(f"\n📝 Опции обработки:")
            print(f"  • Субтитры: {'✅' if task.generate_subtitles else '❌'}")
            print(f"  • Перевод: {'✅' if task.translate else '❌'}")
            print(f"  • Озвучка: {'✅' if task.voiceover else '❌'}")
            print(f"  • Вертикальный формат: {'✅' if task.vertical_format else '❌'}")
            print(f"  • Водяной знак: {'✅' if task.add_watermark else '❌'}")
            
            print(f"\n⏰ Временные метки:")
            print(f"  • Создана: {task.created_at.strftime('%Y-%m-%d %H:%M:%S') if task.created_at else 'N/A'}")
            print(f"  • Начата: {task.started_at.strftime('%Y-%m-%d %H:%M:%S') if task.started_at else 'N/A'}")
            print(f"  • Завершена: {task.completed_at.strftime('%Y-%m-%d %H:%M:%S') if task.completed_at else 'N/A'}")
            
            if task.started_at and task.created_at:
                wait_time = (task.started_at - task.created_at).total_seconds()
                print(f"  • Ожидание в очереди: {wait_time:.1f} сек")
            
            if task.completed_at and task.started_at:
                processing_time = (task.completed_at - task.started_at).total_seconds()
                print(f"  • Время обработки: {processing_time:.1f} сек ({processing_time/60:.1f} мин)")
            
            print(f"\n📂 Файлы:")
            print(f"  • Входной файл: {task.input_file_path or 'N/A'}")
            print(f"  • Выходной файл: {task.output_file_path or 'N/A'}")
            print(f"  • Субтитры: {task.subtitles_file_path or 'N/A'}")
            
            if task.error_message:
                print(f"\n❌ Ошибка: {task.error_message}")
            
            print(f"{'='*60}\n")
            
            # Дополнительная информация
            if task.status.value == "processing":
                elapsed = (datetime.utcnow() - task.started_at).total_seconds() if task.started_at else 0
                print(f"⏳ Задача обрабатывается уже {elapsed:.1f} сек ({elapsed/60:.1f} мин)")
            
    except Exception as e:
        print(f"❌ Ошибка при проверке статуса: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    task_id = int(sys.argv[1]) if len(sys.argv) > 1 else 3
    check_task_status(task_id)
