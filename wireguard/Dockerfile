FROM debian:bookworm-slim

RUN apt-get update && apt-get install -y \
    wireguard-tools \
    iptables \
    iproute2 \
    procps \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

EXPOSE 51820/udp

HEALTHCHECK --interval=60s --timeout=5s --start-period=30s --retries=2 \
    CMD wg show || exit 1

ENTRYPOINT ["/entrypoint.sh"]