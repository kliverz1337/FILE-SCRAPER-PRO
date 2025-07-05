import re
from pathlib import Path
from contextlib import ExitStack
from PySide6.QtCore import QObject, Signal

class ScraperWorker(QObject):
    """
    Worker yang menangani proses scraping file dalam thread terpisah
    untuk menjaga responsivitas UI.
    """
    log_message = Signal(str, str)
    progress_updated = Signal(int, int)
    count_updated = Signal(str, int)
    finished = Signal(str)
    error = Signal(str)

    def __init__(self, folder_path, services_config):
        super().__init__()
        self.folder_path = folder_path
        self.services_config = services_config
        self.is_running = True

    def stop(self):
        """Memberi sinyal untuk menghentikan proses scraping."""
        self.is_running = False

    def run(self):
        """
        Mulai proses scraping. Membaca semua file .txt di folder yang dipilih,
        mencari baris yang cocok dengan port yang dikonfigurasi, dan
        menyimpannya ke file hasil yang sesuai.
        """
        try:
            result_folder = Path('RESULT LIST')
            result_folder.mkdir(exist_ok=True)

            all_ports = [p for s in self.services_config for p in s.get("ports", [])]
            if not all_ports:
                self.error.emit("Tidak ada port yang dikonfigurasi untuk di-scrape.")
                return

            # Pola regex untuk mencocokkan URL dengan port yang ditentukan
            pattern = re.compile(r'https?://\S+:(' + '|'.join(map(re.escape, all_ports)) + r')\|\S+\|\S+')
            
            # Pemetaan dari port ke nama layanan untuk pencarian cepat
            port_map = {p: s["name"] for s in self.services_config for p in s.get("ports", [])}
            
            # Struktur data untuk menyimpan path file output dan jumlah hasil
            service_data = {s["name"]: {"path": result_folder / s["file"], "count": 0} for s in self.services_config}
            
            seen = set() # Untuk melacak baris duplikat
            files_to_process = list(self.folder_path.glob("*.txt"))
            total_files = len(files_to_process)

            if total_files == 0:
                self.log_message.emit(f"Tidak ditemukan file .txt di folder '{self.folder_path.name}'.", "INFO")
                self.finished.emit("Proses selesai, tidak ada file untuk diproses.")
                return

            # Menggunakan ExitStack untuk mengelola file output secara aman
            with ExitStack() as stack:
                files = {name: stack.enter_context(open(data["path"], 'w', encoding='utf-8')) for name, data in service_data.items()}
                
                for i, file_path in enumerate(files_to_process):
                    if not self.is_running:
                        self.log_message.emit("Proses dihentikan oleh pengguna.", "INFO")
                        break
                    
                    self.progress_updated.emit(i + 1, total_files)
                    self.log_message.emit(f"-> Memproses: {file_path.name}", "INFO")
                    
                    try:
                        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                            for line_content in f:
                                for match in pattern.finditer(line_content):
                                    matched_line = match.group(0)
                                    if matched_line not in seen:
                                        seen.add(matched_line)
                                        port_match = re.search(r':(\d+)\|', matched_line)
                                        if port_match:
                                            port = port_match.group(1)
                                            service_name = port_map.get(port)
                                            if service_name:
                                                files[service_name].write(matched_line + '\n')
                                                service_data[service_name]["count"] += 1
                                                self.count_updated.emit(service_name, service_data[service_name]["count"])
                    except Exception as e:
                        self.log_message.emit(f"  -> Gagal memproses file '{file_path.name}': {e}", "ERROR")

            if self.is_running:
                self.finished.emit(f"Proses scrape selesai! Hasil disimpan di folder '{result_folder}'.")

        except Exception as e:
            self.error.emit(f"Terjadi kesalahan tak terduga selama scraping: {e}")