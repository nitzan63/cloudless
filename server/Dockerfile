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
ENV PORT=${PORT:-8080}
ENV HOST=${HOST:-0.0.0.0}

# Expose port
EXPOSE ${PORT}

# Command to run the application
CMD ["python3", "app.py"] 