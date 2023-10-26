import pika, sys, os
from crawler import *


def main():
    QUEUE = 'crawl'

    connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
    channel = connection.channel()

    channel.queue_declare(queue=QUEUE, durable=True)

    def callback(ch, method, properties, body):
        print(f" [x] Received {body}")
        
        channel.basic_ack(delivery_tag=method.delivery_tag)

    channel.basic_consume(queue=QUEUE, on_message_callback=callback)
    channel.basic_qos(prefetch_count=1)

    print(' [*] Waiting for messages. To exit press CTRL+C')
    channel.start_consuming()


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print('Consumer interrupted')
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)