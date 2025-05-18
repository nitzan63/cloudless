from process.fetch_data import fetch_task
from process.execute import submit_to_spark


def process(task_id: str):
    filename = fetch_task(task_id)
    submit_to_spark(filename)