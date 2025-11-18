import tkinter as tk
from tkinter import filedialog, messagebox
import configparser
import os

CONFIG_FILE = "settings.ini"

def load_config_from_file():
    config = configparser.ConfigParser()
    d = {}
    if os.path.exists(CONFIG_FILE):
        config.read(CONFIG_FILE)
        for section in config.sections():
            d[section] = {}
            for key, value in config[section].items():
                d[section][key] = value
    return d

def ensure_all_sections_and_keys(config_dict):
    """
    Ensure all sections/keys present in file defaults exist, just in case file is missing some.
    This avoids key errors later.
    """
    # These are the built-in settings for all possible fields
    # and are only used to check/complete what exists in file
    default_fields = {
        "EMAIL": ["email_from", "email_password", "email_to", "smtp_server", "smtp_port"],
        "REPORT": ["daily", "monthly"],
    }
    # Set basic placeholder values for missing fields
    default_values = {
        "email_from": "",
        "email_password": "",
        "email_to": "",
        "smtp_server": "",
        "smtp_port": "",
        "daily": "1",
        "monthly": "1",
    }
    for section, keys in default_fields.items():
        if section not in config_dict:
            config_dict[section] = {}
        for key in keys:
            if key not in config_dict[section]:
                config_dict[section][key] = default_values[key]
    return config_dict

def load_initial_config():
    config_from_file = load_config_from_file()
    config_complete = ensure_all_sections_and_keys(config_from_file)
    return config_complete

def save_config():
    config = configparser.ConfigParser()
    config["EMAIL"] = {
        "email_from": email_from_entry.get(),
        "email_password": email_pass_entry.get(),
        "email_to": email_to_entry.get(),
        "smtp_server": smtp_server_entry.get(),
        "smtp_port": smtp_port_entry.get(),
    }
    config["REPORT"] = {
        "daily": str(daily_var.get()),
        "monthly": str(monthly_var.get()),
    }

    with open(CONFIG_FILE, "w") as f:
        config.write(f)

    messagebox.showinfo("Saved", "Settings saved successfully.")

def browse_folder():
    folder = filedialog.askdirectory()
    if folder:
        backup_path_entry.delete(0, tk.END)
        backup_path_entry.insert(0, folder)

# Load initial values (from config file, using file as default source)
initial_config = load_initial_config()

root = tk.Tk()
root.title("Restaurant Report Configuration")
root.geometry("450x40")

# Email settings
tk.Label(root, text="\nEmail Settings").pack()

email_from_entry = tk.Entry(root, width=40)
email_pass_entry = tk.Entry(root, show="*", width=40)
email_to_entry = tk.Entry(root, width=40)
smtp_server_entry = tk.Entry(root, width=40)
smtp_port_entry = tk.Entry(root, width=40)

tk.Label(root, text="Sender Email:").pack()
email_from_entry.pack()
email_from_entry.insert(0, initial_config["EMAIL"]["email_from"])

tk.Label(root, text="App Password:").pack()
email_pass_entry.pack()
email_pass_entry.insert(0, initial_config["EMAIL"]["email_password"])

tk.Label(root, text="Recipient Email:").pack()
email_to_entry.pack()
email_to_entry.insert(0, initial_config["EMAIL"]["email_to"])

tk.Label(root, text="SMTP Server:").pack()
smtp_server_entry.pack()
smtp_server_entry.insert(0, initial_config["EMAIL"]["smtp_server"])

tk.Label(root, text="SMTP Port:").pack()
smtp_port_entry.pack()
smtp_port_entry.insert(0, initial_config["EMAIL"]["smtp_port"])

# Report type
daily_var = tk.IntVar()
monthly_var = tk.IntVar()
try:
    daily_var.set(int(initial_config["REPORT"]["daily"]))
except Exception:
    daily_var.set(1)
try:
    monthly_var.set(int(initial_config["REPORT"]["monthly"]))
except Exception:
    monthly_var.set(1)

tk.Checkbutton(root, text="Daily Report", variable=daily_var).pack()
tk.Checkbutton(root, text="Monthly Report", variable=monthly_var).pack()

# Save button
tk.Button(root, text="Save Settings", command=save_config).pack(pady=10)

root.mainloop()
