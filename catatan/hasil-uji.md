# Hasil uji per fase

## Lanjutan pemasangan layanan — 2 November 2026

- **Lulus:** CT101 `adguard2` diubah menjadi `192.168.88.11/24`, gateway `192.168.88.1`, resolver `192.168.88.3`, dan `onboot=1`; CT berhasil start dan interface menunjukkan alamat `.11`.
- **Lulus sebagian:** `AdGuardHome.service` CT101 aktif; port TCP 3000 terbuka dan `curl http://192.168.88.11:3000/` mengembalikan HTTP 302 ke wizard. Belum diuji kueri DNS lewat `.11`; wizard admin menunggu pengguna. DHCP MikroTik tetap membagikan DNS `.3` saja.
- **Lulus:** Jellyfin dipasang pada CT104 memakai image resmi `ghcr.io/jellyfin/jellyfin:latest`, digest `sha256:fea863d0cd9ec445985d9c75fc6ed64e38a1d2766cf0c250a33d553f4fc1b771`. Setelah konfigurasi awal terikat lease `.101`, container dibuat ulang dengan volume konfigurasi/cache yang sama dan port host `8096` tidak lagi terikat ke satu IP; sekarang `0.0.0.0:8096` dan `:::8096`. Container kembali healthy, log `Core startup complete`, ffmpeg tersedia, dan HTTP `.101:8096` merespons 302 ke `/web/`. `/srv/media` tetap kosong/read-only karena HDD dilepas.
- **Lulus sebagian:** Image HAOS 18.4 diunduh dari rilis resmi; checksum SHA256 `756ec485b1b153099ca53e88a5eebd63a801d56b791afe5c6d63ef94a35dc02d` cocok dengan `SHA256SUMS`. QCOW2 valid dan disk virtual 32 GiB. VM202 dibuat UEFI/q35, 2 vCPU, RAM 2048 MiB, disk 32 GiB di local-lvm, VirtIO NIC di vmbr0, onboot=1; status running. Paket dari MAC VM `BC:24:11:60:7C:42` menunjukkan alamat DHCP `.102`; ping 2/2 lulus. `http://192.168.88.102:8123/` mengembalikan 307 ke `http://192.168.88.102/`, dan `http://192.168.88.102/onboarding.html` merespons HTTP 200. QEMU Guest Agent belum aktif. Onboarding admin masih menunggu pengguna.
- **Catatan admin:** Pengguna melaporkan wizard beberapa layanan selesai; tetapi pemeriksaan langsung CT101 pada 2 Nov membuktikan installer AdGuard Home masih terbuka, sehingga status teknis CT101 mengikuti hasil uji tersebut. Setup Jellyfin dan Home Assistant tetap menurut laporan pengguna. Portainer dilanjutkan setelah restart memakai setup token dari log; pengguna memilih Skip untuk Edge Compute dan melaporkan wizard setup selesai. Kata sandi tidak ditangani/dicatat oleh Codex.
- **Belum dikerjakan:** MikroTik SSH tetap tidak bisa dipakai, WinBox automation sebelumnya tidak berhasil; belum ada reservasi DHCP untuk CT104, belum ada perubahan DNS DHCP. Immich menunggu HDD dipasang kembali dan isi diperiksa; Tailscale memerlukan autentikasi akun; Grafana belum memiliki datasource, Prometheus tidak dipasang.
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

- Audit baca-saja pada Proxmox: CT101 berjalan dengan `192.168.88.11/24`; `AdGuardHome.service` berstatus `active`.
- `ss -lntup` di CT101 hanya menunjukkan layanan web AdGuard pada TCP 3000 (serta SSH dan Postfix loopback); tidak ada listener TCP/UDP port 53.
- HTTP ke `192.168.88.11:3000` membalas `302` dengan `Location: /install.html`; log service menyatakan first launch dan mengalihkan ke halaman installer. Ini membuktikan wizard instalasi belum diselesaikan pada instance CT101.
- `dig @192.168.88.11 google.com A` dan `dig @192.168.88.11 google.com AAAA` keduanya gagal dengan `communications error ...#53: connection refused`. DNS CT101 belum siap.
- Tindakan berikutnya: selesaikan wizard di `http://192.168.88.11:3000/install.html`, lalu uji ulang A/AAAA dari LAN. Jangan masukkan `.11` ke DHCP MikroTik sebelum kedua query berhasil; DNS DHCP yang diketahui saat ini tetap `.3`. Kata sandi admin tidak dicatat di repo.
