from process.fetch_data import fetch_task
from process.execute import submit_to_spark


def process(task_id: str):
    task_data = fetch_task(task_id)
    submit_to_spark(task_data['main_file_name'])