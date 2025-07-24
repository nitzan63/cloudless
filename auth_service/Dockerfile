FROM python:3.11-slim

WORKDIR /app


ENV PORT=${PORT:-8003}
ENV HOST=${HOST:-0.0.0.0}

RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

COPY . .

EXPOSE ${PORT}

CMD uvicorn main:app --host $HOST --port $PORT
