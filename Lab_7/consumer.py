import pika, sys, os, json
from crawler import *

class Consumer:

    def __init__(self, name: str, queue: str, max_num_pages=None):
        self.name = name
        self.queue = queue
        self.max_num_pages = max_num_pages
        self.page_counter = 0

    def main(self):
        connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
        channel = connection.channel()

        channel.queue_declare(queue=self.queue)

        processed_urls = set()

        def callback(ch, method, properties, body):
            print(f'{self.name}: Received body: {body}')
            body = body.decode('utf-8')

            if body not in processed_urls:
                processed_urls.add(body)

                if body == 'terminate':
                    print(f'{self.name}: Crawling terminated')
                    channel.basic_publish(exchange='',
                            routing_key=self.queue,
                            body='terminate'
                            )
                    print(f'{self.name}: Sent termination signal further')
                    sys.exit()

                if re.match(r"https://999.md/ro/[0-9]+", body):
                    apart_json = scanAdvertisement(body)
                    
                    option = 'x'
                    if os.path.exists('apartments.txt'):
                        option = 'a'

                    with open('apartments.txt', option) as apart:
                        apart.write(json.dumps(apart_json, ensure_ascii=False, indent=4))
                        apart.write(',\n')
                    
                else:
                    if body == '':
                        print(f'{self.name}: Crawling terminated')
                    else:
                        p_n = 0
                        if 'page' in body:
                            p = re.split(r"&(page=[0-9]+)", body)[1]
                            p_n = int(re.split(r"=", p)[1])
                        else:
                            p_n = 1

                        self.page_counter, list_of_urls = scanPage(body, self.page_counter, p_n)

                        if self.page_counter == -1:
                            print(f'{self.name}: Crawling terminated')
                            channel.basic_publish(exchange='',
                                    routing_key=self.QUEUE,
                                    body='terminate'
                                    )   
                            print(f'{self.name}: Sent termination signal further')
                            sys.exit()

                        for url in list_of_urls:
                            channel.basic_publish(exchange='',
                            routing_key=self.queue,
                            body=url
                            )
                            print(f'{self.name}: Published url: {url}')
                
                channel.basic_ack(delivery_tag=method.delivery_tag)
            
            else:
                print(f'{self.name}: Url {body} is skipped')

        channel.basic_consume(queue=self.queue, on_message_callback=callback)
        channel.basic_qos(prefetch_count=1)

        print(f'{self.name}: Waiting for messages')
        channel.start_consuming()
