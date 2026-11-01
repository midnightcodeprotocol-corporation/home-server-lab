# Hasil uji per fase

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
- Langkah diagnosis berikutnya adalah menguji koneksi HTTPS ke endpoint InRelease tanpa mengubah source apt.
