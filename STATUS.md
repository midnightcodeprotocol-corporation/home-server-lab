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
- Audit clone menemukan host key SSH dan machine ID ikut tersalin pada template lama. Template CT 100 dan VM 200 sudah diganti dengan baseline bersih dan diuji melalui clone; seluruh clone/kandidat audit dihapus. Setelah itu CT101 dan VM201 dibuat sebagai guest layanan pertama.
- Guest layanan pertama dibuat dari template dan menyala: CT 101 `adguard2` (1 core, 512 MiB, DHCP `192.168.0.106`) dan VM 201 `docker-core` (2 core, 2048 MiB, disk 32 GiB; DHCP terakhir `192.168.0.102` setelah reboot). AdGuard Home v0.107.79 terpasang tetapi service disabled; Docker CE 29.9.2 dan Compose 5.6.1 terpasang dan daemon aktif, tanpa container aplikasi. IP target `.11` dan `.20` menunggu MikroTik.
- CT 104 `docker-services` dibuat dari template: Debian 13 unprivileged + nesting, 4 vCPU, RAM 8 GiB, swap 1 GiB, rootfs 64 GiB, DHCP sementara `192.168.0.104`. Docker Debian `26.1.5+dfsg1-9+deb13u1` dan Docker Compose `2.26.1-4` aktif. Portainer CE container berjalan pada HTTPS TCP 9443; wizard admin belum diselesaikan pengguna.
- Rencana layanan terbaru: Tailscale, Jellyfin, Portainer, Grafana, Immich, dan Home Assistant Container ditempatkan di CT104 secara bertahap. Prometheus dikeluarkan dari rencana pemasangan. Grafana/datasource yang sudah ada belum diverifikasi; Grafana memerlukan sumber data terpisah untuk menampilkan metrik.
- SSH baca-saja 1 November mengonfirmasi host masih memakai `192.168.0.200/24`, default gateway `192.168.0.1`, dan DNS `192.168.0.1`. Proxmox masih dibuka melalui router sementara. Konfigurasi rumah yang dituju: `192.168.88.10/24`, gateway `192.168.88.1`, DNS AdGuard `192.168.88.253`; perpindahan ke MikroTik belum diterapkan.

## Langkah berikutnya
1. Buka Portainer di `https://192.168.0.104:9443` dari LAN sementara dan buat akun administrator sendiri; jangan kirim kata sandinya ke chat atau repo.
2. Buat DHCP reservation/IP final CT104 di MikroTik sebelum jaringan rumah menjadi rujukan; semua IP `.0.x` saat ini bersifat sementara.
3. Lanjutkan pemasangan layanan di CT104 satu per satu. Tailscale hanya paket dahulu sampai kebutuhan akses TUN dan autentikasi dibahas; siapkan Jellyfin, Grafana bila belum tersedia, Immich, dan Home Assistant Container.
4. Prometheus tidak dipasang sesuai arahan pengguna. Grafana perlu datasource (misalnya Beszel atau alternatif yang dipilih) sebelum menampilkan metrik.
5. Uji enclosure single-bay dan satu HDD. Identifikasi disk sebelum memformat atau menentukan peran data/backup.
6. Verifikasi BIOS/MemTest86, sensor, firewall, backup, dan hasil uji per bab di `catatan/hasil-uji.md`.

## Masalah terbuka
- BIOS/MemTest86 RAM masih belum diperiksa.
- Jaringan host sementara `192.168.0.200/24`; rencana alamat rumah `192.168.88.10` belum diterapkan.
- Enclosure belum diuji; HDD belum terlihat oleh Proxmox, dan belum ada backup server.
- Wizard admin Portainer pada CT104 belum diselesaikan; Tailscale, Jellyfin, Grafana, Immich, dan Home Assistant belum diverifikasi/dipasang. Enclosure dan HDD belum diuji. AdGuard belum dikonfigurasi. IP final MikroTik, firewall layanan, backup, dan pemulihan belum disiapkan.
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
- 1 Nov: setelah tangkapan layar menunjukkan pesan AF_VSOCK berulang, ditemukan systemd 257.13 pada Debian 13. `systemd.ssh_auto=no` diterapkan ke GRUB VM201 karena socket SSH vsock/Unix opsional tidak digunakan. VM reboot bersih; hostname `docker-core`, SSH TCP, Docker, dan jaringan terverifikasi. Pesan AF_VSOCK tidak muncul pada boot baru. DHCP VM berubah dari `.107` ke `.102`; alamat masih dinamis.
- 1 Nov: sesuai arahan untuk mengurangi jumlah VM, dibuat CT104 `docker-services` sebagai CT unprivileged dengan nesting (telah disetujui pengguna), 4 vCPU, RAM 8 GiB, swap 1 GiB, rootfs 64 GiB, DHCP sementara `192.168.0.104`. Docker Debian dan Compose aktif; Portainer CE `lts` berjalan dan memublikasikan TCP 9443. Setup akun admin masih menunggu pengguna. Prometheus tidak dipasang; status Grafana/datasource belum diverifikasi.
