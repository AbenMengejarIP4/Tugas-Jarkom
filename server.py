import socket
import threading
import queue

messages = queue.Queue()
clients = []

server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server.bind(("localhost", 9999))

def receive():
    while True:
        try:
            message, addr = server.recvfrom(1024)
            messages.put((message, addr))
        except:
            pass

def broadcast():
    while True:
        while not messages.empty():
            message, addr = messages.get()
            decoded_message = message.decode()
            print(decoded_message)
            
            # Add client address if not already in the list
            if addr not in clients:
                clients.append(addr)

            for client in clients:
                try:
                    # Handle new client signup
                    if decoded_message.startswith("SIGNUP_TAG:"):
                        name = decoded_message.split(":")[1]
                        server.sendto(f"{name} joined!".encode('utf-8'), client)
                    else:
                        # Send the message to all clients
                        server.sendto(message, client)
                except:
                    # Remove client if sending failed
                    clients.remove(client)

# Start threads for receiving and broadcasting messages
t1 = threading.Thread(target=receive)
t2 = threading.Thread(target=broadcast)

t1.start()
t2.start()
