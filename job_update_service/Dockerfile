FROM python:3.11-slim

ENV DATA_SERVICE_URL=${DATA_SERVICE_URL:-http://localhost:8002}
ENV LIVY_URL=${LIVY_URL:-http://localhost:8998}
ENV INTERVAL_SECONDS=${INTERVAL_SECONDS:-5}

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

COPY . .

CMD ["python3", "app.py"]