import pika, sys, os, json
from crawler import *

QUEUE = 'crawl'

def main():
    connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
    channel = connection.channel()

    channel.queue_declare(queue=QUEUE)

    processed_urls = set()

    def callback(ch, method, properties, body):
        print(f" [x] Received {body}")
        body = body.decode('utf-8')

        if body not in processed_urls:
            processed_urls.add(body)

            if re.match(r"https://999.md/ro/[0-9]+", body):
                apart_json = scanAdvertisement(body)
                
                option = 'x'
                if os.path.exists('apartments.json'):
                    option = 'a'

                with open('apartments.json', option) as apart:
                    apart.write(json.dumps(apart_json, ensure_ascii=False, indent=4))
                    apart.write(',\n')
                
            else:
                if body == '':
                    print('Crawling terminated')
                else:
                    p_n = 0
                    if 'page' in body:
                        p = re.split(r"&(page=[0-9]+)", body)[1]
                        p_n = int(re.split(r"=", p)[1])
                    else:
                        p_n = 1

                    list_of_urls = scanPage(body, p_n)

                    for url in list_of_urls:
                        channel.basic_publish(exchange='',
                        routing_key=QUEUE,
                        body=url
                        )
                        print(f'Published url: {url}')
            
            channel.basic_ack(delivery_tag=method.delivery_tag)
        
        else:
            print(f'Url {body} is skipped')

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