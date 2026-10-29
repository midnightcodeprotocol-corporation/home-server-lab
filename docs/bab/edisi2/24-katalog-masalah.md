# Bab 24. Katalog Masalah dan Solusi

Kumpulan masalah yang sudah terjadi pada proyek ini (ditandai [Nyata]) dan yang sering muncul. Cari  
gejalanya di tabel.  

## 24.1 Alur cepat: Proxmox tidak bisa dibuka dari browser

1. Pastikan VM/mesin Proxmox menyala dan layar konsol menampilkan Please use your web  
browser ... https://...:8006.  
2. Di laptop ipconfig: catat IPv4 dan gateway adapter yang aktif. Tiga angka depan IP Proxmox harus  
sama dengan laptop.  
3. Di konsol Proxmox: ip a dan ping -c 3 192.168.88.1. Jika gagal, periksa kabel LAN dan bridge-ports.  
4. Pastikan alamat https://IP:8006 (https, bukan http).  
5. Periksa /etc/hosts dan systemctl status pveproxy.  
6. Ping dari laptop: ping IP-Proxmox. Ping berhasil tetapi web tidak = masalah layanan; ping gagal =  
masalah jaringan.  

## 24.2 Tabel masalah

Gejala Penyebab Solusi Bab  
[Nyata] Tidak bisa buka https:/  
/192.168.100.2:8006  
IP Proxmox beda jaringan  
dengan laptop  
Ubah address/gateway di interfaces  
dan hosts, reboot  
9.3  
[Nyata] Layar nano kosong Nama berkas  
interface bukan  
interfaces  
Ctrl+X, buka  
/etc/network/interfaces  
9.3  
[Nyata] apt update: Temporary  
failure resolving  
DNS kosong/salah Isi System &gt; DNS, ping deb.debian.org 9.4  
[Nyata] Tidak menemukan menu  
Repositories  
Ada di bawah Updates  
pada node  
Node &gt; Updates &gt; Repositories 9.5  
[Nyata] Refresh sangat lambat (9  
KB/s)  
Internet lambat/WiFi Kabel LAN, mirror terdekat, jam sepi 9.6  
[Nyata] Perintah sudo tidak  
terbaca  
Sudah root, sudo tidak  
terpasang  
Hapus sudo; di VM Debian gunakan su - 1.7  
[Nyata] ipconfig /release  
memutus WiFi  
IP dilepas tanpa diminta  
kembali  
ipconfig /renew 3.9  
[Nyata] STB punya dua instalasi  
Armbian  
eMMC lama dan SD baru lsblk, findmnt /, putuskan satu 12.2  
[Nyata] Double NAT / router di  
belakang router lain  
Salah urutan perangkat Ikuti Gambar 1.1 3.9  
USB tidak muncul di boot menu Mode boot/Secure  
Boot/penulisan USB  
Rufus DD mode, sesuaikan GPT/MBR,  
matikan Secure Boot  
6.4  
Layanan web Proxmox mati  
setelah ganti IP  
/etc/hosts masih IP  
lama  
Perbarui hosts, cek hostname  
--ip-address  
9.3  
Error 401 pada repository  
enterprise  
Repo berbayar aktif Disable enterprise, tambah no-subscription 9.5  
Container tidak dapat IP Reservasi/bridge/DHCP Cek lease MikroTik; IP statis 10.5  
VM tak bisa start: KVM tidak  
tersedia  
VT-x belum aktif Aktifkan VT-x di BIOS (Bab 27.5), cek /dev/kvm 11  
Peringatan cdrom saat apt update Sumber apt installer  
tersisa  
Beri tanda # pada baris cdrom 11.5  
Port 53 sudah dipakai systemd-resolved  
stub  
DNSStubListener=no, restart 12.3  
Subnet Tailscale tidak terjangkau Rute belum disetujui /  
forwarding mati  
Setujui rute, ip_forward=1 12.4  
Satu perangkat masih  
menampilkan iklan  
DNS sendiri/lease lama Matikan Secure DNS, renew, aturan firewall  
opsional  
13.10  
Portainer timed out Admin awal telat dibuat docker restart portainer 14.4  
Docker permission denied User bukan root/grup  
docker  
Jadi root atau tambah ke grup docker 14.4  
Forgejo: clone SSH gagal Port 2222 tidak diset SSH_PORT = 2222 di app.ini 15  
Nextcloud: untrusted domain Domain belum terdaftar occ config:system:set  
trusted_domains  
16.3  
HAOS tidak boot Secure Boot/boot order efidisk pre-enrolled-keys=0, boot  
order=scsi0  
18  
Dashboard: Host validation failed Host belum di  
ALLOWED_HOSTS  
Tambahkan di compose.yaml 19  
k3s NotReady RAM kurang Naikkan RAM VM, matikan VM lain 20  
Flux: permission denied (publickey) Deploy key tanpa izin tulis Tambahkan deploy key dengan write  
access  
21  
Renovate tidak membuat PR Izin bot / versi latest Collaborator + pin versi image 22  
Restore sukses tapi tanpa jaringan Nama kartu fisik beda Ubah bridge-ports, ifreload -a 23  

## 24.3 Cara meminta bantuan dengan efektif

• Apa yang dilakukan dan pesan error persis (salin teks).  
• Keluaran ip a, ip route, dan cat /etc/resolv.conf dari server bermasalah.  
• ipconfig dari laptop untuk masalah jaringan.  
• Log: klik dua kali tugas di panel Tasks Proxmox, atau journalctl -u NAMA -n 50.  
• Foto layar konsol server atau tangkapan layar Proxmox (Hardware dan Network).
