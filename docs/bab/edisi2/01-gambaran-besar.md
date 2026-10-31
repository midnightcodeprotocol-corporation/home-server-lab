# Bab 1. Gambaran Besar dan Konsep Dasar

Buku ini memandu Anda membangun home server lab dari nol: memasang Proxmox VE di mesin asli (Lenovo ThinkCentre M710q),  
menyiapkan jaringan MikroTik, lalu memasang layanan satu per satu:  
AdGuard Home, Tailscale, Docker, Portainer, Git pribadi, Nextcloud, Home Assistant, dashboard,  
Kubernetes, GitOps, dan Renovate. Setiap langkah disertai penjelasan (apa yang dilakukan dan  
mengapa), dan setiap bab diakhiri bagian Kasus Nyata dari masalah yang benar-benar terjadi pada  
proyek ini.  
CATATAN - Perubahan di Edisi 2  
Edisi 2 ini mengikuti sistem Debian GNU/Linux 13 "trixie" untuk semua VM, dan semua perintah ditulis tanpa  
sudo (login sebagai root). Alasannya dijelaskan di 1.7. Alamat jaringan memakai jaringan MikroTik  
192.168.88.0/24.  

## 1.1 Tujuan proyek

• Belajar mengelola server tanpa takut merusak mesin asli.  
• Memakai perangkat yang sudah ada (ThinkCentre M710q, NVMe 500 GB, HDD 2 TB, STB, router) tanpa biaya tambahan.  
• Menyiapkan konfigurasi, catatan, dan backup sejak awal, supaya server yang rusak atau diinstal ulang bisa dipulihkan dari backup.  

## 1.2 Perangkat yang dipakai

Perangkat Peran Keterangan  
IndiHome Sumber internet Tidak ada kabel LAN yang bisa dipakai, jadi uplink lewat  
WiFi.  
TP-Link TL-WR840N Router penerima Mode WISP: menerima WiFi IndiHome, memberi kabel LAN  
ke MikroTik.  
MikroTik RB750GL Router utama Gateway, DHCP, dan firewall jaringan rumah  
(192.168.88.0/24).  
TP-Link TL-WR820N Access Point Mode AP di belakang MikroTik untuk WiFi rumah.  
TP-Link LiteWave LS1005 Switch Memperbanyak port LAN.  
STB HG680 (Armbian) DNS utama + Tailscale AdGuard Home dan Tailscale, selalu hidup, di luar Proxmox.  
Lenovo ThinkCentre M710q Server Proxmox Core i5-6500T; RAM 16+8 GB (Linux melaporkan 23 GiB, BIOS/MemTest belum diverifikasi); NVMe Samsung 476,9 GB; Proxmox berjalan, VT-x/KVM aktif. IP sementara 192.168.0.200, target rumah 192.168.88.10.
HDD 2 TB Disk data / backup Disk kedua (bay 2,5" atau USB), dipakai untuk datastore backup.  

## 1.3 Prinsip: yang kritis dipisah dari yang bereksperimen

Server Proxmox akan sering di-reboot, di-update, dan kadang rusak karena eksperimen. Karena itu  
layanan yang menjaga internet dan akses jarak jauh rumah tidak ditaruh di dalamnya.  
Selalu hidup (di luar Proxmox) Boleh sering diutak-atik (di Proxmox)  
MikroTik, TP-Link penerima, TP-Link AP VM Debian 13: Docker, Portainer, Git (Forgejo), Nextcloud,  
dashboard, Renovate  
AdGuard Home utama di STB Container AdGuard Home kedua (pasangan failover)  
Tailscale (subnet router) di STB VM Home Assistant OS  
VM k3s untuk Kubernetes dan GitOps  
TrueNAS (nanti, di mesin asli)  

## 1.4 Topologi jaringan

IndiHome (uplink WiFi)  
TL-WR840N (mode WISP)  
LAN 192.168.0.1  
MikroTik RB750GL  
ether1 = 192.168.0.100 (dari WR840N)  
LAN 192.168.88.1/24, DHCP .100-.254  
STB HG680  
AdGuard + Tailscale  
192.168.88.253  
TL-WR820N (AP)  
mode Access Point  
192.168.88.2  
Switch  
LiteWave LS1005  
(opsional)  
Mesin Proxmox  
192.168.88.10  
(ThinkCentre M710q)  
Garis = kabel LAN (kecuali uplink IndiHome)  
Gambar 1.1 - Topologi jaringan rumah (skematis). Alamat IP adalah rencana yang dipakai di buku ini.  

## 1.5 Konsep dasar yang sering membingungkan

Bagian ini menjawab hal-hal yang biasanya membuat orang berhenti di tengah instalasi. Baca sekali, lalu  
rujuk lagi saat perlu.  
Istilah Penjelasan sederhana Contoh di proyek ini  
IP address Alamat sebuah perangkat di jaringan, seperti nomor rumah. 192.168.88.10 = Proxmox  
CIDR /24 Menunjukkan ukuran jaringan. /24 berarti tiga angka  
pertama sama untuk semua perangkat (192.168.88.x).  
Setara subnet mask 255.255.255.0.  
192.168.88.10/24  
Gateway Perangkat tempat semua lalu lintas ke luar jaringan dititipkan  
(biasanya router).  
MikroTik: 192.168.88.1  
Istilah Penjelasan sederhana Contoh di proyek ini  
DNS Penerjemah nama situs (google.com) menjadi alamat IP. AdGuard: 192.168.88.253  
DHCP Layanan yang membagikan IP otomatis ke perangkat yang  
baru tersambung.  
MikroTik, pool .100 sampai .254  
Static lease Pengaturan DHCP agar satu perangkat selalu mendapat IP  
yang sama (berdasarkan MAC).  
Proxmox VM, LXC, STB  
MAC address Nomor unik kartu jaringan (contoh BC:24:11:AA:BB:CC).  
Dipakai DHCP untuk mengenali perangkat.  
Lihat di tab Hardware VM  
ISO Berkas salinan DVD instalasi. Dipasang ke VM atau ditulis  
ke USB.  
proxmox-ve_9.2-1.iso  
Root Akun administrator tertinggi di Linux. Login Proxmox, Debian, dan STB  
Shell / Konsol /  
Terminal  
Jendela tempat mengetik perintah teks. Menu Shell di web Proxmox  
Hostname / FQDN Nama komputer / nama lengkap dengan domain. pve / pve.lab.local  
Node Satu server Proxmox di dalam cluster (lab ini hanya satu  
node).  
Node bernama pve  
Bridge (vmbr0) Saklar virtual di dalam Proxmox yang menghubungkan VM  
dan container ke kabel LAN.  
vmbr0 terhubung ke kartu fisik  
VM vs LXC VM = komputer virtual penuh dengan kernel sendiri. LXC =  
container ringan yang berbagi kernel host.  
LXC: AdGuard. VM: Docker,  
HAOS, k3s  
Realm Jenis otentikasi saat login web Proxmox. Pilih Linux PAM standard  
authentication  

## 1.6 Cara membaca kotak di buku ini

Setiap perintah ditulis di kotak gelap bernomor, satu perintah per kotak, dengan penjelasan di  
bawahnya. Isi berkas konfigurasi ditulis di kotak berkas yang punya nama berkas dan nomor baris.  
Contohnya:  

**TERMINAL (login sebagai root)** | Contoh. Dijalankan di Shell Proxmox

```
ip a
```
> Penjelasan: Menampilkan semua kartu jaringan dan alamat IP-nya.
```
ping -c 3 8.8.8.8
```
> Penjelasan: Mengirim 3 paket uji ke 8.8.8.8 untuk memastikan internet tersambung.

**BERKAS: /etc/contoh.conf** | Contoh berkas dengan nomor baris

```
baris_pertama = nilai
baris_kedua = nilai
# komentar
```

Contoh hasil yang benar  
64 bytes from 8.8.8.8: icmp_seq=1 ttl=117 time=24.1 ms  
3 packets transmitted, 3 received, 0% packet loss  
Awalan di kotak Artinya  
# Prompt root di Linux (Proxmox, Debian, STB). Jangan ikut diketik.  
Awalan di kotak Artinya  
$ Prompt user biasa di Linux atau Git Bash.  
C:\&gt; Command Prompt Windows.  
PS&gt; PowerShell Windows.  
&gt; Terminal MikroTik (WinBox: New Terminal).  
CATATAN - Catatan  
Informasi tambahan.  
TIPS - Tips  
Jalan pintas atau kebiasaan baik.  
PERINGATAN - Peringatan  
Langkah yang bisa menghapus data atau memutus koneksi. Baca dulu sebelum menjalankan.  
KASUS NYATA - Contoh  
Gejala: Apa yang terlihat.  
Penyebab: Mengapa terjadi.  
Solusi: Cara memperbaiki.  
Teks seperti &lt;IP-PROXMOX&gt; adalah placeholder yang harus diganti dengan nilai Anda (tanpa tanda  
kurung sudut).  

## 1.7 Tentang sudo dan root

Di buku ini tidak ada perintah yang diawali sudo. Penyebabnya: pada Proxmox, container, dan Armbian  
Anda login sebagai root, dan pada instalasi Debian standar yang diberi password root, program sudo  
bahkan tidak terpasang. Mengetik sudo apt update akan menghasilkan sudo: command not found.  
Cukup ketik apt update.  
Tempat Login sebagai Pakai sudo?  
Shell Proxmox, konsol VM Proxmox root Tidak  
Container LXC root Tidak  
STB Armbian (PuTTY/SSH) root Tidak  
VM Debian 13 (dibuat di Bab 11) root, atau user biasa lalu su - untuk menjadi  
root  
Tidak (sudo tidak  
terpasang)  
KASUS NYATA - Perintah sudo tidak terbaca  
Gejala: Saat mengikuti panduan lama, perintah yang diawali sudo gagal atau tidak dikenali, sedangkan apt  
update langsung jalan.  
Penyebab: Sudah login sebagai root, atau sudo tidak terpasang di Debian 13 yang diinstal dengan password  
root.  
Solusi: Hapus kata sudo dari perintah. Jika di VM Debian Anda login sebagai user biasa, ketik su - lalu  
masukkan password root.  

**TERMINAL (login sebagai root)** | VM Debian 13, hanya jika ingin memakai sudo

```
su -
```
> Penjelasan: Berpindah menjadi root dengan lingkungan root yang lengkap (tanda minus penting). Dipakai di VM
Debian jika login sebagai user biasa.  
```
apt install -y sudo
```
> Penjelasan: Opsional: memasang sudo agar user biasa dapat memakainya.
```
usermod -aG sudo NAMAUSER
```
> Penjelasan: Opsional: memasukkan user ke grup sudo (login ulang agar berlaku).

## 1.8 Cara menjalankan perintah dengan nyaman (copy-paste)

Mengetik panjang di layar fisik server tidak nyaman. Gunakan salah satu cara:  
Cara Langkah Paste  
Shell di web Proxmox Buka https://IP:8006 &gt; pilih node &gt; menu Shell Ctrl+Shift+V  
SSH dari PowerShell Ketik ssh root@192.168.88.10 Klik kanan  
PuTTY Host = IP, port 22, Open Klik kanan  
Layar dan keyboard fisik server Hanya untuk instalasi, darurat, atau sebelum IP jadi Tidak ada
