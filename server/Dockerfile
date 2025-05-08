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

# Set environment variables
ENV GCS_BUCKET_NAME=${GCS_BUCKET_NAME:-cloudless-files}
ENV PORT=${PORT:-8000}
ENV HOST=${HOST:-0.0.0.0}
ENV POSTGRES_USER=${POSTGRES_USER:-myuser}
ENV POSTGRES_PASSWORD=${POSTGRES_PASSWORD:-mypassword}
ENV POSTGRES_DB=${POSTGRES_DB:-mydatabase}
ENV POSTGRES_PORT=${POSTGRES_PORT:-5432}
ENV POSTGRES_HOST=${POSTGRES_HOST:-localhost}
ENV RABBITMQ_USER=${RABBITMQ_USER:-user}
ENV RABBITMQ_PASS=${RABBITMQ_PASS:-pass}
ENV RABBITMQ_HOST=${RABBITMQ_HOST:-localhost}

# Expose port
EXPOSE ${PORT}

# Command to run the application
CMD ["python3", "app.py"] 