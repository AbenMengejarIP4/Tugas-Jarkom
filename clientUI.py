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
        self.login_frame.pack(padx=10, pady=10)

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
            messagebox.showerror("Invalid Port", "Masukkan nomor port yang valid.")
            return

        self.username = self.username_entry.get()
        password = self.password_entry.get()
        
        if not self.username or not password:
            messagebox.showerror("Input Error", "Username dan password tidak boleh kosong.")
            return
        
        self.socket.sendto(f"LOGIN:{password}:{self.username}".encode('utf-8'), (self.server_host, self.server_port))
        
        response, _ = self.socket.recvfrom(1024)
        response_message = response.decode('utf-8')
        messagebox.showinfo("Login", response_message)
        
        if "Login berhasil" in response_message:
            self.login_frame.pack_forget()
            self.setup_chat_ui()
            threading.Thread(target=self.receive_messages, daemon=True).start()

    def setup_chat_ui(self):
        self.chat_frame = tk.Frame(self.master)
        self.chat_frame.pack(padx=10, pady=10)

        self.chat_log = scrolledtext.ScrolledText(self.chat_frame, state='disabled', width=50, height=20)
        self.chat_log.grid(row=0, column=0)

        self.message_entry = tk.Entry(self.chat_frame, width=40)
        self.message_entry.grid(row=1, column=0)

        self.send_button = tk.Button(self.chat_frame, text="Send", command=self.send_message)
        self.send_button.grid(row=1, column=1)

        self.logout_button = tk.Button(self.chat_frame, text="Logout", command=self.logout)
        self.logout_button.grid(row=2, columnspan=2)

    def receive_messages(self):
        while True:
            try:
                data, _ = self.socket.recvfrom(1024)
                message = data.decode('utf-8')
                # Display the message without any duplication
                self.chat_log.configure(state='normal')
                self.chat_log.insert(tk.END, f"{message}\n")  # Directly insert received message
                self.chat_log.configure(state='disabled')
                self.chat_log.yview(tk.END)  # Scroll to the end
            except Exception as e:
                print(f"Error: {e}")
                break

    def send_message(self):
        message = self.message_entry.get()
        if message:
            formatted_message = f"{self.username}: {message}"  # Format the sent message
            self.socket.sendto(message.encode('utf-8'), (self.server_host, self.server_port))
            self.chat_log.configure(state='normal')
            self.chat_log.insert(tk.END, f"{formatted_message}\n")  # Show the sent message
            self.chat_log.configure(state='disabled')
            self.message_entry.delete(0, tk.END)

    def logout(self):
        self.socket.close()
        self.master.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    client = ChatClient(root)
    root.mainloop()
