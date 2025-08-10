FROM debian:bookworm-slim

RUN apt-get update && apt-get install -y \
    wireguard-tools \
    iptables \
    iproute2 \
    procps \
    curl \
    python3 \
    python3-pip \
    python3-venv \
    python3-requests \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Copy Flask app and requirements
COPY ./app.py /app.py
COPY ./requirements.txt /requirements.txt

# Install Python dependencies
RUN python3 -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

RUN pip install -r /requirements.txt

COPY ./entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

EXPOSE 51820/udp 5000/tcp

HEALTHCHECK --interval=60s --timeout=5s --start-period=30s --retries=2 \
    CMD curl -f http://localhost:5000/health || exit 1

ENTRYPOINT ["/entrypoint.sh"]