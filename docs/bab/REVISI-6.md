# Revisi 6: Template Debian 13 dan status jaringan host

**Tanggal:** 1 November 2026  
**Cakupan:** pembaruan buku berdasarkan tangkapan layar Proxmox dan konfirmasi pengguna tentang template yang dibuat.

## Progres host

- Proxmox VE 9.2.24 tampil pada antarmuka; kernel aktif yang sebelumnya dicatat adalah `7.0.14-26-pve`.
- Template VM 200 bernama `Template-VM` dan template CT 100 bernama `Template-CT` terlihat pada pohon Proxmox.
- Pengguna mengonfirmasi Debian 13 dipakai pada kedua template.
- Ringkasan CT 100 memperlihatkan 1 CPU, RAM 512 MiB, swap 512 MiB, dan disk 8 GiB. Paket tambahan pada VM 200 belum dicatat.
- Belum ada guest layanan atau hasil clone yang dilaporkan.
- Host masih dibuka melalui alamat sementara `192.168.0.200`; target MikroTik adalah `192.168.88.10/24`, gateway `192.168.88.1`, DNS AdGuard `192.168.88.253`. Perubahan IP belum diterapkan.

## Penomoran guest

| ID | Nama | Jenis | Status |
|---:|---|---|---|
| 100 | `Template-CT` | LXC template | Debian 13; 1 CPU, 512 MiB RAM, 512 MiB swap, disk 8 GiB |
| 200 | `Template-VM` | VM template | Debian 13; paket dasar belum dicatat |
| 101+ | LXC layanan | LXC | ID layanan tetap mengikuti peta guest |
| 201+ | VM layanan | VM | ID layanan tetap mengikuti peta guest |
| 9000 | `debian13-template` | VM cloud-init | Rencana lama untuk k3s; keberadaan aktual belum diverifikasi |

Template 100 dan 200 tidak bertabrakan dengan ID guest layanan yang direncanakan mulai dari 101 dan 201. Jangan membuat ulang ID template tersebut selama masih terdaftar. Sebelum membuat clone Docker, pastikan VM 200 memiliki Docker dan paket yang memang diperlukan; jika belum, lengkapi baseline atau ikuti prosedur Bab 49 dengan catatan bahwa template akan diubah.

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

Status template dan spesifikasi CT 100 diambil dari tangkapan layar pengguna; Debian 13 pada keduanya dikonfirmasi pengguna. Isi paket VM 200, hasil uji clone, perpindahan IP host, dan layanan belum diverifikasi dari shell Proxmox.

## Pembaruan buku

Edisi Terpadu 2026.11 dibangun ulang dari sumber Markdown saat ini: 258 halaman A4, termasuk sampul, ilustrasi jaringan dengan status host sementara dan target MikroTik, tabel, kotak perintah, serta daftar isi. PDF disimpan di folder lokal `06-Book`; sumber dan instruksi build ada di repo. Pemeriksaan sampel visual dilakukan pada sampul, status, diagram, dan halaman isi.
