# Bagian 1. Keamanan dan Akses Jarak Jauh: Lembar Pembaruan, Glosarium, Syarat Lulus Fase 1

Lembar Pembaruan untuk Edisi 2  
Daftar bab Edisi 2 yang perlu disesuaikan setelah Suplemen 1. Edisi 2 tidak ditulis ulang; cukup ubah atau  
tambahkan sesuai tabel.  
Bab Edisi 2 Perubahan Rujukan  

## 1.7 Tentang sudo dan root Tambahkan: login SSH ke VM Debian sebagai pengguna biasa lalu su -

; perintah tetap tanpa sudo  
Bab 25.6  

## 3.8 MikroTik Ganti catatan "www sengaja dibiarkan aktif" dengan pembatasan ke

192.168.88.0/24; tambah aturan firewall  
Bab 25.8  

## 9.8 Kebiasaan baik Tambahkan akun admin terpisah, 2FA, SSH hanya kunci, firewall

Proxmox  
Bab 25.3 sampai  
25.5  

## 10.4 Tips SSH ke LXC Jangan lagi menganjurkan PermitRootLogin yes; pakai konsol atau

kunci SSH  
Bab 25.4  
11 VM Debian Tambahkan langkah kunci SSH, UFW, dan update keamanan otomatis Bab 25.6  
12.1 dan 12.4 STB Peran Tailscale pindah dari STB 1 ke STB 2 (sementara VM Debian);  
pakai tailscale set dan tag  
Bab 26.2 dan 26.4  

## 13.8 Subnet router cadangan Tambahkan tag:router dan kebijakan akses Bab 26.6

## 14.4 Portainer Tambahkan catatan: port Docker melewati UFW Bab 25.6

23 Backup Tambahkan item: kunci SSH, Recovery Keys 2FA, backup MikroTik,  
arsip /etc/pve  
Bab 25.9  
24 Katalog masalah Tambahkan baris pada tabel di bawah Bab 25.11 dan 26.11  
Baris tambahan untuk Bab 24  
Gejala Penyebab Solusi Bab  
Permission denied (publickey) Kunci belum terpasang atau  
salah izin  
Cek authorized_keys (izin 600), pakai konsol  
darurat  
25.4  
Web Proxmox tertutup setelah  
firewall  
Alamat laptop di luar jaringan  
lokal  
pve-firewall stop dari konsol, koreksi aturan 25.5  
Kode 2FA ditolak Jam menyimpang atau kode  
salah  
timedatectl status; pakai Recovery Keys 25.3  
Port container terbuka walau  
UFW menolak  
Docker melewati UFW Pahami, audit di Bab 38 25.6  
Router tidak bisa dibuka setelah  
aturan  
Aturan input salah Safe Mode, kabel ke ether2, pulihkan  
backup  
25.8  
Rute 192.168.88.x tidak  
terjangkau  
Rute belum disetujui atau  
forwarding mati  
Setujui rute, ip_forward=1 26.4  
Internet HP mati dengan DNS  
global  
AdGuard tidak terjangkau Matikan Override DNS servers 26.7  
Glosarium tambahan  
Istilah Arti  
2FA / TOTP Kode 6 digit yang berubah tiap 30 detik dari aplikasi autentikator, tambahan di atas  
password.  
Kunci SSH Pasangan kunci privat (di laptop) dan publik (di server) pengganti password.  
Passphrase Kata sandi yang melindungi berkas kunci privat itu sendiri.  
UFW Antarmuka sederhana untuk firewall Linux.  
Safe Mode (MikroTik) Mode yang membatalkan perubahan otomatis bila koneksi ke router terputus.  
Tailnet, subnet router, tag,  
grants, split DNS  
Lihat tabel Bab 26.1.  
Syarat Lulus Fase 1  
Sebelum Suplemen 2 (Monitoring) dimulai, pastikan semua poin berikut benar. Laporkan hasilnya, termasuk  
pesan error bila ada, supaya perbaikan dilakukan di suplemen ini saja.  
No Poin Ya / Tidak  
1 Backup sebelum perubahan ada di luar server  
2 Akun adminlab dan root@pam memakai 2FA; Recovery Keys tersimpan  
3 SSH Proxmox dan VM Debian hanya dengan kunci; root VM ditolak  
4 Firewall Proxmox aktif dan web Proxmox terbuka dari LAN  
5 UFW dan update otomatis aktif di VM Debian  
6 MikroTik memiliki aturan penutup WAN dan layanan tambahan mati  
7 Tailscale aktif di server, laptop, dan HP  
8 Dari HP (data seluler) web Proxmox terbuka; tanpa Tailscale gagal  
9 Kebijakan akses dan tag:router terpasang  
Berikutnya: Suplemen 2 berisi Uptime Kuma dan Gotify, Prometheus dan Grafana dengan node_exporter, serta  
Scrutiny dan aturan alert, lengkap dengan sisi server dan sisi klien (aplikasi HP).
