#!/bin/bash

sleep 3

SPARK_MASTER_IP=${SPARK_MASTER_IP:-10.10.0.1}
SPARK_MASTER_PORT=${SPARK_MASTER_PORT:-7077}
WORKER_PORT=${WORKER_PORT:-8881}
SPARK_MASTER_URL=spark://10.10.0.1:7077

/opt/bitnami/spark/bin/spark-class org.apache.spark.deploy.worker.Worker spark://${SPARK_MASTER_IP}:${SPARK_MASTER_PORT} --port ${WORKER_PORT}
