import socket
import threading
import tkinter as tk
from tkinter import scrolledtext, messagebox

class ChatClient:
    def __init__(self, master):
        self.master = master
        self.master.title("Chat Room Client")

        self.server_host = None
        self.server_port = None
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.username = None

        self.login_frame = tk.Frame(self.master)
        self.login_frame.pack(padx=50, pady=10)

        tk.Label(self.login_frame, text="IP Server:").grid(row=0, column=0)
        self.server_entry = tk.Entry(self.login_frame)
        self.server_entry.grid(row=0, column=1)

        tk.Label(self.login_frame, text="Port Server:").grid(row=1, column=0)
        self.port_entry = tk.Entry(self.login_frame)
        self.port_entry.grid(row=1, column=1)

        tk.Label(self.login_frame, text="Username:").grid(row=2, column=0)
        self.username_entry = tk.Entry(self.login_frame)
        self.username_entry.grid(row=2, column=1)

        tk.Label(self.login_frame, text="Password:").grid(row=3, column=0)
        self.password_entry = tk.Entry(self.login_frame, show='*')
        self.password_entry.grid(row=3, column=1)

        self.login_button = tk.Button(self.login_frame, text="Login", command=self.login)
        self.login_button.grid(row=4, columnspan=2)

        self.chat_frame = None

    def login(self):
        self.server_host = self.server_entry.get()
        try:
            self.server_port = int(self.port_entry.get())
        except ValueError:
            self.send_error_log_to_server("Invalid Port: Masukkan nomor port yang valid.")
            messagebox.showerror("Invalid Port", "Masukkan nomor port yang valid.")
            return

        self.username = self.username_entry.get()
        password = self.password_entry.get()
        
        if not self.username or not password:
            messagebox.showerror("Input Error", "Username dan password tidak boleh kosong.")
            return
        
        correct_password = "rahasia123"

        if password != correct_password:
            self.socket.sendto(f"{self.username}".encode('utf-8'), (self.server_host, self.server_port))
            messagebox.showerror("Input Error", "Password anda salah")
            return
        
        try:
            self.socket.sendto(f"LOGIN:{password}:{self.username}".encode('utf-8'), (self.server_host, self.server_port))
            response, _ = self.socket.recvfrom(1024)
            response_message = response.decode('utf-8')
            
            if "Login berhasil" in response_message:
                self.login_frame.pack_forget()
                self.setup_chat_ui()
                threading.Thread(target=self.receive_messages, daemon=True).start()
            else:
                messagebox.showerror("Login Error", response_message)
        except (socket.gaierror, socket.error) as e:

            messagebox.showerror("Connection Error", "IP/Port Salah")
    

    def setup_chat_ui(self):
        self.chat_frame = tk.Frame(self.master)
        self.chat_frame.pack(padx=10, pady=10)

        self.chat_log = scrolledtext.ScrolledText(self.chat_frame, state='disabled', width=50, height=20)
        self.chat_log.grid(row=0, column=0, columnspan=2) 

        self.username_frame = tk.Label(self.chat_frame, text = f"{self.username}", width=6)
        self.username_frame.grid(row=1, column=0)

        self.message_entry = tk.Entry(self.chat_frame, width=50)
        self.message_entry.grid(row=1, column=1)

        self.send_button = tk.Button(self.chat_frame, text="Send", command=self.send_message)
        self.send_button.grid(row=1, column=2)

        self.logout_button = tk.Button(self.chat_frame, text="Logout", command=self.logout)
        self.logout_button.grid(row=2, columnspan=2)

    def receive_messages(self):
        while True:
            try:
                data, _ = self.socket.recvfrom(1024)
                message = data.decode('utf-8')
          
                self.chat_log.configure(state='normal')
                self.chat_log.insert(tk.END, f"{message}\n")
                self.chat_log.configure(state='disabled')
                self.chat_log.yview(tk.END) 
            except Exception as e:
                print(f"Error: {e}")
                break

    def send_message(self):
        message = self.message_entry.get()
        if message:
            formatted_message = f"{self.username}: {message}" 
            self.socket.sendto(message.encode('utf-8'), (self.server_host, self.server_port))
            self.chat_log.configure(state='normal')
            self.chat_log.insert(tk.END, f"{formatted_message}\n") 
            self.chat_log.configure(state='disabled')
            self.message_entry.delete(0, tk.END)

    def logout(self):
 
        self.socket.sendto(f"LOGOUT:{self.username}".encode('utf-8'), (self.server_host, self.server_port))
        self.socket.close()
        self.chat_frame.pack_forget()
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.username_entry.delete(0, tk.END)
        self.password_entry.delete(0, tk.END)
        self.server_entry.delete(0, tk.END)
        self.port_entry.delete(0, tk.END)
        self.login_frame.pack(padx=50, pady=10)



if __name__ == "__main__":
    root = tk.Tk()
    client = ChatClient(root)
    root.mainloop()
