import pika
import os
from multiprocessing import Pool, Manager

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

    DB_NAME = 'apartments.json'
    TABLE_NAME = 'advertisements'
    if os.path.exists(DB_NAME):
        os.remove(DB_NAME)

    channel.queue_declare(queue=QUEUE, durable=False)

    site_url = 'https://999.md/ro/list/real-estate/apartments-and-rooms?applied=1&eo=12900&eo=12912&eo=12885&eo=13859&ef=32&ef=33&o_33_1=776&page=10'
    channel.basic_publish(exchange='',
                        routing_key=QUEUE,
                        body=site_url,
                        properties=pika.BasicProperties(
                            delivery_mode=pika.spec.PERSISTENT_DELIVERY_MODE
                        ))

    print(f' [x] Sent initial url: {site_url}')
    connection.close()

    manager = Manager()
    shared_lock = manager.Lock()
    for i in range(0, NUMBER_OF_CONSUMERS):
        worker = Consumer(f'C{i}', QUEUE, DB_NAME, shared_lock, TABLE_NAME, MAX_NUM_PAGES)
        consumers.append(worker)

    pool.map(run_consumer, consumers)

    pool.close()
    pool.join()


if __name__ == '__main__':
    main()
