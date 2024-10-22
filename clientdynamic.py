import socket
import threading

class ChatClient:
    def __init__(self):
        self.server_host = None
        self.server_port = None
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.username = None

    def start(self):
        self.server_host = input("Masukkan IP server: ")
        while True:
            try:
                self.server_port = int(input("Masukkan port server: "))
                break
            except ValueError:
                print("Masukkan nomor port yang valid.")

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
    client = ChatClient()
    client.start()
