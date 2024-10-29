import socket
import threading

class ChatServer:
    def __init__(self, password):
        self.password = password
        self.clients = {} 
        self.lock = threading.Lock()
        self.socket = None
        self.port = None

    def start(self):
        hostname = socket.gethostname()
        local_ip = socket.gethostbyname(hostname)
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        while True:
            try:
                self.port = int(input("Masukkan nomor port untuk server: "))
                self.socket.bind((local_ip, self.port))
                break
            except OSError:
                print(f"Port {self.port} sudah digunakan. Silakan coba port lain.")
            except ValueError:
                print("Masukkan nomor port yang valid.")

        print(f"Server berjalan di {local_ip}:{self.port}")
        while True:
            try:
                data, addr = self.socket.recvfrom(1024)
                threading.Thread(target=self.handle_client, args=(data, addr)).start()
            except Exception as e:
                print(f"Error: {e}")

    def handle_client(self, data, addr):
        message = data.decode('utf-8')
        
        if addr not in self.clients:
            if message.startswith("LOGIN:"):
                _, password, username = message.split(':')
                if password == self.password:
                    with self.lock:
                        if username in self.clients.values():
                            self.socket.sendto("Username sudah digunakan.".encode('utf-8'), addr)
                        else:
                            self.clients[addr] = username
                            print(f"{username} bergabung dari {addr}")
                            self.broadcast(f"{username} bergabung ke chat room.", addr)
                            self.socket.sendto("Login berhasil.".encode('utf-8'), addr)
                else:
                    self.socket.sendto("Password salah.".encode('utf-8'), addr)
        else:
            username = self.clients[addr]
            print(f"Pesan dari {username}")
            self.broadcast(f"{username}: {message}", addr)  
            
    def broadcast(self, message, sender_addr):
        for client_addr in self.clients:
            if client_addr != sender_addr:
                self.socket.sendto(message.encode('utf-8'), client_addr)

if __name__ == "__main__":
    server = ChatServer("rahasia123") 
    server.start()