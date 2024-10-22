import socket
import threading

class ChatClient:
    def __init__(self, server_host, server_port):
        self.server_host = server_host
        self.server_port = server_port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.username = None

    def start(self):
        self.username = input("Masukkan username: ")
        password = input("Masukkan password: ")
        self.socket.sendto(f"LOGIN:{password}:{self.username}".encode('utf-8'), (self.server_host, self.server_port))
        
        response, _ = self.socket.recvfrom(1024)
        print(response.decode('utf-8'))
        
        if "Login berhasil" in response.decode('utf-8'):
            threading.Thread(target=self.receive_messages).start()
            self.send_messages()

    def receive_messages(self):
        while True:
            try:
                data, _ = self.socket.recvfrom(1024)
                print(data.decode('utf-8'))
            except Exception as e:
                print(f"Error: {e}")
                break

    def send_messages(self):
        while True:
            message = input()
            if message.lower() == 'quit':
                break
            self.socket.sendto(message.encode('utf-8'), (self.server_host, self.server_port))

if __name__ == "__main__":
    server_host = input("Masukkan IP server: ")
    server_port = int(input("Masukkan port server: "))
    client = ChatClient(server_host, server_port)
    client.start()
