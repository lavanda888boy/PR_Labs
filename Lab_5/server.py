import socket
import threading

HOST = '127.0.0.1' 
PORT = 8080

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind((HOST, PORT))

server_socket.listen()
print(f"Server is listening on {HOST}:{PORT}")


def handle_client(client_socket, client_address):
    print(f"Accepted connection from {client_address}")
    while True:
        message = client_socket.recv(1024).decode('utf-8')

        if not message:
            break

        print(f"Received from {client_address}: {message}")
        
        for client in clients:
            if client != client_socket:
                client.send(message.encode('utf-8'))

    clients.remove(client_socket)
    client_socket.close()


clients = []
while True:
    client_socket, client_address = server_socket.accept()
    clients.append(client_socket)
    client_thread = threading.Thread(target=handle_client, args=(client_socket, client_address))
    client_thread.start()