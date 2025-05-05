from postgres_db import PostgresDB

if __name__ == "__main__":
    db = PostgresDB()
    db.execute("""
        CREATE TABLE IF NOT EXISTS task (
            id TEXT PRIMARY KEY,
            creation_time TIMESTAMP NOT NULL,
            created_by TEXT NOT NULL,
            requested_workers_amount INTEGER NOT NULL,
            script_path TEXT NOT NULL,
            status TEXT NOT NULL
        );
    """)
    db.close()
