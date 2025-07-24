import bcrypt
import hashlib
from db.postgres_db import PostgresDB

class UserService:
    def __init__(self):
        self.db = PostgresDB()
        self._create_table()

    def _create_table(self):
        query = """
        CREATE TABLE IF NOT EXISTS users (
            id VARCHAR(64) PRIMARY KEY,
            username VARCHAR(255) UNIQUE NOT NULL,
            password_hash VARCHAR(255) NOT NULL,
            type VARCHAR(20) NOT NULL CHECK (type IN ('provider', 'submitter'))
        );
        """
        self.db.execute(query)

    def _hash_username(self, username: str) -> str:
        return hashlib.sha256(username.encode('utf-8')).hexdigest()

    def create_user(self, username: str, password: str, user_type: str):
        if user_type not in ("provider", "submitter"):
            raise ValueError("Invalid user type")
        user_id = self._hash_username(username)
        password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        query = "INSERT INTO users (id, username, password_hash, type) VALUES (%s, %s, %s, %s) RETURNING id;"
        result = self.db.execute(query, (user_id, username, password_hash, user_type))
        return result[0][0] if result else None

    def get_user_by_username(self, username: str):
        query = "SELECT id, username, password_hash, type FROM users WHERE username = %s;"
        result = self.db.execute(query, (username,))
        if not result:
            return None
        columns = ["id", "username", "password_hash", "type"]
        return dict(zip(columns, result[0]))

    def verify_password(self, username: str, password: str):
        user = self.get_user_by_username(username)
        if not user:
            return False
        return bcrypt.checkpw(password.encode('utf-8'), user['password_hash'].encode('utf-8'))

    def __del__(self):
        if hasattr(self, 'db'):
            self.db.close() 