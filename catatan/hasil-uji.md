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
- Aplikasi AdGuard Home, Docker, serta stack layanan belum dipasang. Lanjutkan setelah host tersambung ke MikroTik dan reservasi alamat dibuat untuk MAC kedua guest.
