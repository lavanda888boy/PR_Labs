import socket
import threading
import json
import re
import os
import shutil

HOST = '127.0.0.1' 
PORT = 8080
CHUNK = 1024
MEDIA_FOLDER = 'client_media'

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

client_socket.connect((HOST, PORT))
print(f"Connected to {HOST}:{PORT}")


def perform_server_connection():
    name = input('Introduce your name: ')
    room = input('Introduce the room you would like to join: ')

    connection_message = {
                        "type": "connect",
                        "payload": {
                            "name": name,
                            "room": room
                        }
                    }   
    
    data = json.dumps(connection_message)
    client_socket.sendall(bytes(data, encoding='utf-8'))

    return name, room


def receive_messages(name):
    while True:
        server_message = client_socket.recv(1024).decode('utf-8')
        if not server_message:
            break 

        data = json.loads(server_message)
        if (data['type'] == 'connect_ack') or (data['type'] == 'notification'):
            print(data['payload']['message'])
        elif data['type'] == 'download-ack':
            download_thread = threading.Thread(target=download_file, args=(client_socket, data, name))
            download_thread.start()
            download_thread.join()
            
        elif data['type'] == 'message':
            print(f"\nRoom: {data['payload']['room']}, {data['payload']['sender']}: {data['payload']['text']}")
        else:
            print(f'\nInvalid message received: {data}')


def upload_file(message, name, room):
    file_path = message.split(r' ')[1]
    tokens = file_path.split(r'/')
    file_name = tokens[len(tokens) - 1]
    
    if os.path.exists(file_path):
        file_size = os.path.getsize(file_path)
        file_upload_message = {
                            "type": "upload",
                            "payload": {
                                "file_name": file_name,
                                "file_size": file_size,
                                "name": name,
                                "room": room
                            }
                        }
        data = json.dumps(file_upload_message) 
        client_socket.sendall(bytes(data, encoding='utf-8'))

        if file_size > CHUNK:
            with open(file_path, 'rb') as file:
                while True:
                    chunk = file.read(CHUNK)
                    if not chunk:
                        break
                    client_socket.sendall(chunk)
        else:
            with open(file_path, 'rb') as file:
                chunk = file.read(file_size)
                client_socket.sendall(chunk)
    else:
        print(f'File {file_name} does not exist!')


def download_file(client_socket, data, name):
    option = 'w'
    if not os.path.exists(f"{MEDIA_FOLDER}/{name}/{data['payload']['file_name']}"):
        option = 'x'

    if data['payload']['file_size'] > CHUNK:
        with open(f"{MEDIA_FOLDER}/{name}/{data['payload']['file_name']}", f'{option}b') as received_file:
            index = 0
            while index < data['payload']['file_size']:
                chunk = client_socket.recv(CHUNK)
                received_file.write(chunk)
                index += CHUNK
    else:
        with open(f"{MEDIA_FOLDER}/{name}/{data['payload']['file_name']}", f'{option}b') as received_file:
            chunk = client_socket.recv(data['payload']['file_size'])
            received_file.write(chunk)

    print('File was downloaded succesfully')


def main():
    name, room = perform_server_connection()

    if not os.path.isdir(MEDIA_FOLDER):
        os.mkdir(MEDIA_FOLDER)
    if not os.path.isdir(f"{MEDIA_FOLDER}/{name}"):
        os.mkdir(f"{MEDIA_FOLDER}/{name}")

    receive_thread = threading.Thread(target=receive_messages, args=(name,))
    receive_thread.daemon = True
    receive_thread.start()
    
    while True:
        message = input()
        if message.lower() == 'exit':
            disconnect_message = {
                                "type": "disconnect",
                                "payload": {
                                    "name": name,
                                    "room": room
                                }
                            }   
            data = json.dumps(disconnect_message)
            client_socket.sendall(bytes(data, encoding='utf-8'))
            break

        if re.match(r'upload ([A-Za-z\./]+)', message):
            upload_thread = threading.Thread(target=upload_file, args=(message, name, room))   
            upload_thread.start() 
            upload_thread.join()
        elif re.match(r'download ([A-Za-z\.]+)', message):
            file_download_message = {
                            "type": "download",
                            "payload": {
                                "file_name": message.split(r' ')[1],
                                "name": name,
                                "room": room
                            }
                        }
            data = json.dumps(file_download_message)
            client_socket.sendall(bytes(data, encoding='utf-8'))
        else:
            chat_message = {
                            "type": "message",
                            "payload": {
                                "sender": name,
                                "room": room,
                                "text": f'{message}\n'
                            }
                        }
            
            data = json.dumps(chat_message)
            client_socket.sendall(bytes(data, encoding='utf-8'))

    shutil.rmtree(f'{MEDIA_FOLDER}/{name}')
    client_socket.close()


if __name__ == '__main__':
    main()