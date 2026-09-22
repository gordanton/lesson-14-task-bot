"""Точка входа. Запуск: python main.py"""

import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

from bot.config import require_token
from bot.database import init_db
from bot.handlers import setup_routers


async def main() -> None:
    # logging показывает в консоли, что бот жив и какие апдейты приходят.
    logging.basicConfig(level=logging.INFO)

    init_db()

    # Bot — отправка сообщений. Dispatcher — принимает апдейты и отдаёт их роутерам.
    # MemoryStorage помнит, кто сейчас вводит задачу. После перезапуска бота это забывается.
    bot = Bot(token=require_token())
    dispatcher = Dispatcher(storage=MemoryStorage())
    dispatcher.include_router(setup_routers())

    # start_polling — бот сам спрашивает Telegram «есть новое?». Для учёбы этого хватает.
    # На сервере обычно ставят webhook, но для локального запуска polling проще.
    await dispatcher.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
