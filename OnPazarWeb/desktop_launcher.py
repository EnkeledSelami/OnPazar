from __future__ import annotations

import os
import secrets
import socket
import sys
import threading
import time
import urllib.request
import webbrowser
from pathlib import Path


def user_data_dir() -> Path:
    base = Path(os.environ.get("LOCALAPPDATA") or Path.home() / "AppData" / "Local")
    folder = base / "OnPazar"
    folder.mkdir(parents=True, exist_ok=True)
    return folder


def prepare_runtime_environment() -> None:
    data_dir = user_data_dir()
    os.environ.setdefault("PRICEPAL_DB", str(data_dir / "onpazar-web.sqlite3"))
    key_file = data_dir / "secret.key"
    if not os.environ.get("PRICEPAL_SECRET_KEY"):
        try:
            key = key_file.read_text(encoding="utf-8").strip()
        except OSError:
            key = secrets.token_hex(32)
            key_file.write_text(key, encoding="utf-8")
        os.environ["PRICEPAL_SECRET_KEY"] = key


def free_local_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as probe:
        probe.bind(("127.0.0.1", 0))
        return int(probe.getsockname()[1])


def wait_until_ready(url: str, timeout: float = 20.0) -> bool:
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        try:
            with urllib.request.urlopen(url, timeout=1) as response:
                if response.status == 200:
                    return True
        except Exception:
            time.sleep(0.2)
    return False


def browser_fallback(url: str, message: str) -> None:
    import tkinter as tk
    from tkinter import messagebox

    try:
        webbrowser.open(url, new=1)
    except Exception:
        pass

    root = tk.Tk()
    root.title("OnPazar is running")
    root.geometry("400x185")
    root.resizable(False, False)
    root.configure(bg="#0a0f0c")
    tk.Label(root, text="OnPazar is running on this computer", bg="#0a0f0c", fg="#f4f7f4",
             font=("Segoe UI", 14, "bold")).pack(pady=(24, 8))
    tk.Label(root, text="The app opened in your browser. Keep this window open while you use it.",
             bg="#0a0f0c", fg="#aab8ae", wraplength=340, justify="center",
             font=("Segoe UI", 10)).pack(pady=4)
    if message:
        tk.Label(root, text=message[:180], bg="#0a0f0c", fg="#e5bd74", wraplength=350,
                 justify="center", font=("Segoe UI", 8)).pack(pady=4)
    buttons = tk.Frame(root, bg="#0a0f0c")
    buttons.pack(pady=12)
    tk.Button(buttons, text="Open OnPazar", command=lambda: webbrowser.open(url),
              bg="#168256", fg="white", activebackground="#1c9965", relief="flat",
              padx=16, pady=7).pack(side="left", padx=5)
    tk.Button(buttons, text="Exit", command=root.destroy, bg="#18221c", fg="white",
              activebackground="#293b30", relief="flat", padx=18, pady=7).pack(side="left", padx=5)
    root.protocol("WM_DELETE_WINDOW", root.destroy)
    root.mainloop()


def main() -> None:
    prepare_runtime_environment()

    # Imported after configuring the writable user-data location so the DB and
    # persistent browser-session key never live inside PyInstaller's temp folder.
    from app import app
    from waitress import create_server

    port = free_local_port()
    server = create_server(app, host="127.0.0.1", port=port, threads=8)
    server_thread = threading.Thread(target=server.run, name="OnPazar-local-server", daemon=True)
    server_thread.start()
    base_url = f"http://127.0.0.1:{port}"
    if not wait_until_ready(base_url + "/health"):
        server.close()
        raise RuntimeError("OnPazar's local service did not become ready.")

    try:
        import webview
        webview.create_window("OnPazar", base_url, width=1420, height=940,
                              min_size=(960, 650), text_select=True)
        webview.start(debug=False)
    except Exception as exc:
        browser_fallback(base_url, f"Embedded browser unavailable; opened standard browser. {exc}")
    finally:
        server.close()


if __name__ == "__main__":
    main()
