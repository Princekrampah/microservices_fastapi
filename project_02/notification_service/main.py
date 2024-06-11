import pika
import sys
import os
import time
import email_service
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
RABBITMQ_URL = os.environ.get("RABBITMQ_URL")

def main():
    # rabbitmq connection
    connection = pika.BlockingConnection(pika.ConnectionParameters(host=RABBITMQ_URL))
    channel = connection.channel()

    def callback(ch, method, properties, body):
        try:
            err = email_service.notification(body)
            if err:
                print(err , "well")
                ch.basic_nack(delivery_tag=method.delivery_tag)
            else:
                print(err)
                ch.basic_ack(delivery_tag=method.delivery_tag)
        except Exception as e:
            print(f"Error processing message: {e}")
            ch.basic_nack(delivery_tag=method.delivery_tag)

    # Listen for messages with "email_notification" queue, if a message is received, call the callback function
    # that sends the email notification
    channel.basic_consume(
        queue="email_notification", on_message_callback=callback
    )

    print("Waiting for messages. To exit press CTRL+C")

    channel.start_consuming()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("Interrupted")
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)