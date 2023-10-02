import socket
from bs4 import BeautifulSoup
import re
import os
import json

HOST = '127.0.0.1'
PORT = 8080

simple_endpoints = ['/', '/home', '/about', '/contacts']
product_endpoints = ['/products', '/product']


def process_endpoints():
    for ep in simple_endpoints:
        body = send_endpoint_request(ep)

        ep = re.sub(r'/', r'page_', ep)
        option = 'w'
        if len(os.listdir('Lab_4/data')) == 0:
            option = 'x'
        
        with open(f'Lab_4/data/{ep}.html', option) as f:
            f.write(body)

    body = send_endpoint_request(product_endpoints[0])
    parser = BeautifulSoup(body, 'lxml')

    list_of_products = []
    for pl in parser.find_all('a'):
        product_info = {}
        product_info['Route'] = pl['href']
        response = send_endpoint_request(pl['href'])
        detail_parser = BeautifulSoup(response, 'lxml')

        details = detail_parser.find_all('p')
        for index in range(1, len(details)):
            key_value = details[index].contents[0].split(r':')
            product_info[key_value[0].strip()] = key_value[1].strip()
        
        list_of_products.append(product_info)

    option = 'w'
    if not os.path.exists('Lab_4/data/products.json'):
        option = 'x'

    with open('Lab_4/data/products.json', option) as prods:
        prods.write(json.dumps(list_of_products, indent=4))


def send_endpoint_request(endpoint: str):
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((HOST, PORT))
    request = f'GET {endpoint} HTTP/1.1\nHost: {HOST}:{PORT}'
    client_socket.send(request.encode('utf-8'))

    response = client_socket.recv(4096).decode('utf-8')
    header, body = response.split('\n', 1)
    print(f'Response status: {header}')
    client_socket.close()

    return body


def main():
    try:
        process_endpoints()
    except KeyboardInterrupt:
        pass


if __name__ == '__main__':
    main()