# Revisi 9: fondasi AdGuard dan Docker

**Tanggal:** 1 November 2026

## CT 101 `adguard2`

- `curl` terpasang melalui APT Debian 13.
- Installer resmi AdGuard Home memasang rilis `v0.107.79` ke `/opt/AdGuardHome` dan membuat unit systemd `AdGuardHome`.
- Unit sengaja dihentikan dan dinonaktifkan sesudah pemasangan. Wizard awal tidak memakai akun sampai pemilik membuatnya; menahannya mencegah halaman setup terbuka di jaringan sementara.
- Belum ada DNS yang diarahkan ke CT101 dan belum ada konfigurasi AdGuard. Jalankan service setelah alamat final `192.168.88.11` dibuat melalui MikroTik, lalu selesaikan wizard dan buat kredensial admin.

## VM 201 `docker-core`

- Repository APT resmi Docker untuk Debian Trixie ditambahkan menggunakan keyring `/etc/apt/keyrings/docker.asc`.
- Docker Engine CE `29.9.2`, Docker CLI, containerd `2.4.2`, Buildx `0.38.1`, dan Compose plugin `5.6.1` terpasang.
- Service Docker aktif; daftar container masih kosong. Portainer, Caddy, monitoring, dan aplikasi lain belum dipasang.
- Direktori `/opt/stacks` dibuat dengan izin `0750` milik root; jaringan Docker internal `proxy` dibuat untuk Caddy dan container terkait. Jaringan ini belum dipakai container mana pun dan tidak memublikasikan port.
- Pasang Portainer setelah VM mendapat alamat final `192.168.88.20`, lalu buat admin password sendiri segera setelah membuka wizard awal. Jangan menyimpan password ke Git.

## Jaringan dan catatan

Host masih berada di router sementara `192.168.0.0/24`; CT101 mendapat `192.168.0.106`, VM201 `192.168.0.107`. IP final dan reservasi DHCP MikroTik belum dibuat. Pemeriksaan menunjukkan `/etc/default/locale` CT memakai `LANG=C`; peringatan `en_US.UTF-8` muncul dari lingkungan perintah administrasi dan tidak menghentikan instalasi.

Instruksi Docker mengikuti [dokumentasi resmi Docker untuk Debian](https://docs.docker.com/engine/install/debian/); binary AdGuard Home berasal dari installer di [repo resmi AdGuardTeam/AdGuardHome](https://github.com/AdguardTeam/AdGuardHome).
