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
    # Get execution metadata (download_url, file_name)
    resp = requests.get(f"{DATA_SERVICE_URL}/tasks/exec/{task_id}")
    resp.raise_for_status()
    info = resp.json()

    if info.get('status') != 'success':
        raise RuntimeError(f"Failed to fetch task info: {info}")

    file_name = info['file_name']
    download_url = info['download_url']

    # If the URL is relative (local storage), prefix data-service base URL
    if download_url.startswith('/'):
        download_url = f"{DATA_SERVICE_URL}{download_url}"

    os.makedirs(SHARED_SCRIPTS_PATH, exist_ok=True)
    file_path = os.path.join(SHARED_SCRIPTS_PATH, file_name)

    with requests.get(download_url, stream=True) as r:
        r.raise_for_status()
        with open(file_path, 'wb') as f:
            for chunk in r.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)

    logger.info(f"Downloaded script to {file_path}")
    return file_name