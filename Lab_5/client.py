import socket
import threading
import json

HOST = '127.0.0.1' 
PORT = 8080

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


def receive_messages():
    while True:
        server_message = client_socket.recv(1024).decode('utf-8')
        if not server_message:
            break 

        data = json.loads(server_message)
        if (data['type'] == 'connect_ack') or (data['type'] == 'notification'):
            print(data['payload']['message'])
        elif data['type'] == 'message':
            print(f"\nRoom: {data['payload']['room']}, {data['payload']['sender']}: {data['payload']['text']}")
        else:
            print(f'\nInvalid message received: {data}')


def main():
    name, room = perform_server_connection()

    receive_thread = threading.Thread(target=receive_messages)
    receive_thread.daemon = True
    receive_thread.start()

    while True:
        message = input("Enter a message (or 'exit' to quit): ")
        if message.lower() == 'exit':
            break

        chat_message = {
                        "type": "message",
                        "payload": {
                            "sender": name,
                            "room": room,
                            "text": message
                        }
                    }
        
        data = json.dumps(chat_message)
        client_socket.sendall(bytes(data, encoding='utf-8'))

    client_socket.close()


if __name__ == '__main__':
    main()