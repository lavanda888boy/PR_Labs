import pika
import os

from multiprocessing import Pool
from consumer import Consumer


def run_consumer(worker: Consumer):
    worker.main()


def main():
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(host='localhost'))
    channel = connection.channel()

    QUEUE = 'crawl'
    NUMBER_OF_CONSUMERS = 4
    MAX_NUM_PAGES = 2
    pool = Pool(processes=NUMBER_OF_CONSUMERS)
    consumers = []

    if os.path.exists('apartments.txt'):
        os.remove('apartments.txt')

    channel.queue_declare(queue=QUEUE)

    site_url = 'https://999.md/ro/list/real-estate/apartments-and-rooms?applied=1&eo=12900&eo=12912&eo=12885&eo=13859&ef=32&ef=33&o_33_1=776&page=200'
    channel.basic_publish(exchange='',
                        routing_key=QUEUE,
                        body=site_url,
                        properties=pika.BasicProperties(
                            delivery_mode=pika.spec.PERSISTENT_DELIVERY_MODE
                        ))

    print(f' [x] Sent initial url: {site_url}')
    connection.close()

    for i in range(0, NUMBER_OF_CONSUMERS):
        worker = Consumer(f'C{i}', QUEUE, MAX_NUM_PAGES)
        consumers.append(worker)

    pool.map(run_consumer, consumers)

    pool.close()
    pool.join()


if __name__ == '__main__':
    main()
