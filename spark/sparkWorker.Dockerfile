FROM bitnami/spark

USER root

RUN apt-get update
RUN apt-get install -y wireguard
RUN apt-get install -y iproute2
RUN apt-get install -y wireguard-tools openresolv
RUN rm -rf /var/lib/apt/lists/*

COPY ./wg0.conf /etc/wireguard/wg0.conf

COPY run_spark_worker.sh /run.sh
RUN chmod +x /run.sh

COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]