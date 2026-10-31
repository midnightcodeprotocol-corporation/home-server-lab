# Hasil uji per fase

Isi setiap kali satu bab selesai diuji. Tulis pesan error persis dan bab yang perlu direvisi.

Status: **pengujian bab lengkap masih berlangsung**. Pemeriksaan awal host Proxmox di M710q sudah berhasil dan dicatat di bawah. Hasil uji sebelumnya di lab VMware ada di `kasus-nyata-lab.md`; catatan itu hanya menjadi riwayat.

| Fase | Bagian / Bab | Tanggal | Lulus? | Catatan / error | Revisi buku |
|---|---|---|---|---|---|
| 1 | Keamanan dan Tailscale (25-26) | | | | |
| 2 | Mesin M710q: RAM, BIOS, instal Proxmox (6, 8, 9, 27, 28, 30) | 31 Okt 2026 | Parsial | Proxmox terpasang dan diperbarui; cek host lulus. BIOS/MemTest dan keseluruhan bab belum diuji. Detail di bawah. |
| 3 | Monitoring (31-34) | | | | |
| 4 | Caddy dan sertifikat lokal (35-38) | | | | |
| 5 | Web, WordPress, n8n, tunnel (39-43) | | | | |
| 6 | Vaultwarden, AFFiNE, Nextcloud (44-47) | | | | |
| 7 | Peta, templat, PBS, firewall, audit (48-52) | | | | |
| 8 | Navidrome (53) | | | | |
| 9 | Pocket ID, Immich, profil RAM (54-56) | | | | |

Uji Proxmox dan jaringan lebih dulu. Setelah itu uji Tailscale (Bab 26) dan Caddy (Bab 36-37); bagian 5 ke atas bergantung pada keduanya.

## Templat catatan per langkah

```text
Bab: <nomor>   Tanggal: <tanggal>
Langkah: <nomor/uraian>
Hasil: lulus | gagal | perlu revisi
Pesan error (persis): <salin>
Butir [BELUM PASTI] terjawab: <ya/tidak, jawabannya>
Penyimpangan dari buku: <catat>
```

## Pemeriksaan awal host Proxmox — 31 Oktober 2026

### Hasil yang berhasil
- `uname -r` setelah reboot: `7.0.14-26-pve`.
- `systemctl --failed`: `0 loaded units listed`.
- `free -h`: Mem total `23Gi`, tersedia `21Gi`; swap `8.0Gi`.
- `lsblk -d -o NAME,SIZE,MODEL,TRAN`: `nvme0n1 476.9G SAMSUNG MZALQ512HALU-000L2 nvme`.
- `pvesm status`: `local` dan `local-lvm` aktif; local-lvm belum terpakai.
- Pembaruan melalui GUI selesai; ringkasan apt: 193 paket upgraded, 2 paket baru, 0 paket dihapus.

### Gangguan DNS saat update pertama
Jaringan host saat itu sementara, bukan MikroTik:
- Host: `vmbr0 = 192.168.0.200/24`; gateway `192.168.0.1`.
- `/etc/resolv.conf` sebelumnya menunjuk ke `192.168.88.253`, sehingga nama Debian/Proxmox tidak ter-resolve dari jaringan sementara.
- `ping 1.1.1.1` berhasil, tetapi `getent hosts deb.debian.org` awalnya tidak mengembalikan alamat.
- DNS diubah ke `192.168.0.1`; resolusi nama berhasil. `apt-get -o Acquire::ForceIPv4=true update` kemudian berhasil mengunduh indeks Debian Trixie dan Proxmox.
- Pengguna mengonfirmasi alamat `192.168.0.0/24` hanya untuk sementara sampai server kembali tersambung ke MikroTik. Jangan menyimpulkan ini sebagai perubahan jaringan rumah.

### Catatan perangkat dan pekerjaan tersisa
- RAM terpasang 16 GB + 8 GB; Linux melaporkan 23 GiB. Ini mengonfirmasi OS melihat kapasitas yang diharapkan, tetapi BIOS dan MemTest86 belum diperiksa.
- NVMe Samsung terdeteksi pada 476,9 GB. Dua HDD 2 TB belum tersambung.
- Pengguna menemukan enclosure single-bay lama; fungsi enclosure belum diuji. Enclosure dan HDD akan diuji setelah pengguna tiba di rumah.
- Belum ada VM/LXC atau backup. Penggunaan local-lvm untuk guest dimungkinkan, tetapi konfigurasi guest dan alamat jaringan final belum dibuat.
