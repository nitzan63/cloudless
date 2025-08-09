from process.fetch_data import fetch_task
from process.execute import submit_to_spark
import logging
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def process(task_id: str):
    logger.info(f"------------Start Processing {task_id}------------")
    filename = fetch_task(task_id)

    # Build arguments for the job
    # Fetch task execution info again to include dataset download URL if present
    from dotenv import load_dotenv
    import requests
    load_dotenv()
    data_service_url = os.environ.get('DATA_SERVICE_URL')
    info = requests.get(f"{data_service_url}/tasks/exec/{task_id}").json()

    args = []
    if 'dataset_download_url' in info:
        args.append(info['dataset_download_url'])

    submit_to_spark(filename, task_id, args=args)
    logger.info(f"------------End Processing {task_id}------------")