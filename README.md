# File Scraper Pro

File Scraper Pro adalah sebuah aplikasi desktop yang dirancang untuk memindai ribuan file teks (`.txt`) secara efisien untuk mencari dan menyortir baris data berdasarkan port layanan yang spesifik. Aplikasi ini dibangun dengan Python dan PySide6, menyediakan antarmuka pengguna yang modern dan responsif.

 
![Tampilan Aplikasi File Scraper Pro](assets/Screenshot.png)

## Fitur Utama

- **Pemindaian Cepat**: Menggunakan satu pola Regex yang digabungkan untuk memindai semua layanan secara bersamaan.
- **Antarmuka Responsif**: Proses scraping berjalan di *thread* terpisah, sehingga antarmuka pengguna tidak akan "beku" saat memproses banyak file.
- **Konfigurasi Fleksibel**: Layanan yang dicari (misalnya, FTP, SSH, cPanel) dapat dengan mudah dikonfigurasi melalui file `services_config.json`.
- **Drag & Drop**: Mendukung pemilihan folder dengan menyeret dan melepaskannya ke dalam jendela aplikasi.
- **Tampilan Modern**: Antarmuka yang bersih dan modern dibuat dengan PySide6 dan QSS.
- **Penghapusan Duplikat**: Secara otomatis memastikan tidak ada baris data duplikat yang disimpan di hasil akhir.

## Instalasi

Untuk menjalankan aplikasi ini, Anda memerlukan Python 3 dan beberapa pustaka Python.

1.  **Clone repositori ini:**
    ```bash
    git clone https://github.com/kliverz1337/FILE-SCRAPER-PRO.git
    cd file-scraper-pro
    ```

2.  **(Opsional tapi direkomendasikan) Buat dan aktifkan lingkungan virtual:**
    ```bash
    # Windows
    python -m venv venv
    .\venv\Scripts\activate

    # macOS / Linux
    python3 -m venv venv
    source venv/bin/activate
    ```

3.  **Instal dependensi yang diperlukan:**
    Gunakan file `requirements.txt` untuk menginstal semua dependensi proyek dengan satu perintah:
    ```bash
    pip install -r requirements.txt
    ```

## Cara Menjalankan

Setelah instalasi selesai, Anda dapat menjalankan aplikasi dengan mengeksekusi file `main.py`:

```bash
python main.py
```

Aplikasi akan membuat file `services_config.json` secara otomatis saat pertama kali dijalankan. Anda dapat mengedit file ini untuk menambah, mengubah, atau menghapus layanan yang ingin Anda cari.

## Cara Menggunakan

1.  Jalankan aplikasi.
2.  Seret folder yang berisi file `.txt` ke dalam area yang ditentukan, atau klik tombol **"Mulai Scraping"** untuk memilih folder.
3.  Proses scraping akan dimulai secara otomatis. Anda dapat melihat progresnya di jendela aplikasi.
4.  Setelah selesai, semua hasil yang ditemukan akan disortir dan disimpan dalam file-file terpisah di dalam folder `RESULT LIST`.