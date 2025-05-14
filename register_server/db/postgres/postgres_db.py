import psycopg2
import os
from dotenv import load_dotenv
from pathlib import Path

load_dotenv()

class PostgresDB:
    def __init__(self):
        self.conn = psycopg2.connect(
            dbname=os.environ.get("POSTGRES_DB", "mydatabase"),
            user=os.environ.get("POSTGRES_USER", "myuser"),
            password=os.environ.get("POSTGRES_PASSWORD", "mypassword"),
            host=os.environ.get("POSTGRES_HOST", "localhost"),
            port=int(os.environ.get("POSTGRES_PORT", 5432))
        )
        self.conn.autocommit = True

    def execute(self, query, params=None):
        with self.conn.cursor() as cur:
            cur.execute(query, params)
            if cur.description:
                return cur.fetchall()
            return None

    def close(self):
        self.conn.close()
