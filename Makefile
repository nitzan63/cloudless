PYTHON = venv/Scripts/python

services:
	docker-compose up -d

stop-services:
	docker-compose down

local-env:
	docker-compose -f local-env-docker-compose.yml up -d --build

stop-local-env:
	docker-compose -f local-env-docker-compose.yml down -v

server:
	./server/$(PYTHON) ./server/app.py

build-server:
	cd server && \
	docker build -f Dockerfile -t cloudless-main-server .

server-set-up:
	cd server && \
	python -m venv venv && \
	venv\Scripts\activate && \
	pip install -r requirements.txt

task-executor:
	./task_executor/$(PYTHON) ./task_executor/app.py

tast-executor-set-up:
	cd task_executor && \
	python -m venv venv && \
	venv\Scripts\activate && \
	pip install -r requirements.txt

migrations:
	./server/$(PYTHON) ./server/db/postgres/migrations.py

build-spark-worker:
	cd spark && \
	docker build -f sparkWorker.Dockerfile -t spark-worker-vpn .

run-spark-worker:
	docker run -it --rm --cap-add=NET_ADMIN --device /dev/net/tun spark-worker-vpn

run-spark-master:
	docker run -d --name spark-master -p 7077:7077 -p 7079:7079 -p 7078:7078 -p 8080:8080 -e PYSPARK_PYTHON=python -e SPARK_MODE=master -e SPARK_MASTER_URL=spark://34.134.59.39:7077  bitnami/spark:latest

run-spark-job:
	bin/spark-submit --conf spark.driver.host=34.134.59.39 --conf spark.driver.port=7078 --conf spark.blockManager.port=7079 --conf spark.driver.bindAddress=0.0.0.0 --master spark://34.134.59.39:7077 /wordcount.py

remove-none-docker-images:
	for /f "tokens=*" %i in ('docker images -f "dangling=true" -q') do docker rmi %i