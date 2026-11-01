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
- Audit clone menemukan host key SSH dan machine ID ikut tersalin pada template lama. Template CT 100 dan VM 200 sudah diganti dengan baseline bersih dan diuji melalui clone; seluruh clone/kandidat sementara telah dihapus. Inventaris final hanya memiliki CT 100 dan VM 200 sebagai template, keduanya berhenti.
- Guest layanan pertama dibuat dari template dan menyala: CT 101 `adguard2` (1 core, 512 MiB, DHCP `192.168.0.106`) dan VM 201 `docker-core` (2 core, 2048 MiB, disk 32 GiB, DHCP `192.168.0.107`). AdGuard Home v0.107.79 terpasang tetapi service disabled; Docker CE 29.9.2 dan Compose 5.6.1 terpasang dan daemon aktif, tanpa container aplikasi. IP target `.11` dan `.20` menunggu MikroTik.
- SSH baca-saja 1 November mengonfirmasi host masih memakai `192.168.0.200/24`, default gateway `192.168.0.1`, dan DNS `192.168.0.1`. Proxmox masih dibuka melalui router sementara. Konfigurasi rumah yang dituju: `192.168.88.10/24`, gateway `192.168.88.1`, DNS AdGuard `192.168.88.253`; perpindahan ke MikroTik belum diterapkan.

## Langkah berikutnya
1. Siapkan perubahan jaringan host dari subnet sementara ke MikroTik; pastikan `192.168.88.10` tidak bentrok, lalu sambungkan kabel dan verifikasi panel/DNS.
2. Pindahkan host ke MikroTik, pastikan DHCP reservation untuk MAC CT101/VM201 mengarah ke `.11`/`.20`, lalu periksa ulang akses.
3. Setelah IP final stabil, jalankan wizard AdGuard pada CT101 dan buat akun admin; pasang Portainer pada VM201 lalu atur kredensial admin sendiri.
4. Uji enclosure single-bay dan satu HDD. Identifikasi disk sebelum memformat atau menentukan peran data/backup.
5. Verifikasi BIOS/MemTest86, sensor, firewall, backup, dan hasil uji per bab di `catatan/hasil-uji.md`.

## Masalah terbuka
- BIOS/MemTest86 RAM masih belum diperiksa.
- Jaringan host sementara `192.168.0.200/24`; rencana alamat rumah `192.168.88.10` belum diterapkan.
- Enclosure belum diuji; HDD belum terlihat oleh Proxmox, dan belum ada backup server.
- Paket tambahan di VM 200 belum dicatat. Enclosure dan HDD belum diuji. AdGuard belum dikonfigurasi; Portainer/Caddy dan stack layanan belum dipasang. Firewall layanan, backup, dan pemulihan belum disiapkan.
- Terapkan profil RAM 24 GB Bab 56 secara konservatif dan pantau penggunaan nyata.
- Firewall guest, backup, dan pemulihan belum diuji pada M710q.

## Catatan sesi terakhir
- 30 Okt: buku lengkap disusun dari 75 sumber bab/lampiran/fase; PDF lengkap 235 halaman, ringkasan 32 halaman dipisahkan, dan edisi 300 halaman diarsipkan.
- 31 Okt: pengguna mengonfirmasi mini PC sudah tiba; RAM 8 GB × 2 awalnya, modul pertama diganti dengan 16 GB, sehingga kapasitas fisik diperkirakan 24 GB (16+8). SSD NVMe M.2 500 GB dipasang di slot M.2 1.
- 31 Okt: apt update awal gagal akibat DNS lama `192.168.88.253` tidak terjangkau dari jaringan sementara. DNS diubah ke `192.168.0.1`, update IPv4 berhasil, lalu GUI dist-upgrade selesai.
- 31 Okt: kernel `7.0.14-26-pve` aktif, tidak ada unit systemd gagal; RAM 23 GiB dan NVMe Samsung 476,9 GB terdeteksi.
- 31 Okt: VM gagal start karena VT-x mati; pengguna mengaktifkan VT-x lewat thinklmi tanpa monitor. Setelah reboot, `Virtualization: VT-x` dan `/dev/kvm` terverifikasi. VT-d tetap Disabled; lihat `docs/bab/REVISI-5.md`.
- 31 Okt: koneksi SSH Windows ke port 22 lulus dan fingerprint host cocok; autentikasi Codex belum disiapkan.
- 31 Okt: langkah berikut yang diminta pengguna adalah template VM dan CT tepat setelah update Proxmox; enclosure lama ditemukan tetapi belum diuji.
- 1 Nov: tangkapan layar Proxmox VE 9.2.24 menunjukkan CT 100 `Template-CT` dan VM 200 `Template-VM`. CT 100: 1 CPU, RAM 512 MiB, swap 512 MiB, disk 8 GiB. Host masih di `192.168.0.200`; persiapan menuju MikroTik `192.168.88.0/24` berlanjut. Buku edisi Terpadu 2026.11 dibangun ulang 259 halaman dengan renderer dan aset ilustrasi/tabel yang terpelihara di `tools/book_builder/`.
- 1 Nov: pengguna mengonfirmasi VM 200 dan CT 100 memakai Debian 13; paket VM belum dicatat. Clone menemukan host key SSH dan machine ID VM yang ikut tersalin. Template CT 100 dan VM 200 diperbaiki, diuji melalui clone, lalu seluruh guest uji dihapus; inventaris kembali hanya berisi dua template.
- 1 Nov: dibuat CT 101 `adguard2` dan VM 201 `docker-core` dari template bersih. Keduanya boot dengan DHCP router sementara; host key SSH CT baru, QEMU Guest Agent VM aktif, dan hostname VM diubah sesuai plan. Aplikasi belum dipasang; IP final menunggu MikroTik.
- 1 Nov: dependensi curl terpasang; AdGuard Home v0.107.79 dipasang dari rilis resmi pada CT101 lalu servicenya dinonaktifkan sementara agar wizard admin tidak terbuka di jaringan sementara. Docker CE 29.9.2 dan Compose v5.6.1 dipasang dari repository resmi pada VM201; daemon aktif dan belum ada container aplikasi.
