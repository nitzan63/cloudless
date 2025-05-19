import pika
import os
import time
import json
from pika.exceptions import AMQPConnectionError, AMQPChannelError

class RabbitMQService:
    def __init__(self):
        self.queue = "tasks"
        self.credentials = pika.PlainCredentials(
            os.environ.get("RABBITMQ_USER"), 
            os.environ.get("RABBITMQ_PASS")
        )
        self.parameters = pika.ConnectionParameters(
            host=os.environ.get("RABBITMQ_HOST"),
            credentials=self.credentials,
            heartbeat=600,  # Add heartbeat
            blocked_connection_timeout=300  # Add timeout
        )
        self.connection = None
        self.channel = None
        self.connect()

    def connect(self):
        max_retries = 10
        retry_delay = 4  # seconds
        
        for attempt in range(max_retries):
            try:
                if self.connection and not self.connection.is_closed:
                    self.connection.close()
                
                self.connection = pika.BlockingConnection(self.parameters)
                self.channel = self.connection.channel()
                self.channel.queue_declare(queue=self.queue, durable=True)  # Make queue durable
                break
            except (AMQPConnectionError, ConnectionResetError) as e:
                if attempt == max_retries - 1:
                    raise Exception(f"Failed to connect to RabbitMQ after {max_retries} attempts") from e
                print(f"Connection attempt {attempt + 1} failed, retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)
                retry_delay *= 2

    def send_message(self, message):
        try:
            # Ensure message is properly serialized
            if not isinstance(message, str):
                message = json.dumps(message)
            
            # Check if connection is still valid
            if not self.connection or self.connection.is_closed:
                self.connect()
            
            self.channel.basic_publish(
                exchange='',
                routing_key=self.queue,
                body=message,
                properties=pika.BasicProperties(
                    delivery_mode=2,  # Make message persistent
                )
            )
            print(f"[x] Sent: {message}")
        except (AMQPConnectionError, AMQPChannelError, ConnectionResetError):
            # Attempt to reconnect and resend
            self.connect()
            self.send_message(message)  # Retry sending the message

    def close(self):
        if self.connection and not self.connection.is_closed:
            self.connection.close()
