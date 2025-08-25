import uuid
from datetime import datetime
from db.postgres_db import PostgresDB
from config import storage_service
import json

class TaskService:
    def __init__(self):
        self.db = PostgresDB()
        self._create_table()

    def _create_table(self):
        self.db.execute("""
            CREATE TABLE IF NOT EXISTS task (
                id TEXT PRIMARY KEY,
                creation_time TIMESTAMP NOT NULL,
                created_by TEXT NOT NULL,
                requested_workers_amount INTEGER NOT NULL,
                script_path TEXT NOT NULL,
                main_file_name TEXT NOT NULL,
                status TEXT NOT NULL,
                batch_job_id INTEGER,
                logs TEXT,
                app_id TEXT,
                executors TEXT
            );
        """)

    def create_task(self, created_by, requested_workers_amount, file_path, file_name, app_id=None, executors=None):
        task_id = str(uuid.uuid4())
        creation_time = datetime.utcnow()
        
        # Convert executors list to JSON string if provided
        executors_json = json.dumps(executors) if executors else None
        
        self.db.execute("""
            INSERT INTO task (id, creation_time, created_by, requested_workers_amount, script_path, main_file_name, status, batch_job_id, logs, app_id, executors)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (task_id, creation_time, created_by, requested_workers_amount, file_path, file_name, 'submitted', None, None, app_id, executors_json))
        return task_id

    def get_task(self, task_id):
        cursor = self.db.conn.cursor()
        cursor.execute("SELECT * FROM task WHERE id = %s", (task_id,))
        rows = cursor.fetchall()
        if rows:
            columns = [desc[0] for desc in cursor.description]
            task_dict = dict(zip(columns, rows[0]))
            
            # Convert executors JSON string back to list if it exists
            if task_dict.get('executors'):
                try:
                    task_dict['executors'] = json.loads(task_dict['executors'])
                except (json.JSONDecodeError, TypeError):
                    task_dict['executors'] = None
            
            return task_dict
        return None

    def get_task_to_execute(self, task_id):
        task = self.get_task(task_id)
        if task == None:
            return None
        print("Starting to fetch file")
        file_data = storage_service.get_file(task['script_path'])
        return file_data

    def update_task(self, task_id, **kwargs):
        allowed_fields = {"created_by", "requested_workers_amount", "script_path", "main_file_name", "status", "batch_job_id", "logs", "app_id", "executors"}
        fields = []
        values = []
        for key, value in kwargs.items():
            if key in allowed_fields:
                if key == "executors" and value is not None:
                    # Convert executors list to JSON string
                    value = json.dumps(value)
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
        with self.db.conn.cursor() as cur:
            cur.execute("SELECT * FROM task")
            rows = cur.fetchall()
            if not rows:
                return []
            columns = [desc[0] for desc in cur.description]
            tasks = []
            for row in rows:
                task_dict = dict(zip(columns, row))
                # Convert executors JSON string back to list if it exists
                if task_dict.get('executors'):
                    try:
                        task_dict['executors'] = json.loads(task_dict['executors'])
                    except (json.JSONDecodeError, TypeError):
                        task_dict['executors'] = None
                tasks.append(task_dict)
            return tasks

    def get_tasks_not_finished(self):
        with self.db.conn.cursor() as cur:
            cur.execute("SELECT * FROM task WHERE status not in ('completed', 'failed') and batch_job_id is not null")
            rows = cur.fetchall()
            if not rows:
                return []
            columns = [desc[0] for desc in cur.description]
            tasks = []
            for row in rows:
                task_dict = dict(zip(columns, row))
                # Convert executors JSON string back to list if it exists
                if task_dict.get('executors'):
                    try:
                        task_dict['executors'] = json.loads(task_dict['executors'])
                    except (json.JSONDecodeError, TypeError):
                        task_dict['executors'] = None
                tasks.append(task_dict)
            return tasks