"""Настройки бота. Токен читаем из .env, в код его не пишем."""

import os
from pathlib import Path

from dotenv import load_dotenv

# Корень проекта — папка, где лежат main.py и .env.
# __file__ — этот файл (bot/config.py), parent — bot/, parent.parent — корень.
PROJECT_ROOT = Path(__file__).resolve().parent.parent

# load_dotenv подхватывает переменные из .env в окружение процесса.
# Сам .env уже есть в проекте и в .gitignore, создавать его не нужно.
load_dotenv(PROJECT_ROOT / ".env")

# Токен пустой, если в .env нет строки BOT_TOKEN.
BOT_TOKEN = os.getenv("BOT_TOKEN", "").strip()

# Файл базы рядом с проектом: lesson_14/data/tasks.db
DATABASE_PATH = PROJECT_ROOT / "data" / "tasks.db"


def require_token() -> str:
    """Вернуть токен или остановить запуск с понятной ошибкой."""
    if not BOT_TOKEN or BOT_TOKEN.startswith("123456789:"):
        raise SystemExit(
            "В .env нет настоящего BOT_TOKEN.\n"
            "Открой @BotFather, скопируй токен и вставь его в .env:\n"
            "BOT_TOKEN=твой_токен"
        )
    return BOT_TOKEN
