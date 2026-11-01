# STATUS (perbarui setiap sesi)

**Terakhir diperbarui:** 1 November 2026

## Posisi sekarang
- Jaringan rumah memakai MikroTik, access point, dan STB AdGuard. Server masih memakai jaringan sementara `192.168.0.200/24` sampai kembali tersambung ke MikroTik.
- Mini PC server **Lenovo ThinkCentre M710q** sudah tersedia (Intel Core i5-6500T, 4 core/4 thread).
- RAM 16 GB + 8 GB terpasang; Linux Proxmox melaporkan **23 GiB**. BIOS dan MemTest86 belum diperiksa.
- NVMe Samsung MZALQ512HALU-000L2 terdeteksi sebagai `nvme0n1` berukuran **476,9 GB**; Proxmox berjalan.
- Dua HDD Seagate Surveillance 2 TB, 3,5 inci belum dipasang. Enclosure single-bay lama ditemukan, belum diuji, dan berada di rumah bersama HDD.
- Proxmox VE 9.2.24 selesai diperbarui dan reboot: kernel `7.0.14-26-pve`; `systemctl --failed` melaporkan nol unit gagal. Storage `local` dan `local-lvm` aktif.
- VT-x/KVM aktif setelah perbaikan BIOS tanpa monitor melalui `thinklmi`; setelah reboot `lscpu` menunjukkan `Virtualization: VT-x` dan `/dev/kvm` tersedia. VT-d tetap `Disabled`.
- SSH dari Codex ke `root@192.168.0.200` berhasil dengan kunci ed25519 yang dikelola pengguna; fingerprint host cocok. Pemeriksaan Proxmox baca-saja berhasil. Kunci privat dan isi `authorized_keys` tidak disimpan di repo.
- SSH baca-saja 1 November mengonfirmasi VM 200 dan CT 100 berstatus template dan stopped. Nama aktual: `Tamplate-VM` dan `Tamplate-CT` (kemungkinan typo). VM 200: Debian 13 menurut pengguna, 1 vCPU, 2048 MiB RAM, disk 32 GiB di `local-lvm`, QEMU Agent aktif pada konfigurasi, bridge `vmbr0` dengan firewall; isi paket guest belum diperiksa. CT 100: Debian 13 menurut pengguna, 1 vCPU, 512 MiB RAM/swap, 8 GiB di `local-lvm`, unprivileged, nesting, DHCP pada `vmbr0` dengan firewall. Guest layanan dan clone belum dibuat.
- SSH baca-saja 1 November mengonfirmasi host masih memakai `192.168.0.200/24`, default gateway `192.168.0.1`, dan DNS `192.168.0.1`. Proxmox masih dibuka melalui router sementara. Konfigurasi rumah yang dituju: `192.168.88.10/24`, gateway `192.168.88.1`, DNS AdGuard `192.168.88.253`; perpindahan ke MikroTik belum diterapkan.

- Nama VM/CT pada konfigurasi Proxmox tertulis `Tamplate-VM` dan `Tamplate-CT`; kemungkinan typo ini belum diubah.

## Langkah berikutnya
1. Siapkan perubahan jaringan host dari subnet sementara ke MikroTik; pastikan `192.168.88.10` tidak bentrok, lalu sambungkan kabel dan verifikasi panel/DNS.
2. Catat paket dasar template VM 200; uji clone pertama dengan ID guest yang belum digunakan.
3. Uji enclosure single-bay dan satu HDD. Identifikasi disk sebelum memformat atau menentukan peran data/backup.
4. Verifikasi BIOS/MemTest86, sensor, firewall, backup, dan hasil uji per bab di `catatan/hasil-uji.md`.

## Masalah terbuka
- BIOS/MemTest86 RAM masih belum diperiksa.
- Jaringan host sementara `192.168.0.200/24`; rencana alamat rumah `192.168.88.10` belum diterapkan.
- Enclosure belum diuji; HDD belum terlihat oleh Proxmox, dan belum ada backup server.
- Template Debian 13 VM 200 dan CT 100 sudah dibuat. Paket dasar VM 200 belum dicatat; guest layanan dan hasil clone belum dilaporkan.
- Terapkan profil RAM 24 GB Bab 56 secara konservatif dan pantau penggunaan nyata.
- Guest layanan, firewall host, backup, dan pemulihan belum diuji pada M710q.

## Catatan sesi terakhir
- 30 Okt: buku lengkap disusun dari 75 sumber bab/lampiran/fase; PDF lengkap 235 halaman, ringkasan 32 halaman dipisahkan, dan edisi 300 halaman diarsipkan.
- 31 Okt: pengguna mengonfirmasi mini PC sudah tiba; RAM 8 GB × 2 awalnya, modul pertama diganti dengan 16 GB, sehingga kapasitas fisik diperkirakan 24 GB (16+8). SSD NVMe M.2 500 GB dipasang di slot M.2 1.
- 31 Okt: apt update awal gagal akibat DNS lama `192.168.88.253` tidak terjangkau dari jaringan sementara. DNS diubah ke `192.168.0.1`, update IPv4 berhasil, lalu GUI dist-upgrade selesai.
- 31 Okt: kernel `7.0.14-26-pve` aktif, tidak ada unit systemd gagal; RAM 23 GiB dan NVMe Samsung 476,9 GB terdeteksi.
- 31 Okt: VM gagal start karena VT-x mati; pengguna mengaktifkan VT-x lewat thinklmi tanpa monitor. Setelah reboot, `Virtualization: VT-x` dan `/dev/kvm` terverifikasi. VT-d tetap Disabled; lihat `docs/bab/REVISI-5.md`.
- 31 Okt: koneksi SSH Windows ke port 22 lulus dan fingerprint host cocok; autentikasi Codex belum disiapkan.
- 31 Okt: langkah berikut yang diminta pengguna adalah template VM dan CT tepat setelah update Proxmox; enclosure lama ditemukan tetapi belum diuji.
- 1 Nov: tangkapan layar Proxmox VE 9.2.24 menunjukkan CT 100 `Template-CT` dan VM 200 `Template-VM`. CT 100: 1 CPU, RAM 512 MiB, swap 512 MiB, disk 8 GiB. Host masih di `192.168.0.200`; persiapan menuju MikroTik `192.168.88.0/24` berlanjut. Buku edisi Terpadu 2026.11 dibangun ulang 258 halaman dengan renderer dan aset ilustrasi/tabel yang terpelihara di `tools/book_builder/`.
- 1 Nov: pengguna mengonfirmasi VM 200 dan CT 100 memakai Debian 13; paket yang dipasang ke VM 200 belum dicatat.
