FROM bitnami/spark:4.0.0

USER root

RUN apt-get update
RUN apt-get install -y wireguard
RUN apt-get install -y iproute2
RUN apt-get install -y wireguard-tools openresolv
RUN rm -rf /var/lib/apt/lists/*

COPY ./run_spark_worker.sh /opt/bitnami/spark/run.sh
RUN chmod +x /opt/bitnami/spark/run.sh

CMD ["/bin/bash", "-c", "wg-quick up wg0 && /opt/bitnami/spark/run.sh"]