import requests
import os
from dotenv import load_dotenv
load_dotenv()


BASE_URL = f"{os.environ.get('MAIN_SERVER_URL')}/api/tasks"

def fetch_task(task_id):
    task_res = requests.get(f"{BASE_URL}/{task_id}")
    file_res = requests.get(f"{BASE_URL}/file/{task_id}")

    task_data = task_res.json()

    if file_res.status_code == 200:
        # Extract filename from Content-Disposition header
        cd = file_res.headers.get("Content-Disposition", "")
        filename = cd.split("filename=")[-1].strip('"') if "filename=" in cd else f"{task_id}_script.py"
        dir_name = "files"
        os.makedirs(dir_name, exist_ok=True)
        file_path = os.path.join(dir_name, filename)

        with open(file_path, "wb") as f:
            f.write(file_res.content)
    else:
        file_path = None

    return task_data