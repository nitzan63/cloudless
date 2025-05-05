FROM bitnami/spark:latest

USER root

RUN apt-get update
RUN apt-get install -y wget tar unzip ca-certificates
RUN rm -rf /var/lib/apt/lists/*

ENV LIVY_VERSION 0.8.0
ENV LIVY_HOME /opt/livy

COPY apache-livy-0.8.0-incubating_2.11-bin.zip apache-livy-0.8.0-incubating_2.11-bin.zip
RUN unzip apache-livy-0.8.0-incubating_2.11-bin.zip
RUN mv apache-livy-0.8.0-incubating_2.11-bin $LIVY_HOME
RUN rm apache-livy-0.8.0-incubating_2.11-bin.zip

COPY log4j.properties /opt/livy/conf/log4j.properties

RUN mkdir -p /opt/livy/logs && \
    chmod -R 777 /opt/livy/logs

ENV PATH $LIVY_HOME/bin:$PATH

WORKDIR $LIVY_HOME

EXPOSE 8998

CMD ["livy-server"]
