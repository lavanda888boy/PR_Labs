import pika
import os
import re
from multiprocessing import Process, Manager

from consumer import Consumer
from crawler import scanPage


def run_consumer(worker: Consumer):
    worker.main()


def main():
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(host='localhost'))
    channel = connection.channel()

    QUEUE = 'crawl'
    NUMBER_OF_CONSUMERS = 4
    MAX_NUM_PAGES = 2

    DB_NAME = 'apartments.json'
    TABLE_NAME = 'advertisements'
    if os.path.exists(DB_NAME):
        os.remove(DB_NAME)

    channel.queue_declare(queue=QUEUE, durable=False)

    site_url = 'https://999.md/ro/list/real-estate/apartments-and-rooms?applied=1&eo=12900&eo=12912&eo=12885&eo=13859&ef=32&ef=33&o_33_1=776&page=10'

    init_page = 0
    if 'page' in site_url:
        p = re.split(r"&(page=[0-9]+)", site_url)[1]
        init_page = int(re.split(r"=", p)[1])
    else:
        init_page = 1

    manager = Manager()
    shared_lock = manager.Lock()

    processes = []
    for i in range(NUMBER_OF_CONSUMERS):
        worker = Consumer(f'C{i}', QUEUE, DB_NAME, shared_lock, TABLE_NAME)
        process = Process(target=run_consumer, args=(worker,))
        processes.append(process)
        process.start()

    marker, list_of_urls = scanPage(site_url, init_page, init_page + MAX_NUM_PAGES)
    copy_init_page = init_page
    
    while (marker != -1) and (list_of_urls[len(list_of_urls) - 1] != ''):
        for index in range(len(list_of_urls) - 1):
            channel.basic_publish(exchange='',
                                routing_key=QUEUE,
                                body=list_of_urls[index],
                                properties=pika.BasicProperties(
                                    delivery_mode=pika.spec.PERSISTENT_DELIVERY_MODE
                                ))
            print(f'Published url: {list_of_urls[index]}')
        
        copy_init_page += 1
        marker, list_of_urls = scanPage(list_of_urls[len(list_of_urls) - 1], copy_init_page, init_page + MAX_NUM_PAGES)

    for i in range(NUMBER_OF_CONSUMERS):
        channel.basic_publish(exchange='',
                            routing_key=QUEUE,
                            body='terminate',
                            properties=pika.BasicProperties(
                                delivery_mode=pika.spec.PERSISTENT_DELIVERY_MODE
                            ))
        
    connection.close()

    for process in processes:
        process.join()

    print('Crawling terminated')
    for process in processes:
        process.terminate()


if __name__ == '__main__':
    main()
