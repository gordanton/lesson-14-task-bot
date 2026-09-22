# Бот общего списка задач

Telegram-бот для команды: задачи пишутся в один список, хранятся в SQLite и выгружаются в CSV.

## Команды

| Команда | Что делает |
| --- | --- |
| `/start` | Приветствие и подсказка |
| `/add` | Добавить задачу по шагам |
| `/list` | Показать все задачи |
| `/list_csv` | Прислать список файлом CSV |

`/add` можно написать вместе с текстом: `/add Подготовить сверку часов`. Дальше бот спрашивает ответственного, категорию и статус.

Категории: бизнес-требование, разработка, организация, формализация.

Статусы: новое, в работе, выполнено.

## Стек

- Python 3.12
- aiogram 3 — библиотека для Telegram-бота
- SQLite — база в одном файле, отдельный сервер не нужен
- Docker — запуск на сервере

## Структура

```
main.py                  точка входа
bot/config.py            токен и путь к базе
bot/database/tasks.py    таблица tasks
bot/handlers/            команды /start, /add, /list, /list_csv
bot/keyboards/           кнопки команд, категории и статуса
Dockerfile
docker-compose.yml
```

Таблица `tasks`: `id`, `text`, `user`, `responsible`, `category`, `status`, `created_at`.

`user` — кто добавил задачу. `responsible` — кто её делает.

## Запуск на компьютере

```bash
pip install -r requirements.txt
```

Токен выдаёт @BotFather. Его нужно вписать в файл `.env` в корне проекта. Образец строки лежит в `EnvExample`. Сам `.env` в Git не попадает.

```bash
python main.py
```

База создаётся сама: `data/tasks.db`.

## Запуск в Docker

```bash
docker compose up -d --build
```

Токен по-прежнему берётся из `.env` рядом с `docker-compose.yml`. Файл базы лежит в томе `bot-data` и не стирается при пересборке контейнера.

Обновление на сервере:

```bash
git pull
docker compose up -d --build
```
