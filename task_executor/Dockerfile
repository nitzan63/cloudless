FROM python:3.11-slim

ENV RABBITMQ_USER=${RABBITMQ_USER:-user}
ENV RABBITMQ_PASS=${RABBITMQ_PASS:-pass}
ENV RABBITMQ_HOST=${RABBITMQ_HOST:-localhost}
ENV RABBITMQ_PORT=${RABBITMQ_PORT:-5672}
ENV DATA_SERVICE_URL=${DATA_SERVICE_URL:-http://localhost:8002}
ENV LIVY_URL=${LIVY_URL:-http://localhost:8998}
ENV SHARED_SCRIPTS_PATH=${SHARED_SCRIPTS_PATH:-/app/scripts}

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

COPY . .

CMD ["python3", "app.py"]