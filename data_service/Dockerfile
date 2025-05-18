FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1
ENV GCS_BUCKET_NAME=${GCS_BUCKET_NAME:-cloudless-files}
ENV PORT=${PORT:-8002}
ENV HOST=${HOST:-0.0.0.0}
ENV POSTGRES_USER=${POSTGRES_USER:-myuser}
ENV POSTGRES_PASSWORD=${POSTGRES_PASSWORD:-mypassword}
ENV POSTGRES_DB=${POSTGRES_DB:-mydatabase}
ENV POSTGRES_PORT=${POSTGRES_PORT:-5432}
ENV POSTGRES_HOST=${POSTGRES_HOST:-localhost}

WORKDIR /app

RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

COPY . .

EXPOSE ${PORT}

CMD uvicorn main:app --host $HOST --port $PORT
