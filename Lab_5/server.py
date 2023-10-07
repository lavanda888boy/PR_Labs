import socket
import threading
import json

HOST = '127.0.0.1' 
PORT = 8080

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server_socket.bind((HOST, PORT))

server_socket.listen()
print(f'Server is listening on {HOST}:{PORT}')


def handle_client(client_socket, client_address, clients):
    print(f'Accepted connection from {client_address}')

    while True:
        message = client_socket.recv(1024).decode('utf-8')
        if not message:
            break

        print(f'Received from {client_address}: {message}')

        data = json.loads(message)
        if data['type'] == 'connect':
            acknowledge_message = {
                                    "type": "connect_ack",
                                    "payload": {
                                        "message": f"\nYou succcesfully connected to the room '{data['payload']['room']}'."
                                    }
                                }
            server_data = json.dumps(acknowledge_message)
            client_socket.send(bytes(server_data, encoding='utf-8'))
        
        elif data['type'] == 'message':
            for client in clients:
                if client != client_socket:
                    client.send(message.encode('utf-8'))

    clients.remove(client_socket)
    client_socket.close()


def main():
    clients = []
    while True:
        client_socket, client_address = server_socket.accept()
        clients.append(client_socket)
        client_thread = threading.Thread(target=handle_client, args=(client_socket, client_address, clients))
        client_thread.start()


if __name__ == '__main__':
    main()