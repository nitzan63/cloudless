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

time.sleep(5)

connection = pika.BlockingConnection(
    pika.ConnectionParameters(
        host=os.environ.get('RABBITMQ_HOST'),
        credentials=pika.PlainCredentials(
            username=os.environ.get('RABBITMQ_USER'),
            password=os.environ.get('RABBITMQ_PASS'),
        )
    )
)
channel = connection.channel()

channel.queue_declare(queue='tasks', durable=True)

def callback(ch, method, properties, body):
    task_id = body.decode('utf-8')
    logger.info(f"Process task: {task_id}")
    process(task_id)

channel.basic_consume(
    queue='tasks',
    on_message_callback=callback,
    auto_ack=True
)

print('Task executor is waiting for commands')
channel.start_consuming()
