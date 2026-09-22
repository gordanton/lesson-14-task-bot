# Образ с Python. slim — урезанная версия Linux, без лишних программ.
FROM python:3.12-slim

WORKDIR /app

# Сначала зависимости. Если потом меняется только код, Docker не ставит пакеты заново.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Код бота. Файл .env сюда не попадает: он указан в .dockerignore.
COPY . .

# python main.py — та же команда, что и на компьютере.
CMD ["python", "main.py"]
