# Build stage
FROM alpine:3.19 as builder

RUN apk add --no-cache \
    python3 \
    py3-pip \
    py3-virtualenv

COPY ./requirements.txt /requirements.txt

# Create virtual environment and install dependencies
RUN python3 -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r /requirements.txt

# Runtime stage
FROM alpine:3.19

# Install only runtime dependencies
RUN apk add --no-cache \
    wireguard-tools \
    iptables \
    iproute2 \
    procps \
    curl \
    python3

# Copy virtual environment from builder
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copy application files
COPY ./app.py /app.py
COPY ./entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

EXPOSE 51820/udp 5000/tcp

HEALTHCHECK --interval=60s --timeout=5s --start-period=30s --retries=2 \
    CMD curl -f http://localhost:5000/health || exit 1

ENTRYPOINT ["/entrypoint.sh"]