FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

WORKDIR /app

# Сначала копируем зависимости, используем кэш слоёв
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt


COPY main.py server.py bot.py ./

# Запускаем Long Polling-бота
CMD ["python", "bot.py"]