import sys
import os
import io
import glob
import socket
import threading
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageDraw

PORT = 49152
COMMAND_NEXT = b"TRIGGER_NEXT_IMAGE"

class DisplayApp:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Экран с картинками")
        self.root.geometry("640x520")

        if getattr(sys, 'frozen', False):
            base_dir = os.path.dirname(sys.executable)
        else:
            base_dir = os.path.dirname(os.path.abspath(__file__))
            
        self.images_dir = os.path.join(base_dir, "images")
        
        self.image_files = self._load_image_paths()
        self.current_idx = 0
        self.placeholder_colors = ["#3b82f6", "#ef4444", "#10b981", "#f59e0b", "#8b5cf6"]

        self._setup_ui()
        self._show_current_image()

        self.running = True
        self.listener_thread = threading.Thread(target=self._listen_broadcast, daemon=True)
        self.listener_thread.start()

    def _load_image_paths(self):
        if not os.path.exists(self.images_dir):
            os.makedirs(self.images_dir, exist_ok=True)
        patterns = ["*.png", "*.jpg", "*.jpeg", "*.webp", "*.bmp"]
        files = []
        for p in patterns:
            files.extend(glob.glob(os.path.join(self.images_dir, p)))
        return sorted(files)

    def _setup_ui(self):
        self.container = ttk.Frame(self.root, padding=10)
        self.container.pack(expand=True, fill="both")

        self.img_label = ttk.Label(self.container, anchor="center")
        self.img_label.pack(expand=True, fill="both")

        self.status_bar = ttk.Label(
            self.root,
            text=f"Слушаю порт {PORT}...",
            relief="sunken",
            anchor="w",
            padding=(10, 4)
        )
        self.status_bar.pack(side="bottom", fill="x")

    def _generate_fallback_image(self, color_hex: str, label_text: str):
        img = Image.new("RGB", (560, 420), color=color_hex)
        draw = ImageDraw.Draw(img)
        draw.text((20, 20), label_text, fill="white")
        draw.text((20, 50), "Положите файлы в папку /images для показа фотографий", fill="white")
        return img

    def _show_current_image(self):
        w = max(self.root.winfo_width() - 40, 560)
        h = max(self.root.winfo_height() - 80, 420)

        if self.image_files:
            file_path = self.image_files[self.current_idx % len(self.image_files)]
            img = Image.open(file_path)
            img.thumbnail((w, h), Image.Resampling.LANCZOS)
            name = os.path.basename(file_path)
        else:
            color = self.placeholder_colors[self.current_idx % len(self.placeholder_colors)]
            img = self._generate_fallback_image(color, f"Генерация #{self.current_idx + 1}")
            name = f"Placeholder #{self.current_idx + 1}"

        bio = io.BytesIO()
        img.save(bio, format="PNG")
        
        self.tk_img = tk.PhotoImage(data=bio.getvalue())
        
        self.img_label.config(image=self.tk_img)
        self.status_bar.config(text=f"Отображается: {name} (Слушаю порт {PORT})")

    def next_image(self):
        self.current_idx += 1
        self._show_current_image()

    def _listen_broadcast(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        try:
            sock.bind(("", PORT))
            while self.running:
                data, addr = sock.recvfrom(1024)
                if data == COMMAND_NEXT:
                    self.root.after(0, self.next_image)
        except Exception as e:
            if self.running:
                print(f"Ошибка сокета: {e}")
        finally:
            sock.close()

    def close(self):
        self.running = False
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = DisplayApp(root)
    root.protocol("WM_DELETE_WINDOW", app.close)
    root.mainloop()