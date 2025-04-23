.PHONY: db stop-db server server-set-up migrations

PYTHON = ./server/venv/Scripts/python

db:
	docker-compose up -d

stop-db:
	docker-compose down

server:
	$(PYTHON) ./server/app.py

server-set-up:
	cd server && \
	python -m venv venv && \
	venv\Scripts\activate.bat && \
	pip install -r requirements.txt

migrations:
	$(PYTHON) ./server/db/postgres/migrations.py
