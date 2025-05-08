import uuid
from datetime import datetime

class TaskService:
    def __init__(self, db):
        self.db = db
        db.execute("""
            CREATE TABLE IF NOT EXISTS task (
                id TEXT PRIMARY KEY,
                creation_time TIMESTAMP NOT NULL,
                created_by TEXT NOT NULL,
                requested_workers_amount INTEGER NOT NULL,
                script_path TEXT NOT NULL,
                main_file_name TEXT NOT NULL,
                status TEXT NOT NULL
            );
        """)

    def create_task(self, created_by, requested_workers_amount, status, script_path, main_file_name):
        task_id = str(uuid.uuid4())
        creation_time = datetime.utcnow()
        self.db.execute("""
            INSERT INTO task (id, creation_time, created_by, requested_workers_amount, script_path, main_file_name, status)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (task_id, creation_time, created_by, requested_workers_amount, script_path, main_file_name, status))
        return task_id

    def get_task(self, task_id):
        cursor = self.db.conn.cursor()
        cursor.execute("SELECT * FROM task WHERE id = %s", (task_id,))
        rows = cursor.fetchall()
        if rows:
            columns = [desc[0] for desc in cursor.description]
            return dict(zip(columns, rows[0]))
        return None

    def update_task(self, task_id, **kwargs):
        allowed_fields = {"created_by", "requested_workers_amount", "script_path", "main_file_name", "status"}
        fields = []
        values = []
        for key, value in kwargs.items():
            if key in allowed_fields:
                fields.append(f"{key} = %s")
                values.append(value)
        if not fields:
            return False
        values.append(task_id)
        self.db.execute(f"""
            UPDATE task SET {', '.join(fields)} WHERE id = %s
        """, tuple(values))
        return True

    def delete_task(self, task_id):
        self.db.execute("DELETE FROM task WHERE id = %s", (task_id,))
        return True

    def list_tasks(self):
        rows = self.db.execute("SELECT * FROM task")
        if not rows:
            return []
        with self.db.conn.cursor() as cur:
            cur.execute("SELECT * FROM task")
            columns = [desc[0] for desc in cur.description]
        return [dict(zip(columns, row)) for row in rows]
