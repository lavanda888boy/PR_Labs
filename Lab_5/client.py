import socket
import threading

HOST = '127.0.0.1' 
PORT = 8080

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

client_socket.connect((HOST, PORT))
print(f"Connected to {HOST}:{PORT}")


def receive_messages():
    while True:
        message = client_socket.recv(1024).decode('utf-8')
        
        if not message:
            break 
        
        print(f"Received: {message}")


receive_thread = threading.Thread(target=receive_messages)
receive_thread.daemon = True
receive_thread.start()

while True:
    message = input("Enter a message (or 'exit' to quit): ")
    
    if message.lower() == 'exit':
        break
    
    client_socket.send(message.encode('utf-8'))

client_socket.close()