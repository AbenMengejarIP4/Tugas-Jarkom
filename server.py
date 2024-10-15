import socket
import threading

# Konfigurasi server
SERVER_IP = '127.0.0.1'  # Alamat IP server
SERVER_PORT = 12345  # Port server
PASSWORD = "password123"  # Password untuk client

clients = {}  # Dictionary untuk menyimpan username dan alamat client


# Fungsi untuk menangani pesan dari client
def handle_client(data, client_address):
    try:
        message = data.decode('utf-8')

        if client_address not in clients.values():
            # Validasi password client
            if message.startswith("PASS "):
                client_password = message.split(" ")[1]
                if client_password == PASSWORD:
                    server_socket.sendto("OK".encode('utf-8'), client_address)
                    print(f"Client {client_address} berhasil masuk.")
                else:
                    server_socket.sendto("PASSWORD SALAH".encode('utf-8'), client_address)
                    return
            else:
                return

        elif message.startswith("USER "):
            # Set username untuk client
            username = message.split(" ")[1]
            clients[username] = client_address
            print(f"Client {username} masuk dari {client_address}.")
            broadcast(f"{username} telah bergabung ke chatroom.".encode('utf-8'), client_address)

        else:
            # Proses pesan chat dan broadcast ke semua client lain
            for username, address in clients.items():
                if address != client_address:
                    server_socket.sendto(data, address)
            print(f"Pesan dari {client_address}: {message}")

    except Exception as e:
        print(f"Error: {e}")


# Fungsi untuk mengirim pesan ke semua client kecuali pengirim
def broadcast(message, sender_address):
    for address in clients.values():
        if address != sender_address:
            server_socket.sendto(message, address)


# Fungsi utama server
def start_server():
    global server_socket
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_socket.bind((SERVER_IP, SERVER_PORT))

    print(f"Server berjalan di {SERVER_IP}:{SERVER_PORT}")

    while True:
        try:
            data, client_address = server_socket.recvfrom(1024)
            threading.Thread(target=handle_client, args=(data, client_address)).start()
        except KeyboardInterrupt:
            print("Server dihentikan.")
            break


if __name__ == "__main__":
    start_server()
