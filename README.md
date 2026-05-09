# ShortURL — Pemendek Tautan

Aplikasi web pemendek URL berbasis Flask yang di-deploy ke Railway (PaaS).

Dibuat untuk Tugas Mandiri Mata Kuliah **Komputasi Awan (BBK3CAB3)**  
Program Studi S1 Sistem Informasi — Universitas Telkom

---

## Stack Teknologi

| Komponen | Teknologi |
|---|---|
| Backend Framework | Flask 3.1 |
| ORM | Flask-SQLAlchemy |
| Database (lokal) | SQLite |
| Database (produksi) | PostgreSQL (Railway Add-on) |
| WSGI Server | Gunicorn |
| Deployment | Railway (PaaS) |

---

## Endpoint

| Method | URL | Keterangan |
|---|---|---|
| `GET` | `/` | Halaman utama UI |
| `POST` | `/shorten` | Memperpendek URL |
| `GET` | `/<short_code>` | Redirect ke URL asli |
| `GET` | `/health` | Health check endpoint |
| `GET` | `/api/urls` | Daftar 10 URL terakhir (JSON) |

---

## Cara Menjalankan Secara Lokal

```bash
# 1. Clone repository
git clone <url-repo-kamu>
cd url-shortener

# 2. Buat virtual environment
python -m venv venv
source venv/bin/activate        # Linux/macOS
# venv\Scripts\activate         # Windows

# 3. Install dependencies
pip install -r requirements.txt

# 4. Jalankan aplikasi
python app.py
```

Buka di browser: http://localhost:5000

---

## Deploy ke Railway

```bash
# 1. Login Railway
railway login

# 2. Buat project baru
railway new

# 3. Tambah PostgreSQL add-on di dashboard Railway
# Salin DATABASE_URL ke environment variable

# 4. Deploy
railway up
```

Railway otomatis mendeteksi `Procfile` dan menjalankan `gunicorn app:app`.

---

## Variabel Lingkungan

| Variable | Keterangan |
|---|---|
| `DATABASE_URL` | URL koneksi PostgreSQL dari Railway |
| `PORT` | Port server (otomatis diisi Railway) |
