import socket
import threading
import time

class ChatServer:
    def __init__(self, password):
        self.password = password
        self.clients = {} 
        self.lock = threading.Lock()
        self.socket = None
        self.port = None
    
    def log(self, message):
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        print(f"[{timestamp}] {message}")

    def start(self):
        hostname = socket.gethostname()
        local_ip = socket.gethostbyname(hostname)
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        while True:
            try:
                self.port = int(input("Masukkan nomor port untuk server: "))
                if not (1 <= self.port <= 65535):
                    raise ValueError("Port number out of valid range.")
                self.socket.bind((local_ip, self.port))
                break
            except OSError:
                self.log("Terjadi kesalahan input port.")
                print(f"Port {self.port} sudah digunakan. Silakan coba port lain.")
            except (ValueError, OverflowError):
                self.log("Terjadi kesalahan input port.")

        print(f"Server berjalan di {local_ip}:{self.port}")
        
        while True:
            try:
                data, addr = self.socket.recvfrom(1024)
                threading.Thread(target=self.handle_client, args=(data, addr)).start()
            except Exception as e:
                self.log(f"Error dalam menerima data: {e}")
    
    def handle_client(self, data, addr):
        encrypted_message = data.decode('utf-8')
        if addr not in self.clients:
            if encrypted_message.startswith("LOGIN:"):
                _, password, username = encrypted_message.split(':')
                if password != self.password:
                    self.socket.sendto("Password salah.".encode('utf-8'), addr)
                else:
                    with self.lock:
                        if username in self.clients.values():
                            self.socket.sendto("Username sudah digunakan.".encode('utf-8'), addr)
                        else:
                            self.clients[addr] = username
                            self.log(f"Login berhasil: {username} bergabung dari {addr}")
                            self.broadcast(f"{username} bergabung ke chat room.", addr)
                            self.socket.sendto("Login berhasil.".encode('utf-8'), addr)

        elif encrypted_message.startswith("LOGOUT:"):
            username = self.clients.pop(addr, None)
            if username:
                self.log(f"Logout: {username} dari {addr}")
                self.broadcast(f"{username} telah keluar dari chat room.", addr)

        else:
            username = self.clients[addr]
            decrypted_message = self.decrypt_message(encrypted_message)
            self.log(f"Pesan dari {username} ({addr}): {decrypted_message}")
            self.broadcast(f"{decrypted_message}", addr)
            
    def broadcast(self, message, sender_addr):
        for client_addr in self.clients:
            if client_addr != sender_addr:
                self.socket.sendto(message.encode('utf-8'), client_addr)
    
    def encrypt_message(self, message):
        
        encrypted = ''.join(chr((ord(char) - 32 + 10) % 95 + 32) if 32 <= ord(char) <= 126 else char for char in message)
        return encrypted

    def decrypt_message(self, message):
      
        decrypted = ''.join(chr((ord(char) - 32 - 10) % 95 + 32) if 32 <= ord(char) <= 126 else char for char in message)
        return decrypted


if __name__ == "__main__":
    server = ChatServer("rahasia123") 
    server.start()