from postgres_db import PostgresDB

if __name__ == "__main__":
    db = PostgresDB()
    db.execute("DROP TABLE IF EXISTS provider;")
    db.close()
