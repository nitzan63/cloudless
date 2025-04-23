import pika
import time
import os
import pika.credentials
from dotenv import load_dotenv

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

channel.queue_declare(queue='tasks')

def callback(ch, method, properties, body):
    print(f" [x] Received {body}")

channel.basic_consume(
    queue='tasks',
    on_message_callback=callback,
    auto_ack=True
)

print('Task executor is waiting for commands')
channel.start_consuming()
