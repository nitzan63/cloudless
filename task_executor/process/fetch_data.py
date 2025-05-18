import requests
import os
from dotenv import load_dotenv
load_dotenv()


DATA_SERVICE_URL = f"{os.environ.get('DATA_SERVICE_URL')}"

def fetch_task(task_id):
    response = requests.get(f"{DATA_SERVICE_URL}/tasks/exec/{task_id}")

    file_data = response.json()

    filename = None
    print(response.json())

    if response.status_code == 200:
        filename = file_data['file_name']
        dir_name = "files"
        os.makedirs(dir_name, exist_ok=True)
        file_path = os.path.join(dir_name, filename)

        with open(file_path, "wb") as f:
            f.write(file_data['file_content'])
    else:
        file_path = None

    return filename