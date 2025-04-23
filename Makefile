.PHONY: db server

PYTHON = ./server/venv/bin/python

db:
	docker-compose up -d

stop_db:
	docker-compose down

server:
	$(PYTHON) ./server/app.py

migrations:
	$(PYTHON) ./server/db/postgres/migrations.py
