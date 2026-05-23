# 🚀 Simple ETL Pipeline: Competitor Product Scraper (Fashion Studio)

Sistem *pipeline* ETL sederhana yang dirancang untuk mengekstrak data produk dari situs kompetitor **Fashion Studio**, melakukan transformasi data (termasuk konversi mata uang), dan memuatnya ke dalam format yang siap dianalisis.

---

## 👤 Profil Pengembang
* **Nama:** Puspita
* **Email:** baharipuspita@apps.ipb.ac.id
* **Institusi:** IPB University

---

## 📝 Deskripsi Proyek
Proyek ini mengotomatiskan penarikan data produk dari *platform* e-commerce kompetitor, **Fashion Studio** (https://fashion-studio.dicoding.dev). Hasil dari *pipeline* ini dapat digunakan oleh tim bisnis untuk melakukan analisis harga (*pricing analysis*) dan memantau tren produk kompetitor secara *real-time*.

### Alur Kerja ETL (Pipeline Architecture)



1. **Extract**: Mengambil data mentah produk langsung dari website Fashion Studio.
2. **Transform**: 
   * Membersihkan struktur data penamaan produk, ukuran, dan gender.
   * Melakukan konversi harga dari **USD ke IDR** dengan standarisasi kurs ($1 USD = Rp 16.000$).
3. **Load**: Menyimpan data yang telah bersih dan terstruktur ke dalam format siap pakai (seperti CSV/JSON atau Database).

---

## 📊 Skema Data (Data Features)
Data yang berhasil diekstrak dan diproses mencakup informasi berikut:

| Nama Kolom | Deskripsi | Tipe Data / Format |
| :--- | :--- | :--- |
| `Title` | Nama atau judul produk | String |
| `Price_USD` | Harga asli produk dalam satuan USD | Float / Numeric |
| `Price_IDR` | Harga produk setelah dikonversi ke Rupiah | Integer / Numeric |
| `Colors` | Jumlah variasi warna yang tersedia | Integer |
| `Size` | Ukuran produk yang tersedia (S, M, L, XL, dll) | String / Array |
| `Gender` | Kategori gender target produk (Men, Women, Unsex) | String |
| `Rating` | Penilaian atau ulasan konsumen (Skala 1 - 5) | Float |

---

## 🛠️ Prasyarat & Instalasi

Sebelum menjalankan proyek ini, pastikan Anda telah menginstal Python di komputer Anda.

1. **Clone Repositori** (atau unduh folder proyek Anda):
   ```bash
   git clone [https://github.com/username-kamu/nama-repo-kamu.git](https://github.com/username-kamu/nama-repo-kamu.git)
   cd nama-folder-proyek
