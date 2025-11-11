"""History and task details handler."""
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message
from db.crud import get_user_tasks
from db.models import Task
from config.constants import TaskStatus
from bot.i18n import tr, all_translations_for_key

router = Router()
HISTORY_BUTTONS = list(all_translations_for_key("menu.history"))


def format_task_line(task: Task) -> str:
    """Format single task line for history."""
    duration = int(task.duration or 0)
    mm = duration // 60
    ss = duration % 60
    dur_str = f"{mm:02d}:{ss:02d}"
    status_emoji = "✅" if task.status == TaskStatus.COMPLETED else ("❌" if task.status == TaskStatus.FAILED else "⏳")
    return f"#{task.id} · {dur_str} · {status_emoji}"


@router.message(Command("history"))
@router.message(F.text.in_(HISTORY_BUTTONS))
async def cmd_history(message: Message, user, db, **kwargs):
    """Show last 5 tasks."""
    tasks = await get_user_tasks(db, user.id, limit=5)
    if not tasks:
        await message.answer(tr(user, "🧾 Последние задачи\nПока пусто. Отправь видео, чтобы начать.", "🧾 Recent tasks\nNo tasks yet. Send a video to start."))
        return
    text = tr(user, "🧾 Последние задачи", "🧾 Recent tasks") + "\n\n"
    text += "\n".join(format_task_line(t) for t in tasks)
    await message.answer(text)


