import pika
import os

class RabbitMQService:
    def __init__(self):
        self.queue = "tasks"
        credentials = pika.PlainCredentials(os.environ.get("RABBITMQ_USER"), os.environ.get("RABBITMQ_PASS"))
        parameters = pika.ConnectionParameters(host=os.environ.get("RABBITMQ_HOST"), credentials=credentials)
        self.connection = pika.BlockingConnection(parameters)
        self.channel = self.connection.channel()
        self.channel.queue_declare(queue=self.queue)

    def send_message(self, message: str):
        self.channel.basic_publish(
            exchange='',
            routing_key=self.queue,
            body=message
        )
        print(f"[x] Sent: {message}")

    def close(self):
        self.connection.close()
