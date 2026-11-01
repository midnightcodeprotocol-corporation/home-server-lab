# Revisi 6: Template Debian 13 dan status jaringan host

**Tanggal:** 1 November 2026  
**Cakupan:** pembaruan buku berdasarkan tangkapan layar Proxmox dan konfirmasi pengguna tentang template yang dibuat.

## Progres host

- Proxmox VE 9.2.24 tampil pada antarmuka; kernel aktif yang sebelumnya dicatat adalah `7.0.14-26-pve`.
- Pemeriksaan SSH baca-saja 1 November mengonfirmasi VM 200 dan CT 100 berstatus template serta berhenti. Nama aktual pada konfigurasi adalah `Tamplate-VM` dan `Tamplate-CT` (kemungkinan typo; belum diubah).
- Pengguna mengonfirmasi Debian 13 dipakai pada kedua template.
- VM 200: 1 vCPU, RAM 2048 MiB, disk 32 GiB di `local-lvm`, QEMU Agent aktif pada konfigurasi, jaringan `vmbr0` + firewall. Paket di dalam guest belum diperiksa karena template berhenti. CT 100: 1 vCPU, RAM/swap 512 MiB, disk 8 GiB, unprivileged, nesting aktif, DHCP di `vmbr0` + firewall.
- Belum ada guest layanan atau hasil clone yang dilaporkan.
- SSH baca-saja mengonfirmasi host masih memakai `192.168.0.200/24`, gateway/DNS `192.168.0.1`; target MikroTik adalah `192.168.88.10/24`, gateway `192.168.88.1`, DNS AdGuard `192.168.88.253`. Perubahan IP belum diterapkan.

## Penomoran guest

| ID | Nama | Jenis | Status |
|---:|---|---|---|
| 100 | `Tamplate-CT` | LXC template | Debian 13; 1 CPU, 512 MiB RAM, 512 MiB swap, disk 8 GiB; unprivileged, nesting, DHCP |
| 200 | `Tamplate-VM` | VM template | Debian 13; 1 CPU, 2 GiB RAM, disk 32 GiB; QEMU Agent disetel; paket guest belum diperiksa |
| 101+ | LXC layanan | LXC | ID layanan tetap mengikuti peta guest |
| 201+ | VM layanan | VM | ID layanan tetap mengikuti peta guest |
| 9000 | `debian13-template` | VM cloud-init | Rencana lama untuk k3s; keberadaan aktual belum diverifikasi |

Template 100 dan 200 tidak bertabrakan dengan ID guest layanan yang direncanakan mulai dari 101 dan 201. Jangan membuat ulang ID template tersebut selama masih terdaftar. Sebelum membuat clone Docker, pastikan VM 200 memiliki Docker dan paket yang memang diperlukan; jika belum, lengkapi baseline atau ikuti prosedur Bab 49 dengan catatan bahwa template akan diubah.

## Akses SSH dan catatan nama

Pengguna menambahkan kunci publik khusus ke `/root/.ssh/authorized_keys`; koneksi Codex ke Proxmox kini aktif sebagai root. SSH dipakai untuk audit baca-saja pada sesi ini. Jangan menyimpan kunci privat, passphrase, atau isi `authorized_keys` di repo. Akses root dapat dicabut dengan menghapus baris kunci tersebut dari `authorized_keys`. Nama template pada konfigurasi aktual tertulis `Tamplate-VM` dan `Tamplate-CT`; kemungkinan typo ini belum diubah.

## Pembaruan dokumen

| Lokasi | Pembaruan |
|---|---|
| `data/guest.yaml` | Mencatat Debian 13 pada template 200/100 dan spesifikasi CT yang terlihat. |
| Bab 48-49 | Menyamakan peta dan perintah template dengan ID aktual 200/100; menandai paket VM yang belum diketahui. |
| `README.md`, `STATUS.md`, papan proyek | Menandai template selesai dibuat; guest layanan masih belum dilaporkan. |
| `tools/book_builder/` | Memelihara renderer bergaya buku, aset tabel/gambar, dan instruksi build lintas platform. |
| Bab 9 dan konsep penomoran | Menjelaskan ID template 100/200, ID layanan 101+/201+, dan template cloud-init 9000 secara terpisah. |

## Langkah berikutnya

1. Selesaikan perpindahan konfigurasi jaringan host dari `192.168.0.200/24` ke jaringan MikroTik dan verifikasi panel di `192.168.88.10:8006`.
2. Catat paket dasar VM 200 dari konfigurasi guest; jangan mengasumsikan Docker sudah terpasang.
3. Buat dan uji clone pertama memakai ID guest berikutnya yang belum dipakai; periksa hostname, alamat IP, akses jaringan, dan identitas SSH sebelum memasang layanan.

## Batas verifikasi

Konfigurasi VM/CT, status template, bridge, dan IP host diverifikasi melalui SSH baca-saja pada 1 November. Debian 13 dikonfirmasi pengguna. Paket di dalam VM 200, hasil uji clone, perpindahan IP host, dan layanan belum diverifikasi.

## Pembaruan buku

Edisi Terpadu 2026.11 dibangun ulang dari sumber Markdown saat ini: 258 halaman A4, termasuk sampul, ilustrasi jaringan dengan status host sementara dan target MikroTik, tabel, kotak perintah, serta daftar isi. PDF disimpan di folder lokal `06-Book`; sumber dan instruksi build ada di repo. Pemeriksaan sampel visual dilakukan pada sampul, status, diagram, dan halaman isi.
