import requests
import os
from dotenv import load_dotenv
import logging

load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

DATA_SERVICE_URL = f"{os.environ.get('DATA_SERVICE_URL')}"
SHARED_SCRIPTS_PATH = f"{os.environ.get('SHARED_SCRIPTS_PATH')}"

def fetch_task(task_id):
    response = requests.get(f"{DATA_SERVICE_URL}/tasks/exec/{task_id}")

    file_data = response.json()
    logger.info(f"File data: {file_data}")
    filename = None

    if response.status_code == 200:
        filename = file_data['file_name']
        os.makedirs(SHARED_SCRIPTS_PATH, exist_ok=True)
        file_path = os.path.join(SHARED_SCRIPTS_PATH, filename)

        with open(file_path, "w") as f:
            f.write(file_data['file_content'])
    else:
        file_path = None

    return filename