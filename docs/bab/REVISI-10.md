# Revisi 10: pesan AF_VSOCK pada konsol VM201

**Tanggal:** 1 November 2026

## Gejala dan diagnosis

Konsol VM201 menunjukkan berulang kali:

```text
systemd-ssh-generator: Failed to query local AF_VSOCK CID: Cannot assign requested address
```

VM tetap boot ke prompt login. Pemeriksaan menunjukkan Debian 13 memakai systemd `257.13-1~deb13u1`; layanan `ssh.service` aktif dan mendengarkan TCP port 22. Pesan berasal dari generator socket SSH tambahan yang mencoba memakai AF_VSOCK. VM ini memakai SSH melalui jaringan VirtIO dan QEMU Guest Agent, bukan SSH over-vsock. Laporan Debian mencatat gejala yang sama pada systemd 257.13.

Nama `debian-docker` yang sempat terlihat pada tangkapan layar adalah tampilan konsol lama sebelum perubahan hostname. Nilai sekarang `/etc/hostname` dan `hostnamectl --static` adalah `docker-core`; `/etc/issue` memakai escape getty agar hostname ditampilkan dinamis pada layar login.

## Perbaikan

- Kernel command line GRUB diubah menjadi `quiet systemd.ssh_auto=no`.
- `update-grub` berhasil dan baris Linux di `/boot/grub/grub.cfg` memuat opsi tersebut.
- VM201 dimatikan dan dinyalakan kembali dengan bersih untuk menerapkan opsi.

Opsi `systemd.ssh_auto=no` mematikan pembuatan otomatis socket SSH tambahan AF_VSOCK/AF_UNIX. Layanan SSH jaringan (`ssh.service`) tetap aktif. Rujukan resmi menjelaskan opsi ini dan fungsi generator; laporan Debian merekam bug systemd `257.13-1~deb13u1`.

## Hasil setelah reboot

- `/proc/cmdline` memuat `systemd.ssh_auto=no`.
- Hostname: `docker-core`.
- SSH: `active`; listener TCP 22 tetap tersedia.
- Docker: `active`; belum ada container aplikasi.
- Filter log boot baru tidak menemukan error AF_VSOCK.
- DHCP sementara VM berubah dari `192.168.0.107` menjadi `192.168.0.102`. Host tetap `192.168.0.200`; CT101 tetap `192.168.0.106`. IP akhir MikroTik belum ditetapkan.

Rujukan: [systemd-ssh-generator](https://www.freedesktop.org/software/systemd/man/latest/systemd-ssh-generator.html), [Debian bug #1137216](https://bugs.debian.org/cgi-bin/bugreport.cgi?bug=1137216), [systemd issue #42188](https://github.com/systemd/systemd/issues/42188).
