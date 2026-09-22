"""Сборка роутеров.

Роутер (Router) в aiogram 3 — это группа обработчиков.
Каждый пакет со своими командами, в main.py подключаем их одним вызовом.
"""

from aiogram import Router

from bot.handlers.start import router as start_router
from bot.handlers.tasks import router as tasks_router


def setup_routers() -> Router:
    """Собрать все команды в один корневой роутер."""
    root = Router()
    root.include_router(start_router)
    root.include_router(tasks_router)
    return root
