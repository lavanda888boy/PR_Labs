import socket
from bs4 import BeautifulSoup
import re
import os

def main():
    HOST = '127.0.0.1'
    PORT = 8080

    simple_endpoints = ['/', '/home', '/about', '/contacts']
    product_endpoints = ['/products', '/product']

    for ep in simple_endpoints:
        header, body = send_endpoint_request(ep, HOST, PORT)

        print(f'Response status: {header}')

        ep = re.sub(r'/', r'page_', ep)
        option = 'w'
        if len(os.listdir('Lab_4/data')) == 0:
            option = 'x'
        
        with open(f'Lab_4/data/{ep}.html', option) as f:
            f.write(body)

    header, body = send_endpoint_request(product_endpoints[0], HOST, PORT)


def send_endpoint_request(endpoint: str, host: str, port: int):
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((host, port))
    request = f'GET {endpoint} HTTP/1.1\nHost: {host}:{port}'
    client_socket.send(request.encode('utf-8'))

    response = client_socket.recv(4096).decode('utf-8')
    header, body = response.split('\n', 1)
    client_socket.close()

    return header, body


if __name__ == '__main__':
    main()