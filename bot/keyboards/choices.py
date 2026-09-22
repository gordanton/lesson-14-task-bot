"""Кнопки выбора категории и статуса.

В кнопку кладём короткий код, а в базу и CSV — русское название.
Код нужен, потому что Telegram ограничивает служебные данные кнопки 64 байтами.
"""

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

# Код -> подпись. Порядок такой, как в задании.
CATEGORIES = {
    "bt": "бизнес-требование",
    "dev": "разработка",
    "org": "организация",
    "form": "формализация",
}

STATUSES = {
    "new": "новое",
    "work": "в работе",
    "done": "выполнено",
}


def _choice_keyboard(prefix: str, options: dict[str, str]) -> InlineKeyboardMarkup:
    """Одна кнопка в строке: на кнопке текст, внутри — код вида category:dev."""
    rows = [
        [InlineKeyboardButton(text=label, callback_data=f"{prefix}:{code}")]
        for code, label in options.items()
    ]
    return InlineKeyboardMarkup(inline_keyboard=rows)


def category_keyboard() -> InlineKeyboardMarkup:
    """Четыре фиксированные категории. Свободный ввод здесь не нужен."""
    return _choice_keyboard("category", CATEGORIES)


def status_keyboard() -> InlineKeyboardMarkup:
    """Три статуса задачи."""
    return _choice_keyboard("status", STATUSES)
