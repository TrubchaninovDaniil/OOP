import socket
import tkinter as tk
from tkinter import ttk

PORT = 49152
COMMAND_NEXT = b"TRIGGER_NEXT_IMAGE"

class ControllerApp:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Пульт управления")
        self.root.geometry("400x300")
        self.root.resizable(False, False)

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

        self._setup_ui()

    def _setup_ui(self):
        frame = ttk.Frame(self.root, padding=30)
        frame.pack(expand=True, fill="both")

        title = ttk.Label(
            frame, 
            text="Remote Control", 
            font=("Segoe UI", 16, "bold")
        )
        title.pack(pady=(0, 20))

        self.btn = tk.Button(
            frame,
            text="Сменить картинку",
            font=("Segoe UI", 13, "bold"),
            bg="#2563eb",
            fg="white",
            activebackground="#1d4ed8",
            activeforeground="white",
            relief="flat",
            padx=20,
            pady=15,
            cursor="hand2",
            command=self.send_signal
        )
        self.btn.pack(expand=True, fill="x", pady=10)

        self.status_lbl = ttk.Label(
            frame,
            text="Готов к отправке",
            font=("Segoe UI", 9),
            foreground="#6b7280"
        )
        self.status_lbl.pack(pady=(10, 0))

    def send_signal(self):
        try:
            self.sock.sendto(COMMAND_NEXT, ("255.255.255.255", PORT))
            self.status_lbl.config(
                text="Сигнал отправлен!", 
                foreground="#16a34a"
            )
            self.root.after(
                1000, 
                lambda: self.status_lbl.config(
                    text="Готов к отправке", 
                    foreground="#6b7280"
                )
            )
        except Exception as e:
            self.status_lbl.config(
                text=f"Ошибка сети: {e}", 
                foreground="#dc2626"
            )

    def close(self):
        self.sock.close()
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = ControllerApp(root)
    root.protocol("WM_DELETE_WINDOW", app.close)
    root.mainloop()
