import pika
import time
import os
import pika.credentials
from dotenv import load_dotenv
import logging
from process.processor import process

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()

RABBITMQ_HOST = os.environ.get('RABBITMQ_HOST')
RABBITMQ_USER = os.environ.get('RABBITMQ_USER')
RABBITMQ_PASS = os.environ.get('RABBITMQ_PASS')
QUEUE_NAME = 'tasks'

def connect_with_retries(max_retries=10, initial_delay=2):
    delay = initial_delay
    for attempt in range(1, max_retries + 1):
        try:
            logger.info(f"Attempting to connect to RabbitMQ (attempt {attempt})...")
            connection = pika.BlockingConnection(
                pika.ConnectionParameters(
                    host=RABBITMQ_HOST,
                    credentials=pika.PlainCredentials(
                        username=RABBITMQ_USER,
                        password=RABBITMQ_PASS,
                    )
                )
            )
            logger.info("Connected to RabbitMQ successfully.")
            return connection
        except pika.exceptions.AMQPConnectionError as e:
            logger.warning(f"Connection attempt {attempt} failed: {e}")
            if attempt == max_retries:
                logger.error("Max retries reached. Could not connect to RabbitMQ.")
                raise
            logger.info(f"Retrying in {delay} seconds...")
            time.sleep(delay)
            delay *= 2  # Exponential backoff
        except Exception as e:
            logger.error(f"Unexpected error while connecting to RabbitMQ: {e}")
            raise

connection = connect_with_retries()

channel = connection.channel()
channel.queue_declare(queue=QUEUE_NAME, durable=True)

def callback(ch, method, properties, body):
    task_id = body.decode('utf-8')
    logger.info(f"Process task: {task_id}")
    process(task_id)

channel.basic_consume(
    queue=QUEUE_NAME,
    on_message_callback=callback,
    auto_ack=True
)

logger.info('Task executor is waiting for commands')
channel.start_consuming()
