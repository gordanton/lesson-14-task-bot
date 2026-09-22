"""Работа с базой задач. Снаружи пакета импортируем функции отсюда."""

from bot.database.tasks import add_task, get_all_tasks, init_db

__all__ = ["add_task", "get_all_tasks", "init_db"]
