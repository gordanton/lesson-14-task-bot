"""SQLite: одна таблица tasks.

SQLite — база в одном файле, отдельный сервер не нужен.
Для учебного бота этого достаточно.
"""

import sqlite3
from contextlib import contextmanager
from datetime import datetime

from bot.config import DATABASE_PATH


@contextmanager
def _connect():
    """Открыть файл базы и закрыть его, когда блок with закончится.

    Обычный with у sqlite3 только сохраняет транзакцию, файл при этом
    остаётся открытым. Здесь закрываем соединение сами.
    """
    DATABASE_PATH.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(DATABASE_PATH)
    # row_factory даёт доступ к полям по имени: row["text"], а не row[1].
    connection.row_factory = sqlite3.Row
    try:
        yield connection
        connection.commit()
    finally:
        connection.close()


def init_db() -> None:
    """Создать таблицу, если её ещё нет, и добавить новые колонки в старый файл.

    CREATE TABLE не меняет уже существующую таблицу. Поэтому для базы,
    которая появилась до ответственного, категории и статуса, колонки
    добавляем отдельно. Старые задачи при этом не удаляются.
    """
    with _connect() as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                text TEXT NOT NULL,
                user TEXT NOT NULL,
                responsible TEXT NOT NULL DEFAULT '',
                category TEXT NOT NULL DEFAULT '',
                status TEXT NOT NULL DEFAULT 'новое',
                created_at TEXT NOT NULL
            )
            """
        )
        # PRAGMA table_info — список колонок. name берём у каждой строки ответа.
        existing = {
            row["name"]
            for row in connection.execute("PRAGMA table_info(tasks)").fetchall()
        }
        # ALTER TABLE добавляет колонку в конец. DEFAULT заполняет старые строки.
        columns = {
            "responsible": "TEXT NOT NULL DEFAULT ''",
            "category": "TEXT NOT NULL DEFAULT ''",
            "status": "TEXT NOT NULL DEFAULT 'новое'",
        }
        for name, definition in columns.items():
            if name not in existing:
                connection.execute(f"ALTER TABLE tasks ADD COLUMN {name} {definition}")


def add_task(text: str, user: str, responsible: str, category: str, status: str) -> int:
    """Сохранить задачу и вернуть её id."""
    created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with _connect() as connection:
        cursor = connection.execute(
            """
            INSERT INTO tasks (text, user, responsible, category, status, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (text, user, responsible, category, status, created_at),
        )
        # lastrowid — номер, который SQLite только что выдал новой строке.
        return int(cursor.lastrowid)


def get_all_tasks() -> list[dict]:
    """Все задачи, сначала старые. Так список читается сверху вниз по времени.

    В словарь копируем сразу: после закрытия соединения строка базы
    может стать недоступной.
    """
    with _connect() as connection:
        rows = connection.execute(
            """
            SELECT id, text, user, responsible, category, status, created_at
            FROM tasks
            ORDER BY id
            """
        ).fetchall()
        return [dict(row) for row in rows]
