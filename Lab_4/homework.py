import socket
from bs4 import BeautifulSoup
import re
import os

HOST = '127.0.0.1'
PORT = 8080

simple_endpoints = ['/', '/home', '/about', '/contacts']
product_endpoints = ['/products', '/product']

for ep in simple_endpoints:
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((HOST, PORT))
    request = f'GET {ep} HTTP/1.1\nHost: {HOST}:{PORT}'
    client_socket.send(request.encode('utf-8'))

    response = client_socket.recv(4096).decode('utf-8')
    header, body = response.split('\n', 1)

    ep = re.sub(r'/', r'page_', ep)
    option = 'w'
    if len(os.listdir('Lab_4/data')) == 0:
        option = 'x'
    
    with open(f'Lab_4/data/{ep}.html', option) as f:
        f.write(body)

client_socket.close()