# Gemini Chat Application

## Deskripsi Proyek
Aplikasi chat berbasis AI menggunakan Gemini API dengan fitur login, registrasi, dan interaksi chat yang dinamis.

## Prasyarat
- Python 3.8+
- MySQL Server
- Koneksi Internet

## Persiapan Lingkungan

### 1. Clone Repository
```bash
git https://github.com/fathka/GeminiChat-Api-Tkinter-MySql.git
cd GeminiChat-Api-Tkinter-MySql
```

### 2. Buat Virtual Environment
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Instalasi Dependensi
```bash
pip install -r requirements.txt
```

### 4. Konfigurasi Database MySQL
1. Buat database baru:
```sql
CREATE DATABASE gemini_chat;

USE gemini_chat;

CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_username ON users(username);

```

2. Konfigurasi Koneksi Database
- Buka script dan sesuaikan kredensial di `DatabaseManager` class
- Atau atur environment variables:
  - `DB_HOST`: "localhost",
  - `DB_USER`: "root",
  - `DB_PASSWORD`: "password Anda",
  - `DB_NAME`: "gemini_chat"

### 5. Siapkan Background Image
- Letakkan file `bg.jpeg` di direktori yang sama dengan script

### 6. Konfigurasi API Key Gemini
- Ganti API key di `GeminiChatBot` class dengan API key Anda sendiri dari Google AI Studio

## Menjalankan Aplikasi
```bash
python gemini.py
```

## Fitur Aplikasi
- Login/Registrasi Pengguna
- Chat dengan Gemini AI
- Kontrol parameter AI (Temperature, Top K, Top P)
- Simpan riwayat chat

## Troubleshooting
- Pastikan semua dependensi terinstal
- Periksa koneksi database
- Pastikan API key valid
- Gunakan python 3.8+ 
