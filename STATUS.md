# STATUS (perbarui setiap sesi)

**Terakhir diperbarui:** 28 Oktober 2026

## Posisi sekarang
- Mesin asli sudah ada: **Lenovo ThinkCentre M710q** (i5-6500T, RAM 16 GB terpasang, NVMe 500 GB). RAM cadangan 16 GB dan 8 GB belum dipasang. HDD 2 TB belum dipasang ke server.
- Buku sudah direvisi ke **Revisi 3** (tanpa VMware dan tanpa instal-ke-disk-dulu). Lihat `docs/bab/REVISI-3.md`.
- **Proxmox belum diinstal di M710q.** Jaringan rumah (MikroTik, AP, STB AdGuard) sudah jalan sejak Oktober 2026.
- Tailscale **ditunda** sampai STB 2 tiba (bab 26 memakai CT103 di Proxmox sebagai gantinya; keputusan dapat ditinjau ulang).

## Langkah berikutnya (urut)
1. Pasang RAM 16 GB cadangan (total 32 GB), jalankan MemTest86 (Bab 27.1, 27.3).
2. Atur BIOS Lenovo (Bab 27.5).
3. Buat USB bootable dan instal Proxmox (Bab 6, 8, 28), lihat `docs/09-mulai-di-m710q.md`.
4. Konfigurasi awal dan pasca-instalasi (Bab 9, 30).
5. Keamanan dan Tailscale (Bab 25, 26), lalu lanjut sesuai `docs/04-board.md`.

## Masalah terbuka
- Muat tidaknya HDD 2 TB di bay 2,5" M710q (atau pakai casing USB): Bab 27.4.
- Ukuran disk data contoh (musik, foto, PBS) terlalu besar untuk NVMe 500 GB: Bab 27.4.
- Nama menu BIOS Lenovo dan nama kartu LAN (`enp0s31f6` hanyalah contoh) harus dicocokkan di mesin.
- Semua isi buku belum diuji: lihat `catatan/hasil-uji.md`.

## Catatan sesi terakhir
Repo dibuat dan diperbarui untuk Revisi 3. Belum ada perintah buku yang dijalankan di M710q.
