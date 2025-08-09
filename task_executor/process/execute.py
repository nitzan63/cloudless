from dotenv import load_dotenv
from services.livy_service import LivyService 
import requests
import time
import uuid
import os
from services.task_service import TaskService

load_dotenv()

SHARED_SCRIPTS_PATH = f"{os.environ.get('SHARED_SCRIPTS_PATH')}"


def submit_to_spark(file_name, task_id, args=None, conf=None):
    livy_service = LivyService(os.environ.get("LIVY_URL"))
    task_service = TaskService(os.environ.get("DATA_SERVICE_URL"))
    job_name = str(uuid.uuid4())

    # Build local file path reference inside Livy/spark container
    job_id = livy_service.submit_batch(
        f"local:{SHARED_SCRIPTS_PATH}/{file_name}",
        job_name,
        args=args or [],
        conf=conf or {}
    )
    task_service.update_task(task_id, {"status": "running", "batch_job_id": job_id})
    print(f"Start job: {job_id}")

    # print("Waiting for batch job to finish...")
    # while True:
    #     resp = livy_service.get_batch_status(job_id)
    #     state = resp.json()["state"]
    #     print(f"  Batch State: {state}")
    #     if state in ("success", "dead", "error", "killed"):
    #         break
    #     time.sleep(2)

    # livy_service.get_batch_logs(job_id)