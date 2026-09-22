"""Команды списка задач: добавить, показать, скачать CSV."""

import csv
import io

from aiogram import F, Router
from aiogram.filters import Command, CommandObject
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import BufferedInputFile, CallbackQuery, Message, User

from bot.database import add_task, get_all_tasks
from bot.keyboards import CATEGORIES, STATUSES, category_keyboard, status_keyboard

router = Router()


class AddTask(StatesGroup):
    """Шаги диалога. Бот помнит, на каком вопросе остановился человек.

    Текст и ответственный приходят обычными сообщениями.
    Категория и статус — нажатием кнопки, чтобы не было опечаток в CSV.
    """

    waiting_text = State()
    waiting_responsible = State()
    waiting_category = State()
    waiting_status = State()


# Лимит одного сообщения в Telegram — 4096 символов. Оставляем запас.
_MESSAGE_LIMIT = 4000

# Заголовки CSV. Имена совпадают с колонками таблицы, так файл проще сверять с базой.
_CSV_COLUMNS = ["id", "text", "responsible", "category", "status", "user", "created_at"]


def _user_label(user: User | None) -> str:
    """Кто добавил задачу: @username, а если его нет — имя и id.

    Берём человека из нажатия кнопки, а не из сообщения бота:
    у сообщения с кнопками автор — сам бот.
    """
    if user is None:
        return "неизвестный"
    if user.username:
        return f"@{user.username}"
    return f"{user.full_name} (id {user.id})"


def _format_tasks(rows) -> str:
    """Собрать человекочитаемый список. Пустая база — отдельная фраза."""
    if not rows:
        return "Список пуст. Добавь задачу командой /add"
    blocks = []
    for row in rows:
        responsible = row["responsible"] or "не указан"
        category = row["category"] or "не указана"
        status = row["status"] or "новое"
        blocks.append(
            f"{row['id']}. {row['text']}\n"
            f"ответственный: {responsible}\n"
            f"категория: {category}\n"
            f"статус: {status}\n"
            f"добавил: {row['user']}, {row['created_at']}"
        )
    return "\n\n".join(blocks)


def _choice_label(options: dict[str, str], code: str) -> str | None:
    """Русское название по коду кнопки. None — кнопки с таким кодом нет."""
    return options.get(code)


async def _ask_responsible(message: Message, state: FSMContext, text: str) -> None:
    """Запомнить текст и перейти к следующему вопросу."""
    await state.update_data(text=text)
    await state.set_state(AddTask.waiting_responsible)
    await message.answer("Кто ответственный? Напиши имя следующим сообщением.")


async def _save_draft(message: Message, state: FSMContext, status: str, author: str) -> None:
    """Собрать ответы из памяти диалога и записать одну строку в базу."""
    draft = await state.get_data()
    task_text = (draft.get("text") or "").strip()
    responsible = (draft.get("responsible") or "").strip()
    category = (draft.get("category") or "").strip()
    if not task_text or not responsible or not category:
        await state.clear()
        await message.answer("Черновик задачи потерялся. Начни заново: /add")
        return

    task_id = add_task(task_text, author, responsible, category, status)
    await state.clear()
    await message.answer(
        f"Задача #{task_id} добавлена.\n"
        f"ответственный: {responsible}\n"
        f"категория: {category}\n"
        f"статус: {status}"
    )


@router.message(Command("add"))
async def cmd_add(message: Message, command: CommandObject, state: FSMContext) -> None:
    """Начать задачу.

    /add Текст — текст уже есть, сразу спрашиваем ответственного.
    /add без текста — сначала ждём текст задачи.
    """
    text = (command.args or "").strip()
    if not text:
        await state.set_state(AddTask.waiting_text)
        await message.answer("Напиши текст задачи следующим сообщением.")
        return

    await _ask_responsible(message, state, text)


@router.message(Command("list"))
async def cmd_list(message: Message, state: FSMContext) -> None:
    """Показать все задачи. Длинный список режем на несколько сообщений."""
    # Другая команда отменяет незаконченный ввод.
    await state.clear()
    text = _format_tasks(get_all_tasks())
    for start in range(0, len(text), _MESSAGE_LIMIT):
        await message.answer(text[start : start + _MESSAGE_LIMIT])


@router.message(Command("list_csv"))
async def cmd_list_csv(message: Message, state: FSMContext) -> None:
    """Собрать CSV в памяти и отправить как файл, без записи на диск."""
    await state.clear()
    rows = get_all_tasks()

    # StringIO — «файл» в оперативной памяти. utf-8-sig нужен, чтобы Excel
    # открыл кириллицу без кракозябр (в начале файла будет метка BOM).
    buffer = io.StringIO()
    writer = csv.writer(buffer)
    writer.writerow(_CSV_COLUMNS)
    for row in rows:
        writer.writerow([row[column] for column in _CSV_COLUMNS])

    document = BufferedInputFile(
        buffer.getvalue().encode("utf-8-sig"),
        filename="tasks.csv",
    )
    caption = "Список задач" if rows else "Задач пока нет — в файле только заголовки"
    await message.answer_document(document, caption=caption)


@router.callback_query(AddTask.waiting_category, F.data.startswith("category:"))
async def pick_category(callback: CallbackQuery, state: FSMContext) -> None:
    """Сохранить категорию с кнопки и спросить статус."""
    code = (callback.data or "").split(":", 1)[1]
    category = _choice_label(CATEGORIES, code)
    if category is None:
        await callback.answer("Такой категории нет")
        return

    await state.update_data(category=category)
    await state.set_state(AddTask.waiting_status)
    if isinstance(callback.message, Message):
        await callback.message.edit_text(
            f"Категория: {category}\nВыбери статус:",
            reply_markup=status_keyboard(),
        )
    # answer убирает «часики» на кнопке. Без этого Telegram крутит нажатие.
    await callback.answer()


@router.callback_query(AddTask.waiting_status, F.data.startswith("status:"))
async def pick_status(callback: CallbackQuery, state: FSMContext) -> None:
    """Статус — последний шаг. После него задача пишется в базу."""
    code = (callback.data or "").split(":", 1)[1]
    status = _choice_label(STATUSES, code)
    if status is None:
        await callback.answer("Такого статуса нет")
        return

    await callback.answer()
    if not isinstance(callback.message, Message):
        await state.clear()
        return

    await callback.message.edit_reply_markup(reply_markup=None)
    await _save_draft(callback.message, state, status, _user_label(callback.from_user))


@router.callback_query(F.data.startswith("category:") | F.data.startswith("status:"))
async def outdated_choice(callback: CallbackQuery) -> None:
    """Старая кнопка: диалог уже закончился или бот перезапускали."""
    await callback.answer("Это меню уже неактивно. Начни заново: /add", show_alert=True)


@router.message(AddTask.waiting_text)
async def task_text(message: Message, state: FSMContext) -> None:
    """Первый шаг: текст задачи."""
    text = (message.text or "").strip()
    if not text:
        await message.answer("Нужен обычный текст. Напиши, что сделать.")
        return

    await _ask_responsible(message, state, text)


@router.message(AddTask.waiting_responsible)
async def task_responsible(message: Message, state: FSMContext) -> None:
    """Второй шаг: имя ответственного свободным текстом."""
    responsible = (message.text or "").strip()
    if not responsible:
        await message.answer("Напиши имя ответственного.")
        return

    await state.update_data(responsible=responsible)
    await state.set_state(AddTask.waiting_category)
    await message.answer("Выбери категорию:", reply_markup=category_keyboard())


@router.message(AddTask.waiting_category)
async def task_category_text(message: Message) -> None:
    """Если вместо кнопки прислали текст — просим нажать кнопку."""
    await message.answer("Категорию нужно выбрать кнопкой под сообщением выше.")


@router.message(AddTask.waiting_status)
async def task_status_text(message: Message) -> None:
    """То же для статуса: в CSV попадают только три заданных значения."""
    await message.answer("Статус нужно выбрать кнопкой под сообщением выше.")
