import socket
import json
import re

HOST = '127.0.0.1'
PORT = 8080

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind((HOST, PORT))

server_socket.listen()
print(f"Server is listening on {HOST}:{PORT}")


def handle_request(server, list_of_products):
    request_data = server.recv(1024).decode('utf-8')
    print(f"Received Request:\n{request_data}")

    request_lines = request_data.split('\n')
    request_line = request_lines[0].strip().split()
    print(request_line)
    path = request_line[1]

    response_content = ''
    status_code = 200

    if path == '/':
        response_content = 'Welcome Page'
    elif path == '/home':
        with open('Lab_4/web/home.html', 'r') as home:
            response_content = home.read()
    elif path == '/about':
        with open('Lab_4/web/about.html', 'r') as about:
            response_content = about.read()
    elif path == '/contacts':
        with open('Lab_4/web/contacts.html', 'r') as contacts:
            response_content = contacts.read()
    elif path == '/products':
        response_content += 'List of products<br>'
        for product in list_of_products:
            response_content += f"<a href='/product/{product['id']}'> Product {product['name']} </a><br>"
    elif re.match(r"/product/[0-9]+", path):
        id = int(re.split(r"/", path)[2])
        check = 0
        p = {}
        for product in list_of_products:
            if int(product['id']) == id:
                p = product
                check += 1
                break
        
        if check != 0:
            response_content = f"""<p> ID : {p['id']} </p><br>""" +\
                                f"""<p> Name : {p['name']} </p><br>""" +\
                                f"""<p> Author : {p['author']} </p><br>""" +\
                                f"""<p> Price : {p['price']} </p><br>"""  +\
                                f"""<p> Description : {p['description']} </p><br>""" 
        else:
            response_content = '404 Product Not Found'
        status_code = 404
    else:
        response_content = '404 Not Found'
        status_code = 404

    response = f'HTTP/1.1 {status_code} OK\nContent-Type: text/html\n\n{response_content}'
    server.send(response.encode('utf-8'))

    server.close()


def load_products():
    list_of_products = []
    with open('Lab_4/web/products.json', 'r') as prods:
        list_of_products = json.load(prods)

    return list_of_products


def main():
    list_of_products = load_products()

    while True:
        server, client_address = server_socket.accept()
        print(f"Accepted connection from {client_address[0]}:{client_address[1]}")
        try:
            handle_request(server, list_of_products)
        except KeyboardInterrupt:
            pass


if __name__ == '__main__':
    main()