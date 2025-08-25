import os
import logging
import requests
import re
from apscheduler.schedulers.blocking import BlockingScheduler
from dotenv import load_dotenv
from services.task_service import TaskService
from services.livy_service import LivyService
from bs4 import BeautifulSoup
load_dotenv()

task_service = TaskService(os.environ.get('DATA_SERVICE_URL', 'http://localhost:8002'))
livy_service = LivyService(os.environ.get('LIVY_URL', 'http://localhost:8998'))
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

def get_app_id_from_logs(logs):
    match = re.search(r'app-\d{14}-\d{4}', logs)
    if match:
        return match.group()
    return ""

def get_executors(app_id):
    try:
        spark_ui_url = os.environ.get('SPARK_UI_URL', 'http://10.10.0.1:8080')
        url = f"{spark_ui_url}/app/?appId={app_id}"
        response = requests.get(url)
        html = response.text

        soup = BeautifulSoup(html, "html.parser")
        worker_ids = []
        for table in soup.find_all("table"):
            for row in table.find_all("tr"):
                cells = row.find_all("td")
                if len(cells) >= 2:
                    worker_link = cells[1].find("a")
                    if worker_link:
                        worker_ids.append(worker_link.text.strip())
        return worker_ids
    except Exception as e:
        logging.error(f"Can't get workers from {app_id}, Message: {str(e)}")
        return []


def update_task_status(task_id, new_status, logs, app_id, executors):
    try:
        task_service.update_task(task_id, {
            "status": new_status,
            "logs": logs,
            "app_id": app_id,
            "executors": executors 
        })
        logging.info(f"Task {task_id} status updated: {new_status}")
    except Exception as e:
        logging.error(f"Error updating task {task_id} status: {e}")

def job():
    tasks = fetch_unfinished_tasks()
    for task in tasks:
        batch_id = task.get('batch_job_id')
        task_id = task.get('id')
        if (batch_id == None) or (task_id == None):
            logging.warning(f"Task missing batch_id or task_id: {task}")
            continue
        status = get_livy_status(batch_id)
        if status in ("dead", "error", "killed", "success"):
            if status in ("dead", "error", "killed"):
                db_status = "failed"
            elif status == 'success':
                db_status = 'completed'
            logs = livy_service.get_batch_logs(batch_id)
            app_id = get_app_id_from_logs(logs)
            executors = get_executors(app_id)
            update_task_status(task_id, db_status, logs, app_id, executors)

if __name__ == '__main__':
    scheduler = BlockingScheduler()
    scheduler.add_job(job, 'interval', seconds=INTERVAL_SECONDS)
    logging.info(f"Service started. Running every {INTERVAL_SECONDS} seconds.")
    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        logging.info("Service stopped.")