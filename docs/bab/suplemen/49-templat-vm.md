# Bab 49. Templat VM Debian + Docker dan Cara Membuat VM Baru

PENEMPATAN - BARU - VM 9100 (templat), lalu klon per layanan  
Tempat: VM 9100 tpl-debian-docker di host Proxmox. Templat tidak pernah dinyalakan setelah jadi; ia hanya  
disalin.  
Alasan: Satu sumber yang sama untuk semua VM Docker: cepat, seragam, dan pembaruan keamanan dasar sudah  
ada. Setiap layanan lalu mendapat salinan penuh yang berdiri sendiri.  
Tidak termasuk: Tailscale (setiap node harus punya identitas sendiri) dan layanan apa pun.  

## 49.1 Rencana: dari mana templat dibuat

Keadaan Anda Yang dilakukan  
VM Debian dari Edisi 2 masih bersih (belum ada  
layanan)  
Jadikan VM itu templat setelah 49.2 dan 49.3, lalu buat docker-core dari  
templat  
VM Debian sudah berisi layanan Suplemen 3 dan 4 Biarkan menjadi VM 201 docker-core (ganti ID bila perlu) dan buat  
templat dari instalasi Debian baru di 49.2  
Belum ada VM Debian Ikuti 49.2 dari awal  

## 49.2 Membuat dan mengisi VM dasar

Pemasangan Debian secara rinci ada di Edisi 2 (Debian 13, ISO netinst, tanpa lingkungan desktop). Ringkasnya  
di Proxmox:  
1. Di web Proxmox klik Create VM. VM ID 9100, Name tpl-debian-docker. Pada OS pilih ISO Debian 13 netinst.  
2. System: biarkan bawaan dan centang QEMU Agent. Disks: Bus SCSI, ukuran 24 GiB (Debian + Docker dan  
layanan kecil; data besar nanti pakai disk kedua). CPU 2 inti. Memory 2048.  
3. Network: bridge vmbr0, model VirtIO. Selesaikan, jalankan, dan pasang Debian lewat konsol: hanya SSH  
server dan standard system utilities yang dipilih.  
4. Setelah masuk sebagai root (su -), lanjutkan di bawah.  

**TERMINAL VM TEMPLAT** | VM 9100, sebagai root (setelah su -)

```
apt update && apt upgrade -y
```
> Penjelasan: Memperbarui paket dasar.
```
apt install -y qemu-guest-agent unattended-upgrades ca-certificates curl nano
```
> Penjelasan: Agen tamu (Proxmox bisa membekukan sistem berkas saat backup), pembaruan keamanan otomatis,
dan alat dasar.  
```
install -m 0755 -d /etc/apt/keyrings
```
> Penjelasan: Folder kunci repositori.
```
curl -fsSL https://download.docker.com/linux/debian/gpg -o /etc/apt/keyrings/docker.asc
```
> Penjelasan: Mengunduh kunci repositori resmi Docker.
```
chmod a+r /etc/apt/keyrings/docker.asc
```
> Penjelasan: Membuat kunci bisa dibaca apt.
```
nano /etc/apt/sources.list.d/docker.sources
```
> Penjelasan: Isi seperti kotak di bawah.

**/etc/apt/sources.list.d/docker.sources** | Isi berkas

```
Types: deb
URIs: https://download.docker.com/linux/debian
Suites: trixie
Components: stable
Signed-By: /etc/apt/keyrings/docker.asc
```

**TERMINAL VM TEMPLAT** | VM 9100, sebagai root

```
apt update
apt install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
```
> Penjelasan: Memasang Docker Engine dan Compose dari repositori resmi. Ketersediaan paket dan langkah
pemasangan Debian 13 perlu dicocokkan lagi dengan dokumentasi resmi saat instalasi.

```
docker run --rm hello-world
```
> Penjelasan: Uji: harus mencetak pesan sukses. Mengunduh image sekali.
```
systemctl status qemu-guest-agent --no-pager
```
> Penjelasan: Agen harus aktif setelah opsi QEMU Agent di Proxmox diaktifkan dan VM dimulai ulang sekali.
```
mkdir -p /opt/stacks
```
> Penjelasan: Folder induk semua layanan Docker (konvensi Suplemen 3 Bab 31).
KEAMANAN  
Jangan memasang Tailscale, Docker Compose layanan, atau akun layanan di templat. Templat harus polos; setiap  
klon memberi identitasnya sendiri.  

## 49.3 Membersihkan dan menjadikan templat

**TERMINAL VM TEMPLAT** | VM 9100, sebagai root

```
apt clean && rm -f /etc/ssh/ssh_host_*
```
> Penjelasan: Membersihkan cache paket dan menghapus kunci host SSH agar setiap klon membuat kuncinya
sendiri (tanpa ini semua VM berbagi satu identitas SSH).  
```
truncate -s 0 /etc/machine-id
```
> Penjelasan: Mengosongkan ID mesin; systemd membuat yang baru pada boot pertama setiap klon.
```
history -c && poweroff
```
> Penjelasan: Menghapus riwayat sesi dan mematikan VM.
1. Di Proxmox klik kanan VM 9100 &gt; Convert to template (atau di shell host: qm template 9100). Setelah ini  
VM tidak bisa dinyalakan, hanya disalin.  
2. Opsional: di Options templat, matikan Start at boot.  

## 49.4 Penyiapan awal setiap VM hasil klon

Prosedur ini dipakai oleh semua bab yang membuat VM baru (kotak penempatan menyebut "Bab 49.4"). Contoh  
di bawah untuk VM 205 vault; ganti ID, nama, dan IP sesuai peta 48.3.  

**TERMINAL HOST PROXMOX** | Shell node Proxmox (host), sebagai root

```
qm clone 9100 205 --name vault --full 1
```
> Penjelasan: Salinan penuh (bukan terkait) sehingga VM berdiri sendiri dan templat bisa dihapus tanpa
merusaknya.  
```
qm set 205 --memory 1024 --cores 1 --onboot 1
```
> Penjelasan: RAM, inti, dan nyalakan otomatis saat host hidup.
```
qm start 205
```
> Penjelasan: Menyalakan klon. Buka Console VM 205 di web Proxmox.
```
qm config 205 | grep net0
```
> Penjelasan: Menampilkan alamat MAC VM (nilai setelah virtio=). Dibutuhkan untuk reservasi IP di MikroTik.

**TERMINAL VM BARU** | Konsol VM baru (205), login lalu su -

```
hostnamectl set-hostname vault
```
> Penjelasan: Memberi nama host sesuai peta.
```
nano /etc/hosts
```
> Penjelasan: Ganti nama lama pada baris 127.0.1.1 menjadi vault.
```
dpkg-reconfigure openssh-server
```
> Penjelasan: Membuat kunci host SSH baru dan menyalakan ulang SSH. Wajib, karena kunci templat sudah
dihapus (49.3).  
Alamat tetap lewat MikroTik (DNS tetap otomatis dari DHCP, sehingga tetap menunjuk AdGuard). Dari Terminal  
di WinBox atau SSH ke MikroTik:  

**TERMINAL MIKROTIK** | Terminal WinBox atau SSH ke 192.168.88.1

```
/ip dhcp-server print
```
> Penjelasan: Melihat nama server DHCP (misalnya defconf) untuk dipakai di bawah.
2  
[admin@MikroTik] &gt; /ip dhcp-server lease add address=192.168.88.24  
mac-address=AA:BB:CC:DD:EE:FF server=defconf comment=vault  
> Penjelasan: Mereservasi 192.168.88.24 untuk MAC VM. Ganti MAC dan nama server. Alamat di luar rentang pool
100-254 untuk lease statis umumnya diterima [BELUM PASTI]; bila ditolak, atur IP statis di Debian.  

**TERMINAL VM BARU** | Konsol VM baru, sebagai root

```
systemctl restart networking
```
> Penjelasan: Meminta alamat baru. Bila tidak berubah, jalankan reboot.
```
ip -4 -br a
```
> Penjelasan: Memastikan alamat 192.168.88.24 dipakai.
```
ping -c1 192.168.88.253 && ping -c1 1.1.1.1
```
> Penjelasan: Uji DNS lokal dan internet.
TIPS  
Pasang agen Beszel (Suplemen 3 Bab 33) pada setiap VM baru dan tambahkan monitor di Uptime Kuma. Disk besar  
untuk data (misalnya Nextcloud kelak) sebaiknya disk kedua, bukan memperbesar disk sistem.  

## 49.5 Sisi klien: mengelola VM dari Windows, Android, iPhone

Perangkat Cara Catatan  
Windows Browser ke https://192.168.88.10:8006 untuk Proxmox;  
PowerShell: ssh &lt;USER&gt;@192.168.88.24 untuk VM  
Konsol web (noVNC) tetap bisa dipakai bila  
SSH terkunci firewall  
Android Chrome ke alamat Proxmox lewat Tailscale (rute subnet dari  
router-vm aktif)  
Cukup untuk melihat status, menyalakan  
atau mematikan VM; pekerjaan panjang di  
laptop  
iPhone Safari ke alamat yang sama dengan Tailscale aktif;  
peringatan sertifikat Proxmox perlu disetujui  
Sama seperti Android  
CATATAN  
Aplikasi pihak ketiga untuk Proxmox ada di toko aplikasi, tetapi tidak dibahas di sini karena kebijakan buku ini  
memakai alat resmi dan peramban.
