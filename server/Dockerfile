FROM --platform=linux/amd64 python:3.9-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV PORT=${PORT:-8000}
ENV HOST=${HOST:-0.0.0.0}
ENV DATA_SERVICE_URL=${DATA_SERVICE_URL:-http://localhost:8002}
ENV RABBITMQ_USER=${RABBITMQ_USER:-user}
ENV RABBITMQ_PASS=${RABBITMQ_PASS:-pass}
ENV RABBITMQ_HOST=${RABBITMQ_HOST:-localhost}
ENV RABBITMQ_PORT=${RABBITMQ_PORT:-5672}

# Expose port
EXPOSE ${PORT}

# Command to run the application
CMD ["python3", "app.py"] 