# Revisi 8: guest layanan pertama

**Tanggal:** 1 November 2026
**Cakupan:** pembuatan CT 101 dan VM 201 dari template bersih; host tetap berada di router sementara.

## Guest yang dibuat

- **CT 101 `adguard2`** dibuat sebagai full clone CT 100. Konfigurasi: 1 core, RAM 512 MiB, swap 512 MiB, disk 8 GiB, unprivileged, nesting, firewall Proxmox, DHCP. Status running; alamat sementara `192.168.0.106/24`.
- **VM 201 `docker-core`** dibuat sebagai full clone VM 200. Konfigurasi: 2 core, RAM 2048 MiB, disk 32 GiB di `local-lvm`, VirtIO pada `vmbr0`, firewall Proxmox, QEMU Guest Agent aktif, DHCP. Status running; alamat sementara `192.168.0.107/24`.
- Hostname VM diubah dari `debian-docker` menjadi `docker-core`. CT sudah memakai hostname `adguard2`.
- Keduanya menggunakan ID layanan sesuai peta: CT pada rentang 100–199 dan VM pada rentang 201–299. Template CT 100 dan VM 200 tetap ada serta tidak diubah.

## Jaringan dan pekerjaan berikutnya

Host masih berada pada router sementara `192.168.0.0/24`, gateway `192.168.0.1`. Alamat rumah yang direncanakan adalah CT101 `192.168.88.11` dan VM201 `192.168.88.20`; alamat tersebut belum ditetapkan. Jangan pasang AdGuard sebagai DNS layanan atau membuka akses Docker sebelum host tersambung ke MikroTik, reservasi DHCP dibuat untuk MAC guest, dan alamat final diverifikasi.

Aplikasi AdGuard Home pada CT101, Docker/Portainer/Caddy dan stack yang direncanakan pada VM201 belum dipasang. Ikuti Bab 13 untuk AdGuard dan Bab 14 serta suplemen Docker setelah jaringan rumah aktif. HDD, backup, dan pemulihan tetap belum dikonfigurasi.

## Pemeriksaan setelah pembuatan

- `qm list` dan `pct list` menunjukkan template 100/200 serta guest 101/201; keduanya berstatus running.
- QEMU Guest Agent melaporkan hostname `docker-core` dan DHCP `192.168.0.107` pada `ens18`.
- CT melaporkan hostname `adguard2` dan DHCP `192.168.0.106` pada `eth0`.
- Storage `local` dan `local-lvm` tetap aktif; penggunaan `local-lvm` sekitar 1,70% segera setelah full clone VM.
