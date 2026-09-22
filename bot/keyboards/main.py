"""Кнопки под полем ввода. Нажатие отправляет текст кнопки как обычное сообщение."""

from aiogram.types import KeyboardButton, ReplyKeyboardMarkup


def main_keyboard() -> ReplyKeyboardMarkup:
    """Четыре кнопки = четыре команды. Так не нужно помнить синтаксис."""
    return ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text="/add"),
                KeyboardButton(text="/list"),
            ],
            [KeyboardButton(text="/list_csv")],
        ],
        resize_keyboard=True,
        input_field_placeholder="Задача: /add Текст задачи",
    )
