# STATUS (perbarui setiap sesi)

**Terakhir diperbarui:** 30 Oktober 2026

> Keadaan server di bawah ini terakhir diverifikasi pada 28 Oktober 2026. Pada 30 Oktober pengguna melaporkan memiliki dua HDD Seagate Surveillance 2 TB; unit belum diperiksa langsung. Tidak ada perubahan pada server.

## Posisi sekarang
- Mesin asli sudah ada: **Lenovo ThinkCentre M710q** (i5-6500T, RAM 16 GB terpasang, NVMe 500 GB). RAM cadangan 16 GB dan 8 GB belum dipasang. Ada dua HDD Seagate Surveillance 2 TB berukuran 3,5 inci. Rencana sementara memakai satu unit melalui enclosure single-bay yang tersedia dan menunda unit kedua. Belum ada yang dipasang; model tiap unit belum dicatat dan setidaknya satu belum diformat.
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
- Verifikasi model dan kondisi HDD yang akan dipakai; tentukan peruntukan data/backup. HDD kedua ditunda sampai enclosure tersedia (Bab 27.4).
- Ukuran disk data contoh (musik, foto, PBS) terlalu besar untuk NVMe 500 GB: Bab 27.4.
- Nama menu BIOS Lenovo dan nama kartu LAN (`enp0s31f6` hanyalah contoh) harus dicocokkan di mesin.
- Semua isi buku belum diuji: lihat `catatan/hasil-uji.md`.

## Catatan sesi terakhir
- Repo dirapikan: README diperluas dengan diagram jaringan dan status aktual vs target.
- Duplikasi pada `docs/00-ide-awal.md` dan `docs/08-keputusan.md` dihapus; pohon repo di `docs/03-pohon.md` diselaraskan.
- Konflik lama terkait Tailscale di STB HG680 ditandai dan diselaraskan dengan rancangan terbaru.
- Contoh firewall Bab 51, blok instalasi Docker Bab 49, Caddyfile dan batas jaringan Docker Bab 36, YAML Homepage Bab 34, serta beberapa contoh perintah Bab 41–47 dirapikan.
- Konfigurasi Vaultwarden dan Cloudflare Tunnel memakai variabel versi; nilai versi perlu diverifikasi dan diisi saat implementasi. Token Cloudflare tetap hanya disimpan lokal di `.env`.
- Indeks Edisi 2 kini mengarahkan ke status dan peta guest terbaru; blok perintah yang rusak di Bab 11–14, 16, 18, 21, 23–25, 27, 32, 37, 41–47, 49–55 telah dirapikan.
- Katalog masalah Bab 24 diubah menjadi tabel Markdown; `AGENTS.md` diselaraskan dengan status Proxmox belum terpasang, status Tailscale, dan alur koordinasi SSH.
- Audit statis repo dilanjutkan pada 30 Oktober: Compose Homepage diperbaiki, Cloudflared memakai variabel versi, Caddyfile operasional ditambahkan, stack Kuma/Gotify/Beszel disambungkan ke jaringan proxy, dan tautan Homepage memakai nama HTTPS Caddy. Contoh Bab 34 dan Bab 36 diselaraskan.
- Audit ini memperbarui dokumentasi dan konfigurasi repo GitHub serta salinan lokal `05-Local-REPO`. Tidak ada konfigurasi yang diterapkan atau diuji di server; nilai versi image dan langkah implementasi tetap perlu diverifikasi saat pemasangan di M710q.
- Audit lanjutan: konflik merge tersisa pada catatan uji lokal diselesaikan; PostgreSQL 18 n8n memakai jalur volume yang benar; akses subnet Tailscale dibatasi ke grup admin; konfigurasi Vaultwarden menutup pendaftaran secara default. Perubahan tercatat di `docs/bab/REVISI-4.md`.
