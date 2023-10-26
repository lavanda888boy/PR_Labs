import pika

connection = pika.BlockingConnection(
    pika.ConnectionParameters(host='localhost'))
channel = connection.channel()

QUEUE = 'crawl'

channel.queue_declare(queue=QUEUE, durable=True)

site_url = 'https://999.md/ro/list/real-estate/apartments-and-rooms?applied=1&eo=12900&eo=12912&eo=12885&eo=13859&ef=32&ef=33&o_33_1=776&page=10'
channel.basic_publish(exchange='',
                      routing_key=QUEUE,
                      body=site_url,
                      properties=pika.BasicProperties(
                        delivery_mode=pika.spec.PERSISTENT_DELIVERY_MODE
                    ))

print(f' [x] Sent initial url: {site_url}')
connection.close()
