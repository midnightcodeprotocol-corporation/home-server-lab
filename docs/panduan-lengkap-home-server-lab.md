# Panduan Lengkap Home Server Lab

## Edisi lengkap 2026

Buku lengkap terdiri dari Bab 1–56 (hanya nomor yang memang ada di repo), lampiran, pengantar dan penutup fase, diagram, panduan perintah, keamanan, backup, pemecahan masalah, dan roadmap. Versi PDF siap baca berjumlah 235 halaman dan Markdown gabungan tersedia di folder lokal `06-Book/`. Generatornya adalah `tools/build_handbook.py`.

- PDF lengkap: `06-Book/Panduan_Lengkap_Home_Server_Lab_Edisi_Lengkap_2026.pdf`
- Markdown lengkap: `06-Book/Panduan_Lengkap_Home_Server_Lab_Edisi_Lengkap_2026.md`
- [Bab 1–24 dan lampiran](bab/edisi2/README.md)
- [Suplemen Bab 25–56 dan panduan fase](bab/suplemen/README.md)
- [Roadmap manfaat dan keamanan](12-roadmap-manfaat-keamanan.md)
- [Status server dan langkah berikut](../STATUS.md)

Buku lengkap menggantikan panduan ringkas 32 halaman sebagai rujukan utama. Edisi lama 300 halaman disimpan di folder lokal sebagai arsip; versi terbaru menghapus materi yang sudah dihentikan dan menyertakan perubahan terbaru, sehingga jumlah halaman berbeda.

## Status dan batas penggunaan

Jaringan rumah sudah berjalan, tetapi Proxmox belum dipasang pada ThinkCentre M710q. Storage, guest, layanan, backup, firewall host, Tailscale, dan prosedur pemulihan di buku adalah rencana hingga diterapkan serta diuji. Jangan anggap konfigurasi sebagai bukti operasional. Catat hasil nyata di [`catatan/hasil-uji.md`](../catatan/hasil-uji.md).

Jangan memasukkan kata sandi, token, private key, serial disk, atau rahasia ke buku maupun repo. Verifikasi versi perangkat lunak, alamat, jalur disk, dan nama antarmuka sebelum menjalankan perintah.

## Memperbarui buku

Ubah bab sumber di repo terlebih dahulu. Lalu dari akar repo jalankan `python tools/build_handbook.py` untuk membangun ulang Markdown gabungan dan PDF lokal. Periksa PDF dan tautan sebelum menyalin hasil final ke `06-Book/`.

