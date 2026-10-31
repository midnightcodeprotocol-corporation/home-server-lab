# Bagian 2. Proxmox di Mesin Asli (ThinkCentre M710q): Lembar Pembaruan dan Syarat Lulus Fase 2

## Lembar pembaruan

| Bab sebelumnya | Perubahan | Rujukan |
|---|---|---|
| Edisi 2, Bab 4 | Hanya satu model: mesin asli | Bab 4 |
| Edisi 2, Bab 5 dan 7; Bab 29 | Dihapus (penanda singkat) | - |
| Edisi 2, Bab 6 | Khusus ThinkCentre M710q | Bab 6 |
| Edisi 2, Bab 9 | 9.10 (open-vm-tools) dihapus; snapshot dan disk data disesuaikan | Bab 9 |
| Edisi 2, Bab 23 | Dari "pindah ke mesin asli" menjadi "instal ulang dan restore" | Bab 23 |
| Bab 56 | Tambah 56.7 untuk RAM 32 GB | Bab 56.7 |

## Syarat lulus Fase 2

| No | Poin | Ya / Tidak |
|---|---|---|
| 1 | RAM yang terpasang dikenali BIOS dan lulus MemTest86 (24 GB dilaporkan; konfirmasi aktual) | |
| 2 | BIOS diatur (VT-x, VT-d, UEFI, Secure Boot mati, AHCI, WoL, After Power Loss) | |
| 3 | Proxmox terpasang di NVMe dan web terbuka di 192.168.88.10:8006 | |
| 4 | `sensors` dan `smartctl -H /dev/nvme0` menampilkan data | |
| 5 | HDD 2 TB terbaca sebagai disk data/backup | |
| 6 | Wake-on-LAN dari STB menyalakan mesin | |
| 7 | Bab 25 dan 26 (keamanan dan Tailscale) dikerjakan di mesin ini | |

