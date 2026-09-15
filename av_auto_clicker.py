import tkinter as tk
from tkinter import ttk, messagebox
import threading
import time

import pyautogui
import keyboard


APP_NAME = "Av Auto Clicker"
VERSION = "1.0"

clicking = False
click_thread = None
click_count = 0


def get_settings():
    """Read and validate the current settings."""
    try:
        interval_ms = float(interval_var.get())
        if interval_ms <= 0:
            raise ValueError

        limit_text = click_limit_var.get().strip()

        if limit_text.lower() in ("", "infinite", "inf", "∞"):
            click_limit = 0
        else:
            click_limit = int(limit_text)
            if click_limit < 1:
                raise ValueError

        button = mouse_button_var.get().lower()
        click_type = click_type_var.get()

        return interval_ms / 1000.0, click_limit, button, click_type

    except (ValueError, TypeError):
        raise ValueError("Enter a valid interval and click limit.")


def click_loop():
    global clicking, click_count

    try:
        interval, click_limit, button, click_type = get_settings()
        local_count = 0

        while clicking:
            if click_limit and local_count >= click_limit:
                break

            if click_type == "Double":
                pyautogui.doubleClick(button=button)
            else:
                pyautogui.click(button=button)

            local_count += 1
            click_count = local_count

            root.after(0, update_counter)
            time.sleep(interval)

    except Exception as error:
        if clicking:
            root.after(
                0,
                lambda: messagebox.showerror(APP_NAME, str(error))
            )

    finally:
        clicking = False
        root.after(0, update_stopped)


def start_clicking():
    global clicking, click_thread, click_count

    if clicking:
        return

    try:
        get_settings()
    except ValueError as error:
        messagebox.showerror(APP_NAME, str(error))
        return

    click_count = 0
    update_counter()

    clicking = True
    update_running()

    click_thread = threading.Thread(
        target=click_loop,
        daemon=True
    )
    click_thread.start()


def stop_clicking():
    global clicking
    clicking = False
    update_stopped()


def toggle_clicking():
    if clicking:
        stop_clicking()
    else:
        start_clicking()


def update_running():
    start_button.config(
        text="STOP",
        bg="#dc2626",
        activebackground="#ef4444"
    )
    status_label.config(
        text="● RUNNING",
        fg="#4ade80"
    )


def update_stopped():
    start_button.config(
        text="START",
        bg="#2563eb",
        activebackground="#3b82f6"
    )
    status_label.config(
        text="● STOPPED",
        fg="#f87171"
    )


def update_counter():
    counter_label.config(text=f"Clicks: {click_count:,}")


def setup_hotkey():
    try:
        keyboard.add_hotkey("f6", toggle_clicking)
    except Exception as error:
        messagebox.showwarning(
            APP_NAME,
            f"Could not register the F6 global hotkey.\n\n{error}"
        )


def on_close():
    global clicking
    clicking = False

    try:
        keyboard.unhook_all()
    except Exception:
        pass

    root.destroy()


# ------------------------------------------------------------
# Window
# ------------------------------------------------------------

root = tk.Tk()
root.title(f"{APP_NAME} v{VERSION}")
root.geometry("440x590")
root.resizable(False, False)
root.configure(bg="#111827")
root.protocol("WM_DELETE_WINDOW", on_close)

# ------------------------------------------------------------
# Variables
# ------------------------------------------------------------

mouse_button_var = tk.StringVar(value="Left")
click_type_var = tk.StringVar(value="Single")
interval_var = tk.StringVar(value="100")
click_limit_var = tk.StringVar(value="∞")

# ------------------------------------------------------------
# Header
# ------------------------------------------------------------

header = tk.Frame(root, bg="#111827")
header.pack(fill="x", padx=35, pady=(28, 5))

tk.Label(
    header,
    text="AV AUTO CLICKER",
    font=("Segoe UI", 23, "bold"),
    fg="white",
    bg="#111827"
).pack()

tk.Label(
    header,
    text=f"Version {VERSION}",
    font=("Segoe UI", 9),
    fg="#9ca3af",
    bg="#111827"
).pack(pady=(2, 0))

tk.Frame(
    root,
    height=2,
    bg="#1f2937"
).pack(fill="x", padx=35, pady=20)

# ------------------------------------------------------------
# Settings
# ------------------------------------------------------------

settings = tk.Frame(root, bg="#111827")
settings.pack(fill="x", padx=42)

label_font = ("Segoe UI", 10, "bold")

def setting_label(text, row):
    tk.Label(
        settings,
        text=text,
        font=label_font,
        fg="#d1d5db",
        bg="#111827"
    ).grid(row=row, column=0, sticky="w", pady=9)


setting_label("Mouse button", 0)

button_menu = ttk.Combobox(
    settings,
    textvariable=mouse_button_var,
    values=("Left", "Right"),
    state="readonly",
    width=18
)
button_menu.grid(row=0, column=1, sticky="e", pady=9)

setting_label("Click type", 1)

type_menu = ttk.Combobox(
    settings,
    textvariable=click_type_var,
    values=("Single", "Double"),
    state="readonly",
    width=18
)
type_menu.grid(row=1, column=1, sticky="e", pady=9)


setting_label("Interval (ms)", 2)

interval_entry = tk.Entry(
    settings,
    textvariable=interval_var,
    width=20,
    font=("Segoe UI", 10),
    bg="#1f2937",
    fg="white",
    insertbackground="white",
    relief="flat"
)
interval_entry.grid(row=2, column=1, sticky="e", pady=9, ipady=5)


setting_label("Click limit", 3)

limit_entry = tk.Entry(
    settings,
    textvariable=click_limit_var,
    width=20,
    font=("Segoe UI", 10),
    bg="#1f2937",
    fg="white",
    insertbackground="white",
    relief="flat"
)
limit_entry.grid(row=3, column=1, sticky="e", pady=9, ipady=5)

# ------------------------------------------------------------
# Start button
# ------------------------------------------------------------

start_button = tk.Button(
    root,
    text="START",
    command=toggle_clicking,
    font=("Segoe UI", 15, "bold"),
    fg="white",
    bg="#2563eb",
    activeforeground="white",
    activebackground="#3b82f6",
    relief="flat",
    bd=0,
    cursor="hand2"
)
start_button.pack(fill="x", padx=42, pady=(32, 12), ipady=12)

# ------------------------------------------------------------
# Status
# ------------------------------------------------------------

status_label = tk.Label(
    root,
    text="● STOPPED",
    font=("Segoe UI", 11, "bold"),
    fg="#f87171",
    bg="#111827"
)
status_label.pack(pady=(5, 2))

counter_label = tk.Label(
    root,
    text="Clicks: 0",
    font=("Segoe UI", 10),
    fg="#9ca3af",
    bg="#111827"
)
counter_label.pack()

# ------------------------------------------------------------
# Hotkey panel
# ------------------------------------------------------------

hotkey_panel = tk.Frame(root, bg="#1f2937")
hotkey_panel.pack(fill="x", padx=42, pady=(25, 10))

tk.Label(
    hotkey_panel,
    text="GLOBAL HOTKEY",
    font=("Segoe UI", 8, "bold"),
    fg="#9ca3af",
    bg="#1f2937"
).pack(pady=(10, 2))

tk.Label(
    hotkey_panel,
    text="F6",
    font=("Segoe UI", 16, "bold"),
    fg="white",
    bg="#1f2937"
).pack(pady=(0, 10))

# ------------------------------------------------------------
# Footer
# ------------------------------------------------------------

tk.Label(
    root,
    text="Av Auto Clicker",
    font=("Segoe UI", 9),
    fg="#4b5563",
    bg="#111827"
).pack(side="bottom", pady=15)

setup_hotkey()
root.mainloop()
