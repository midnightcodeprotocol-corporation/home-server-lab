# Hasil uji per fase

## Lanjutan konfigurasi layanan — 3 November 2026

- **Catatan tindak lanjut:** Pengguna meminta dua topik dilewati dahulu dan diingatkan nanti: menghubungkan share Samba ke Nextcloud memakai SMB/CIFS external storage, serta mengakses share Samba dari Android/iPhone. Belum ada konfigurasi yang diubah; waktu pengingat belum ditentukan.
- **Lulus konfigurasi, menunggu eksekusi penuh:** Audit awal menunjukkan `/cluster/backup` kosong; dibuat job `home-lab-daily`: schedule `daily` (00.00 WIB, zona `Asia/Jakarta`), guest 101,102,103,104,202, storage `pbs-store1`, mode snapshot, ZSTD, retention `keep-last=7`; API mengonfirmasi next-run `2026-11-04 00:00:00 WIB`. Setelah backup uji CT101, PBS terpakai 8.84% (8.65 GiB dari 97.8 GiB). VM212 PBS tidak dimasukkan. Bind mount CT102 (`/srv/media`, `/srv/files`) dan CT104 (`/srv/media`, `/srv/appdata`) terkonfirmasi `backup=0`, jadi data HDD tidak dicakup backup guest.
- **Enkripsi backup:** Storage `pbs-store1` awalnya tidak memiliki `encryption-key`, sehingga backup manual terdahulu tidak terenkripsi sisi klien. Enkripsi sisi klien kini diaktifkan memakai key autogen khusus integrasi PVE; file kunci tetap di `/etc/pve/priv/storage/pbs-store1.enc`. Pengguna mengonfirmasi paperkey disimpan ke password manager dan file paperkey sementara sudah dihapus dari host. Backup uji CT101 terenkripsi sukses dan terlihat di PBS; backup harian penuh serta uji restore masih pending.
- **Lulus:** Setelah pengguna mengonfirmasi paperkey tersimpan di password manager, file paperkey sementara di host dihapus. `vzdump 101 --storage pbs-store1 --mode snapshot --compress zstd` selesai `Backup job finished successfully`; log menyatakan `--crypt-mode=encrypt`, `Encrypting backup with key fingerprint`, dan backup 716.939 MiB diproses (243.986 MiB terkompresi). `pvesm list` menampilkan arsip CT101 bertanggal `2026-11-03T13:49:20Z`; PBS terpakai 8.84%. Jadwal otomatis berikutnya tetap 4 Nov 2026 pukul 00.00 WIB. Uji restore ke CT sementara dicatat pada butir berikutnya.
- **Lulus — uji restore:** Arsip terenkripsi CT101 `2026-11-03T13:49:20Z` dipulihkan ke CT109 sementara pada `local-lvm` menggunakan `pct restore` dan opsi `--unique 1`. Sebelum boot, NIC CT109 diubah ke `ip=manual,link_down=1` agar IP statis `.11` tidak aktif. CT109 boot, `systemctl is-active AdGuardHome` mengembalikan `active`, dan `curl http://127.0.0.1/` menghasilkan HTTP 302. CT109 dihentikan lalu dihapus; volume `vm-109-disk-0` terhapus; CT101 asli tetap running. Ini menguji restore dan startup layanan lokal, tetapi bukan uji seluruh CT/backup VM.
- **Lulus sebagian:** Pemeriksaan terbaru Immich menunjukkan `/srv/media/immich` sekitar 13 GiB dan 6.710 aset pada tabel database. Penyelesaian unggahan ponsel belum dikonfirmasi; backup media tetap ditunda sampai selesai, dump DB baru, dan pemeriksaan ruang tersedia.

- **Lulus:** Audit Proxmox melalui SSH baca-saja menampilkan CT101, CT102, CT103, CT104, VM202, dan VM212 running; CT100/VM200 template stopped, VM201 stopped. Host RAM 23 GiB, tersedia sekitar 18 GiB saat pemeriksaan; `local`, `local-lvm`, dan HDD `backup-disk` aktif.
- **Lulus:** CT104 diatur ke statis `192.168.88.20/24` pada config Proxmox; ping dari PVE berhasil. Portainer HTTPS `.20:9443` HTTP 200; Jellyfin `.20:8096` healthy. HDD mount `/srv/media` dan `/srv/appdata` masing-masing menunjukkan 1.8 TiB total, sekitar 1.7 TiB bebas.
- **Lulus sebagian:** CT102 `.12` menjalankan Samba 4.22.11; `smbd`, `nmbd` aktif dan `testparm` valid. Share `Media` dan `Files` mengarah ke `/srv/media` dan `/srv/files`. Pengguna melaporkan password Samba untuk `labshare` sudah ditetapkan; uji autentikasi klien Windows belum dilakukan.
- **Lulus sebagian:** CT103 dibuat dari template Debian 13, memperoleh lease DHCP sementara `.104` (bukan alamat final), `onboot=1`. Tailscale 1.104.4 aktif; `/dev/net/tun` tersedia; `net.ipv4.ip_forward=1` dan `net.ipv6.conf.all.forwarding=1`. `tailscale up --advertise-routes=192.168.88.0/24 --accept-dns=false` memberikan tautan autentikasi; node logout sampai pengguna login dan menyetujui subnet route.
- **Lulus sebagian:** PBS VM212 `.30` ping 2/2 dan HTTPS 8007 HTTP 200 dari PVE. `onboot=1` kini aktif. Disk 100 GiB `local-lvm` terpasang sebagai `scsi1`; volume lama 1.5 TiB pada HDD masih detached dan file disimpan. `store1` dilaporkan pengguna, tetapi belum diverifikasi dari dalam PBS; belum ada backup/restore.
- **Dalam proses:** Compose dan `.env` Immich resmi disimpan di `/opt/stacks/immich`; foto diarahkan ke `/srv/media/immich`, database ke `/opt/immich/postgres` di SSD lokal CT, `TZ=Asia/Jakarta`, password database dibuat acak dan `.env` mode 0600. Compose lulus `docker compose config --quiet`; penarikan image berjalan dan belum ada container/UI yang dinyatakan siap.
- **Catatan sumber:** Penempatan Immich mengikuti [panduan Docker Compose Immich](https://docs.immich.app/install/docker-compose/) dan kebutuhan penyimpanan database lokal/kapasitas RAM pada [persyaratan Immich](https://docs.immich.app/install/requirements/). Instal Tailscale dan persiapan subnet router mengikuti [dokumentasi instalasi Linux](https://tailscale.com/docs/install/linux) serta [setup subnet router](https://tailscale.com/docs/features/subnet-routers/how-to/setup).

### Pembaruan kondisi akhir — 3 November 2026

- **Uptime Kuma:** Compose resmi dipasang di CT104 pada `/opt/stacks/uptime-kuma`; image `louislam/uptime-kuma:2` berjalan sebagai versi 2.5.9, data di direktori persisten `data`, bind hanya `192.168.88.20:3001`. Log aplikasi menyatakan menunggu aksi pengguna; GET HTTP memberi 302 ke `/setup-database`. Pembuatan akun admin belum dilakukan pengguna.
- **Lulus:** Immich di CT104 menampilkan seluruh empat container (`immich_server`, `immich_postgres`, `immich_machine_learning`, `immich_redis`) healthy; API tersedia di `http://192.168.88.20:2283`. Upload di HDD `/srv/media/immich`, DB di SSD `/opt/immich/postgres`.
- **Lulus menurut laporan pengguna:** Nextcloud 35.0.2.2 di CT104; MariaDB dan Redis sehat. `php occ status` menunjukkan `installed: true`, `maintenance: false`, `needsDbUpgrade: false`; `status.php` merespons JSON berhasil. UI `http://192.168.88.20:8080`; admin awal `labadmin`, password awal pernah disimpan di file mode 0600 pada `/opt/stacks/nextcloud/secrets/nextcloud_admin_password`. Pada 3 Nov pengguna melaporkan login awal, penggantian password, login ulang, serta uji upload/download satu berkas berhasil. Pengujian tersebut belum diverifikasi langsung oleh Codex dan belum diuji dari jaringan luar/klien ponsel. Data Nextcloud `/srv/appdata/nextcloud-data` berada di HDD, database `/opt/stacks/nextcloud/db` pada SSD.
- **Lulus sebagian:** Tailscale CT103 sudah login dan online; `tailscale status --json` menunjukkan `PrimaryRoutes: [192.168.88.0/24]`, Health kosong, forwarding v4/v6 aktif. Uji koneksi dari laptop/HP melalui jaringan luar rumah belum dilakukan. Lease LAN `.104` tetap DHCP dinamis.
- **Belum dikerjakan:** Samba CT102 masih tanpa password Samba untuk `labshare`; SMB daemon dan dua share aktif, tetapi uji dari Windows belum dilakukan. Samba tidak menyediakan web UI; akses langsung melalui File Explorer. Nextcloud menyediakan antarmuka web terpisah pada port 8080.
- **Catatan desain:** Data Nextcloud disimpan terpisah dari share Samba agar perubahan langsung melalui SMB tidak memodifikasi isi internal Nextcloud di luar cache/database-nya. Nextcloud mendukung SMB sebagai external storage, tetapi perlu konfigurasi dan pemindaian perubahan; lihat [dokumentasi external storage SMB/CIFS](https://docs.nextcloud.com/server/stable/admin_manual/configuration_files/external_storage/smb.html).

## Lanjutan pemasangan layanan — 2 November 2026

- **Lulus:** CT101 `adguard2` diubah menjadi `192.168.88.11/24`, gateway `192.168.88.1`, resolver `192.168.88.3`, dan `onboot=1`; CT berhasil start dan interface menunjukkan alamat `.11`.
- **Lulus sebagian:** `AdGuardHome.service` CT101 aktif; port TCP 3000 terbuka dan `curl http://192.168.88.11:3000/` mengembalikan HTTP 302 ke wizard saat pemeriksaan awal; status setelah wizard dan hasil DNS terbaru tercatat di bagian uji DNS CT101. DHCP MikroTik tetap membagikan DNS `.3` saja.
- **Lulus:** Jellyfin dipasang pada CT104 memakai image resmi `ghcr.io/jellyfin/jellyfin:latest`, digest `sha256:fea863d0cd9ec445985d9c75fc6ed64e38a1d2766cf0c250a33d553f4fc1b771`. Setelah konfigurasi awal terikat lease `.101`, container dibuat ulang dengan volume konfigurasi/cache yang sama dan port host `8096` tidak lagi terikat ke satu IP; sekarang `0.0.0.0:8096` dan `:::8096`. Container kembali healthy, log `Core startup complete`, ffmpeg tersedia, dan HTTP `.101:8096` merespons 302 ke `/web/`. `/srv/media` tetap kosong/read-only karena HDD dilepas.
- **Lulus sebagian:** Image HAOS 18.4 diunduh dari rilis resmi; checksum SHA256 `756ec485b1b153099ca53e88a5eebd63a801d56b791afe5c6d63ef94a35dc02d` cocok dengan `SHA256SUMS`. QCOW2 valid dan disk virtual 32 GiB. VM202 dibuat UEFI/q35, 2 vCPU, RAM 2048 MiB, disk 32 GiB di local-lvm, VirtIO NIC di vmbr0, onboot=1; status running. Paket dari MAC VM `BC:24:11:60:7C:42` menunjukkan alamat DHCP `.102`; ping 2/2 lulus. `http://192.168.88.102:8123/` mengembalikan 307 ke `http://192.168.88.102/`, dan `http://192.168.88.102/onboarding.html` merespons HTTP 200. QEMU Guest Agent belum aktif. Onboarding admin masih menunggu pengguna.
- **Catatan admin:** Pengguna melaporkan wizard beberapa layanan selesai; tetapi pemeriksaan langsung CT101 pada 2 Nov membuktikan installer AdGuard Home masih terbuka, sehingga status teknis CT101 mengikuti hasil uji tersebut. Setup Jellyfin dan Home Assistant tetap menurut laporan pengguna. Portainer dilanjutkan setelah restart memakai setup token dari log; pengguna memilih Skip untuk Edge Compute dan melaporkan wizard setup selesai. Kata sandi tidak ditangani/dicatat oleh Codex.
- **Belum dikerjakan:** MikroTik SSH tetap tidak bisa dipakai, WinBox automation sebelumnya tidak berhasil; belum ada reservasi DHCP untuk CT104, belum ada perubahan DNS DHCP. Immich menunggu disk data/HDD unit 2; pengguna ingin kedua HDD untuk aplikasi dan menunda backup; Tailscale memerlukan autentikasi akun; Grafana belum memiliki datasource, Prometheus tidak dipasang.
- **Pengecekan akhir 2 Nov (sebelum setup Portainer selesai):** CT101 tetap running/onboot=1 `.11`, AdGuard service `active`; CT104 running, Portainer HTTPS `.101:9443` 307, Jellyfin healthy `.101:8096` 302; VM202 running, ping lease `.102` 2/2, onboarding `/onboarding.html` HTTP 200.
- **Pengecekan setelah setup Portainer dan lease HAOS — 2 Nov:** CT104 `.101` masih aktif. Portainer CE `2.45.3` berjalan, HTTPS UI `/` HTTP 200, `/api/status` HTTP 200; pengguna menyatakan setup selesai. HAOS MAC `BC:24:11:60:7C:42` sebelumnya terlihat pada `.102`; sesudah pengguna membuat lease target, neighbor table menunjukkan `.21`, HTTP `http://192.168.88.21/onboarding.html` HTTP 200, dan `.102` timeout. Pengguna menyatakan wizard HA selesai. Reservasi DHCP CT104 belum dapat diverifikasi langsung di MikroTik.

Isi setiap kali satu bab selesai diuji. Tulis pesan error persis dan bab yang perlu direvisi.

Status: **pengujian panduan di ThinkCentre M710q sedang berlangsung**. Pemeriksaan dasar host dan KVM sudah berhasil. Hasil uji sebelumnya di lab VMware ada di `kasus-nyata-lab.md` dan tidak membuktikan instalasi pada mesin ini.

| Fase | Bagian / Bab | Tanggal | Lulus? | Catatan / error | Revisi buku |
|---|---|---|---|---|---|
| 1 | Keamanan dan Tailscale (25-26) | | | | |
| 2 | Mesin M710q: RAM, BIOS, instal Proxmox (6, 8, 9, 27, 28, 30) | 31 Okt–1 Nov 2026 | Parsial | Proxmox update/reboot, KVM, dan pembuatan template lulus secara tampilan; BIOS/MemTest, jaringan rumah, HDD, clone, serta layanan belum diuji. | Revisi 5–6 |
| 3 | Monitoring (31-34) | | | | |
| 4 | Caddy dan sertifikat lokal (35-38) | | | | |
| 5 | Web, WordPress, n8n, tunnel (39-43) | | | | |
| 6 | Vaultwarden, AFFiNE, Nextcloud (44-47) | | | | |
| 7 | Peta, templat, PBS, firewall, audit (48-52) | | | | |
| 8 | Navidrome (53) | | | | |
| 9 | Pocket ID, Immich, profil RAM (54-56) | | | | |

Uji Proxmox dan jaringan lebih dulu. Setelah itu uji Tailscale (Bab 26) dan Caddy (Bab 36-37); bagian 5 ke atas bergantung pada keduanya.

## Templat catatan per langkah

```text
Bab: <nomor>   Tanggal: <tanggal>
Langkah: <nomor/uraian>
Hasil: lulus | gagal | perlu revisi
Pesan error (persis): <salin>
Butir [BELUM PASTI] terjawab: <ya/tidak, jawabannya>
Penyimpangan dari buku: <catat>
```

## Kasus nyata: VT-x/KVM dan BIOS Lenovo tanpa monitor - 31 Oktober 2026

Bab terkait: 8, 11, 24, 27.5. Hasil: **gagal, kemudian diperbaiki**; perubahan panduan tercatat di `docs/bab/REVISI-5.md`.

- Pesan saat VM start: `TASK ERROR: KVM virtualisation configured, but not available. Either disable in VM configuration or enable in BIOS.`
- Sebelum perbaikan, `lscpu | grep -i virtualization` kosong dan `/dev/kvm` tidak ada.
- Pengguna tidak memiliki monitor untuk membuka BIOS lokal. Host menyediakan direktori `thinklmi` di `/sys/class/firmware-attributes/`.
- Atribut yang terlihat: `Intel(R) Virtualization Technology` dan `VT-d`. Nilai awal VT-x `Disabled`; pilihan valid `Disabled;Enabled`.
- Pengguna mengaktifkan hanya Intel Virtualization Technology melalui `thinklmi`, lalu reboot. `VT-d` sengaja tetap `Disabled` karena PCI passthrough belum dibutuhkan.
- Setelah reboot, `lscpu | grep -i virtualization` menampilkan `Virtualization: VT-x`; `/dev/kvm` ada (`crw-rw---- 1 root kvm 10, 232 ...`).
- Ketidakpastian: output `save_settings` tidak dicatat. Perubahan terbukti bertahan setelah reboot pada unit ini, tetapi kebutuhan `save_settings` di unit/BIOS lain belum dipastikan. Lihat `catatan/belum-pasti.md`.

## Pemeriksaan host Proxmox dan DNS update - 31 Oktober 2026

- Kernel aktif setelah pembaruan dan reboot: `7.0.14-26-pve`; `systemctl --failed` menghasilkan `0 loaded units listed`.
- `free -h`: RAM total `23Gi`, tersedia `21Gi`, swap `8Gi`. BIOS dan MemTest86 belum dicek.
- `lsblk`: `nvme0n1 476.9G SAMSUNG MZALQ512HALU-000L2 nvme`.
- `pvesm status`: `local` dan `local-lvm` aktif; local-lvm saat diperiksa belum digunakan.
- Jaringan sementara: `vmbr0` `192.168.0.200/24`, gateway `192.168.0.1`. DNS awal `192.168.88.253` tidak terjangkau dari subnet tersebut; ping ke `1.1.1.1` berhasil, tetapi resolusi nama gagal. Setelah DNS host diubah ke `192.168.0.1`, `getent hosts deb.debian.org` berhasil dan `apt-get -o Acquire::ForceIPv4=true update` sukses. Upgrade melalui GUI selesai (193 paket diperbarui, 2 paket baru, 0 dihapus).
- Keluaran jaringan aktual yang dikirim pengguna menunjukkan port `enp0s31f6` dan `eno1`; konfigurasi `vmbr0` menjembatani keduanya, dengan alamat host di bridge. Percakapan Gemini tentang perpindahan sistem dan nama interface ditinjau; rekomendasi generik yang belum diverifikasi tidak diterapkan.
- Windows `192.168.0.100` mencapai TCP 22 pada Proxmox `192.168.0.200`. Fingerprint ED25519 cocok; SSH Codex belum terautentikasi dan belum menjalankan perintah pada host.
- Pada 31 Oktober, VM/LXC dan template VM 200 atau CT 100 belum dibuat. Enclosure single-bay lama ditemukan tetapi belum diuji; HDD belum tersambung.

## Template Debian 13 - 1 November 2026

- Tangkapan layar Proxmox VE 9.2.24 menunjukkan VM 200 `Template-VM` dan CT 100 `Template-CT` pada node `pve`.
- Pengguna mengonfirmasi kedua template memakai Debian 13. CT 100 menampilkan 1 CPU, RAM 512 MiB, swap 512 MiB, dan disk boot 8 GiB.
- Paket tambahan pada VM 200 belum dicatat. Guest layanan dan uji clone belum dilaporkan.
- URL Proxmox yang terlihat masih memakai host sementara `192.168.0.200`; perpindahan jaringan ke MikroTik belum diterapkan.


## SSH baca-saja dan verifikasi template — 1 November 2026

Hasil: **SSH berhasil; audit baca-saja lulus.** Pengguna menambahkan kunci publik Codex ke akun `root`; tidak ada private key, passphrase, atau isi `authorized_keys` yang dicatat. Perintah hanya membaca versi, daftar guest, konfigurasi template, storage, dan jaringan.

- `hostname`: `pve`; Proxmox VE `9.2.24`, kernel aktif `7.0.14-26-pve`.
- VM 200: `stopped`, `template: 1`, Debian 13 menurut pengguna; nama konfigurasi `Tamplate-VM` (kemungkinan typo), 1 vCPU, RAM 2048 MiB, disk 32 GiB pada `local-lvm`, QEMU Guest Agent aktif pada konfigurasi, bridge `vmbr0`, firewall aktif. Isi paket guest belum diperiksa karena template berhenti.
- CT 100: `stopped`, `template: 1`, Debian 13 menurut pengguna; nama `Tamplate-CT` (kemungkinan typo), 1 vCPU, RAM 512 MiB, swap 512 MiB, disk 8 GiB pada `local-lvm`, unprivileged, nesting aktif, DHCP pada `vmbr0`, firewall aktif.
- `qm list` dan `pct list` hanya menunjukkan template 200 dan 100; clone/guest layanan belum ada.
- Host: `vmbr0` `192.168.0.200/24`, gateway `192.168.0.1`, DNS `192.168.0.1`. Perpindahan ke MikroTik dan alamat target `192.168.88.10` belum dilakukan.
- Storage `local` dan `local-lvm` aktif; penggunaan `local-lvm` sekitar 1.09% pada saat audit. HDD belum tersambung.

Tidak ada perubahan konfigurasi Proxmox yang dijalankan oleh Codex pada sesi ini. Nama `Tamplate-*` belum diperbaiki.

## Audit identitas template dan uji clone - 1 November 2026

Hasil: **clone boot dan lulus pemeriksaan jaringan/identitas; template akhir CT 100 dan VM 200 sudah diperbaiki.**

- Clone awal CT 991 dari CT 100 dan VM 990/201 dari VM 200 menampilkan fingerprint ED25519 yang sama dengan template. Ini menunjukkan host key ikut tersalin.
- Perbaikan memasang drop-in ssh.service yang membuat ssh-keygen -A berjalan sebelum sshd -t.
- VM memiliki dua file machine ID, /etc/machine-id dan /var/lib/dbus/machine-id. Mengosongkan file pertama saja tidak cukup. Setelah keduanya dikosongkan dan path D-Bus dijadikan symlink, Debian menghasilkan machine ID unik saat boot.
- CT 102: boot lulus, DHCP 192.168.0.105/24, gateway 192.168.0.1, DNS deb.debian.org berhasil, SSH aktif, fingerprint baru.
- VM 204: Debian 13, boot lulus, DHCP 192.168.0.106/24, DNS berhasil, QEMU Guest Agent dan SSH aktif, fingerprint serta machine ID baru.
- Uji memakai router sementara 192.168.0.0/24. CT 102, VM 204, dan seluruh salinan perantara kemudian dihapus.
- Template CT 100 dan VM 200 dibuat ulang dari salinan bersih, dikembalikan ke ID semula, dan diverifikasi stopped/template=1. Tidak ada guest uji yang tersisa.
- Paket VM, jaringan MikroTik, guest layanan, backup, dan HDD belum diuji.

## Pembuatan guest pertama dari template — 1 November 2026

- CT 101 `adguard2` berhasil dibuat dari CT 100, menyala, memakai 1 core, RAM 512 MiB, swap 512 MiB, disk 8 GiB, dan mendapat DHCP sementara `192.168.0.106/24`.
- VM 201 `docker-core` berhasil dibuat dari VM 200, menyala, memakai 2 core, RAM 2048 MiB, disk 32 GiB, QEMU Guest Agent aktif, dan mendapat DHCP sementara `192.168.0.107/24`.
- Hostname CT adalah `adguard2`; hostname VM disesuaikan dari `debian-docker` menjadi `docker-core`. Kedua guest berada di router sementara `192.168.0.0/24`; target rumah `.11` dan `.20` belum digunakan.
- Pada saat kedua guest pertama selesai dibuat, AdGuard Home dan Docker belum dipasang. Kelanjutannya dicatat di bagian fondasi layanan di bawah.

## Fondasi layanan CT101 dan VM201 — 1 November 2026

- CT101: dependensi `curl` terpasang; installer resmi AdGuard Home memasang rilis `v0.107.79` pada `/opt/AdGuardHome`. Unit `AdGuardHome` dibuat, lalu dinonaktifkan dan dihentikan agar wizard konfigurasi tanpa admin belum terbuka pada jaringan sementara.
- VM201: Docker Engine CE `29.9.2`, containerd `2.4.2`, Buildx `0.38.1`, dan Compose plugin `5.6.1` terpasang dari repository resmi Docker untuk Debian 13. Service Docker aktif; belum ada container aplikasi.
- Direktori `/opt/stacks` dengan izin `0750` milik root dan jaringan Docker `proxy` dibuat pada VM201; belum ada container atau port aplikasi yang dipublikasikan.
- `apt-get update` berhasil pada kedua guest melalui router sementara. CT mengeluarkan peringatan `en_US.UTF-8` dari lingkungan perintah administrasi; `/etc/default/locale` di CT mengatur `LANG=C`, jadi peringatan ini tidak menghentikan instalasi.
- Link sumber instalasi: [Docker Engine Debian](https://docs.docker.com/engine/install/debian/) dan [AdGuard Home resmi](https://github.com/AdguardTeam/AdGuardHome).

## Pesan AF_VSOCK pada konsol VM201 — 1 November 2026

- Screenshot konsol memperlihatkan `systemd-ssh-generator: Failed to query local AF_VSOCK CID: Cannot assign requested address` berulang. VM tidak gagal boot: systemd yang terpasang `257.13-1~deb13u1`, SSH biasa tetap aktif/listening di TCP 22, dan Docker aktif.
- Gejalanya cocok dengan isu Debian `systemd-ssh-generator` pada Debian 13/systemd 257.13. Generator ini menyediakan socket SSH opsional AF_VSOCK dan AF_UNIX; VM ini dikelola melalui jaringan TCP dan QEMU Guest Agent, bukan melalui socket tersebut.
- GRUB VM201 diatur ke `systemd.ssh_auto=no`; `update-grub` berhasil dan `/proc/cmdline` mengonfirmasi opsi aktif setelah VM dimatikan dan dinyalakan kembali secara bersih.
- Pasca-boot: hostname VM `docker-core`, SSH dan Docker `active`, Docker belum memiliki container, serta log boot tidak berisi pesan AF_VSOCK tersebut. CT101 juga tetap aktif; AdGuard tetap disabled.
- IP VM melalui DHCP sementara berubah dari `192.168.0.107` menjadi `192.168.0.102` setelah reboot. Jangan gunakan alamat ini sebagai IP tetap; tunggu reservasi DHCP MikroTik `.20`.
- Rujukan: [systemd-ssh-generator](https://www.freedesktop.org/software/systemd/man/latest/systemd-ssh-generator.html), [laporan Debian #1137216](https://bugs.debian.org/cgi-bin/bugreport.cgi?bug=1137216).

## Docker host CT104 dan Portainer — 1 November 2026

- CT104 `docker-services` diklon penuh dari CT100. Konfigurasi terverifikasi: Debian 13, unprivileged, nesting aktif, 4 vCPU, RAM 8192 MiB, swap 1024 MiB, rootfs 64 GiB, DHCP sementara `192.168.0.104/24`; CT menyala dan `onboot` aktif.
- `apt-get update` berhasil. Paket Debian `docker.io` (`26.1.5+dfsg1-9+deb13u1`), `docker-compose` (`2.26.1-4`), `curl`, dan `ca-certificates` dipasang. `systemctl is-active docker` menghasilkan `active`; `docker-compose --version` mengonfirmasi `2.26.1-4`.
- Portainer Community Edition image `portainer/portainer-ce:lts` berjalan pada CT104 dengan pemetaan `0.0.0.0:9443->9443/tcp`. `docker ps` mengonfirmasi status `Up`; wizard akun administrator belum diselesaikan.
- Satu percobaan awal `docker run` gagal karena tanda `:` terkirim sebagai `;` oleh input terminal, menghasilkan `"docker run" requires at least 1 argument` dan `-bash: 9443: command not found`. Perintah diketik ulang dengan benar; container Portainer kemudian berjalan. Tidak ada data yang terhapus.
- Langkah yang belum diuji: login Portainer dari browser klien, wizard admin, Tailscale/TUN, Jellyfin, Grafana, Immich, Home Assistant Container, jaringan final MikroTik, penyimpanan HDD, dan backup.
- Arahan pengguna: Prometheus tidak perlu dipasang. Grafana tidak mengumpulkan metrik sendiri; status Grafana/datasource masih perlu dipastikan.
- Referensi instalasi: [Dokumentasi Portainer CE Docker](https://docs.portainer.io/start/install-ce/server/docker/linux), [Docker Debian](https://docs.docker.com/engine/install/debian/).

## Persiapan pindah Proxmox ke MikroTik — 1 November 2026

- Sebelum perubahan, `ip -br link` dan `bridge link` menunjukkan NIC fisik `enp0s31f6` menjadi port `vmbr0`; `eno1` tidak ada di daftar antarmuka. Cadangan konfigurasi dibuat sebagai `/etc/network/interfaces.before-mikrotik` dan `/etc/resolv.conf.before-mikrotik`.
- `/etc/network/interfaces` diarahkan ke `192.168.88.10/24`, gateway `192.168.88.1`, bridge hanya `enp0s31f6`; stanza `eno1` yang tidak ada dihapus. `/etc/resolv.conf` diarahkan ke DNS AdGuard `192.168.88.253`; `/etc/hosts` sudah mengarahkan `pve.lab.local` dan `pve` ke `192.168.88.10`.
- `ifquery vmbr0` berhasil menampilkan stanza dengan alamat, gateway, dan port bridge yang benar. `ifreload -a` dijalankan sesuai dokumentasi Proxmox. Sesi shell WebUI lama di `192.168.0.200` berhenti merespons setelah perubahan alamat; keadaan runtime di alamat baru belum dapat diuji dari jaringan sementara.
- Di rumah, sambungkan `enp0s31f6` ke port LAN MikroTik lalu buka `https://192.168.88.10:8006`. Pastikan CT/VM memperoleh lease jaringan `192.168.88.x`; jika masih menyimpan alamat `192.168.0.x`, perbarui lease atau mulai ulang guest. Alamat DNS `.253` dan gateway `.1` mengikuti rencana jaringan yang sudah ada dan belum diuji ulang pada sesi ini.
- Pengguna meminta progres dijeda pada 1 November 2026. Commit progres lokal `18bbce2` belum terunggah; `git push origin main` gagal dengan pesan persis `fatal: unable to access 'https://github.com/midnightcodeprotocol-corporation/home-server-lab.git/': Could not resolve host: github.com`. Tidak ada pemasangan layanan lanjutan setelah jeda.

## Pindah DNS utama ke STB `.3` dan verifikasi Proxmox di MikroTik — 1 November 2026

- Lease DHCP statis STB `stb-adguard` (MAC `00:15:18:01:81:31`) diubah dari `192.168.88.253` ke `192.168.88.3`; pengguna mengonfirmasi Active Address kini `.3`.
- Dari Windows, `nslookup google.com 192.168.88.3` berhasil dan mengembalikan jawaban non-authoritative.
- Pengguna mengubah DHCP Network MikroTik agar membagikan DNS `.3`. `ipconfig /all` menunjukkan laptop `192.168.88.252`, gateway/DHCP server `.1`, DNS `.3` dan `.11`. `.11` belum diverifikasi aktif; pengguna diarahkan agar sementara hanya membagikan `.3`, belum dikonfirmasi.
- MikroTik WinBox Tools → Ping ke `192.168.88.10` menunjukkan 16/16 balasan, 0% loss. Pengguna kemudian mengonfirmasi kabel Proxmox melalui switch port 3, switch port 1 ke MikroTik ether4; Proxmox bukan DHCP client karena IP statis.
- Pengguna melaporkan DNS server host Proxmox diganti ke `192.168.88.3`. Uji resolusi nama dari host belum dilakukan. Gateway tetap `192.168.88.1` dan alamat host `192.168.88.10/24`.
- Pengguna mengonfirmasi susunan port fisik: MikroTik ether1 ke TL-WR840N (WAN), ether2 kosong (calon WAN modem cadangan), ether3 STB AdGuard, ether4 ke switch, ether5 laptop. Switch port 1 uplink MikroTik, port 2 AP, port 3 Proxmox, port 4-5 kosong. WAN cadangan belum dikonfigurasi.
## Pemeriksaan panel Proxmox dan HDD pertama — 1 November 2026

- Screenshot WebUI menunjukkan Proxmox VE 9.2.24 pada node `pve`, uptime sekitar 1 jam, RAM 23.36 GiB, 4 CPU, dan akses `https://192.168.88.10:8006` aktif.
- Node menampilkan CT101 `adguard2`, CT104 `docker-services`, CT100 `Template-CT`, VM201 `docker-core`, dan VM200 `Template-VM`.
- `Disks > Disks`: NVMe sistem `/dev/nvme0n1` berukuran 512.11 GB dengan partisi EFI dan LVM. HDD terdeteksi sebagai `/dev/sda`, model Seagate `ST2000VX008-2E3164`, ukuran 2.00 TB, S.M.A.R.T. `PASSED`; memiliki partisi `/dev/sda1` berjenis NTFS.
- Tidak ada initialize, wipe, format, mount, atau pembuatan storage yang dijalankan. Isi partisi NTFS dan peran disk belum diperiksa/diputuskan. HDD kedua menunggu enclosure lain.
- Koreksi topologi pengguna: Proxmox ke switch port 3; switch port 1 ke MikroTik ether4. MikroTik ether2 kosong dan direncanakan untuk WAN modem cadangan; belum dikonfigurasi.

## Uji resolusi DNS host Proxmox — 1 November 2026

- Pengguna menjalankan `getent hosts deb.debian.org` pada shell root Proxmox setelah mengarahkan DNS host ke `192.168.88.3`.
- Perintah berhasil mengembalikan empat alamat IPv6 AAAA untuk `debian.map.fastlydns.net` / `deb.debian.org`; resolusi IPv6 lulus.
- Record IPv4 dan akses internet dari host belum diuji.

## Uji record DNS IPv4 Proxmox — 1 November 2026

- Pengguna menjalankan `getent ahostsv4 deb.debian.org` pada shell root Proxmox.
- Perintah mengembalikan empat alamat IPv4 `151.101.66.132`, `151.101.130.132`, `151.101.194.132`, dan `151.101.2.132` (Fastly); resolusi A/IPv4 lulus.
- Akses koneksi keluar Proxmox ke repositori paket belum diuji. Langkah berikutnya `apt-get -o Acquire::ForceIPv4=true update` hanya memperbarui daftar paket.

## Uji akses repository Proxmox — 1 November 2026

Perintah: `apt-get -o Acquire::ForceIPv4=true update`

- Repo Debian trixie dan trixie-security dapat diakses (`Hit`/`Get`).
- Repo Proxmox `http://download.proxmox.com/debian/pve trixie InRelease` gagal setelah tiga kali percobaan. Pesan persis: `Could not connect to download.proxmox.com:80 (117.120.5.231). - connect (113: No route to host)`.
- APT melaporkan `Fetched 90.7 kB in 9s (10.6 kB/s)`, `Reading package lists... Done`, serta warning bahwa indeks repo Proxmox gagal diperoleh dan indeks lama/yang ada dipakai. Jadi pembaruan indeks hanya parsial; belum ada upgrade atau instalasi paket.
- Pengguna menguji `curl -4 -I --connect-timeout 10 https://download.proxmox.com/debian/pve/dists/trixie/InRelease`; hasil: `curl: (7) Failed to connect to download.proxmox.com port 443 after 682 ms: Could not connect to server`.
- HTTP port 80 dan HTTPS port 443 ke host Proxmox gagal, sementara repositori Debian pada update APT berhasil. DNS IPv4 sudah terbukti; penyebab spesifik/rute belum diketahui. Tidak ada konfigurasi apt atau jaringan yang diubah.
- Pengguna menguji `curl -4 -I --connect-timeout 10 https://deb.debian.org`; server membalas `HTTP/2 200` melalui cache SIN. HTTPS IPv4 umum dari Proxmox berfungsi.
- Pengguna menjalankan `ip route get 117.120.5.231`; hasil: `117.120.5.231 via 192.168.88.1 dev vmbr0 src 192.168.88.10 uid 0 cache`. Tabel routing host memilih gateway MikroTik yang diharapkan, interface bridge `vmbr0`, dan alamat sumber host `.10`.
- Pengguna menjalankan `ping -c 4 117.120.5.231`. Statistik: 4 paket terkirim, 0 diterima, 2 pesan ICMP error, 100% packet loss. Error yang terlihat: `From 172.30.100.1 icmp_seq=1 Destination Host Unreachable` dan `From 172.30.100.1 icmp_seq=4 Destination Host Unreachable`.
- Pesan ICMP unreachable berasal dari `172.30.100.1`, bukan dari alamat LAN Proxmox `.10` atau gateway LAN MikroTik `.1`. Ini menunjukkan penolakan dilaporkan dari jalur upstream yang terlihat oleh host; perangkat/penyebab pastinya belum dipastikan. Langkah selanjutnya ping gateway LAN `192.168.88.1` dari Proxmox untuk memastikan hop lokal.
- Pengguna menjalankan `ping -c 4 192.168.88.1` dari Proxmox. Hasil 4/4 diterima, 0% loss, RTT rata-rata 0.343 ms (min 0.283, maks 0.422 ms). Konektivitas host ke gateway LAN MikroTik terverifikasi.
- Screenshot WinBox Tools > Ping ke `117.120.5.231`: 0/10 diterima (100% loss); sequence 0, 3, 6, 9 mendapat host unreachable dari `172.30.100.1`; sequence lainnya timeout. Router MikroTik juga belum dapat mencapai target tersebut pada uji ICMP.
- Temuan ini mempersempit masalah ke jalur WAN/upstream atau tujuan/IP target; belum membuktikan penyebabnya. Langkah berikutnya cek hasil DNS IPv4 terkini `download.proxmox.com` dari host Proxmox dan hindari mengubah rute/firewall sampai IP tujuan dipastikan. Belum ada perubahan konfigurasi router atau host.

## Uji ulang koneksi internet dan repo paket — 2 November 2026

- Pengguna melaporkan `ping -c 4 192.168.88.1` ulang: 4/4 diterima, 0% loss, RTT rata-rata 0.343 ms.
- Pengguna menjalankan `apt update`; repo Debian trixie, security, updates, dan repo Proxmox `http://download.proxmox.com/debian/pve trixie InRelease` seluruhnya berhasil (`Hit`/`Get`). Output akhir: `Fetched 384 kB in 2s (244 kB/s)` dan `3 packages can be upgraded`.
- Akses internet dan repo Proxmox dinyatakan bekerja oleh pengguna pada pengujian terbaru. Kegagalan akses spesifik `117.120.5.231` dan ICMP unreachable sebelumnya tidak terulang pada update ini; penyebab insiden sebelumnya belum diketahui.
- Pengguna menjalankan `apt list --upgradable`; tersedia `libnss3` (`2:3.110-1+deb13u4` → `2:3.110-1+deb13u5`), `vim-common` (`2:9.1.1230-2` → `2:9.1.1230-2+deb13u1`), dan `vim-tiny` (versi yang sama naik ke `2:9.1.1230-2+deb13u1`). Ketiganya dari `stable-security`.
- Pengguna menjalankan `apt-get -s upgrade`. Simulasi menyatakan `3 upgraded, 0 newly installed, 0 to remove and 0 not upgraded`; hanya `libnss3`, `vim-common`, dan `vim-tiny` dari `Debian-Security:13/stable-security`.
- Screenshot konsol Proxmox memperlihatkan pengguna menjalankan `apt-get upgrade`, menyetujui prompt, dan berhasil menyelesaikan unpack/setup ketiga paket; prompt `root@pve:~#` kembali. Tidak terlihat error atau permintaan reboot.

## Sesi audit remote Proxmox dan MikroTik — 2 November 2026

- Sesi Chrome yang sudah login menampilkan Proxmox VE 9.2.24 di `192.168.88.10:8006`, console root, dan entri resource CT101, CT104, CT100, VM201, VM200 serta storage `local`/`local-lvm`. Status aktual/IP guest belum berhasil dibaca dari console.
- WinBox yang sudah login menampilkan DHCP Server > Networks: network `192.168.88.0/24`, gateway `192.168.88.1`, DNS `192.168.88.3`. Tidak ada pengaturan MikroTik yang diubah.
- Uji SSH Codex `ssh -o BatchMode=yes -o ConnectTimeout=5 -o StrictHostKeyChecking=yes root@192.168.88.10 ...` gagal lokal dengan persis: `ssh: connect to host 192.168.88.10 port 22: Permission denied`. Belum diketahui apakah ini kebijakan jaringan lingkungan Codex atau keadaan sshd host.
- Otomasi input lewat CUA tidak berhasil mengendalikan console PVE/WinBox; tidak ada perintah console atau perubahan konfigurasi yang dijalankan melalui CUA. Pekerjaan install layanan ditunda sampai audit baca-saja guest, IP, storage dan router dapat dilakukan.

### Hasil audit SSH lanjutan — 2 November 2026

- SSH root ke `192.168.88.10` berhasil setelah koneksi memakai `HostKeyAlias=192.168.0.200`; fingerprint itu cocok dengan kunci host lama yang sudah diverifikasi. Hanya perintah audit baca-saja dijalankan.
- `pvesh get /cluster/resources --type vm --output-format json`: CT100 template stopped; CT101 `adguard2` stopped; CT104 `docker-services` running; VM200 template stopped; VM201 `docker-core` stopped.
- `pct config 101` dan `qm config 201`: `onboot=0` untuk CT101 dan VM201. Keduanya tidak memiliki IP aktif saat berhenti. CT101 AdGuard Home terpasang sebelumnya tetapi service disabled.
- CT104: unprivileged, nesting=1, 4 cores, 8192 MiB RAM, 1024 MiB swap, rootfs 64G, `onboot=1`, `net0` DHCP. `pct exec 104 -- ip -brief address` menunjukkan `192.168.88.101/24`; ini lease DHCP sementara, belum reservasi/final.
- `pct exec 104 -- docker ps -a`: hanya `portainer/portainer-ce:lts` berjalan, TCP 9443. Docker aktif. `pct exec 104 -- ls -la /opt/stacks` menghasilkan `No such file or directory`. Wizard admin Portainer masih menunggu pengguna.
- `pvesm status`: `local` dan `local-lvm` active. `lsblk -f` dan `lsblk -o NAME,MODEL,SIZE,TYPE,TRAN` hanya menunjukkan NVMe Samsung 476.9 GB. HDD `/dev/sda` tidak muncul pada audit 2 Nov, meski screenshot 1 Nov menunjukkan Seagate 2 TB NTFS dan SMART PASSED. Penyebab perbedaan belum diketahui; tidak ada format/mount/inisialisasi.
- SSH MikroTik `192.168.88.1`: pertama gagal `Unable to negotiate ... no matching MAC found. Their offer: hmac-sha1,hmac-md5`; dengan algoritme legacy terbatas per sesi, server kemudian memutus: `Received disconnect from 192.168.88.1 port 22:3:`. Tidak ada autentikasi atau perubahan router. Jangan menurunkan keamanan host key/SSH untuk mengakali kegagalan ini.
- Risiko sebelum instalasi: IP final CT104 belum diputuskan; rencana lokasi Home Assistant/Immich/Tailscale berbeda antara `data/guest.yaml`, `docs/08-keputusan.md`, dan buku. Tunda layanan sampai IP dan penempatan diselaraskan. Prometheus tetap tidak dipasang sesuai keputusan.
- Klarifikasi pengguna setelah audit: HDD Seagate 2 TB sedang memang tidak dipasang; bukan disk yang gagal terdeteksi. Nanti setelah dipasang kembali, lakukan pemeriksaan ulang lalu konfigurasi storage sesuai peran yang diputuskan. Jangan format tanpa memeriksa/menyetujui perlakuan data.

## Uji DNS AdGuard Home CT101 — 2 November 2026

- Pemeriksaan pertama sebelum wizard dilanjutkan: CT101 `.11/24` berjalan dan service aktif, tetapi UI mengarah ke `/install.html`; port 53 belum listen dan kueri ditolak. Ini adalah keadaan sebelum pengguna menyelesaikan layar konfigurasi.
- Setelah pengguna melanjutkan wizard, pemeriksaan baca-saja melalui Proxmox menunjukkan AdGuard Home mendengarkan TCP/UDP 53 dan UI TCP 80. `dig @192.168.88.11 google.com A` menjawab `NOERROR` dengan 6 alamat A (46 ms); kueri AAAA menjawab `NOERROR` dengan 4 alamat AAAA (30 ms).
- DNS CT101 berfungsi dari host Proxmox dan laptop Windows. Pada PowerShell, `nslookup google.com 192.168.88.11` menjawab `Non-authoritative answer`, menampilkan server `adguard2.lab.local` di `192.168.88.11`, serta alamat IPv4 dan IPv6. File dashboard AdGuard Home yang disimpan pengguna menunjukkan upstream publik `https://dns10.quad9.net/dns-query` dan bootstrap `9.9.9.10`, `149.112.112.10`, `2620:fe::10`, `2620:fe::fe:10`, sehingga resolusi domain internet tidak bergantung pada STB `.3`. Private reverse DNS masih menunjukkan resolver default `192.168.88.3:53`; lookup reverse privat dapat bergantung pada STB. DNS DHCP MikroTik belum diubah dan konfigurasi yang terakhir diketahui tetap `.3`. Admin UI: `http://192.168.88.11`. Kata sandi admin tidak dicatat di repo.


## DNS DHCP MikroTik diperbarui — 2 November 2026

- Pengguna melaporkan mengubah daftar DNS pada network DHCP LAN `192.168.88.0/24` menjadi `192.168.88.3` dan `192.168.88.11`; perubahan router belum diverifikasi langsung melalui WinBox/CLI oleh Codex.
- Langkah verifikasi: renew lease Ethernet laptop dan periksa `ipconfig /all` untuk memastikan kedua DNS diterima; kemudian jalankan `nslookup google.com` tanpa menyebut server agar DNS klien default ikut diuji.


## Checkpoint jeda konfigurasi Proxmox/MikroTik — 2 November 2026

- Pengguna meminta jeda sampai kembali ke rumah untuk mematikan perangkat dan membersihkan area server. Pada saat checkpoint, Proxmox dan guest berjalan; pengguna belum melaporkan perangkat sudah dimatikan.
- Audit Proxmox terakhir: storage local dan local-lvm aktif; tidak ada upgrade paket tertunda; CT101, CT104, VM202 running, VM201 stopped. CT104 .101 DHCP, MAC BC:24:11:25:14:4B; Docker menampilkan Portainer Up dan Jellyfin Up (healthy). IP .20 tidak terlihat pada neighbor cache dan tidak membalas dua ping, tetapi konflik alamat belum diverifikasi lengkap lewat DHCP lease MikroTik.
- Pengguna memilih .20 sebagai IP final CT104. Belum ada perubahan jaringan di CT104, reservation MikroTik, restart, atau downtime layanan.
- Kelanjutan setelah di rumah: verifikasi .20 kosong pada WinBox DHCP leases/ARP, reserve MAC CT104 ke .20, lalu reboot CT104 dan cek akses Portainer/Jellyfin. DHCP DNS .3 + .11 sudah diverifikasi diterima laptop; jangan ubah.
- MikroTik SSH gagal negosiasi, WinBox UI automation unavailable. Ether2 MikroTik masih kosong untuk rencana modem WAN backup. Pada saat checkpoint lama itu HDD belum dipasang; status terbaru ada di bagian HDD/PBS di bawah.

## HDD unit 1 dan VM Proxmox Backup Server — 2 November 2026

- Pengguna menyambungkan HDD pertama via enclosure USB. Audit `lsblk`/`blkid`: model Seagate ST2000VX008-2E3164, serial lokal `Z52655EN`, kapasitas 2,000,398,934,016 bytes, satu partisi NTFS label `New Volume`, UUID lama `00404CD1404CCEDA`; disk tidak ter-mount dan belum menjadi storage.
- `smartctl -a` melalui USB bridge: overall health `PASSED` berdasarkan attributes; suhu 31°C; reallocated sectors 0, pending sectors 0, offline uncorrectable 0, UDMA CRC 0, error log kosong, power-on 668 jam. Bridge memberi pesan `SMART Status not supported: Incomplete response, ATA output registers missing`; belum ada self-test pada log.
- Partisi dibaca read-only di `/run/hdd-audit`; opsi mount `ro`. Konten top-level hanya folder `System Volume Information`; filesystem menggunakan 159 MB dari 1.9T. Mount dilepas setelah pemeriksaan.
- Sesuai keputusan proyek bahwa HDD unit 1 dipakai untuk datastore PBS, PVE `wipedisk` menghapus signature NTFS lama, lalu endpoint Directory membuat GPT + ext4. Filesystem UUID baru `f1420efd-4618-4804-8b6b-4f924f31f36c`, mount `/mnt/pve/backup-disk`, `is_mountpoint=1`; `pvesm status` menunjukkan active, kapasitas sekitar 1.8 TiB, used awal sekitar 2 MiB. Tidak ada backup yang tersimpan saat ini.
- ISO PBS 4.2-1 ditemukan di `E:\\93-HOME-SERVER-LAB-PROJECT\\01-INSTALER\\proxmox-backup-server_4.2-1.iso`. SHA256 pada laptop cocok dengan checksum resmi Proxmox `2fb299deac3929253712c9c3dfc9237edbe70af83c8848467616b771a1d5453e`; checksum setelah transfer ke `/var/lib/vz/template/iso/` sama. ISO resmi 4.2-1, 1,480,032,256 bytes.
- VM212 `pbs` dibuat dan running dari ISO: 2 vCPU, RAM 2048 MiB, OS disk 32 GiB di `local-lvm`, SCSI data disk 1.5 TiB qcow2 sparse di `backup-disk` (`backup=0`, iothread), NIC VirtIO MAC `BC:24:11:09:FD:F1`, bridge `vmbr0`, firewall enabled, QEMU agent enabled, `onboot=0`; target IP `.30` belum aktif/reservation belum dibuat. Installer sedang berjalan; belum ada password/email yang dimasukkan.
- Percobaan awal preallocation metadata untuk qcow2 1.5 TiB sangat lambat; proses dihentikan sebelum disk berisi data dan volume parsial dibuang. Storage default `preallocation=off` untuk membuat qcow2 sparse; saat ini file disk baru hanya memakai sekitar 216 KiB.
- Langkah berikut: pengguna buka Proxmox > VM 212 > Console, selesaikan installer dengan memilih disk OS 32 GiB (bukan datastore 1.5 TiB), lalu input password/email secara privat. Gunakan DHCP sementara atau siapkan reservation `.30` di MikroTik sebelum alamat tetap; lanjutkan membuat datastore pada disk 1.5 TiB dalam PBS.

## PBS selesai dipasang; perubahan tujuan HDD — 2 November 2026

- Pengguna melaporkan instalasi PBS selesai. Audit host Proxmox baca-saja: VM212 `running`, CD-ROM ISO sudah `none`, `onboot=0`; QEMU Guest Agent belum aktif. Konfigurasi disk adalah OS 32 GiB `local-lvm` dan disk data 1.5 TiB qcow2 sparse di `backup-disk` (guest terlihat sebagai volume `scsi1`).
- Installer sebelumnya menampilkan konfigurasi `.30/24`, gateway `.1`, DNS `.3`, hostname `pbs`. Setelah instalasi, ping `192.168.88.30` 2/2 gagal dan HTTPS `192.168.88.30:8007` tidak dapat tersambung dari Proxmox; IP/layanan PBS pasca-boot belum diverifikasi.
- Storage host: NVMe `local-lvm` thin pool kapasitas 348.8 GiB, terpakai 22.2 GiB, tersedia sekitar 326.7 GiB saat audit; root filesystem menyisakan 79 GiB. Volume pada HDD `backup-disk` memakai sekitar 2.3 MiB pada sisi host karena qcow2 sparse. Belum ada datastore atau backup.
- Keputusan terbaru pengguna: HDD unit 1 dan HDD kedua nantinya dipakai untuk penyimpanan aplikasi (Nextcloud, Immich, Jellyfin, dll.); backup menyusul. Jangan format datastore di HDD. Disk 1.5 TiB masih terpasang pada VM PBS dan harus dilepas dari konfigurasi tanpa menghapus volumenya sebelum HDD dipakai aplikasi.
- Pengguna mengusulkan backup sementara 100 GiB di NVMe. Ruang thin pool host saat ini memadai secara angka, tetapi disk 100 GiB belum dialokasikan. Rencana langkah aman: pulihkan akses PBS dahulu, matikan VM, lepaskan disk HDD dari VM tanpa menghapus volume, lalu tambahkan disk 100 GiB pada `local-lvm`; buat datastore baru hanya di disk NVMe tersebut.

## PBS dipulihkan dan disk backup sementara dipasang — 2 November 2026

- Pengguna melakukan hard reset; setelah itu PBS boot normal. Host Proxmox memverifikasi `.30` ping 3/3 (0% loss), neighbor MAC `BC:24:11:09:FD:F1`, dan HTTPS `192.168.88.30:8007` HTTP 200. `pve-firewall status` melaporkan `disabled/running`.
- VM212 dimatikan, lalu `scsi1` HDD 1.5 TiB dilepas hanya dari konfigurasi VM (`qm set 212 --delete scsi1`). `pvesm list backup-disk` mengonfirmasi volume `backup-disk:212/vm-212-disk-0.qcow2` tetap tersimpan; volume tidak dihapus. Volume qcow2 sparse hanya memakai sekitar 2.3 MiB pada storage fisik menurut status.
- VM212 menerima disk baru `local-lvm:vm-212-disk-1,size=100G` pada NVMe sebagai `scsi1` (`discard=on`, `iothread=1`, `ssd=1`). PBS dinyalakan kembali; status running, ping `.30` 3/3 dan UI HTTPS 8007 HTTP 200. Thin pool `local-lvm` menunjukkan sekitar 326.7 GiB tersedia. Disk 100 GiB belum diformat di guest, belum menjadi datastore, dan belum ada backup.
- Langkah selanjutnya: di UI PBS `https://192.168.88.30:8007`, verifikasi disk sekitar 100 GiB sebelum membuat ext4 datastore. Jangan pilih/format HDD; kedua HDD disiapkan untuk data aplikasi.

## Datastore PBS sementara — 2 November 2026

- Pengguna melaporkan menyelesaikan dialog **Create: Directory** di PBS dengan `/dev/sdb`, ext4, nama `store1`, dan **Add as Datastore** dicentang. `/dev/sdb` sesuai disk guest tambahan 100 GiB di `scsi1` pada VM212; disk OS 32 GiB ada di `scsi0`, volume HDD 1.5 TiB sudah dilepas dari guest.
- Status pembuatan datastore dicatat berdasarkan konfirmasi pengguna; belum dikonfirmasi secara terpisah melalui daftar datastore dashboard. Belum ada backup job atau backup yang berjalan.

## Monitoring Prometheus dan Grafana — 3 November 2026

- **Lulus:** Prometheus 3.15.1, `prompve/prometheus-pve-exporter` 3.11.0, dan Grafana 13.3.0 dipasang dengan Compose di CT104 `/opt/stacks/prometheus`.
- **Lulus:** endpoint health Grafana menghasilkan JSON `database: ok`; Prometheus API menunjukkan job Prometheus dan Proxmox sama-sama `up`. Query `pve_cpu_usage_ratio{id="node/pve"}` mengembalikan metrik untuk node PVE.
- **Lulus:** datasource Prometheus dan dashboard `Home Server Overview` diprovisikan. Dashboard memuat panel CPU/RAM host dan guest.
- **Keamanan/akses:** API Proxmox menggunakan user/token khusus dengan role `PVEAuditor`; TLS diverifikasi memakai CA PVE. Prometheus menyimpan metrik 30 hari. Grafana tersedia di `http://192.168.88.20:3000`; Prometheus hanya bind ke localhost CT104 pada port 9090 dan PVE exporter hanya di jaringan Docker internal. Rahasia disimpan di direktori `secrets` lokal server yang tidak masuk repo.
- **Belum diuji pengguna:** login pertama Grafana dan tampilan dashboard dari browser klien. Password awal tersedia di `/opt/stacks/prometheus/secrets/grafana_admin_password`; pengguna mengambilnya sendiri melalui shell Proxmox, tidak mengirim password ke chat.
- Keputusan awal untuk tidak memasang Prometheus pada catatan sebelumnya adalah riwayat; pada 3 Nov pengguna mengarahkan untuk menggunakan Prometheus dan stack ini sudah dipasang.
### Login awal Grafana — 3 November 2026

- Pengguna mengonfirmasi login awal Grafana selesai. Belum ada konfirmasi terpisah bahwa dashboard `Home Server Overview` tampil atau password awal sudah diganti.

### Dashboard monitoring dibenahi — 3 November 2026

- **Uptime Kuma:** monitor Samba lama diarahkan ke `https://192.168.88.12/`, sehingga gagal dengan `connect ECONNREFUSED 192.168.88.12:443`. Diubah menjadi monitor TCP `192.168.88.12:445` dan status baru menunjukkan `[Samba] [Up] 0 ms`. Nama monitor `Nextclaud` diperbaiki menjadi `Nextcloud`; `Home Assistance` menjadi `Home Assistant`.
- **Uptime Kuma:** monitor yang sebelumnya memakai lease lama `.101` sudah diarahkan ke layanan aktif CT104 `.20`; monitor Jellyfin memberi `[Jellyfin] [Up] 200 - OK`, Portainer TCP `.20:9443` Up, Proxmox TCP `.10:8006` Up, dan PBS TCP `.30:8007` Up. Riwayat down lama tidak dihapus. Grafana ditambahkan memakai `http://192.168.88.20:3000/api/health` dan memperoleh `[Grafana] [Up] 200 - OK`; Uptime Kuma ditambahkan memakai TCP `.20:3001` dan memperoleh `[Uptime Kuma] [Up] 0 ms`. Dashboard menampilkan 11/11 Up pada sesi ini; statistik riwayat lama pada beberapa monitor masih rendah karena kegagalan konfigurasi sebelumnya.
- **Grafana:** file `konfigurasi/prometheus/grafana-dashboard.json` diperbarui dan tervalidasi JSON. Dashboard `Home Server Overview` menjadi 8 panel: CPU/RAM host dan guest, status scrape Prometheus/PVE exporter, persentase pemakaian storage Proxmox, serta pemakaian disk guest. Prometheus API mengembalikan `up=1` untuk job `prometheus` dan `proxmox`; query metrik disk penggunaan dan ukuran menghasilkan data.
- Berkas dashboard dipasang ke `/opt/stacks/prometheus/grafana-dashboard.json` di CT104. Perubahan berkas bind mount tidak terlihat sampai container Grafana direstart; setelah restart status container `running`, API dashboard menunjukkan versi 2 dan delapan panel. UI browser menampilkan panel Prometheus `UP` serta PVE exporter `UP`; grafik storage/disk tampak dengan seri metriknya.
- Endpoint Grafana dan port internal Uptime Kuma dipantau, tetapi notifikasi eksternal belum dikonfigurasi karena kanal/tujuan notifikasi belum ditetapkan. Prometheus tetap hanya bind localhost CT104:9090.

## Gotify dan Beszel hub — 3 November 2026

- **Lulus:** Audit baca-saja ulang pada Proxmox VE 9.2.24 menunjukkan CT104 tetap running dengan Docker aktif; RAM available sekitar 6.1 GiB dari alokasi 8 GiB. Tidak ada perubahan konfigurasi host Proxmox atau MikroTik pada sesi ini.
- **Lulus:** Compose Gotify dan Beszel divalidasi dengan `docker compose config --quiet`. Gotify berjalan healthy pada `192.168.88.20:8070`; endpoint `/health` menghasilkan HTTP 200. Beszel hub berjalan pada `192.168.88.20:8090`; endpoint `/_/` menghasilkan HTTP 200.
- Gotify admin awal menggunakan nama `admin`; password acak dibuat di server dan hanya tersimpan lokal dengan permission 0600. Pengguna melaporkan login admin serta penggantian password selesai pada 3 Nov; token aplikasi Gotify dan uji notifikasi dari Uptime Kuma ke HP masih pending. Jangan gunakan atau mencatat password awal.
- Pada saat pemasangan awal, akun/agent Beszel dan monitor Kuma masih belum dibuat; progres penyelesaian dicatat pada butir lanjutan di bawah. Notifikasi Gotify masih menunggu token aplikasi dan uji kirim.
- **Audit live integrasi 3 Nov:** layanan Gotify sehat; query read-only pada DB menunjukkan 0 aplikasi. DB Uptime Kuma menunjukkan 0 notification entry. `/etc/pve/notifications.cfg` tidak menunjukkan target atau matcher Gotify. Maka tidak ada integrasi aktif Gotify ↔ Uptime Kuma/PVE saat ini, walaupun pengguna sudah menyelesaikan login Gotify. PVE 9.2.24 menyediakan target Gotify dan matcher notifikasi; token aplikasi khusus Proxmox masih diperlukan. Lihat [dokumentasi resmi notifikasi Proxmox VE](https://github.com/proxmox/pve-docs/blob/master/notifications.adoc). Tidak ada secret yang dibaca/ditulis oleh audit ini.
- Percobaan awal endpoint `127.0.0.1:8070` dan `127.0.0.1:8090` dari CT104 gagal karena port Compose sengaja bind hanya pada IP CT `.20`. Uji ulang melalui `192.168.88.20` sukses; tidak ada perubahan bind yang diperlukan.
- Pengguna mengonfirmasi akun pertama Beszel telah dibuat dan menjalankan perintah pemasangan agent host dari UI Beszel. **Lulus:** `beszel-agent.service` di PVE berstatus `active` dan `enabled`; journal mengonfirmasi `WebSocket connected host=192.168.88.20:8090`. Sesaat setelah start, terdapat tiga respons `unexpected status code: 401`, lalu koneksi berhasil dan agent beralih ke WebSocket; tidak perlu instal ulang.
- Pengguna mengonfirmasi sistem `pve` di Beszel diisi Host/IP `192.168.88.10`. Audit journal lanjutan tetap menunjukkan koneksi WebSocket ke hub `.20:8090`.
- Pengguna memasang agent kedua di CT104. **Lulus:** dari Proxmox, `systemctl is-active` dan `is-enabled` dalam CT104 mengembalikan `active`/`enabled`; journal CT104 mencatat agent tersambung ke hub `192.168.88.20:8090`. Docker service lain tetap berstatus Up, dan endpoint hub tetap HTTP 200.
- **Perlu ditelusuri terpisah:** log agent mencatat `smartctl failed device=/dev/sda err="no serial number (exit status 2)"` dan `smartctl failed device=/dev/nvme0 err="no SMART health data in smartctl output (exit status 4)"`. Koneksi agent ke hub tetap berhasil; pembacaan SMART belum tersedia.
- Audit baca-saja database Kuma mengonfirmasi 13 monitor aktif dan entri `Beszel` tersedia. `Immich` belum ada sebagai monitor. Token Gotify belum dibagikan ke chat atau repo.

## Immich siap diuji dari ponsel — 3 November 2026

- Audit baca-saja: empat container Immich (`immich_server`, `immich_postgres`, `immich_machine_learning`, `immich_redis`) berstatus Up dan server `healthy`. `GET http://192.168.88.20:2283/api/server/ping` mengembalikan `{"res":"pong"}`; halaman web merespons HTTP 200.
- Mount upload server `/data` diarahkan ke `/srv/media/immich` di HDD `backup-disk`; kapasitas mount HDD sekitar 1.7 TiB masih tersedia saat pemeriksaan. Ini ruang kosong saat ini, bukan cadangan kedua.
- Pengguna ingin mencadangkan seluruh foto/video ponsel ke Immich. Login dari aplikasi ponsel, pemilihan album, dan upload pertama belum diuji. Pertahankan salinan asli di ponsel sampai proses selesai dan salinan terpisah/backup tersedia; backup Immich/database ke media terpisah belum disiapkan.
- Pengguna saat ini tidak berada di LAN MikroTik dan tersambung melalui Tailscale. **Lulus dari klien Windows melalui Tailscale:** `Test-NetConnection 192.168.88.20 -Port 2283` mengembalikan `TcpTestSucceeded: True`, dengan interface `Tailscale` dan source `100.94.16.110`. Peer Android terlihat aktif pada tailnet. Ini membuktikan jalur laptop ke layanan; login dan upload dari ponsel sendiri tetap perlu diuji.
- URL server yang dimasukkan di aplikasi Immich ponsel: `http://192.168.88.20:2283`; pastikan Tailscale di ponsel tetap Connected. Pengguna perlu memilih album foto dan video yang ingin diunggah lalu mengaktifkan Backup. Pada Android, optimasi baterai dapat menunda background upload; pada iOS, Background App Refresh perlu aktif. Upload awal sebaiknya dibiarkan berjalan di Wi-Fi dan sambil mengisi daya.

## Audit backup sebelum unggah Immich — 3 November 2026

- Audit Proxmox baca-saja: `pvesm status` menunjukkan `backup-disk`, `local`, dan `local-lvm`; tidak ada storage jenis PBS yang sudah ditambahkan. `pvesh get /cluster/backup --output-format json` mengembalikan `[]`; belum ada job terjadwal.
- Dari Windows di luar LAN, koneksi PBS `192.168.88.30:8007` dan PVE `192.168.88.10:8006` sama-sama lulus melalui interface Tailscale (`TcpTestSucceeded: True`). UI PBS dapat dibuka dari lokasi pengguna saat ini.
- VM212 PBS berjalan dengan disk OS 32 GiB dan disk sementara 100 GiB di `local-lvm`/NVMe. API PBS di `.30:8007` merespons `401` pada endpoint versi tanpa autentikasi (layanan hidup, endpoint memerlukan autentikasi). SSH port 22 terbuka, tetapi tidak ada host key PBS tersimpan dengan alias yang diuji; koneksi dihentikan karena pemeriksaan host key ketat. Karena itu datastore `store1` belum bisa diverifikasi dari audit ini.
- Immich saat audit: `immich_server`, `immich_postgres`, `immich_machine_learning`, dan `immich_redis` Up; server healthy. `/srv/media/immich` memakai sekitar 311 MiB, database `/opt/immich/postgres` sekitar 334 MiB, query database menghitung 99 baris aset. Bind-mount CT104 `mp0` (`/srv/media`) disetel `backup=0`, sehingga vzdump CT104 tidak akan mencadangkan foto/video di sana. `mp1` `/srv/appdata` juga `backup=0`.
- **Belum ada backup yang dijalankan.** Sebelum unggah foto lebih banyak, verifikasi datastore PBS 100 GiB, tambahkan sebagai storage PVE memakai kredensial/token yang hanya dimasukkan di UI lokal, lalu rancang dua cakupan: backup guest PVE dan backup file+database Immich. Backup PBS sementara berada di NVMe yang sama dengan Proxmox; ini tidak melindungi dari kegagalan fisik NVMe.
- Sesudah satu backup awal berhasil diverifikasi, jadwal harian (misalnya 03.00 WIB) dengan retensi awal yang dibatasi dapat dibuat. Jadwal harus mencakup pula media Immich; backup CT biasa saja tidak cukup.
- Pengguna mengonfirmasi pada 3 Nov bahwa datastore `store1` tampak di PBS UI. Free space dan izin datastore belum diverifikasi; belum ada backup. Langkah selanjutnya membuat user/API token khusus PVE dengan izin terbatas pada `/datastore/store1`, menambah storage PBS pada PVE, lalu menjalankan backup awal dan uji hasil.

## Backup guest manual pertama — 3 November 2026

- Storage PBS `pbs-store1` berhasil ditambahkan pada PVE setelah pengguna memasukkan fingerprint sertifikat yang ditampilkan saat koneksi.
- Pengguna melaporkan backup manual dengan mode Snapshot dan kompresi ZSTD untuk CT101 (`adguard2`), CT102 (`files`), CT103 (Tailscale), CT104 (`docker-services`), dan VM202 (`haos`) masing-masing berakhir `TASK OK`.
- Pengguna membuka PBS Content dan mengonfirmasi arsip CT101 terlihat. Arsip empat guest lain belum dikonfirmasi lewat halaman Content.
- Belum ada tes restore, jadwal backup, pemeriksaan ruang kosong datastore, atau backup terpisah untuk data bind-mount Immich. CT104 bind-mount `/srv/media` dan `/srv/appdata` disetel `backup=0`; media Immich di `/srv/media/immich` tidak tercakup backup CT. PBS sementara 100 GiB berada di NVMe yang sama dengan PVE.
- Langkah berikut: cek kapasitas bebas `store1`, kemudian siapkan dan uji backup media serta database Immich sebelum mengaktifkan jadwal otomatis.

## Immich Android: sinkronisasi berhenti karena koneksi timeout — 3 November 2026

- Pengguna melaporkan layar backup menunjukkan Total 12.923 aset, Backup 6.977, Remainder 5.946.
- Screenshot App Logs memperlihatkan `ApiException 400: HTTP connection failed: GET /server/version (Inner exception: ClientException: java.net.SocketTimeoutException: failed to connect to /192.168.88.20 (port 2283) from /192.168.2.104 (port 49040) after 30000ms, uri=http://192.168.88.20:2283/api/server/version)` pada `remote-sync` pukul 18:46.
- Temuan langsung: saat itu ponsel tidak berhasil membuat koneksi TCP ke CT104 `.20:2283`. Ini menjelaskan gagalnya remote-sync; belum ada bukti kerusakan database/foto. Apakah Tailscale tidak aktif, route subnet belum tersedia, atau gangguan jaringan sementara masih belum dipastikan.
- Langkah diagnosis aman: jangan hapus foto asli, reset database Immich, atau instal ulang aplikasi. Dengan Tailscale aktif di Android, uji `http://192.168.88.20:2283/api/server/ping` di browser ponsel dan harapkan `{"res":"pong"}`. Setelah koneksi berhasil, buka kembali aplikasi dan lanjutkan sinkronisasi.
- **Pembaruan pengguna:** penyebab putusnya koneksi ditemukan—aplikasi Tailscale tertutup di ponsel. Pengguna kemudian menjalankan pemeriksaan baca-saja di node PVE: CT104 `mp0` adalah `/mnt/pve/backup-disk/applications/media` ke `/srv/media`, `backup=0`; `mp1` adalah `/mnt/pve/backup-disk/applications/apps` ke `/srv/appdata`, `backup=0`; rootfs `local-lvm:vm-104-disk-0,size=64G`. `proxmox-backup-client version` mengembalikan `client version: 4.2.8`. Ini memastikan jalur sumber media dan client tersedia pada host, belum menjalankan file backup.
- Sebelum melanjutkan upload dari ponsel, buat backup file awal host path `/mnt/pve/backup-disk/applications/media/immich` ke PBS; periksa dahulu ukuran/path dan keberadaan database dump Immich. Setelah backup terverifikasi, aktifkan kembali Tailscale dan uji endpoint ping dari browser ponsel.
- Pengguna menjalankan pemeriksaan baca-saja tambahan pada PVE: `du -sh /mnt/pve/backup-disk/applications/media/immich` menghasilkan `8.3G`. Folder `backups/` memuat `immich-db-backup-20261103T114030-v3.3.5-pg14.19.sql.gz` (45,917,289 bytes), `immich-db-backup-20261103T113941-v3.3.5-pg14.19.sql.gz` (45,832,822 bytes), `immich-db-backup-20261103T020000-v3.3.5-pg14.19.sql.gz` (19,135,377 bytes), dan `.immich` (13 bytes). Proxmox Backup Client tersedia di host, versi `4.2.8`.
- PBS Dashboard yang dilaporkan pengguna: `store1` usage 9.06% (`9.04 GB of 99.70 GB`), sekitar `90.66 GB` available; backup groups: empat CT dan satu VM. Ukuran sumber Immich 8.3G saat ini muat dalam datastore, tetapi ukuran akan bertambah seiring upload foto/video.
- Pengguna menjalankan `proxmox-backup-client key show`; hasilnya `Error: no encryption file provided and no default file found`. Kunci default lalu dibuat melalui `proxmox-backup-client key create`; pengguna mengonfirmasi paperkey disimpan di password manager. Tidak ada nilai kunci atau passphrase yang dicatat di repo. Backup file terenkripsi belum dijalankan.
- **Steering pengguna:** meskipun backup file Immich awalnya direncanakan sebelum upload ponsel dilanjutkan, pengguna menyatakan upload foto/video masih berlangsung dan memilih backup nanti. Upload kini dilaporkan sedang berjalan. Setelah selesai, ukur ulang folder, cek kapasitas PBS terbaru, buat dump database baru, baru jalankan backup file terenkripsi. Salinan asli tetap disimpan.
- **Pembaruan setelah upload — 3 Nov 2026:** Pengguna menyatakan upload selesai. Audit baca-saja dengan SSH ke PVE: semua container Immich Up/server healthy; `du -sh /srv/media/immich` sekitar 19 GiB; query `select count(*) from asset` pada DB Immich menghasilkan 10.638. Catatan ponsel sebelumnya menunjukkan total 12.923, backup 6.977, tersisa 5.946; kemungkinan perbedaan cakupan belum disimpulkan dan perlu dicek sebelum migrasi.
- Dump post-upload dibuat di `/srv/media/immich/backups/immich-db-backup-postupload-20261103T145827Z.sql.gz`, ukuran 81 MiB. `gzip -t` berhasil. Backup ini berada di dalam direktori Immich yang ikut pada arsip media.
- Dry-run PBS menyebut sumber `/mnt/pve/backup-disk/applications/media/immich`; backup aktual memakai PBS target `192.168.88.30`, datastore `store1`, repository identity `pve-backup@pbs!pve-main`, key file privat PVE `/etc/pve/priv/storage/pbs-store1.enc`, dan sertifikat fingerprint yang sudah tersimpan. Password dibaca lewat `PBS_PASSWORD_FILE`; rahasia tidak dicetak atau dimasukkan ke catatan. Enkripsi sisi klien aktif.
- **Lulus:** `proxmox-backup-client backup immich-data.pxar:/mnt/pve/backup-disk/applications/media/immich ... --backup-type host --backup-id immich-data` selesai exit 0 pada 3 Nov 22:07 WIB. Snapshot `host/immich-data/2026-11-03T15:00:28Z`; arsip 18.194 GiB, terkompresi 17.572 GiB. PBS `list` dan `snapshot files` menampilkan snapshot serta arsip `immich-data.pxar.didx` dengan crypt-mode `encrypt`. Datastore terpakai 26.81%, tersedia sekitar 66.6 GiB.
- **Lulus pemulihan:** `proxmox-backup-client restore` memulihkan seluruh arsip 18.36 GiB dari snapshot tersebut ke `/var/tmp/immich-restore-check-20261103`. Dump hasil restore lulus `gzip -t`; SHA-256 sumber dan hasil restore sama (`cde93c600bbe491ef13f72fdbbf2c6924b04dd49959f1f06c4edcbaac559ad7`). Direktori uji dihapus; root kembali sekitar 80 GiB tersedia. Ini menguji dekripsi dan pemulihan arsip, bukan impor DB ke server Immich produksi.
- PBS datastore 100 GiB berada pada NVMe yang sama dengan PVE; backup ini membantu dari kesalahan penghapusan/kerusakan logis, tetapi bukan kegagalan fisik host/disk. Rekonsiliasi jumlah aset masih diperlukan sebelum migrasi Immich.

## Integrasi notifikasi Proxmox → Gotify — 3 November 2026

- Pengguna membuat aplikasi/token Gotify khusus untuk PVE, memasukkan token hanya melalui UI PVE, lalu melaporkan tes target berhasil. Audit konfigurasi nonrahasia PVE menunjukkan target `gotify-proxmox` dengan server `http://192.168.88.20:8070`; file privat token tidak dibaca.
- Sebelum perubahan, `default-matcher` bawaan hanya merutekan ke `mail-to-root`. Dibuat matcher `gotify-all`, mode `all`, tanpa aturan penyaring, target `gotify-proxmox`. Dokumentasi resmi PVE menyatakan matcher tanpa aturan selalu cocok; matcher email bawaan tetap dipertahankan.
- **Lulus (konfigurasi):** `pvesh get /cluster/notifications/matchers --output-format json` mengonfirmasi matcher `gotify-all` berstatus user-created dan targetnya `gotify-proxmox`.
- **Lulus (uji target menurut pengguna):** pengguna melaporkan tes target Gotify berhasil. **Belum diuji:** event PVE biasa/backup yang melewati matcher sampai tampil sebagai notifikasi di ponsel.
- Job backup `home-lab-daily` tidak menetapkan `notification-mode` khusus/legacy; PVE menggunakan pengaturan notifikasi global. Belum ada backup harian yang berjalan sebagai uji notifikasi setelah matcher dibuat.
- Tidak dibuat target atau matcher Uptime Kuma → Gotify dalam langkah ini. Tidak ada token/rahasia yang dicatat di repo.
- Rujukan resmi: [Notifikasi Proxmox VE](https://github.com/proxmox/pve-docs/blob/master/notifications.adoc).

## Audit baca-saja layanan saat menunggu backup terjadwal — 3 November 2026

- **Lulus:** PVE kembali dapat diakses lewat SSH. CT101, CT102, CT103, CT104, VM202, dan VM212 running; CT100/VM200 adalah template stopped; VM201 tetap stopped.
- **Lulus:** storage `backup-disk`, `local`, `local-lvm`, dan `pbs-store1` aktif. `pbs-store1` terpakai sekitar 8.84% pada saat pemeriksaan.
- **Lulus:** semua container Docker yang terlihat pada `docker ps` di CT104 berstatus Up. Gotify dan Uptime Kuma berstatus healthy; `immich_server` juga healthy bersama Postgres, Redis, dan machine learning.
- **Lulus:** dari laptop, koneksi TCP ke `192.168.88.20:2283` berhasil dan `GET /api/server/ping` mengembalikan `{"res":"pong"}`. Ini hanya menguji jalur laptop saat ini; tidak membuktikan upload ponsel sudah selesai.
- Tidak ada perubahan konfigurasi server pada audit ini. Penambahan monitor Immich ke Uptime Kuma masih tertunda; belum diubah melalui database atau tanpa sesi admin yang tervalidasi.

## Portainer Server CT105 dan Agent CT104 — 3 November 2026

- Pengguna menyelesaikan wizard admin Portainer pada CT105 dan memilih Skip untuk Edge Compute.
- Pengguna menjalankan perintah resmi `docker run` untuk `portainer/agent:2.45.3` di CT104 `docker-services` dan melaporkan menambahkan CT104 sebagai environment pada Portainer CT105.
- **Lulus (status container):** SSH baca-saja ke PVE menunjukkan CT104 dan CT105 `running`; `docker ps` di CT104 menunjukkan `portainer_agent Up` dengan TCP 9001 dipetakan ke `0.0.0.0` dan `::`. Portainer server di CT105 `Up`, HTTPS 9443 dipetakan, dan `/api/status` HTTP 200.
- **Belum dikonfirmasi:** status environment `Up` pada dashboard Portainer tidak terlihat dari audit ini. Lease CT105 `.105` masih dinamis, belum reservasi/static.
- **Tindak lanjut keamanan:** perintah agent membuka TCP 9001 di semua interface CT104. Batasi akses ke alamat CT105 setelah IP stabil sebelum migrasi aplikasi; jangan hentikan Portainer lama CT104 selama masa transisi.
- Tidak ada kata sandi atau token dicatat.
- **Lulus (konfirmasi dashboard pengguna):** screenshot Portainer Home menunjukkan 2 environment total dan 2 berstatus `Up`; `CT104-docker-services` memakai URL `tcp://192.168.88.20:9001`, Agent 2.45.3, serta 16/16 container dan 1 node. Environment `local` CT105 juga `Up`.
- Screenshot mengonfirmasi CT105 UI di `https://192.168.88.105:9443`; alamat ini tetap lease DHCP dinamis karena reservasi MikroTik belum dibuat. MAC CT105 pada konfigurasi PVE: `BC:24:11:19:DA:40`.
