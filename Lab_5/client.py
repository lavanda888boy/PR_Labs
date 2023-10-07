import socket
import threading
import json

HOST = '127.0.0.1' 
PORT = 8080

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

client_socket.connect((HOST, PORT))

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

print(f"Connected to {HOST}:{PORT}")


def receive_messages():
    while True:
        message = client_socket.recv(1024).decode('utf-8')
        if not message:
            break 

        data = json.loads(message)
        if data['type'] == 'connect_ack':
            print(data['payload']['message'])


def main():
    receive_thread = threading.Thread(target=receive_messages)
    receive_thread.daemon = True
    receive_thread.start()

    while True:
        message = input("Enter a message (or 'exit' to quit): ")
        if message.lower() == 'exit':
            break
        
        client_socket.send(message.encode('utf-8'))

    client_socket.close()


if __name__ == '__main__':
    main()