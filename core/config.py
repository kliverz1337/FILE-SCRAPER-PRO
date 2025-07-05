import json
from pathlib import Path

# --- MANAJEMEN KONFIGURASI ---
CONFIG_FILE = Path("services_config.json")
DEFAULT_SERVICES = [
    {"name": "FTP", "ports": ["21"], "file": "FTP.txt", "icon": "fa5s.folder-open"},
    {"name": "SSH", "ports": ["22"], "file": "SSH.txt", "icon": "fa5s.terminal"},
    {"name": "cPanel", "ports": ["2082", "2083"], "file": "cPanel.txt", "icon": "fa5s.tachometer-alt"},
    {"name": "WHM", "ports": ["2086", "2087"], "file": "WHM.txt", "icon": "fa5s.users-cog"},
    {"name": "Plesk", "ports": ["8443"], "file": "Plesk.txt", "icon": "fa5s.th-large"},
]

def load_services_config():
    """Memuat konfigurasi layanan dari file JSON. Jika tidak ada, buat default."""
    if not CONFIG_FILE.exists():
        save_services_config(DEFAULT_SERVICES)
        return DEFAULT_SERVICES
    try:
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (json.JSONDecodeError, FileNotFoundError):
        # Jika file rusak atau tidak ditemukan, kembali ke default
        save_services_config(DEFAULT_SERVICES)
        return DEFAULT_SERVICES

def save_services_config(config):
    """Menyimpan konfigurasi layanan ke file JSON."""
    with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=4)