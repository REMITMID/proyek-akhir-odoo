# MR. DIY Enterprise Resource Planning (ERP) - Odoo 16 Suite

Modul Custom Addon Odoo 16 untuk Studi Kasus PT Daya Intiguna Yasa Tbk (MR. DIY Indonesia) yang mencakup 13 pilar modul operasional perusahaan:
- **Accounting & Keuangan:** Entri kas non-operasional (kardus bekas), penutupan buku, rekonsiliasi audit kasir.
- **Purchase & Procurement:** Pengadaan vendor lokal & impor (OEM/ODM China), customs clearance, 3-way matching.
- **Fleet Distribution:** Manajemen armada truk CDC (CDD, CDE, Blind Van), konsumsi BBM, driver manifest.
- **Employees & Attendance:** Manajemen pegawai toko/CDC dan denda presensi keterlambatan.
- **Inventory & Logistik:** Arus barang CDC, Transfer-In, Transfer-Out, Keep Stock wall gondola, scan PDT.
- **Point of Sale (POS):** Kasir gerai ritel terintegrasi mata uang Rupiah (IDR).
- **Payroll (Penggajian):** Kalkulasi gaji pokok, tunjangan, lembur, insentif, potongan BPJS/PPh21, dan bank transfer.
- **Quality Control & BASK:** Validasi mutu barang datang dan Berita Acara Selisih/Kerusakan (BASK).
- **Website & Recruitment:** Publikasi lowongan kerja karir toko dan alur seleksi pelamar.

---

## 🛠️ Prasyarat Sistem (Prerequisites)

Sebelum menjalankan Odoo, pastikan komputer/laptop sudah terpasang:
1. **Python 3.10 - 3.12 (64-bit)** (Wajib centang *"Add Python to PATH"* saat install).
2. **PostgreSQL 14 / 15 / 16 / 17** (Port standar 5432).
3. **Git for Windows** (Opsional, untuk clone repo).

---

## 🚀 Panduan Instalasi & Menjalankan (Step-by-Step)

### 1. Persiapan Database PostgreSQL
Buka Command Prompt (Run as Administrator) atau jalankan SQL Shell (psql):
```cmd
"C:\Program Files\PostgreSQL\<versi_pg>\bin\psql.exe" -U postgres
```
Masukkan password postgres Anda, lalu ketik perintah SQL berikut:
```sql
CREATE USER odoo WITH PASSWORD 'odoo';
ALTER USER odoo WITH SUPERUSER;
CREATE DATABASE odoo OWNER odoo;
\q
```

---

### 2. Setup Virtual Environment & Source Code Odoo 16
Buka terminal / Command Prompt:
```cmd
mkdir C:\odoo
cd C:\odoo

REM 1. Buat & aktifkan virtual environment Python
python -m venv venv
call venv\Scripts\activate

REM 2. Install dependensi inti (Sangat penting agar tidak error!)
python -m pip install --upgrade pip
pip install "setuptools<70.0.0" wheel psycopg2-binary openpyxl pandas

REM 3. Download source code Odoo 16 (ringan ~300MB)
git clone --depth 1 https://github.com/odoo/odoo.git -b 16.0 odoo-16

REM 4. Install requirement Odoo
pip install -r odoo-16\requirements.txt
```

---

### 3. Pasang Modul MR. DIY ERP
1. Salin folder `mr_diy_erp` dari repositori ini ke dalam folder addons Odoo:
```cmd
mkdir C:\odoo\odoo-16\custom_addons
xcopy /E /I /Y "path\ke\repo\mr_diy_erp" "C:\odoo\odoo-16\custom_addons\mr_diy_erp"
```

2. Buat file konfigurasi `C:\odoo\odoo.conf`:
```ini
[options]
db_host = 127.0.0.1
db_port = 5432
db_user = odoo
db_password = odoo
addons_path = C:\odoo\odoo-16\addons,C:\odoo\odoo-16\custom_addons
admin_passwd = admin
http_port = 8069
```

---

### 4. Menjalankan Odoo Server
Nyalakan server Odoo dengan perintah:
```cmd
python odoo-16\odoo-bin -c C:\odoo\odoo.conf -d odoo -i base
```
Tunggu hingga muncul pesan:
```text
HTTP service (werkzeug) running on ... 8069
```

---

### 5. Aktivasi Modul di Browser
1. Buka browser: **`http://localhost:8069`**
2. Login dengan akun:
   - **Email:** `admin`
   - **Password:** `admin`
3. Masuk ke **Settings** -> Scroll ke paling bawah -> Klik **"Activate the developer mode"**.
4. Buka menu **Apps** -> Klik tombol **"Update Apps List"** di bar atas -> Klik **Update**.
5. Hapus filter *"Apps"* di kotak search, ketik `mr_diy`.
6. Klik tombol **Activate / Install** pada modul **"MR DIY ERP – Integrated Suite"**.

---

### 6. Impor Otomatis Data Master & Dashboard Sales (Rupiah)
Setelah modul terpasang, jalankan 3 skrip otomatis yang sudah disediakan di folder `Code/`:
```cmd
cd C:\odoo
call venv\Scripts\activate

REM 1. Impor data master (Vendor, Produk, Pegawai, Armada CDC, Payroll, BASK)
python import_all_data.py

REM 2. Impor data presensi, pelamar rekrutmen, dan lowongan karir
python import_remaining_data.py

REM 3. Setel currency IDR (Rp) dan generate dashboard transaksi penjualan
python setup_dashboard_sales.py
```

Setelah selesai, refresh browser (`Ctrl + F5`), dan seluruh sistem MR. DIY ERP sudah siap digunakan dengan data lengkap dan mata uang Rupiah (Rp)! 🎉
