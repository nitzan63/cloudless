import os
import logging
import requests
from apscheduler.schedulers.blocking import BlockingScheduler
from dotenv import load_dotenv
from services.task_service import TaskService
from services.livy_service import LivyService
load_dotenv()

task_service = TaskService(os.environ.get('DATA_SERVICE_API_URL', 'http://localhost:8002'))
livy_service = LivyService(os.environ.get('LIVY_API_URL', 'http://localhost:8998'))
INTERVAL_SECONDS = int(os.environ.get('INTERVAL_SECONDS', 5))

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')

def fetch_unfinished_tasks():
    try:
        tasks = task_service.get_unfinished_tasks()
        logging.info(f"Unfinished tasks received: {tasks}")
        return tasks
    except Exception as e:
        logging.error(f"Error fetching unfinished tasks: {e}")
        return []

def get_livy_status(batch_id):
    try:
        resp = livy_service.get_batch_status(batch_id)
        state = resp.json()["state"]
        logging.info(f"Batch {batch_id} status: {state}")
        return state
    except Exception as e:
        logging.error(f"Error fetching Livy status for batch {batch_id}: {e}")
        return None

def update_task_status(task_id, new_status):
    try:
        task_service.update_task(task_id, {"status": new_status})
        logging.info(f"Task {task_id} status updated: {new_status}")
    except Exception as e:
        logging.error(f"Error updating task {task_id} status: {e}")

def job():
    tasks = fetch_unfinished_tasks()
    for task in tasks:
        batch_id = task.get('batch_job_id')
        task_id = task.get('id')
        if not batch_id or not task_id:
            logging.warning(f"Task missing batch_id or task_id: {task}")
            continue
        status = get_livy_status(batch_id)
        if status in ("dead", "error", "killed"):
            update_task_status(task_id, "failed")
        if status == 'success':
            update_task_status(task_id, "completed")

if __name__ == '__main__':
    scheduler = BlockingScheduler()
    scheduler.add_job(job, 'interval', seconds=INTERVAL_SECONDS)
    logging.info(f"Service started. Running every {INTERVAL_SECONDS} seconds.")
    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        logging.info("Service stopped.")