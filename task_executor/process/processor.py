from process.fetch_data import fetch_task
from process.execute import submit_to_spark
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def process(task_id: str):
    logger.info(f"------------Start Processing {task_id}------------")
    filename = fetch_task(task_id)
    submit_to_spark(filename)
    logger.info(f"------------End Processing {task_id}------------")