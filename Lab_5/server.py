import socket
import threading
import json
import os

HOST = '127.0.0.1' 
PORT = 8080
CHUNK = 1024
MEDIA_FOLDER = 'server_media'

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server_socket.bind((HOST, PORT))

server_socket.listen()
print(f'Server is listening on {HOST}:{PORT}')


def handle_client(client_socket, client_address, clients, rooms):
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
                                        "message": f"\nYou succcesfully connected to the room '{data['payload']['room']}'.\
                                                    \nEnter your messages or type 'exit' to quit.\
                                                    \n\nType 'upload: <file-path>' to upload the file tot the server.\
                                                    \nType 'download: <file-name.extension>' to download the file from the server.\n"
                                    }
                                }
            server_data = json.dumps(acknowledge_message)
            client_socket.send(bytes(server_data, encoding='utf-8'))

            room = data['payload']['room']
            if room not in rooms:
                rooms[room] = set()

            rooms[room].add(client_socket)

            notification_message = {
                                    "type": "notification",
                                    "payload": {
                                        "message": f"{data['payload']['name']} has joined the room.\n"
                                    }
                                }
            server_data = json.dumps(notification_message)
            send_broadcast_message(client_socket, clients, rooms, bytes(server_data, encoding='utf-8'))
        
        elif data['type'] == 'disconnect':
            notification_message = {
                            "type": "notification",
                            "payload": {
                                "message": f"{data['payload']['name']} left the room.\n"
                            }
                        }
            server_data = json.dumps(notification_message)
            clients.remove(client_socket)
            
            if len(clients) != 0:
                send_broadcast_message(client_socket, clients, rooms, bytes(server_data, encoding='utf-8'))

            for room in rooms:
                if room == data['payload']['room']:
                    rooms[room].remove(client_socket)
                    break

            client_socket.close()
            return
        
        elif data['type'] == 'upload':
            if not os.path.isdir(MEDIA_FOLDER):
                os.mkdir(MEDIA_FOLDER)
            if not os.path.isdir(f"{MEDIA_FOLDER}/{data['payload']['room']}"):
                os.mkdir(f"{MEDIA_FOLDER}/{data['payload']['room']}")
            
            option = 'w'
            if not os.path.exists(f"{MEDIA_FOLDER}/{data['payload']['room']}/{data['payload']['file_name']}"):
                option = 'x'

            if data['payload']['file_size'] > CHUNK:
                with open(f"{MEDIA_FOLDER}/{data['payload']['room']}/{data['payload']['file_name']}", f'{option}b') as received_file:
                    while True:
                        chunk = client_socket.recv(CHUNK)
                        if not chunk:
                            break
                        received_file.write(chunk)
            else:
                with open(f"{MEDIA_FOLDER}/{data['payload']['room']}/{data['payload']['file_name']}", f'{option}b') as received_file:
                    chunk = client_socket.recv(data['payload']['file_size'])
                    received_file.write(chunk)

            notification_message = {
                                    "type": "notification",
                                    "payload": {
                                        "message": f"{data['payload']['name']} uploaded the {data['payload']['file_name']} file.\n"
                                    }
                                }
            server_data = json.dumps(notification_message)
            send_broadcast_message(client_socket, clients, rooms, bytes(server_data, encoding='utf-8'))
        elif data['type'] == 'message':
            send_broadcast_message(client_socket, clients, rooms, message.encode('utf-8'))
        else:
            print(f'\nInvalid client message received: {data}')


def send_broadcast_message(client_socket, clients, rooms, data):
    for client in clients:
        if client != client_socket:
            for room in rooms:
                if (client in rooms[room]) and (client_socket in rooms[room]):
                    client.sendall(data)
                    break


def main():
    clients = []
    rooms = {}
    while True:
        client_socket, client_address = server_socket.accept()
        clients.append(client_socket)
        client_thread = threading.Thread(target=handle_client, args=(client_socket, client_address, clients, rooms))
        client_thread.start()


if __name__ == '__main__':
    main()