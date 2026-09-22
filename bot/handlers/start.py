"""Команда /start — первое сообщение, когда человек открывает бота."""

from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from bot.keyboards import main_keyboard

router = Router()


@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext) -> None:
    """Поприветствовать и показать, какие команды есть."""
    await state.clear()
    await message.answer(
        "Привет! Это общий список задач команды.\n\n"
        "Как добавить задачу:\n"
        "1. /add и текст задачи\n"
        "2. имя ответственного\n"
        "3. категория: бизнес-требование, разработка, организация, формализация\n"
        "4. статус: новое, в работе, выполнено\n\n"
        "Можно сразу: /add Подготовить сверку часов\n"
        "Дальше бот всё равно спросит ответственного, категорию и статус.\n\n"
        "/list — показать все задачи\n"
        "/list_csv — прислать список файлом CSV",
        reply_markup=main_keyboard(),
    )
