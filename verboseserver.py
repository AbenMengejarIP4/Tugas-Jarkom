import socket
import threading
import time

class ChatServer:
    def __init__(self, host, password):
        self.host = host
        self.password = password
        self.clients = {}  # {address: username}
        self.lock = threading.Lock()
        self.socket = None
        self.port = None

    def log(self, message):
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        print(f"[{timestamp}] {message}")

    def start(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        while True:
            try:
                self.port = int(input("Masukkan nomor port untuk server: "))
                self.socket.bind((self.host, self.port))
                break
            except OSError:
                self.log(f"Port {self.port} sudah digunakan. Silakan coba port lain.")
            except ValueError:
                self.log("Masukkan nomor port yang valid.")

        self.log(f"Server berjalan di {self.host}:{self.port}")
        while True:
            try:
                data, addr = self.socket.recvfrom(1024)
                self.log(f"Menerima data dari {addr}")
                threading.Thread(target=self.handle_client, args=(data, addr)).start()
            except Exception as e:
                self.log(f"Error dalam menerima data: {e}")

    def handle_client(self, data, addr):
        message = data.decode('utf-8')
        self.log(f"Pesan diterima dari {addr}: {message}")
        if addr not in self.clients:
            if message.startswith("LOGIN:"):
                _, password, username = message.split(':')
                self.log(f"Upaya login dari {addr} dengan username: {username}")
                if password == self.password:
                    with self.lock:
                        if username in self.clients.values():
                            self.log(f"Login gagal: Username {username} sudah digunakan")
                            self.socket.sendto("Username sudah digunakan.".encode('utf-8'), addr)
                        else:
                            self.clients[addr] = username
                            self.log(f"Login berhasil: {username} bergabung dari {addr}")
                            self.broadcast(f"{username} bergabung ke chat room.", addr)
                            self.socket.sendto("Login berhasil.".encode('utf-8'), addr)
                else:
                    self.log(f"Login gagal: Password salah dari {addr}")
                    self.socket.sendto("Password salah.".encode('utf-8'), addr)
        else:
            username = self.clients[addr]
            self.log(f"Pesan dari {username} ({addr}): {message}")
            self.broadcast(f"{username}: {message}", addr)

    def broadcast(self, message, sender_addr):
        self.log(f"Broadcasting pesan: {message}")
        for client_addr in self.clients:
            if client_addr != sender_addr:
                self.log(f"Mengirim pesan ke {self.clients[client_addr]} ({client_addr})")
                self.socket.sendto(message.encode('utf-8'), client_addr)

if __name__ == "__main__":
    server = ChatServer("0.0.0.0", "rahasia123")
    server.start()
