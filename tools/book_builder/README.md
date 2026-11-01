# Penyusun PDF bergaya buku lama

Berkas ini membangun PDF dari bab Markdown terbaru di repo. `build_handbook.py` menyusun sumber isi dan ilustrasi jaringan; `build_book.py` menyajikan sumber tersebut dengan tata letak buku terpadu, tabel pemulihan, dan gambar dari `oracle/`.

## Bangun PDF lengkap

Dari akar repo, jalankan:

```powershell
python tools/book_builder/build_book.py
```

PDF dibuat di `../06-Book/Panduan_Lengkap_Home_Server_Lab_Edisi_Terpadu_2026.11.pdf`. Berikan jalur keluaran lain sebagai argumen pertama bila diperlukan. Argumen kedua berupa bilangan dapat membatasi jumlah segmen untuk build cepat. Python 3 dan ReportLab diperlukan; font Bitstream Vera berasal dari paket ReportLab, sedangkan font terminal memakai Courier bawaan.

## Sumber dan batas

- Isi bersumber dari indeks bab di `docs/bab/edisi2/README.md` dan `docs/bab/suplemen/README.md`, melalui `tools/build_handbook.py`.
- Tabel dan gambar lama dipulihkan dari data turunan di `oracle/`; PDF referensi tidak dibutuhkan untuk membangun.
- Perbarui Markdown sumber lalu bangun ulang. Jangan menyunting PDF langsung.
- PDF menunjukkan progres proyek, bukan bukti layanan sudah diuji. Catat hasil perangkat aktual di `catatan/hasil-uji.md`.
- Aset oracle berasal dari PDF lama; beberapa tangkapan layar/gambar mungkin menggambarkan antarmuka usang dan diberi keterangan di bab terkait.
