import pika, re
from tinydb import TinyDB

from crawler import *

class Consumer:

    def __init__(self, name: str, queue: str, db_name: str, shared_lock, table_name: str):
        self.name = name
        self.queue = queue
        
        self.db_name = db_name
        self.db_lock = shared_lock
        self.table_name = table_name


    def main(self):
        connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
        channel = connection.channel()

        channel.queue_declare(queue=self.queue, durable=False)

        processed_urls = set()

        def callback(ch, method, properties, body):
            print(f'{self.name}: Received body: {body}')
            body = body.decode('utf-8')

            if body not in processed_urls:
                processed_urls.add(body)

                if re.match(r"https://999.md/ro/[0-9]+", body):
                    apart_json = scanAdvertisement(body)

                    with self.db_lock:
                        db = TinyDB(self.db_name, indent=4)
                        table = db.table(self.table_name)
                        table.insert(apart_json)
                        db.close()
                    
                elif body == 'terminate':
                    channel.basic_ack(delivery_tag=method.delivery_tag)
                    channel.stop_consuming()
                    return
                
                channel.basic_ack(delivery_tag=method.delivery_tag)
            
            else:
                print(f'{self.name}: Url {body} is skipped')

        print(f'{self.name}: Waiting for messages')
        channel.basic_consume(queue=self.queue, on_message_callback=callback)
        channel.basic_qos(prefetch_count=1)
        channel.start_consuming()
