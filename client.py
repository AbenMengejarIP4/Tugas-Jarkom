import socket
import threading

# Fungsi untuk menerima pesan dari server
def receive_messages(client_socket):
    while True:
        try:
            message, _ = client_socket.recvfrom(1024)
            print(f"Pesan diterima: {message.decode('utf-8')}")
        except:
            print("Terputus dari server.")
            break


# Fungsi utama client
def start_client(server_ip, server_port, username, password):
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    # Kirim password ke server
    client_socket.sendto(f"PASS {password}".encode('utf-8'), (server_ip, server_port))

    # Terima balasan dari server
    response, _ = client_socket.recvfrom(1024)
    if response.decode('utf-8') == "OK":
        print("Berhasil masuk ke server.")
    else:
        print("Password salah.")
        return

    # Kirim username ke server
    client_socket.sendto(f"USER {username}".encode('utf-8'), (server_ip, server_port))

    # Jalankan thread untuk menerima pesan
    threading.Thread(target=receive_messages, args=(client_socket,)).start()

    # Kirim pesan ke server
    while True:
        message = input("Ketik pesan: ")
        if message.lower() == 'exit':
            break
        client_socket.sendto(message.encode('utf-8'), (server_ip, server_port))


if __name__ == "__main__":
    server_ip = input("Masukkan IP server: ")
    server_port = int(input("Masukkan port server: "))
    username = input("Masukkan username: ")
    password = input("Masukkan password: ")

    start_client(server_ip, server_port, username, password)

