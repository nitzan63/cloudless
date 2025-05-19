from process.fetch_data import fetch_task
from process.execute import submit_to_spark


def process(task_id: str):
    print("TASK_ID:", task_id)
    filename = fetch_task(task_id)
    submit_to_spark(filename)