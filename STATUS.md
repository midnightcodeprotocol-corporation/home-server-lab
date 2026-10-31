# STATUS (perbarui setiap sesi)

**Terakhir diperbarui:** 31 Oktober 2026

## Posisi sekarang
- Jaringan rumah memakai MikroTik `192.168.88.1`, STB AdGuard `192.168.88.253`, dan perangkat lain sesuai inventaris. Server saat ini **belum tersambung ke jaringan MikroTik** karena pengguna sedang berada di lokasi lain.
- Lenovo ThinkCentre M710q menjalankan Proxmox VE. CPU Intel Core i5-6500T (4 core/4 thread).
- RAM terpasang 16 GB + 8 GB. Linux Proxmox melaporkan **23 GiB** total; pemeriksaan BIOS dan MemTest86 belum dicatat.
- NVMe Samsung MZALQ512HALU-000L2 terdeteksi sebagai `nvme0n1`, ukuran **476,9 GB** (kapasitas pemasaran 512 GB / sekitar 500 GB).
- Setelah pembaruan dan reboot, kernel aktif **`7.0.14-26-pve`**. `systemctl --failed` melaporkan `0 loaded units listed`.
- Storage Proxmox `local` (dir) dan `local-lvm` (lvmthin) aktif. `local-lvm` masih kosong pada saat diperiksa, dengan sekitar 348 GiB tersedia. Belum ada VM atau container yang dibuat.
- Komputer Windows pengguna `192.168.0.100` berhasil menjangkau TCP port 22 pada Proxmox `192.168.0.200` (`Test-NetConnection`, 31 Okt). Fingerprint host cocok dan sudah dikonfirmasi. SSH dari terminal Codex mencapai autentikasi tetapi ditolak karena belum ada kunci/identitas yang terdaftar (`Permission denied (publickey,password)`); belum ada perintah yang dijalankan di server.\n- Konfigurasi jaringan sementara: `vmbr0` pada `192.168.0.200/24`, gateway dan DNS `192.168.0.1`. Target jaringan rumah setelah kembali ke MikroTik: `192.168.88.0/24`; alamat rencana server `192.168.88.10` perlu diterapkan dan diuji saat berada di jaringan itu.
- Dua HDD Seagate Surveillance 2 TB, 3,5 inci belum tersambung ke server. Pengguna menemukan enclosure single-bay lama, tetapi belum menguji apakah enclosure berfungsi; HDD berada di rumah. Belum ada backup server.
- Buku lengkap 235 halaman tersedia. Uji panduan pada M710q baru dimulai; seluruh bab dan layanan belum diuji.

## Progres dan kendala yang sudah ditangani
- `apt-get update` awal gagal mengambil Debian/Proxmox karena DNS menunjuk ke `192.168.88.253`, yang tidak terjangkau dari jaringan sementara `192.168.0.0/24`. Akses internet berdasarkan alamat IP tetap berhasil.
- DNS host diganti ke `192.168.0.1`; `getent hosts deb.debian.org` kemudian berhasil.
- `apt-get -o Acquire::ForceIPv4=true update` berhasil mengambil indeks Debian Trixie dan Proxmox.
- Pembaruan melalui menu Proxmox selesai: 193 paket diperbarui, 2 paket baru dipasang, 0 paket dihapus. Setelah reboot, kernel baru aktif dan tidak ada unit systemd gagal.

## Langkah berikutnya
1. Saat kembali di rumah, sambungkan server ke MikroTik dan verifikasi akses web/SSH pada jaringan rumah. Terapkan alamat server yang direncanakan hanya setelah rute, gateway, DNS, serta pemakaian NIC dipastikan.
2. Sebelum VM/LXC diberi alamat statis, putuskan skema alamat final; sementara ini DHCP lebih mudah bila guest dibuat di jaringan sementara.
3. Uji enclosure single-bay dengan satu HDD. Identifikasi model, serial, ukuran, partisi, dan kondisi disk sebelum memformat atau mengubah apa pun.
4. Tentukan apakah satu HDD akan menjadi storage data atau tujuan backup. Uji backup dan pemulihan sebelum menganggap backup tersedia.
5. Setelah jaringan dan storage dasar diputuskan, buat guest awal di `local-lvm`; jangan mengalokasikan seluruh kapasitas NVMe.
6. Catat hasil bab yang benar-benar diuji di `catatan/hasil-uji.md`. BIOS/MemTest86, firewall, layanan, dan pemulihan masih perlu diuji.

## Hal yang masih perlu diperiksa
- BIOS dan MemTest86 untuk RAM 16+8 GB.
- Isi lengkap `/etc/network/interfaces` dan port fisik yang benar-benar digunakan. Catatan sebelumnya menunjukkan `vmbr0` menjembatani `enp0s31f6` dan `eno1`; jangan mengubahnya dari jauh sebelum topologi kabel diketahui.
- Migrasi dari jaringan sementara `192.168.0.0/24` ke MikroTik `192.168.88.0/24`.
- Enclosure belum diuji; HDD belum terlihat oleh Proxmox, belum ada uji SMART, dan peran kedua HDD belum ditetapkan.
- Belum ada VM/LXC, backup, Tailscale, PBS, atau layanan proyek yang berjalan pada host ini.

## Catatan sesi terakhir
- 30 Okt: buku lengkap disusun dari 75 sumber bab/lampiran/fase; PDF lengkap 235 halaman, ringkasan 32 halaman dipisahkan, dan edisi 300 halaman diarsipkan.
- 31 Okt: Proxmox berhasil diperbarui dan reboot. Pemeriksaan menunjukkan RAM 23 GiB, NVMe Samsung 476,9 GB, storage `local` dan `local-lvm` aktif, serta tidak ada unit gagal.
- 31 Okt: pengguna menjelaskan bahwa jaringan `192.168.0.0/24` hanya sementara sampai kembali ke MikroTik. Enclosure lama ditemukan, belum diuji, dan akan diperiksa setelah tiba di rumah.
