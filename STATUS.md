# STATUS (perbarui setiap sesi)

**Terakhir diperbarui:** 31 Oktober 2026

## Posisi sekarang
- Jaringan rumah memakai MikroTik, access point, dan STB AdGuard. Server masih memakai jaringan sementara `192.168.0.200/24` sampai kembali tersambung ke MikroTik.
- Mini PC server **Lenovo ThinkCentre M710q** sudah tersedia (Intel Core i5-6500T, 4 core/4 thread).
- RAM 16 GB + 8 GB terpasang; Linux Proxmox melaporkan **23 GiB**. BIOS dan MemTest86 belum diperiksa.
- NVMe Samsung MZALQ512HALU-000L2 terdeteksi sebagai `nvme0n1` berukuran **476,9 GB**; Proxmox berjalan.
- Dua HDD Seagate Surveillance 2 TB, 3,5 inci belum dipasang. Enclosure single-bay lama ditemukan, belum diuji, dan berada di rumah bersama HDD.
- Proxmox selesai diperbarui dan reboot: kernel `7.0.14-26-pve`; `systemctl --failed` melaporkan nol unit gagal. Storage `local` dan `local-lvm` aktif; belum ada VM/LXC, template, Tailscale, PBS, atau backup.
- VT-x/KVM aktif setelah perbaikan BIOS tanpa monitor melalui `thinklmi`; setelah reboot `lscpu` menunjukkan `Virtualization: VT-x` dan `/dev/kvm` tersedia. VT-d tetap `Disabled`.
- Windows `192.168.0.100` berhasil menjangkau TCP 22 pada host `192.168.0.200`. Fingerprint ED25519 cocok; autentikasi SSH dari Codex belum ada, dan tidak ada perintah host dijalankan lewat Codex.
- Buku dan catatan lokal diselaraskan dengan progres terverifikasi sampai 31 Oktober: Revisi 5 mencatat kasus thinklmi dan menempatkan template VM 9100 serta CT 9200 setelah update host dan pemeriksaan KVM, sebelum guest layanan. Template dan layanan belum dibuat atau diuji.

## Langkah berikutnya
1. Sesudah update Proxmox dan verifikasi KVM, buat template VM 9100 dan CT 9200 sesuai Bab 49; kemudian clone guest dengan nama/IP/resource unik.
2. Saat kembali di rumah, pindahkan host ke MikroTik dan tetapkan jaringan/IP manajemen final.
3. Uji enclosure single-bay dan satu HDD. Identifikasi disk sebelum memformat atau menentukan peran data/backup.
4. Verifikasi BIOS/MemTest86, sensor, firewall, dan hasil uji per bab di `catatan/hasil-uji.md`.

## Masalah terbuka
- BIOS/MemTest86 RAM masih belum diperiksa.
- Jaringan host sementara `192.168.0.200/24`; rencana alamat rumah `192.168.88.10` belum diterapkan.
- Enclosure belum diuji; HDD belum terlihat oleh Proxmox, dan belum ada backup server.
- Template VM 9100 dan CT 9200 belum dibuat.
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
