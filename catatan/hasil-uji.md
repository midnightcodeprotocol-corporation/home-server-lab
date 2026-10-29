# Hasil uji per fase

Isi setiap kali satu bab selesai diuji. Tulis pesan error persis dan bab yang perlu direvisi.
Status: **belum ada bab yang diuji di mesin asli (ThinkCentre M710q)**. Hasil uji sebelumnya di lab VMware ada di `kasus-nyata-lab.md` (tidak lagi relevan untuk instalasi).

| Fase | Bagian / Bab | Tanggal | Lulus? | Catatan / error | Revisi buku |
|---|---|---|---|---|---|
| 2 | Mesin M710q: RAM, BIOS, instal Proxmox (6, 8, 9, 27, 28, 30) | | | | |
| 1 | Keamanan dan Tailscale (25-26) | | | | |
| 3 | Monitoring (31-34) | | | | |
| 4 | Caddy dan sertifikat lokal (35-38) | | | | |
| 5 | Web, WordPress, n8n, tunnel (39-43) | | | | |
| 6 | Vaultwarden, AFFiNE, Nextcloud (44-47) | | | | |
| 7 | Peta, templat, PBS, firewall, audit (48-52) | | | | |
| 8 | Navidrome (53) | | | | |
| 9 | Pocket ID, Immich, profil RAM (54-56) | | | | |

Urutan penting: uji Proxmox dan jaringan lebih dulu, lalu Tailscale (Bab 26) dan Caddy (Bab 36-37), karena Bagian 5 ke atas bergantung pada keduanya.

## Templat catatan per langkah
```
Bab: <nomor>   Tanggal: <tanggal>
Langkah: <nomor/uraian>
Hasil: lulus | gagal | perlu revisi
Pesan error (persis): <salin>
Butir [BELUM PASTI] terjawab: <ya/tidak, jawabannya>
Penyimpangan dari buku: <catat>
```
