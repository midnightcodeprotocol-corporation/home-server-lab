# Revisi 7: audit identitas dan uji clone template Debian

**Tanggal:** 1 November 2026  
**Cakupan:** uji clone langsung pada Proxmox VE 9.2.24 di ThinkCentre M710q; perubahan jaringan host tidak dilakukan.

## Temuan utama

Clone awal CT 991 dari template CT 100 dan VM 990 dari VM 200 berhasil dibuat, tetapi fingerprint SSH ED25519 clone sama persis dengan sumber. Perbandingan dua VM clone independen dari template 200 juga menunjukkan fingerprint yang sama. Ini berisiko membuat host SSH tertukar dan melemahkan pemisahan identitas.

Di VM Debian 13, isi `/etc/machine-id` juga tersalin ke clone. Image memiliki dua berkas machine ID biasa: `/etc/machine-id` dan `/var/lib/dbus/machine-id`. Mengosongkan hanya yang pertama tidak cukup; ID lama muncul kembali saat boot. Setelah keduanya dikosongkan dan jalur D-Bus dibuat symlink ke `/etc/machine-id`, Debian menghasilkan ID baru dan `dbus-uuidgen --get` mengembalikan nilai yang sama.

## Perbaikan dan hasil yang dibuktikan

- Clone awal CT 991 dari CT 100 dan VM 990/201 dari VM 200 memiliki fingerprint SSH ED25519 yang sama dengan template. Temuan ini membuktikan template lama membawa host key bersama.
- Drop-in layanan SSH menjalankan ssh-keygen -A sebelum sshd -t. Urutan bawaan Debian menguji konfigurasi lebih dulu dan layanan gagal bila belum ada host key.
- VM Debian memakai dua file machine ID: /etc/machine-id dan /var/lib/dbus/machine-id. Mengosongkan file pertama saja tidak cukup. Keduanya dikosongkan dan /var/lib/dbus/machine-id dibuat symlink ke /etc/machine-id; clone baru menghasilkan ID unik dan dbus-uuidgen --get cocok dengan /etc/machine-id.
- Clone CT 102: boot lulus, DHCP 192.168.0.105/24, gateway 192.168.0.1, DNS deb.debian.org berhasil, SSH aktif, dan host key baru.
- Clone VM 204: Debian 13, boot lulus, DHCP 192.168.0.106/24, DNS berhasil, QEMU Guest Agent aktif, SSH aktif, host key dan machine ID baru.
- Tes dilakukan pada jaringan router sementara 192.168.0.0/24, bukan MikroTik. Seluruh guest uji dihentikan dan dihapus setelah pemeriksaan.

## Keadaan akhir Proxmox

- Template CT 100 Template-CT dan VM 200 Template-VM dibuat ulang dari kandidat bersih dengan ID yang sama seperti semula.
- Keduanya berhenti dan berstatus template. Inventaris VM/LXC hanya berisi ID 200 dan 100.
- Semua kandidat dan clone sementara selama audit telah dihapus. ID layanan CT 101+ dan VM 201+ kembali tersedia.
- Paket tambahan VM belum diperiksa. Guest layanan, perpindahan jaringan ke MikroTik, backup, dan HDD belum diuji.

Prosedur template diperbaiki pada Bab 49. Jangan masukkan private key, passphrase, token, atau isi authorized_keys ke repo.