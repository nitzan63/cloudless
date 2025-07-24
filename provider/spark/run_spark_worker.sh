#!/bin/bash

sleep 3

/opt/bitnami/spark/bin/spark-class org.apache.spark.deploy.worker.Worker spark://10.10.0.1:7077
