from dotenv import load_dotenv
from services.livy_service import LivyService 
import requests
import time
import uuid

load_dotenv()

def submit_to_spark(file_path):
    livy_service = LivyService()
    # TODO: add file name to task metadata and use it like this example below
    job_id = livy_service.submit_batch("local:/scripts/20250505_194512_wordcount.py", str(uuid.uuid4()))
    print(f"Start job: {job_id}")

    print("Waiting for batch job to finish...")
    while True:
        resp = livy_service.get_batch_status(job_id)
        state = resp.json()["state"]
        print(f"  Batch State: {state}")
        if state in ("success", "dead", "error", "killed"):
            break
        time.sleep(2)

    livy_service.get_batch_logs(job_id)