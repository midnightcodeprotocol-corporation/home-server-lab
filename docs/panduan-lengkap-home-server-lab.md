# Buku Panduan Lengkap Home Server Lab

## Edisi Terpadu 2026.11 - 1 November 2026

Panduan menyeluruh dari persiapan komputer, jaringan, instalasi Proxmox, VM/LXC, layanan, keamanan, backup, pemantauan, hingga pemulihan. Edisi ini menggabungkan Bab 1-56, lampiran, serta sembilan pengantar dan penutup fase dari materi proyek yang masih berlaku.

> **Status aktual (1 November 2026):** Proxmox VE 9.2.24 berjalan dan sudah diperbarui pada ThinkCentre M710q; kernel aktif `7.0.14-26-pve`. RAM 16+8 GB terbaca Linux sebagai 23 GiB, tetapi BIOS/MemTest86 belum diperiksa. VT-x/KVM aktif setelah perbaikan tanpa monitor melalui `thinklmi`; VT-d tetap Disabled. NVMe Samsung terdeteksi pada 476,9 GB. Jaringan host sementara `192.168.0.200/24`, gateway/DNS `192.168.0.1`, sampai tersambung kembali ke MikroTik. Template Debian 13 VM 200 dan CT 100 sudah dibuat dan diverifikasi melalui SSH. Nama aktual `Tamplate-VM`/`Tamplate-CT` (kemungkinan typo). VM: 1 vCPU, 2 GiB RAM, disk 32 GiB, QEMU Agent aktif pada konfigurasi. CT: 1 vCPU, RAM/swap 512 MiB, disk 8 GiB, unprivileged, nesting, DHCP. Paket VM, guest layanan, backup, HDD, dan clone belum diuji.

## Sebelum mulai

- Bacalah bab berurutan dan kerjakan satu perubahan pada satu waktu.
- Gunakan konfigurasi di direktori `konfigurasi/` sebagai sumber YAML/Compose yang benar; sebagian teks sumber berasal dari ekstraksi dan format kodenya perlu dicocokkan.
- Jangan menaruh password, token, private key, serial disk, atau konfigurasi rahasia di GitHub, buku, tangkapan layar, atau chat.
- Operasi instalasi, partisi, firewall, SSH, hapus guest, dan ubah jaringan dapat memutus akses atau menghapus data. Baca peringatan dan siapkan console lokal sebelum menekan Apply.
- Jika hasil berbeda dari petunjuk, berhenti, simpan pesan error persis, dan catat di `catatan/hasil-uji.md`.
- Label **[BELUM PASTI]** harus diverifikasi pada perangkat/versi aktual. Panduan ini bukan bukti bahwa server sudah berhasil dipasang.

## Peta jaringan aktual dan target

[[ILUSTRASI:JARINGAN]]

Garis dan kotak menjelaskan jaringan rumah yang sudah berjalan dan status host Proxmox. Host saat ini berada di jaringan sementara `192.168.0.200/24`; `192.168.88.10` adalah alamat target setelah disambungkan ke MikroTik. Jangan membuka panel admin ke internet. Akses Tailscale dan aplikasi privat belum aktif sampai dikonfigurasi dan diuji.

## Koreksi keamanan dan versi terbaru

Revisi 4 mencatat koreksi Tailscale, PostgreSQL pada n8n, pendaftaran Vaultwarden, dan `.gitignore`. Revisi 5 mencatat DNS/update, KVM/VT-x, dan diagnosis jaringan. Revisi 6 mencatat template Debian 13 VM 200 dan CT 100 serta persiapan perpindahan host ke MikroTik. Baca [Revisi 4](docs/bab/REVISI-4.md), [Revisi 5](docs/bab/REVISI-5.md), dan [Revisi 6](docs/bab/REVISI-6.md). Contoh email Tailscale tetap placeholder dan harus diganti sebelum menerapkan kebijakan.

## Daftar isi



<!-- SOURCE: docs/bab/edisi2/01-gambaran-besar.md -->

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

| Perangkat | Peran | Keterangan |
| --- | --- | --- |
| IndiHome | Sumber internet | Tidak ada kabel LAN yang bisa dipakai, jadi uplink lewat WiFi. |
| TP-Link TL-WR840N | Router penerima | Mode WISP: menerima WiFi IndiHome, memberi kabel LAN ke MikroTik. |
| MikroTik RB750GL | Router utama | Gateway, DHCP, dan firewall jaringan rumah (192.168.88.0/24). |
| TP-Link TL-WR820N | Access Point | Mode AP di belakang MikroTik untuk WiFi rumah. |
| TP-Link LiteWave LS1005 | Switch | Memperbanyak port LAN. |
| STB HG680 (Armbian) | DNS utama + Tailscale | AdGuard Home dan Tailscale, selalu hidup, di luar Proxmox. |
| Lenovo ThinkCentre M710q | Server Proxmox | Core i5-6500T; RAM 16+8 GB (Linux melaporkan 23 GiB; BIOS/MemTest belum diverifikasi); NVMe Samsung 476,9 GB; Proxmox berjalan, VT-x/KVM aktif. |
| HDD 2 TB | Disk data / backup | Disk kedua (bay 2,5" atau USB), dipakai untuk datastore backup. |

## 1.3 Prinsip: yang kritis dipisah dari yang bereksperimen

Server Proxmox akan sering di-reboot, di-update, dan kadang rusak karena eksperimen. Karena itu layanan yang menjaga internet dan akses jarak jauh rumah tidak ditaruh di dalamnya.

| Selalu hidup (di luar Proxmox) | Boleh sering diutak-atik (di Proxmox) |
| --- | --- |
| MikroTik, TP-Link penerima, TP-Link AP | VM Debian 13: Docker, Portainer, Git (Forgejo), Nextcloud, dashboard, Renovate |
| AdGuard Home utama di STB | Container AdGuard Home kedua (pasangan failover) |
| Tailscale (subnet router) di STB | VM Home Assistant OS |
|  | VM k3s untuk Kubernetes dan GitOps |
|  | TrueNAS (nanti, di mesin asli) |

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

Bagian ini menjawab hal-hal yang biasanya membuat orang berhenti di tengah instalasi. Baca sekali, lalu rujuk lagi saat perlu.

| Istilah | Penjelasan sederhana | Contoh di proyek ini |
| --- | --- | --- |
| IP address | Alamat sebuah perangkat di jaringan, seperti nomor rumah. | 192.168.88.10 = Proxmox |
| CIDR /24 | Menunjukkan ukuran jaringan. /24 berarti tiga angka pertama sama untuk semua perangkat (192.168.88.x). Setara subnet mask 255.255.255.0. | 192.168.88.10/24 |
| Gateway | Perangkat tempat semua lalu lintas ke luar jaringan dititipkan (biasanya router). | MikroTik: 192.168.88.1 |
| DNS | Penerjemah nama situs (google.com) menjadi alamat IP. | AdGuard: 192.168.88.253 |
| DHCP | Layanan yang membagikan IP otomatis ke perangkat yang baru tersambung. | MikroTik, pool .100 sampai .254 |
| Static lease | Pengaturan DHCP agar satu perangkat selalu mendapat IP yang sama (berdasarkan MAC). | Proxmox VM, LXC, STB |
| MAC address | Nomor unik kartu jaringan (contoh BC:24:11:AA:BB:CC). Dipakai DHCP untuk mengenali perangkat. | Lihat di tab Hardware VM |
| ISO | Berkas salinan DVD instalasi. Dipasang ke VM atau ditulis ke USB. | proxmox-ve_9.2-1.iso |
| Root | Akun administrator tertinggi di Linux. | Login Proxmox, Debian, dan STB |
| Shell / Konsol / Terminal | Jendela tempat mengetik perintah teks. | Menu Shell di web Proxmox |
| Hostname / FQDN | Nama komputer / nama lengkap dengan domain. | pve / pve.lab.local |
| Node | Satu server Proxmox di dalam cluster (lab ini hanya satu node). | Node bernama pve |
| Bridge (vmbr0) | Saklar virtual di dalam Proxmox yang menghubungkan VM dan container ke kabel LAN. | vmbr0 terhubung ke kartu fisik |
| VM vs LXC | VM = komputer virtual penuh dengan kernel sendiri. LXC = container ringan yang berbagi kernel host. | LXC: AdGuard. VM: Docker, HAOS, k3s |
| Realm | Jenis otentikasi saat login web Proxmox. | Pilih Linux PAM standard authentication |

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


<!-- SOURCE: docs/bab/edisi2/02-unduhan-dan-alat.md -->

# Bab 2. Daftar Unduhan dan Alat

Semua perangkat lunak yang dipakai di buku ini beserta tautan resminya. Tautan bisa berubah; jika
mendapat halaman 404, buka halaman induknya dan cari nama berkasnya.

## 2.1 Sistem operasi dan ISO

Nama Fungsi Tautan
Debian 13 (netinst, amd64) ISO instalasi VM server (Docker, k3s,
dll)
debian-13.7.0-amd64-netinst.iso
Daftar rilis Debian Jika berkas di atas berganti versi, lihat
daftarnya
cdimage.debian.org/.../iso-cd/
Proxmox VE ISO Server virtualisasi (unduh Proxmox VE
9.2 atau lebih baru)
proxmox.com/en/downloads
Arsip ISO Proxmox Daftar langsung berkas ISO dan
checksum
enterprise.proxmox.com/iso/
Image cloud Debian Untuk template cloud-init (opsional) cloud.debian.org/images/cloud/
Home Assistant OS VM Home Assistant (berkas
haos_ova-\*.qcow2.xz)
github.com/home-assistant/operating-system/re
leases
Armbian untuk STB Image Armbian Amlogic (ophub) github.com/ophub/amlogic-s9xxx-armbian
TrueNAS NAS (nanti, di mesin asli) truenas.com

## 2.2 Alat di Windows

Nama Fungsi Tautan
Rufus Membuat USB bootable dari ISO (Windows) rufus.ie
balenaEtcher Membuat USB bootable (alternatif,
Windows/Mac/Linux)
etcher.balena.io
Ventoy USB multi-ISO: salin ISO ke flashdisk tanpa
menulis ulang
ventoy.net
WinBox Mengelola MikroTik mikrotik.com/download
PuTTY SSH dari Windows chiark.greenend.org.uk/~sgtatham/putty
WinSCP Menyalin berkas ke/dari server (SFTP) winscp.net
Git untuk Windows Perintah git dan Git Bash git-scm.com

## 2.3 Aplikasi server

Aplikasi Fungsi Tautan
AdGuard Home DNS pemblokir iklan adguard.com/adguard-home
Pi-hole Alternatif pemblokir iklan pi-hole.net
Tailscale VPN mesh; konsol admin tailscale.com/download , admin
Docker Engine Menjalankan container docs.docker.com/engine/install/debian
Portainer Antarmuka web untuk Docker docs.portainer.io
Forgejo Git pribadi forgejo.org
Nextcloud Cloud pribadi nextcloud.com
Home Assistant Otomasi rumah home-assistant.io
Homepage Dashboard pintasan gethomepage.dev
dnsdist Pembagi DNS (untuk ide balancer) dnsdist.org
k3s Kubernetes ringan k3s.io
Flux GitOps fluxcd.io
Renovate Pembaruan otomatis docs.renovatebot.com

## 2.4 Memverifikasi ISO yang diunduh

ISO yang rusak atau terpotong adalah penyebab umum instalasi gagal. Bandingkan nilai SHA256 berkas
Anda dengan nilai yang tertulis di halaman unduhan.

**COMMAND PROMPT WINDOWS** | Windows

```
certutil -hashfile "C:\Users\NAMA\Downloads\proxmox-ve_9.2-1.iso" SHA256
```
> Penjelasan: Menghitung sidik jari (hash) berkas. Hasilnya harus sama persis dengan SHA256 di halaman
unduhan Proxmox. Ganti jalur dan nama berkas sesuai milik Anda.


<!-- SOURCE: docs/bab/edisi2/03-jaringan-mikrotik.md -->

# Bab 3. Fondasi Jaringan Rumah (MikroTik)

> [!NOTE]
> **Peta Edisi 2, diselaraskan dengan Revisi 3:** STB HG680 .253 menjalankan AdGuard Home saja. Tailscale subnet router ditunda sampai STB 2 tersedia; CT103 adalah pilihan sementara bila diperlukan. Daftar guest dan alamat terbaru ada di [peta penempatan Bab 48](../suplemen/48-peta-penempatan.md) dan [data/guest.yaml](../../../data/guest.yaml).


Seluruh bab berikutnya mengandalkan jaringan MikroTik 192.168.88.0/24. Bab ini menyiapkan
fondasinya dan membuat "resep" yang akan dipakai berulang: reservasi IP (static lease), pengaturan DNS
di DHCP, dan pengamanan dasar. Jika MikroTik Anda sudah terkonfigurasi, baca 3.2, 3.5, dan 3.6 lalu
lanjutkan.

## 3.1 Alur koneksi

1. Sinyal IndiHome diterima TL-WR840N (mode WISP). Port LAN-nya memberi alamat 192.168.0.x.
2. Kabel dari port LAN TL-WR840N masuk ke ether1 MikroTik, yang meminta alamat lewat DHCP client
(contoh 192.168.0.100).
3. MikroTik membuat jaringan lokal 192.168.88.0/24 dan membagikan alamat .100 sampai .254.
4. TL-WR820N dalam mode Access Point memberi WiFi untuk perangkat rumah.
5. STB HG680 dan server Proxmox dicolok ke port LAN MikroTik (atau switch) dan diberi alamat tetap.

## 3.2 Rencana alamat IP

Pembagian alamat yang rapi menghindari bentrok dan membuat catatan mudah. Rentang DHCP MikroTik
adalah .100 sampai .254, jadi semua perangkat penting diberi alamat di bawah .100 (diluar pool), lewat
static lease.
Alamat Perangkat Cara mendapat alamat
192.168.88.1 MikroTik (gateway, DHCP, DNS relay) Statis di router
192.168.88.2 TL-WR820N (Access Point) Statis di router AP
192.168.88.10 Proxmox (mesin asli (ThinkCentre M710q)) Statis di Proxmox
(/etc/network/interfaces)
192.168.88.11 AdGuard Home kedua (LXC 101) Static lease MikroTik
192.168.88.12 Samba / file share (LXC 102) Static lease MikroTik
192.168.88.20 VM Debian 13 (Docker, Portainer, Git, Nextcloud,
dashboard)
Static lease MikroTik
192.168.88.21 VM Home Assistant OS Static lease MikroTik
192.168.88.22 VM k3s (Kubernetes) Static lease MikroTik
192.168.88.253 STB HG680 (AdGuard Home utama saja) Static lease MikroTik
192.168.88.100 - .254 Laptop, HP, dan perangkat lain DHCP otomatis
IndiHome (uplink WiFi)
TL-WR840N (mode WISP)
LAN 192.168.0.1
MikroTik RB750GL
ether1 = 192.168.0.100 (dari WR840N)
LAN 192.168.88.1/24, DHCP .100-.254
STB HG680
AdGuard Home saja
192.168.88.253
TL-WR820N (AP)
mode Access Point
192.168.88.2
Switch
LiteWave LS1005
(opsional)
Mesin Proxmox
192.168.88.10
(lab: VM di laptop)
Garis = kabel LAN (kecuali uplink IndiHome)
Gambar 3.1 - Posisi tiap perangkat pada jaringan 192.168.88.0/24.

## 3.3 TL-WR840N sebagai penerima (mode WISP)

Mode WISP membuat router menerima internet lewat WiFi (bukan kabel), lalu membaginya lewat port
LAN. Cocok karena IndiHome tidak menyediakan kabel LAN.
1. Sambungkan laptop ke router dan buka http://192.168.0.1 atau http://tplinkwifi.net.
> Penjelasan: Alamat bawaan TP-Link TL-WR840N adalah 192.168.0.1. Nama tplinkwifi.net berfungsi bila laptop
tersambung langsung ke router.
2. Buat password admin baru saat diminta.
> Penjelasan: Router baru meminta password admin pertama kali. Catat di password manager.
3. Buka Quick Setup (atau Operation Mode) dan pilih WISP.
> Penjelasan: WISP = Wireless ISP: sisi "WAN" router memakai radio WiFi untuk terhubung ke router lain.
4. Pilih Scan, pilih SSID IndiHome, masukkan password WiFi-nya.
> Penjelasan: Router akan terhubung ke WiFi IndiHome sebagai klien.
5. Biarkan DHCP server router ini aktif.
> Penjelasan: MikroTik akan meminta alamat dari DHCP ini di ether1.
6. Simpan, tunggu restart, tes internet dari perangkat yang terhubung ke port LAN-nya.
> Penjelasan: Jika internet bekerja di sini, sisi penerima sudah benar.
CATATAN
Menu bisa berbeda antar versi firmware. Cari tulisan "Operation Mode", "WISP", atau "Client Router".

## 3.4 MikroTik RB750GL: pengaturan awal

Gunakan WinBox. Sambungkan kabel laptop ke ether2 (bukan ether1, yang ke WAN), buka WinBox, tab
Neighbors, klik MAC address perangkat, lalu Connect. Login admin dengan password kosong
(konfigurasi bawaan).
1. Perbarui RouterOS: System &gt; Packages &gt; Check For Updates, channel stable, Download and
Install.
> Penjelasan: Versi stabil yang dipakai proyek ini adalah 6.49.23. Pembaruan menutup celah keamanan dan
memperbaiki bug.
2. Pastikan IP &gt; DHCP Client pada ether1 berstatus \*bound\*.
> Penjelasan: Artinya MikroTik sudah mendapat alamat dari TL-WR840N.
3. Uji internet: Tools &gt; Ping ke 8.8.8.8 dan google.com.
> Penjelasan: Ping ke 8.8.8.8 menguji koneksi. Ping ke google.com menguji DNS. Jika yang kedua gagal, atur
DNS di 3.6.
4. Pastikan IP &gt; Addresses punya 192.168.88.1/24 di bridge/LAN dan IP &gt; DHCP Server memakai
pool 192.168.88.100-254.
> Penjelasan: Inilah jaringan lokal Anda. Alamat .1 adalah gateway.
5. Pastikan IP &gt; Firewall &gt; NAT memiliki aturan masquerade pada interface ether1.
> Penjelasan: Masquerade membuat semua perangkat LAN berbagi satu alamat ke luar. Tanpa ini perangkat LAN
tidak bisa ke internet.

**TERMINAL MIKROTIK** | WinBox &gt; New Terminal

```
/system backup save name=awal-ok
```
> Penjelasan: Menyimpan backup biner (termasuk password) di Files router.
```
/export file=config-awal-ok
```
> Penjelasan: Mengekspor konfigurasi sebagai teks yang bisa dibaca di Files router.
Buka menu Files, klik kanan kedua berkas dan Download ke laptop. Simpan di folder aman sebagai titik
pemulihan.

## 3.5 Resep: reservasi IP (static lease) untuk setiap perangkat

Resep ini dipakai di hampir semua bab. Tujuannya: perangkat selalu mendapat IP yang sama, dan semua
alamat tercatat di satu tempat (MikroTik). Ada dua cara.
Cara A: dari lease yang sudah ada
1. Nyalakan perangkat (VM/LXC/STB) dan biarkan mendapat IP lewat DHCP.
> Penjelasan: MikroTik otomatis mencatatnya sebagai lease dinamis.
2. WinBox: IP &gt; DHCP Server &gt; Leases. Cari perangkat berdasarkan MAC atau hostname.
> Penjelasan: Kolom Status berisi bound.
3. Klik kanan baris itu &gt; Make Static.
> Penjelasan: Lease berubah menjadi statis (tanda D hilang).
4. Klik dua kali baris, ubah Address menjadi IP rencana (contoh 192.168.88.20), isi Comment, OK.
> Penjelasan: Setelah itu perangkat memperbarui lease (reboot perangkat atau ipconfig /renew / restart
jaringan) dan mendapat IP baru.
Cara B: menambah manual lewat terminal

**TERMINAL MIKROTIK** | WinBox &gt; New Terminal

```
/ip dhcp-server lease add address=192.168.88.20 mac-address=BC:24:11:AA:BB:CC
```
> Penjelasan: Membuat reservasi: perangkat bermac itu selalu mendapat 192.168.88.20. Ganti alamat dan MAC.
```
/ip dhcp-server lease set [find address=192.168.88.20] comment="vm-debian-docker"
```
> Penjelasan: Memberi komentar pada reservasi tersebut agar mudah dikenali.
```
/ip dhcp-server lease print
```
> Penjelasan: Menampilkan daftar lease untuk dicek.
TIPS
MAC address VM/LXC ada di Proxmox: pilih VM &gt; Hardware &gt; Network Device (kolom
virtio=BC:24:11:...), atau CT &gt; Network.
PERINGATAN
Jika terminal menolak perintah di atas karena baris terlalu panjang, tempel dalam dua langkah, atau tambahkan
lewat WinBox (IP &gt; DHCP Server &gt; Leases &gt; tombol + ).

## 3.6 Mengatur DNS pada DHCP MikroTik

DHCP membagikan alamat DNS ke setiap klien. Di sinilah Anda mengarahkan seluruh rumah ke AdGuard
Home.
WinBox - IP &gt; DHCP Server &gt; Networks &gt; 192.168.88.0/24
Address 192.168.88.0/24
Gateway 192.168.88.1
Netmask 24
1 DNS Servers 192.168.88.253, 192.168.88.11
Domain lan
Apply OK
Gambar 3.2 - Ilustrasi skematis jendela DHCP Network pada WinBox. Kolom bernomor 1 diisi dengan dua DNS (AdGuard
utama lalu cadangan).

**TERMINAL MIKROTIK** | WinBox &gt; New Terminal

```
/ip dhcp-server network print
```
> Penjelasan: Melihat nomor baris jaringan DHCP (biasanya 0).
```
/ip dhcp-server network set 0 dns-server=192.168.88.253
```
> Penjelasan: Mengisi DNS hanya AdGuard utama dulu. DNS kedua ditambah di Bab 13.
```
/ip dns set servers=192.168.88.253 allow-remote-requests=no
```
> Penjelasan: Mengatur DNS yang dipakai router sendiri (untuk update, NTP). allow-remote-requests=no
agar router tidak menjadi DNS terbuka.
PERINGATAN
Jangan mengisi DNS publik (8.8.8.8) sebagai DNS kedua di DHCP. Klien Windows memakai DNS secara
bergantian, sehingga sebagian permintaan lolos tanpa pemblokiran iklan.

## 3.7 TL-WR820N sebagai Access Point

1. Hubungkan laptop langsung ke router, buka halaman admin.
> Penjelasan: Alamat bawaan biasanya 192.168.0.1 atau 192.168.1.1.
2. Ubah Operation Mode menjadi Access Point.
> Penjelasan: Dalam mode AP, router hanya menjadi pemancar WiFi, bukan router.
3. Matikan DHCP server router ini.
> Penjelasan: MikroTik yang membagi alamat. Dua DHCP di satu jaringan menyebabkan bentrok.
4. Beri IP statis 192.168.88.2, gateway 192.168.88.1.
> Penjelasan: Agar halaman admin AP selalu bisa dibuka di 192.168.88.2.
5. Atur nama WiFi dan password.
> Penjelasan: Gunakan WPA2/WPA3 dan password kuat.
6. Colok kabel dari MikroTik/switch ke port LAN AP (bukan port WAN/Internet).
> Penjelasan: Port WAN akan mengaktifkan fungsi router yang sudah dimatikan dan membuat jaringan ganda.

## 3.8 Pengamanan dasar MikroTik

PERINGATAN
Lakukan lewat kabel LAN dan buat backup dulu. Kesalahan membatasi alamat bisa mengunci Anda dari router.

**TERMINAL MIKROTIK** | WinBox &gt; New Terminal

```
/user set admin password=GANTI_PASSWORD_KUAT
```
> Penjelasan: Mengganti password admin (jangan biarkan kosong).
```
/ip service disable telnet,ftp,api,api-ssl,www-ssl
```
> Penjelasan: Mematikan layanan yang tidak dipakai (pintu masuk yang tak perlu).
```
/ip service set winbox address=192.168.88.0/24
```
> Penjelasan: Membatasi WinBox hanya dari jaringan lokal.
```
/ip service set ssh address=192.168.88.0/24
```
> Penjelasan: Membatasi SSH hanya dari jaringan lokal.
```
/tool mac-server set allowed-interface-list=none
```
> Penjelasan: Mematikan login lewat MAC address.
```
/tool mac-server mac-winbox set allowed-interface-list=none
```
> Penjelasan: Mematikan WinBox lewat MAC address.
```
/ip neighbor discovery-settings set discover-interface-list=none
```
> Penjelasan: Mematikan pengumuman keberadaan router ke jaringan.
```
/ip service print
```
> Penjelasan: Memeriksa hasil: layanan yang mati bertanda X.
CATATAN
Pada proyek ini layanan www (port 80, WebFig) sengaja dibiarkan aktif agar router dapat dibuka lewat browser,
termasuk dari jauh setelah Tailscale terpasang. Untuk lebih ketat: /ip service set www
address=192.168.88.0/24. Setelah mematikan MAC server, WinBox hanya bisa dibuka dengan IP
(192.168.88.1), bukan lagi lewat MAC.

## 3.9 Kasus nyata pada jaringan rumah

KASUS NYATA - Router penerima ternyata di belakang router lain
Gejala: TL-WR820N menunjukkan WAN 192.168.1.7 dengan gateway 192.168.1.1; perangkat di belakangnya
masih mendapat 192.168.1.x.
Penyebab: Router itu mengambil internet lewat WAN router lain (double NAT). Alamat 192.168.2.100 yang
tampak adalah IP milik router perantara.
Solusi: Gambar urutan perangkat dulu. Sambungkan sesuai Gambar 1.1: penerima WISP -&gt; MikroTik -&gt; AP.
KASUS NYATA - Password admin tidak diterima di halaman router yang tampak sama
Gejala: 192.168.1.1 dan 192.168.2.1 sama-sama menampilkan TP-Link TL-WR820N, tetapi password dari
salah satunya ditolak di yang lain.
Penyebab: Itu dua router berbeda (atau satu router dilihat dari dua jaringan); password dan pengaturannya
terpisah.
Solusi: Beri label fisik pada tiap router dan catat alamatnya. Setelah skema akhir, setiap router punya IP tetap
yang tercatat di Bab 3.2.
KASUS NYATA - Setelah ipconfig /release WiFi laptop terputus
Gejala: Laptop kehilangan koneksi dan IP-nya hilang.
Penyebab: ipconfig /release melepas alamat tanpa memintanya kembali.
Solusi: Jalankan ipconfig /renew, atau matikan-nyalakan adapter WiFi. Untuk menguji DNS baru cukup
ipconfig /renew.
KASUS NYATA - Tidak ada kabel LAN dari IndiHome
Gejala: Router IndiHome tidak menyediakan port LAN yang bisa dipakai.
Penyebab: Hanya WiFi yang tersedia.
Solusi: Pakai TL-WR840N mode WISP (3.3), lalu kabel dari port LAN-nya ke ether1 MikroTik.


<!-- SOURCE: docs/bab/edisi2/04-instal-proxmox-satu-model.md -->

# Bab 4. Instal Proxmox di Mesin Asli (Satu Model)

## 4.1 Keputusan: satu model saja

Proxmox VE dipasang **langsung di mesin asli** (Lenovo ThinkCentre M710q). Hasil akhirnya server Proxmox dengan web di port 8006, disk sistem di NVMe 500 GB.

| Pada Edisi 2/3 | Pada Revisi 3 | Alasan |
|---|---|---|
| Model A: Proxmox di VM VMware | **Dihapus** | Mesin asli sudah ada; lab nested lambat dan tidak bisa dipindah ke mesin asli |
| Model B: mesin asli | **Satu-satunya model** | Performa penuh, fitur perangkat keras (passthrough, sensor, Wake-on-LAN) tersedia |
| Model C: instal ke disk dulu, lalu dipindah | **Dihapus** | Mesin asli bisa boot dari USB; tidak perlu memindah disk dan memperbaiki nama kartu jaringan |

Bab 5 dan Bab 7 (serta Bab 29) tetap ada sebagai penanda singkat agar nomor bab dan rujukan silang tidak bergeser.

## 4.2 Urutan kerja

| Langkah | Bab |
|---|---|
| Kenali mesin: spesifikasi, RAM, disk, BIOS | Bab 27 |
| Siapkan perangkat dan USB bootable, boot dari USB | Bab 6 |
| Instal layar demi layar | Bab 8 (dan Bab 28 untuk nilai khusus M710q) |
| Konfigurasi awal: jaringan, DNS, repository, update | Bab 9 |
| Pasca-instalasi: sensor, SMART, Wake-on-LAN | Bab 30 |


<!-- SOURCE: docs/bab/edisi2/06-instal-proxmox-m710q.md -->

# Bab 6. Instal Proxmox di Lenovo ThinkCentre M710q

> **Revisi 3.** Bab ini sekarang khusus untuk **Lenovo ThinkCentre M710q**. Model A (VMware) dan Model C (instal ke disk dulu) dihapus.

> **Status mesin (31 Oktober 2026):** Proxmox sudah terpasang dan diperbarui. Host sementara berada di `192.168.0.200/24`; `192.168.88.10` adalah alamat target saat kembali ke MikroTik. RAM fisik 16+8 GB dilaporkan Linux sebagai 23 GiB; BIOS/MemTest86 belum diperiksa. Dua HDD 3,5 inci belum terpasang dan memerlukan enclosure berdaya sendiri; enclosure lama belum diuji.

## 6.1 Perangkat yang dibutuhkan

| Kebutuhan | Mesin Anda (M710q) | Catatan |
|---|---|---|
| CPU | Intel Core i5-6500T (4 core, 4 thread, 35 W), mendukung VT-x dan VT-d | Cukup untuk Proxmox; thread terbatas, jangan memberi banyak core ke tiap VM |
| RAM | 16 GB + 8 GB (total fisik 24 GB) | Proxmox melaporkan 23 GiB; BIOS dan MemTest86 belum diperiksa. Lihat Bab 27.1–27.3 |
| Disk sistem | SSD NVMe M.2 500 GB | Proxmox dan disk VM |
| Disk data / backup | Dua HDD 3,5 inci Seagate Surveillance 2 TB | Belum tersambung; gunakan enclosure eksternal berdaya sendiri. Enclosure single-bay belum diuji; lihat Bab 27.4 |
| Jaringan | 1 port Gigabit Ethernet | Kabel ke MikroTik; jangan memakai WiFi |
| Saat instalasi | Monitor, keyboard, flashdisk 8 GB | Setelah itu dikelola lewat web |

## 6.2 Pengaturan BIOS/UEFI

Lengkapnya ada di **Bab 27.5**. Ringkasnya: Intel Virtualization Technology (VT-x) wajib untuk VM; VT-d opsional dan hanya diperlukan untuk passthrough perangkat PCI. Gunakan UEFI, matikan Secure Boot, SATA AHCI, Wake on LAN aktif, After Power Loss = Power On. Masuk BIOS dengan **F1** saat logo Lenovo muncul; menu boot sekali pakai dengan **F12**.

## 6.3 Membuat USB bootable

Siapkan flashdisk minimal 8 GB. Semua isinya akan dihapus. Pilih salah satu alat berikut (tautan di Bab
2.2).
Cara 1: Rufus (Windows)
1. Buka Rufus, pilih flashdisk pada Device.
> Penjelasan: Pastikan itu flashdisk yang benar, bukan HDD.
2. Klik SELECT, pilih berkas proxmox-ve_9.2-1.iso.
3. Partition scheme: GPT untuk mesin UEFI (MBR untuk BIOS lama).
> Penjelasan: Harus sesuai mode boot mesin tujuan.
4. Klik START. Jika muncul pertanyaan mode, pilih Write in DD Image mode.
> Penjelasan: ISO Proxmox adalah image hybrid; mode DD memastikan struktur boot tertulis benar.
5. Tunggu sampai READY.
Cara 2: balenaEtcher
1. Pilih Flash from file &gt; pilih ISO.
2. Select target &gt; pilih flashdisk.
3. Flash! lalu tunggu selesai.
> Penjelasan: Etcher selalu menulis sebagai image mentah.
Cara 3: Ventoy
Pasang Ventoy ke flashdisk sekali, lalu cukup salin berkas ISO ke flashdisk. Praktis untuk banyak ISO,
tetapi pada beberapa mesin installer Proxmox bermasalah lewat Ventoy. Jika instalasi aneh, gunakan
Rufus DD atau Etcher.

## 6.4 Boot dari USB

1. Colokkan USB ke mesin, nyalakan, dan tekan tombol boot menu berkali-kali.
> Penjelasan: Tombol umum: F12, F11, F8, Esc. Tertulis di layar logo.
2. Pilih flashdisk (cari nama USB, kadang berawalan "UEFI:").
> Penjelasan: Pilihan berawalan UEFI cocok bila mesin memakai mode UEFI.
3. Menu instalasi Proxmox muncul. Lanjut ke Bab 8.

## 6.5 Setelah instalasi

• Cabut USB saat mesin restart pertama kali.
• Mesin menampilkan alamat web: https://192.168.88.10:8006. Monitor dan keyboard sudah boleh
dicabut (mesin dikelola lewat web).
• Beberapa BIOS menolak boot tanpa keyboard; jika terjadi, matikan opsi "Halt on keyboard error" di
BIOS.
• Tambahkan disk data (HDD/SSD kedua) lewat Node &gt; Disks (Bab 9.9).
PERINGATAN
Pada layar Target Harddisk pastikan memilih disk yang benar. Disk yang dipilih akan dihapus seluruhnya.
KASUS NYATA - Flashdisk tidak muncul di menu boot
Gejala: Mesin langsung masuk Windows/OS lama atau menampilkan "no bootable device".
Penyebab: Mode boot tidak cocok (GPT/MBR vs UEFI/Legacy), Secure Boot aktif, atau flashdisk belum ditulis
dengan benar.
Solusi: Tulis ulang dengan Rufus (DD mode), ganti skema partisi sesuai mode BIOS, matikan Secure Boot,
dan pilih entri USB yang berawalan UEFI.


<!-- SOURCE: docs/bab/edisi2/08-instalasi-proxmox.md -->

# Bab 8. Instalasi Proxmox VE, Layar demi Layar

Bab ini berlaku untuk instalasi di mesin asli (ThinkCentre M710q). Mesin di-boot dari USB, lalu langkah di installer sama untuk semua mesin.
CATATAN
Gambar di bab ini adalah ilustrasi skematis tata letak layar installer. Tampilan asli bisa sedikit berbeda, tetapi
nama kolom dan urutannya sama.

## 8.1 Siapkan data ini sebelum mulai

Data Nilai yang dipakai di buku Catatan
Hostname (FQDN) pve.lab.local Nama lengkap server. Bagian depan (pve) menjadi nama
node.
Alamat IP/CIDR 192.168.88.10/24 Di luar rentang DHCP MikroTik (.100 - .254).
Gateway 192.168.88.1 Alamat MikroTik.
DNS 192.168.88.253 AdGuard di STB. Jika belum ada, pakai 1.1.1.1.
Password root (buat sendiri, kuat) Simpan di password manager. Jangan sampai lupa.
Email bebas, contoh
admin@lab.local
Untuk notifikasi sistem.

## 8.2 Boot installer

1. Boot dari USB (Bab 6.4).
> Penjelasan: Tekan F12 saat logo Lenovo muncul, lalu pilih flashdisk (entri berawalan UEFI).
2. Pada menu hitam-biru, pilih Install Proxmox VE (Graphical) lalu tekan Enter.
> Penjelasan: Mode grafis memudahkan pemilihan dengan mouse.
Pilihan di menu boot Fungsi
Install Proxmox VE (Graphical) Pilihan normal.
Install Proxmox VE (Terminal UI) Installer berbasis teks. Pakai jika layar grafis bermasalah atau terlalu
kecil.
Install Proxmox VE (Terminal UI, Serial Console) Untuk server tanpa monitor lewat konsol serial.
Advanced Options Debug mode, Rescue Boot (memperbaiki instalasi yang ada), dan
Test memory (Memtest).
PERINGATAN
Jika muncul peringatan No support for KVM virtualization detected, VT-x belum aktif di BIOS (Bab 27.5). Installer tetap bisa
dilanjutkan, tetapi VM di dalam Proxmox nanti tidak bisa berjalan normal.

## 8.3 Layar 1: persetujuan lisensi

Klik I agree. Ini adalah lisensi AGPL v3 Proxmox. Tidak ada yang perlu diisi.

## 8.4 Layar 2: Target Harddisk

Proxmox VE Installer - Target Harddisk
1 Target harddisk /dev/nvme0n1 (465.76GiB, NVMe SSD 500GB)
2 Filesystem (klik Options) ext4
hdsize 465.8
swapsize (otomatis)
maxroot / minfree / maxvz (kosongkan)
Options Next
Gambar 8.1 - Ilustrasi layar Target Harddisk. (1) Pilih disk tujuan. (2) Pilih filesystem lewat tombol Options.
1. Pada Harddisk, pilih disk tujuan.
> Penjelasan: Pilih NVMe 500 GB (nvme0n1). Jangan memilih HDD 2 TB (lepas dari mesin selama instalasi). Seluruh isi disk akan dihapus.
2. Klik Options untuk memilih filesystem.
> Penjelasan: Menentukan cara disk diformat. Lihat tabel di bawah.
3. Klik Next.
Filesystem Cocok untuk Catatan
ext4 (bawaan) Lab, satu disk, RAM kecil Ringan dan sederhana. Membuat storage local
dan local-lvm. Pilihan untuk M710q (satu NVMe).
xfs Alternatif ext4 Mirip ext4.
ZFS (RAID0) Satu disk dengan fitur ZFS Butuh RAM lebih besar; berguna untuk snapshot
dan kompresi.
ZFS (RAID1/mirror) Mesin asli dengan 2 SSD Pelindung dari satu disk rusak. Disarankan di
server asli bila ada 2 disk identik.
ZFS (RAIDZ-1/2/3, RAID10) Mesin asli dengan 3+ disk Butuh RAM besar (16 GB atau lebih).
Btrfs Eksperimen Masih dianggap teknologi preview pada Proxmox.
Opsi lanjutan Arti Nilai
hdsize Total ruang disk yang dipakai instalasi (GB) Biarkan penuh
Opsi lanjutan Arti Nilai
swapsize Ukuran swap (memori cadangan di disk) Biarkan otomatis
maxroot Ukuran maksimum partisi sistem (root) Biarkan
minfree Ruang kosong yang disisakan dalam LVM Biarkan
maxvz Ukuran maksimum storage data local-lvm Biarkan
TIPS
Jika mesin asli memiliki satu SSD kecil (untuk sistem) dan satu HDD besar (untuk data), instal Proxmox hanya
di SSD, lalu tambahkan HDD sebagai storage setelah instalasi (Bab 9.9).

## 8.5 Layar 3: lokasi, zona waktu, dan keyboard

Proxmox VE Installer - Location and Time Zone selection
1 Country Indonesia
2 Time zone Asia/Jakarta
3 Keyboard Layout U.S. English
Previous Next
Gambar 8.2 - Ilustrasi layar lokasi. (1) Negara. (2) Zona waktu. (3) Tata letak keyboard.
1. Country: ketik atau pilih Indonesia.
> Penjelasan: Menentukan mirror unduhan dan zona waktu otomatis.
2. Time zone: Asia/Jakarta (WIB). Gunakan Asia/Makassar atau Asia/Jayapura untuk WITA/WIT.
> Penjelasan: Waktu yang benar penting untuk log, jadwal backup, dan sertifikat.
3. Keyboard Layout: U.S. English.
> Penjelasan: Hampir semua keyboard di Indonesia berlayout US. Salah layout membuat tanda tertentu (|, \, /)
salah saat mengetik password.

## 8.6 Layar 4: password dan email

Proxmox VE Installer - Administration Password and Email Address
1 Password \*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*
1 Confirm \*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*
2 Email admin@lab.local
Previous Next
Gambar 8.3 - Ilustrasi layar password. (1) Password root diisi dua kali. (2) Email administrator.
1. Isi Password dan Confirm dengan password root yang kuat.
> Penjelasan: Password ini dipakai untuk login web dan login konsol/SSH sebagai root. Panjang minimal 8
karakter; gunakan 12 atau lebih.
2. Isi Email.
> Penjelasan: Dipakai Proxmox mengirim peringatan (misalnya backup gagal). Boleh diisi email apa saja jika
belum mengatur pengiriman email.
PERINGATAN
Jangan lupa password root. Memulihkannya butuh boot ke mode rescue.

## 8.7 Layar 5: konfigurasi jaringan manajemen

Proxmox VE Installer - Management Network Configuration
1 Management Interface enp0s31f6 - XX:XX:XX:XX:XX:XX (e1000e)
2 Hostname (FQDN) pve.lab.local
3 IP Address (CIDR) 192.168.88.10 / 24
4 Gateway 192.168.88.1
5 DNS Server 192.168.88.253
Previous Next
Gambar 8.4 - Ilustrasi layar jaringan. Nilai di sini adalah yang dipakai di buku (jaringan MikroTik).
1. Management Interface: pilih kartu jaringan yang tersambung ke LAN.
> Penjelasan: Di VM biasanya hanya satu. Di mesin asli pilih port yang tercolok kabel ke MikroTik. Nama kartu
(contoh enp0s31f6, enp3s0) akan dipakai bridge vmbr0.
2. Hostname (FQDN): pve.lab.local.
> Penjelasan: Nama lengkap server. Bagian pertama menjadi nama node.
3. IP Address (CIDR): 192.168.88.10 / 24.
> Penjelasan: Alamat tetap Proxmox. /24 berarti jaringan 192.168.88.x.
4. Gateway: 192.168.88.1.
> Penjelasan: Alamat MikroTik. Tanpa gateway yang benar Proxmox tidak bisa ke internet.
5. DNS Server: 192.168.88.253 (AdGuard) atau 1.1.1.1 jika AdGuard belum siap.
> Penjelasan: Tanpa DNS yang benar apt update gagal dengan "Temporary failure resolving".
PERINGATAN
Alamat IP, gateway, dan DNS harus berada di jaringan yang sama dengan laptop/komputer Anda (tiga
angka depan sama). Jika Anda sedang berada di jaringan lain (misalnya 192.168.2.x), isi dengan alamat
jaringan itu dan ubah nanti (Bab 9.3).
TIPS
Installer biasanya sudah mengisi kolom ini dari DHCP. Periksa nilainya, lalu ganti IP menjadi alamat tetap yang
Anda rencanakan.

## 8.8 Layar 6: ringkasan dan instalasi

Proxmox VE Installer - Summary
Filesystem ext4
Disk /dev/sda
Country / Time zone Indonesia / Asia/Jakarta
Keyboard / Email us / admin@lab.local
Management interface enp0s31f6
1 Hostname / IP / Gateway pve.lab.local / 192.168.88.10/24 / 192.168.88.1
2 Automatically reboot [x] centang
Previous Install
Gambar 8.5 - Ilustrasi layar ringkasan. (1) Periksa alamat sekali lagi. (2) Biarkan reboot otomatis tercentang.
1. Periksa semua isi ringkasan, terutama IP, gateway, dan disk.
> Penjelasan: Setelah klik Install, disk dihapus dan tidak bisa dibatalkan.
2. Klik Install.
> Penjelasan: Instalasi memakan sekitar 5 sampai 15 menit (lebih lama pada HDD).
3. Tunggu hingga selesai. Jika Automatically reboot tercentang, mesin restart sendiri.
4. Cabut USB saat mesin restart.
> Penjelasan: Agar mesin boot dari disk, bukan dari installer lagi.

## 8.9 Setelah instalasi

Layar konsol menampilkan teks seperti berikut. Catat alamatnya.
Contoh hasil yang benar
Welcome to the Proxmox Virtual Environment. Please use your web browser to
configure this server - connect to:
 https://192.168.88.10:8006/
pve login:

**TERMINAL (login sebagai root)** | Konsol VM/mesin (login root dengan password dari langkah 8.6)

```
pveversion
```
> Penjelasan: Menampilkan versi Proxmox (contoh 9.2.x).
```
egrep -c '(vmx|svm)' /proc/cpuinfo
```
> Penjelasan: Menghitung baris yang berisi vmx/svm. Hasil harus lebih dari 0 (VT-x tersedia). 0 = VT-x belum
aktif di BIOS (Bab 27.5).
```
ls -l /dev/kvm
```
> Penjelasan: Memastikan perangkat KVM ada. Tanpa ini VM di dalam Proxmox sangat lambat.
```
ip a
```
> Penjelasan: Menampilkan alamat IP. Pada vmbr0 harus ada 192.168.88.10/24.

## 8.10 Login web pertama

https://192.168.88.10:8006 - Proxmox VE Login
1 User name root
2 Password \*\*\*\*\*\*\*\*
3 Realm Linux PAM standard authentication
Language English - English
Login
Gambar 8.6 - Ilustrasi layar login web.
1. Dari browser di laptop buka https://192.168.88.10:8006 (gunakan https dan port 8006).
> Penjelasan: Proxmox hanya melayani web lewat HTTPS di port 8006.
2. Klik Advanced &gt; Proceed to ... (unsafe).
> Penjelasan: Peringatan sertifikat muncul karena sertifikat dibuat sendiri oleh Proxmox. Wajar dan aman di
jaringan rumah.
3. Login: User name root, Password dari langkah 8.6, Realm Linux PAM standard authentication.
4. Jendela No valid subscription: klik OK.
> Penjelasan: Hanya pengingat langganan berbayar. Bisa diabaikan.

## 8.11 Pertanyaan yang sering muncul saat instalasi

Masalah / pertanyaan Jawaban
Layar installer terlalu kecil / buram Gunakan Install Proxmox VE (Terminal UI).
Bagaimana memilih disk? Pilih NVMe 500 GB berdasarkan ukuran dan merek di daftar.
Kolom IP kosong / berisi alamat aneh Installer tidak mendapat DHCP. Isi manual sesuai 8.1. Pastikan kabel/adapter
bridged benar.
Instalasi gagal di tengah ISO rusak (cek hash, Bab 2.4), RAM VM terlalu kecil (minimal 4 GB), atau disk
bermasalah.
Masalah / pertanyaan Jawaban
Setelah reboot masuk installer lagi ISO/USB masih terpasang. Lepas ISO atau cabut USB.
Layar hitam setelah reboot Tunggu 1 sampai 2 menit (boot pertama). Jika tetap, periksa mode boot (Model
B/C: UEFI/Legacy).
Apakah mengisi IP statis di installer
wajib?
Ya, Proxmox memakai IP tetap. Jangan memakai DHCP untuk host Proxmox.


<!-- SOURCE: docs/bab/edisi2/09-konfigurasi-awal-proxmox.md -->

# Bab 9. Konfigurasi Awal Proxmox di Jaringan MikroTik

> **Periksa jaringan yang sedang dipakai sebelum menyalin alamat di bab ini.** Host saat ini sementara berada di `192.168.0.200/24` dengan gateway dan DNS `192.168.0.1`. Alamat `192.168.88.10`, gateway `.88.1`, dan DNS AdGuard `.88.253` baru dipakai setelah host kembali ke MikroTik. Jangan memakai gateway atau DNS dari subnet lain; sesuaikan juga `/etc/hosts` saat mengganti alamat host.

## 9.1 Memastikan koneksi jaringan

Dari konsol atau Shell Proxmox, uji koneksi bertahap: gateway, internet, lalu DNS.
Pada jaringan sementara, gunakan `192.168.0.1` sebagai gateway; contoh `.88.1` di bawah berlaku ketika server terhubung ke MikroTik.

**TERMINAL (login sebagai root)** | Shell Proxmox

```
ping -c 3 192.168.88.1
```
> Penjelasan: Menguji MikroTik (gateway). Gagal = masalah kabel/bridge/IP.
```
ping -c 3 8.8.8.8
```
> Penjelasan: Menguji internet tanpa DNS. Gagal tetapi gateway berhasil = masalah di MikroTik/uplink.
```
ping -c 3 deb.debian.org
```
> Penjelasan: Menguji DNS. Gagal tetapi 8.8.8.8 berhasil = DNS salah (lihat 9.4).
Dari sisi MikroTik, pastikan Proxmox terlihat:

**TERMINAL MIKROTIK** | WinBox &gt; New Terminal

```
/ping 192.168.88.10 count=3
```
> Penjelasan: Mengirim ping dari router ke Proxmox.
```
/ip arp print where address=192.168.88.10
```
> Penjelasan: Menampilkan MAC address Proxmox pada tabel ARP router. Muncul = terhubung di LAN.

## 9.2 Mencatat Proxmox di MikroTik

**TERMINAL MIKROTIK** | WinBox &gt; New Terminal

```
/ip firewall address-list add list=servers address=192.168.88.10 comment="proxmox"
```
> Penjelasan: Mencatat Proxmox di daftar alamat bernama servers. Berguna untuk dokumentasi dan aturan
firewall nanti.
CATATAN
Proxmox memakai IP statis (192.168.88.10, di luar pool DHCP), jadi tidak perlu static lease. Perangkat lain (VM,
LXC, STB) memakai static lease (Bab 3.5).

## 9.3 Mengubah IP/gateway/DNS bila instal di jaringan lain

Jika saat instalasi Proxmox diberi alamat jaringan lain (misalnya 192.168.100.2 atau 192.168.2.x) dan
sekarang Anda pindah ke jaringan MikroTik, ubah tiga hal: /etc/network/interfaces, /etc/hosts, dan
DNS. Tidak perlu instal ulang.

**TERMINAL (login sebagai root)** | Konsol VM atau Shell Proxmox

```
ls /etc/network/
```
> Penjelasan: Memeriksa nama berkas yang benar: harus ada interfaces (dengan huruf s di akhir).
```
cat -n /etc/network/interfaces
```
> Penjelasan: Menampilkan isi berkas dengan nomor baris sebelum diubah.
```
nano /etc/network/interfaces
```
> Penjelasan: Membuka editor. Ubah hanya address dan gateway.

**BERKAS: /etc/network/interfaces** | Ubah baris address dan gateway (nama enp0s31f6 sesuaikan dengan milik Anda)

```
auto lo
```

 2 iface lo inet loopback
 3
 4 iface enp0s31f6 inet manual
 5
 6 auto vmbr0
 7 iface vmbr0 inet static
 8 address 192.168.88.10/24
 9 gateway 192.168.88.1
10 bridge-ports enp0s31f6
11 bridge-stp off
12 bridge-fd 0
13
14 source /etc/network/interfaces.d/\*
Tombol nano Fungsi
Panah Pindah kursor
Ctrl+O lalu Enter Simpan (Write Out)
Ctrl+X Keluar
Ctrl+W Cari teks
Ctrl+K / Ctrl+U Potong / tempel satu baris

**TERMINAL (login sebagai root)** | Konsol VM atau Shell Proxmox

```
nano /etc/hosts
```
> Penjelasan: Ganti IP lama pada baris hostname menjadi 192.168.88.10.
```
hostname --ip-address
```
> Penjelasan: Harus menampilkan 192.168.88.10 (cocok dengan /etc/hosts).
```
reboot
```
> Penjelasan: Menerapkan semua perubahan. Alternatif tanpa reboot: ifreload -a.

**BERKAS: /etc/hosts** | Baris hostname harus berisi IP yang benar

```
127.0.0.1 localhost.localdomain localhost
192.168.88.10 pve.lab.local pve
```

PERINGATAN
Jika IP di /etc/hosts berbeda dari IP asli, layanan Proxmox (pveproxy, pve-cluster) bisa gagal start dan
web tidak terbuka.
Gambar 9.1 - Kasus nyata: judul nano tertulis /etc/network/interface (tanpa huruf s), sehingga editor kosong. Keluar
(Ctrl+X) lalu buka /etc/network/interfaces.
Alternatif lewat antarmuka web
1. Node pve &gt; System &gt; Network.
2. Klik vmbr0 &gt; Edit; ubah IPv4/CIDR dan Gateway &gt; OK.
3. Klik Apply Configuration.
> Penjelasan: Koneksi web akan terputus sebentar; buka alamat baru.
4. Perbarui /etc/hosts seperti di atas.
> Penjelasan: Perubahan lewat web tidak memperbarui berkas hosts.

## 9.4 Mengatur DNS

1. Node pve &gt; System &gt; DNS &gt; Edit.
2. Isi DNS server 1 192.168.88.253 (AdGuard), DNS server 2 1.1.1.1.
> Penjelasan: DNS ke-2 publik hanya dipakai oleh host Proxmox sendiri agar update tetap jalan jika AdGuard
sedang mati.
3. Klik OK.

**TERMINAL (login sebagai root)** | Shell Proxmox

```
cat /etc/resolv.conf
```
> Penjelasan: Memeriksa isi akhir: harus ada baris nameserver 192.168.88.253.

## 9.5 Repository: ganti ke no-subscription

Proxmox memakai repository enterprise (berbayar) secara bawaan sehingga apt update gagal. Untuk
lab dan rumah, pakai repository no-subscription (gratis).
1. Pilih node pve di panel kiri.
2. Di kolom menu kedua klik Updates (ikon panah melingkar), lalu Repositories tepat di
bawahnya.
> Penjelasan: Menu ini ada di bawah Updates, bukan di Datacenter.
3. Pilih baris pve-enterprise &gt; Disable. Lakukan juga pada ceph-enterprise.
> Penjelasan: Repository enterprise butuh langganan; jika dibiarkan aktif akan memunculkan error 401.
4. Klik Add &gt; pilih No-Subscription &gt; Add.
> Penjelasan: Ini repository gratis yang dipakai di rumah.
5. Periksa hasil seperti di Gambar 9.2.
Gambar 9.2 - Hasil yang benar. (1) ceph-enterprise disabled. (2) pve-no-subscription aktif. (3)
pve-enterprise disabled. Repository Debian (trixie, trixie-updates, trixie-security) aktif. Peringatan kuning
"no-subscription is not recommended for production" aman diabaikan di rumah.
CATATAN
Proxmox VE 9 berbasis Debian 13 (nama kode trixie). Daftar repository memakai format .sources di
/etc/apt/sources.list.d/.

## 9.6 Update dan upgrade

**TERMINAL (login sebagai root)** | Shell Proxmox

```
apt update
```
> Penjelasan: Mengunduh daftar paket terbaru dari repository. Harus berakhir tanpa baris Err:.
```
apt full-upgrade -y
```
> Penjelasan: Memperbarui semua paket. full-upgrade (bukan upgrade) yang disarankan pada Proxmox
karena paket dependensi bisa berubah.
```
pveversion
```
> Penjelasan: Memeriksa versi setelah pembaruan.
```
reboot
```
> Penjelasan: Dibutuhkan bila kernel diperbarui. Tunggu 1 sampai 2 menit lalu buka web lagi.
Atau lewat web: Updates &gt; Refresh (harus berakhir TASK OK), lalu Upgrade.
Setelah pembaruan dan reboot, **sebelum membuat template atau guest**, verifikasi akselerasi KVM:

```
lscpu | grep -i virtualization
```
> Penjelasan: Pada M710q harus menampilkan `Virtualization: VT-x`. Jika tidak ada baris, VT-x mungkin mati di BIOS; lihat Bab 27.5.

```
ls -l /dev/kvm
```
> Penjelasan: Perangkat KVM harus ada. Bila tidak ada, jangan lanjut membuat template VM; selesaikan pemeriksaan VT-x dahulu.

Jika `apt update` gagal dengan `Temporary failure resolving`, periksa DNS dan kecocokan jaringan host sebelum melanjutkan. Contoh jaringan sementara `192.168.0.0/24` dicatat pada STATUS dan Bab 24. Jangan gunakan DNS rumah yang tidak terjangkau dari jaringan aktif.
TIPS
Jika unduhan lambat (9 KB/s pada kasus nyata): pakai kabel LAN, update di jam sepi, atau ganti URIs: di
/etc/apt/sources.list.d/debian.sources ke mirror Debian terdekat dari daftar resmi mirror. Baris Ign:
lalu Get: pada log adalah percobaan ulang, bukan error.

## 9.7 Mengenal antarmuka

Gambar 9.3 - Antarmuka Proxmox 9.2.2, node pve. (1) Menu Updates &gt; Repositories ada di kolom menu kedua. (2) Panel
Tasks di bawah: baris merah adalah error (di sini apt-get update yang gagal karena DNS).
Bagian Isi
Panel kiri (Server View) Pohon Datacenter &gt; node pve &gt; VM, container, dan storage.
Panel tengah Menu objek yang dipilih (Summary, Console, Hardware, Backup, Snapshots, dan
seterusnya).
Panel bawah (Tasks) Riwayat tugas. Klik dua kali untuk melihat log lengkap. Merah = error.
Kanan atas Tombol Create VM, Create CT, Reboot, Shutdown, Shell.
Datacenter &gt; Storage Daftar storage: local (ISO, template, backup) dan local-lvm (disk VM/CT).
Node &gt; System &gt; Network Bridge vmbr0 yang menghubungkan VM/CT ke LAN.
Node &gt; Disks Disk fisik dan pembuatan LVM, LVM-Thin, Directory, ZFS.

## 9.8 Kebiasaan baik

• Matikan dengan benar: node &gt; Shutdown di web, atau poweroff di Shell. Jangan menekan tombol power lama atau mencabut kabel daya
saat VM berjalan.
• Penomoran proyek: CT 100 untuk template dan CT 101+ untuk layanan; VM 200 untuk template dan VM 201+ untuk layanan. VM 9000 tetap dicadangkan untuk template cloud-init. Catat di Lampiran B.
• Ambil snapshot Proxmox (VM &gt; Snapshots) pada titik penting: sebelum upgrade, sebelum eksperimen besar.
• Snapshot bukan backup. Jangan menumpuk banyak snapshot karena disk membengkak dan VM
melambat.

## 9.9 Menambah disk data (opsional)

Pasang HDD/SSD kedua (bay 2,5" atau USB, lihat Bab 27.4). Disk muncul di
Node &gt; Disks (contoh /dev/sdb).
1. Disks &gt; Directory &gt; Create: Directory, pilih disk, filesystem ext4, beri nama.
> Penjelasan: Membuat storage direktori yang otomatis terdaftar di Datacenter &gt; Storage.
2. Atur Content storage itu (Datacenter &gt; Storage &gt; Edit): centang Disk image, Container,
VZDump backup file sesuai tujuan.
> Penjelasan: Menentukan jenis data yang boleh disimpan.
PERINGATAN
Membuat Directory/LVM/ZFS pada disk menghapus isinya. Pastikan memilih disk yang benar.

## 9.11 Kasus nyata pada konfigurasi awal

KASUS NYATA - Proxmox tidak bisa dibuka dari browser
Gejala: Browser gagal tersambung ke https://192.168.100.2:8006.
Penyebab: Saat instalasi laptop tidak terhubung ke jaringan rumah; IP Proxmox (192.168.100.x) beda jaringan
dengan laptop (192.168.2.106 gateway 192.168.2.1).
Solusi: Cocokkan tiga angka depan: ubah IP Proxmox ke jaringan laptop atau ke 192.168.88.10 setelah laptop
dipindah ke jaringan MikroTik (9.3).
KASUS NYATA - apt update: Temporary failure resolving
Gejala: Log berisi Err: ... Temporary failure resolving untuk semua repository dan tugas merah di
panel Tasks.
Penyebab: DNS Proxmox kosong atau masih alamat jaringan lama.
Solusi: Isi DNS di System &gt; DNS (9.4), uji ping deb.debian.org, lalu Refresh lagi.
KASUS NYATA - Tidak menemukan menu Repositories
Gejala: Menu tidak terlihat.
Penyebab: Letaknya di bawah Updates di kolom menu kedua.
Solusi: Node &gt; Updates &gt; Repositories (Gambar 9.3).


<!-- SOURCE: docs/bab/edisi2/10-lxc-pertama.md -->

# Bab 10. Container LXC Pertama

LXC adalah container Linux yang ringan: berbagi kernel dengan Proxmox, sehingga memakai RAM jauh
lebih sedikit daripada VM. Cocok untuk AdGuard Home dan layanan kecil lainnya.

## 10.1 Mengunduh template

1. Panel kiri: pilih storage local (di bawah node pve).
> Penjelasan: Template container disimpan di storage ini.
2. Buka CT Templates &gt; Templates.
> Penjelasan: Daftar template resmi Proxmox dan TurnKey.
3. Pilih debian-13-standard &gt; Download. Tunggu TASK OK.
> Penjelasan: Jika gagal, hampir pasti DNS Proxmox bermasalah (Bab 9.4).

## 10.2 Membuat container

Create: LXC Container - General
Node pve
1 CT ID 101
2 Hostname adguard2
3 Unprivileged container [x] dicentang
4 Password \*\*\*\*\*\*\*\*
Back Next
Gambar 10.1 - Ilustrasi tab General. (1) ID unik. (2) Nama. (3) Unprivileged lebih aman. (4) Password root container.
1. Klik Create CT (kanan atas).
2. General: CT ID 101, Hostname adguard2, centang Unprivileged container, isi password root.
> Penjelasan: Unprivileged: root di dalam container bukan root di host (lebih aman).
3. Template: pilih Debian 13 yang diunduh.
4. Disks: storage local-lvm, ukuran 4 GB.
> Penjelasan: Cukup untuk AdGuard Home.
5. CPU: 1 core. Memory: 256 MB, swap 256 MB.
> Penjelasan: AdGuard sangat ringan.
6. Network: Name eth0, Bridge vmbr0, IPv4 DHCP.
> Penjelasan: IP akan diatur lewat static lease MikroTik (10.4) agar semua alamat dikelola di satu tempat.
7. DNS: biarkan "use host settings".
8. Confirm: centang Start after created, klik Finish.

## 10.3 Memberi IP tetap lewat MikroTik

1. Pilih CT 101 &gt; Network (atau Hardware), salin MAC address (hwaddr=BC:24:11:...).
> Penjelasan: DHCP mengenali perangkat dari MAC ini.
2. Di MikroTik buat reservasi: lihat Bab 3.5 dengan address 192.168.88.11 dan comment
lxc-adguard2.
3. Restart container (CT &gt; Shutdown lalu Start).
> Penjelasan: Agar mendapat IP baru dari reservasi.

**TERMINAL MIKROTIK** | WinBox &gt; New Terminal

```
/ip dhcp-server lease add address=192.168.88.11 mac-address=BC:24:11:AA:BB:CC
```
> Penjelasan: Reservasi IP .11 untuk MAC container. Ganti MAC sesuai milik Anda.
```
/ip dhcp-server lease set [find address=192.168.88.11] comment="lxc-adguard2"
```
> Penjelasan: Memberi komentar.

## 10.4 Masuk dan memperbarui isi container

1. Pilih CT 101 &gt; tab Console, login root dengan password dari langkah 10.2.
> Penjelasan: Tidak perlu sudo karena sudah root.

**TERMINAL (login sebagai root)** | Console container 101

```
ip a
```
> Penjelasan: Memastikan eth0 memiliki 192.168.88.11.
```
ping -c 3 deb.debian.org
```
> Penjelasan: Memastikan internet dan DNS bekerja dari dalam container.
```
apt update && apt full-upgrade -y
```
> Penjelasan: Memperbarui paket container.
```
apt install -y curl nano
```
> Penjelasan: Memasang curl (untuk mengunduh skrip instalasi) dan nano (editor).
TIPS
Untuk masuk lewat SSH dari laptop: ssh root@192.168.88.11. Jika ditolak, itu karena login root dengan
password dimatikan secara bawaan. Gunakan konsol Proxmox, atau izinkan sementara dengan mengubah
PermitRootLogin yes di /etc/ssh/sshd_config lalu systemctl restart ssh.

## 10.5 Operasi sehari-hari

Tujuan Cara (web) Cara (Shell Proxmox)
Start / Stop Tombol Start / Shutdown pct start 101 / pct shutdown 101
Masuk konsol Tab Console pct enter 101
Tujuan Cara (web) Cara (Shell Proxmox)
Ubah RAM / CPU Resources &gt; Edit pct set 101 -memory 512 -cores 2
Backup Backup &gt; Backup now vzdump 101 --storage local --mode
stop
Hapus More &gt; Remove pct destroy 101
KASUS NYATA - Container tidak mendapat IP / tidak ada internet
Gejala: ip a di container tidak punya alamat atau ping gagal.
Penyebab: Bridge belum benar, DHCP tidak membalas MAC baru (WiFi), atau reservasi MikroTik belum benar.
Solusi: Cek lease print di MikroTik, pastikan Proxmox terhubung kabel LAN ke MikroTik, atau beri IP statis
di tab Network container (192.168.88.11/24, gateway 192.168.88.1).


<!-- SOURCE: docs/bab/edisi2/11-vm-debian-13.md -->

# Bab 11. VM Debian 13 (untuk Docker, Git, Nextcloud, dan lainnya)

Container tidak cocok untuk semuanya. Docker, Home Assistant, dan Kubernetes sebaiknya di VM. Bab
ini membuat VM Debian GNU/Linux 13 "trixie" dari ISO, menginstalnya layar demi layar, dan
memberinya IP tetap dari MikroTik.

## 11.1 Mengunggah ISO Debian 13

ISO yang dipakai: debian-13.7.0-amd64-netinst.iso (ukuran sekitar 800 MB, perlu internet saat instalasi).
Jika tautan itu 404, buka folder iso-cd dan pilih berkas debian-13.x.x-amd64-netinst.iso terbaru.
1. Di Proxmox: storage local &gt; ISO Images &gt; Download from URL.
> Penjelasan: Proxmox mengunduh langsung dari internet, tanpa lewat laptop.
2. Tempel URL ISO, klik Query URL, lalu Download.
> Penjelasan: Query URL memeriksa nama berkas dan ukurannya.
3. Tunggu TASK OK. ISO muncul di daftar ISO Images.
> Penjelasan: Alternatif: Upload berkas dari laptop.

## 11.2 Membuat VM lewat wizard

Create: Virtual Machine - System / Disks / CPU / Memory
1 VM ID / Name 201 / debian-docker
2 OS: ISO image debian-13.7.0-amd64-netinst.iso
3 System: Qemu Agent [x] dicentang; SCSI: VirtIO SCSI single
4 Disks: Bus / size SCSI / 40 GiB, Discard
5 CPU: sockets / cores / type 1 / 2 / host
6 Memory 4096 MiB
7 Network: bridge / model vmbr0 / VirtIO
Back Finish
Gambar 11.1 - Ilustrasi pengaturan VM 201 (ringkasan dari semua tab wizard).
1. Klik Create VM. General: VM ID 201, Name debian-docker.
> Penjelasan: ID mengikuti rencana (VM 200-299).
2. OS: pilih ISO Debian 13, Type Linux, Version 6.x - 2.6 Kernel.
> Penjelasan: Memberi tahu Proxmox jenis sistem tamu.
3. System: biarkan default (i440fx, SeaBIOS). Centang Qemu Agent. SCSI Controller VirtIO SCSI
single.
> Penjelasan: Qemu Agent membuat Proxmox bisa membaca IP VM dan mematikannya dengan bersih.
4. Disks: Bus SCSI, Storage local-lvm, Disk size 40 GiB, centang Discard.
> Penjelasan: Docker, Nextcloud, dan Git butuh ruang; 40 GiB nyaman.
5. CPU: 1 socket, 2 cores, Type host.
> Penjelasan: Type host memberi performa lebih baik karena fitur CPU diteruskan langsung.
6. Memory: 4096 MiB (minimal 2048).
> Penjelasan: Docker + Nextcloud + Portainer + Git membutuhkan RAM lebih banyak.
7. Network: Bridge vmbr0, Model VirtIO (paravirtualized).
> Penjelasan: VirtIO adalah kartu jaringan tercepat untuk VM Linux.
8. Confirm: Finish. Pilih VM 201 &gt; Start &gt; Console.

## 11.3 Menginstal Debian 13, layar demi layar

Instalasi memakai installer teks Debian (menu biru). Gunakan panah dan Enter, Tab untuk pindah tombol,
spasi untuk mencentang.
1. Menu awal: pilih Install (bukan Graphical Install).
> Penjelasan: Installer teks lebih ringan dan stabil di konsol Proxmox.
2. Select a language: English (atau Indonesia). Location: Indonesia (jika tidak ada pilih "other" &gt;
Asia &gt; Indonesia).
> Penjelasan: Bahasa installer dan zona waktu.
3. Keymap: American English.
> Penjelasan: Sesuai keyboard US.
4. Hostname: debian-docker. Domain name: lab.local.
> Penjelasan: Nama server di jaringan.
5. Root password: isi password root dan ulangi.
> Penjelasan: Jika diisi, root bisa login dan sudo tidak dipasang. Jangan dikosongkan kecuali ingin memakai
sudo.
6. Create a user: nama lengkap, username (contoh admin), password.
> Penjelasan: User biasa untuk SSH; login root lewat SSH ditolak secara bawaan.
7. Time zone: pilih Western Indonesia (Jakarta).
> Penjelasan: Agar waktu log benar.
Debian GNU/Linux installer - Partition disks
1 Partitioning method Guided - use entire disk
2 Select disk SCSI3 (0,0,0) (sda) - 42.9 GB QEMU HARDDISK
3 Partitioning scheme All files in one partition (recommended)
4 Finish Finish partitioning and write changes to disk
Go Back Continue
Gambar 11.2 - Ilustrasi pemartisian disk Debian. Pilih urutan 1 sampai 4, lalu Yes pada konfirmasi Write the changes to
disks.
1. Partition disks: Guided - use entire disk &gt; pilih disk &gt; All files in one partition &gt; Finish
partitioning &gt; Yes (Write changes).
> Penjelasan: Pemartisian paling sederhana untuk VM. Hanya menghapus disk virtual 40 GB itu, bukan disk lain.
2. Scan another CD/DVD: No. Debian archive mirror country: Indonesia (atau negara terdekat),
mirror deb.debian.org, HTTP proxy kosongkan.
> Penjelasan: Mengatur sumber paket. Jika dilewati, berkas apt menyisakan baris cdrom yang menyebabkan
peringatan (lihat 11.5).
3. Participate in the package usage survey: No.
Debian GNU/Linux installer - Software selection
1 Debian desktop environment [ ] (kosongkan)
1 GNOME / Xfce / ... [ ] (kosongkan)
web server [ ]
2 SSH server [x] CENTANG
3 standard system utilities [x] CENTANG
Go Back Continue
Gambar 11.3 - Ilustrasi Software selection. Server tidak memakai desktop. Pilih hanya (2) SSH server dan (3) standard
system utilities.
1. Software selection: hilangkan centang desktop environment dan GNOME. Centang SSH server
dan standard system utilities (spasi mencentang).
> Penjelasan: Tanpa desktop VM lebih ringan; SSH server untuk akses jarak jauh.
2. Install the GRUB boot loader: Yes &gt; pilih /dev/sda.
> Penjelasan: GRUB adalah pemuat boot; tanpa ini VM tidak boot.
3. Installation complete: Continue. VM restart.
> Penjelasan: Pastikan ISO tidak boot lagi (11.4).

## 11.4 Melepas ISO dan boot pertama

1. Di Proxmox: VM 201 &gt; Hardware &gt; CD/DVD Drive &gt; Edit &gt; Do not use any media &gt; OK.
> Penjelasan: Mencegah installer berjalan lagi.
2. Jika VM kembali ke installer, Reset VM.
3. Di Console, login root dengan password root.
> Penjelasan: Prompt akan berakhiran #.

**TERMINAL (login sebagai root)** | Console VM 201 (root)

```
ip a
```
> Penjelasan: Mencatat IP sementara dari DHCP (contoh 192.168.88.150) dan nama kartu (ens18).
```
apt update && apt full-upgrade -y
```
> Penjelasan: Memperbarui sistem. Tanpa sudo, karena Anda sudah root.
```
apt install -y qemu-guest-agent curl nano ca-certificates
```
> Penjelasan: Memasang agen Proxmox, curl, nano, dan sertifikat.
```
systemctl enable --now qemu-guest-agent
```
> Penjelasan: Menyalakan agen sekarang dan setiap boot.
Di Proxmox, VM 201 &gt; Options &gt; QEMU Guest Agent &gt; pastikan Enabled. Setelah itu IP VM terlihat di
tab Summary.

## 11.5 Memperbaiki sumber apt (jika muncul peringatan cdrom)

**TERMINAL (login sebagai root)** | Console VM 201

```
grep -rn cdrom /etc/apt/
```
> Penjelasan: Mencari baris cdrom di berkas apt. Jika tidak ada hasil, lewati langkah ini.
```
nano /etc/apt/sources.list
```
> Penjelasan: Beri tanda # di awal baris yang mengandung cdrom, simpan (Ctrl+O, Enter, Ctrl+X). Jika baris ada
di /etc/apt/sources.list.d/\*.sources, edit berkas itu.
```
apt update
```
> Penjelasan: Memastikan tidak ada lagi peringatan cdrom.

## 11.6 Memberi IP tetap lewat MikroTik

1. Proxmox: VM 201 &gt; Hardware &gt; Network Device, salin MAC (virtio=BC:24:11:...).
2. MikroTik: buat reservasi (Bab 3.5) address 192.168.88.20, comment vm-debian-docker.
3. Di VM: reboot (atau ifdown ens18 && ifup ens18).
> Penjelasan: VM meminta IP lagi dan mendapat 192.168.88.20.
4. Dari laptop: ssh admin@192.168.88.20, lalu su - untuk menjadi root.
> Penjelasan: Login root lewat SSH ditolak secara bawaan, jadi masuk sebagai user biasa lalu naik ke root.

**POWERSHELL WINDOWS** | PowerShell Windows (laptop)

```
ssh admin@192.168.88.20
```
> Penjelasan: Login SSH ke VM sebagai user biasa.

**TERMINAL (login sebagai root)** | Di dalam VM (SSH)

```
su -
```
> Penjelasan: Menjadi root. Masukkan password root. Prompt berubah menjadi #.
```
hostname -I
```
> Penjelasan: Memastikan IP VM adalah 192.168.88.20.

## 11.7 Template cloud-init (lanjutan, opsional)

Template membuat VM baru dari hasil kloning dalam hitungan detik. Gunakan image cloud resmi Debian
13. Periksa nama berkas di cloud.debian.org/images/cloud/trixie sebelum mengunduh.

**TERMINAL (login sebagai root)** | Shell Proxmox

```
cd /var/lib/vz/template/iso
```
> Penjelasan: Pindah ke folder ISO Proxmox.
```
URL=https://cloud.debian.org/images/cloud/trixie/latest
```
> Penjelasan: Menyimpan alamat dasar dalam variabel agar perintah berikutnya pendek.
```
wget $URL/debian-13-genericcloud-amd64.qcow2
```
> Penjelasan: Mengunduh image cloud Debian 13.
```
IMG=/var/lib/vz/template/iso/debian-13-genericcloud-amd64.qcow2
```
> Penjelasan: Menyimpan jalur image dalam variabel.
```
qm create 9000 --name debian13-template --memory 2048 --cores 2 --cpu host \
  --net0 virtio,bridge=vmbr0 --scsihw virtio-scsi-pci
```
> Penjelasan: Membuat VM kosong ID 9000.
```
qm set 9000 --scsi0 local-lvm:0,import-from=$IMG
```
> Penjelasan: Mengimpor image sebagai disk VM.
```
qm set 9000 --ide2 local-lvm:cloudinit
```
> Penjelasan: Menambah drive cloud-init untuk user, password, dan IP.
```
qm set 9000 --boot order=scsi0 --serial0 socket --vga serial0 --agent enabled=1
```
> Penjelasan: Mengatur boot dari disk, konsol serial, dan guest agent.
```
qm template 9000
```
> Penjelasan: Mengubah VM 9000 menjadi template (tidak bisa dinyalakan lagi, hanya dikloning).

**TERMINAL (login sebagai root)** | Shell Proxmox

```
qm clone 9000 203 --name k3s --full
```
> Penjelasan: Mengkloning template menjadi VM 203 bernama k3s.
```
qm set 203 --ciuser debian --cipassword 'GANTI_PASSWORD'
```
> Penjelasan: Mengisi user dan password lewat cloud-init.
```
qm set 203 --ipconfig0 ip=dhcp --nameserver 192.168.88.253
```
> Penjelasan: IP lewat DHCP (reservasi MikroTik akan memberi .22).
```
qm resize 203 scsi0 20G
```
> Penjelasan: Memperbesar disk menjadi 20 GB.
```
qm set 203 --memory 4096 --cores 2 && qm start 203
```
> Penjelasan: Mengatur RAM/CPU dan menyalakan VM.
CATATAN
Image cloud tidak berisi qemu-guest-agent secara bawaan. Setelah VM hidup, jalankan apt install -y
qemu-guest-agent seperti di 11.4.
KASUS NYATA - VM tidak mau start: KVM tidak tersedia
Gejala: Task Start gagal; pesan KVM virtualisation dikonfigurasi tetapi tidak tersedia.
Penyebab: Pada M710q yang diuji, VT-x belum aktif di BIOS.
Solusi: Aktifkan Intel Virtualization Technology dengan BIOS lokal atau metode thinklmi bila atribut tersedia (Bab 27.5). Reboot, lalu pastikan `lscpu | grep -i virtualization` menunjukkan VT-x dan `/dev/kvm` ada sebelum menyalakan VM lagi.
KASUS NYATA - VM Debian sangat lambat
Gejala: Instalasi atau boot memakan puluhan menit.
Penyebab: RAM host penuh (swap) atau terlalu banyak VM menyala bersamaan.
Solusi: Periksa free -m di host, pilih CPU type host, kurangi VM aktif (Bab 56).
KASUS NYATA - sudo: command not found di VM Debian
Gejala: Mengetik sudo apt update gagal.
Penyebab: Debian diinstal dengan password root sehingga sudo tidak terpasang.
Solusi: Ketik su - untuk menjadi root lalu jalankan perintah tanpa sudo (lihat Bab 1.7).


<!-- SOURCE: docs/bab/edisi2/12-stb-adguard-tailscale.md -->

# Bab 12. STB HG680: AdGuard Home dan Tailscale

> [!IMPORTANT]
> **Catatan Revisi 3:** Bab ini adalah materi historis Edisi 2. Dalam rancangan saat ini, STB HG680 .253 menjalankan AdGuard Home saja; Tailscale subnet router ditunda sampai STB 2 tersedia, dengan CT103 Proxmox sebagai pilihan sementara. Jangan ikuti langkah pemasangan Tailscale di STB 1 dari bab ini. Gunakan [Bab 26 versi terbaru](../suplemen/26-tailscale.md) dan [status proyek](../../../STATUS.md).


## 12.1 Ringkasan

Item Isi
Perangkat STB HG680 (Amlogic S905x) dengan Armbian (build ophub, contoh v25.05.0, Linux 6.1)
Peran DNS pemblokir iklan utama (AdGuard Home) dan akses jarak jauh (Tailscale subnet router)
Alamat 192.168.88.253 (static lease MikroTik)
Kenapa di STB Selalu hidup dan terpisah dari Proxmox, sehingga internet rumah dan akses jauh tidak mati saat
Proxmox diutak-atik

## 12.2 Persiapan STB

Menyambungkan dan memberi IP tetap
1. Colokkan STB ke port MikroTik (contoh ether4) dan nyalakan.
> Penjelasan: STB mendapat IP DHCP sementara dari MikroTik.
2. Di MikroTik: IP &gt; DHCP Server &gt; Leases, cari STB (hostname armbian), Make Static, ubah
Address menjadi 192.168.88.253.
> Penjelasan: Resep di Bab 3.5.
3. Reboot STB agar mengambil alamat baru.

**TERMINAL MIKROTIK** | WinBox &gt; New Terminal

```
/ip dhcp-server lease print
```
> Penjelasan: Mencari baris STB dan nomornya.
```
/ip dhcp-server lease make-static numbers=0
```
> Penjelasan: Menjadikan lease nomor 0 sebagai statis (ganti 0 dengan nomor STB).
```
/ip dhcp-server lease set numbers=0 address=192.168.88.253 comment="stb-adguard"
```
> Penjelasan: Menetapkan alamat dan komentar.
Masuk lewat SSH (PuTTY)
1. Buka PuTTY. Host Name 192.168.88.253, Port 22, Connection type SSH, klik Open.
> Penjelasan: Tautan unduh PuTTY ada di Bab 2.2.
2. Klik Accept pada peringatan kunci host (hanya pertama kali).
> Penjelasan: PuTTY menyimpan sidik jari server.
3. Login root. Password bawaan Armbian: 1234, lalu sistem meminta password baru dan
pembuatan user.
> Penjelasan: Pada instalasi Armbian pertama kali ada wizard yang meminta password root baru.
Atau dari PowerShell: ssh root@192.168.88.253.
Memeriksa apakah sistem berjalan dari eMMC atau SD

**TERMINAL (login sebagai root)** | SSH ke STB

```
lsblk
```
> Penjelasan: Daftar disk. mmcblk1 biasanya kartu SD (misal 29 GB), mmcblk2 adalah eMMC internal (misal 7,3
GB).
```
findmnt /
```
> Penjelasan: Menunjukkan partisi root yang sedang dipakai (misal /dev/mmcblk1p2 = SD).
```
df -h /
```
> Penjelasan: Ukuran dan sisa ruang partisi root.
Contoh hasil: sistem aktif ada di SD (mmcblk1)
NAME SIZE TYPE MOUNTPOINTS
mmcblk1 29.7G disk
+-mmcblk1p1 256M part /boot
+-mmcblk1p2 29.4G part /
mmcblk2 7.3G disk
+-mmcblk2p1 256M part
+-mmcblk2p2 7G part
KASUS NYATA - Dua instalasi Armbian di satu STB
Gejala: Tidak jelas sistem aktif ada di eMMC atau SD. lsblk memperlihatkan mmcblk1 (SD 29 GB) dan
mmcblk2 (eMMC 7,3 GB).
Penyebab: eMMC masih menyimpan instalasi lama (label BOOT_EMMC dan ROOTFS_EMMC) sedangkan
SD menjalankan instalasi baru.
Solusi: Pastikan dengan findmnt /. Pilih satu. Untuk menjalankan dari eMMC gunakan armbian-install
lalu cabut SD setelah selesai. Pada pengalaman proyek lain Armbian di eMMC kadang layar kosong setelah
STB dimatikan; simpan SD cadangan dan periksa /boot/uEnv.txt (contoh
FDT=/dtb/amlogic/meson-gxl-s905x-p212.dtb).
Memperbarui sistem dan pengaturan dasar

**TERMINAL (login sebagai root)** | SSH ke STB (root)

```
apt update && apt full-upgrade -y
```
> Penjelasan: Memperbarui paket Armbian (tanpa sudo karena login root).
```
apt install -y curl nano
```
> Penjelasan: Memasang curl dan nano.
```
hostnamectl set-hostname stb-adguard
```
> Penjelasan: Memberi nama STB.
```
timedatectl set-timezone Asia/Jakarta
```
> Penjelasan: Mengatur zona waktu WIB agar log AdGuard benar.

## 12.3 Instal dan konfigurasi AdGuard Home

Membebaskan port 53
Ubuntu/Debian memakai systemd-resolved yang menahan port 53 pada alamat 127.0.0.53, sehingga
AdGuard tidak bisa memakai port itu. Matikan "stub listener"-nya.

**TERMINAL (login sebagai root)** | SSH ke STB

```
nano /etc/systemd/resolved.conf
```
> Penjelasan: Buka berkas. Di bagian [Resolve] ubah/tambahkan DNSStubListener=no (hapus tanda # jika
ada).
```
mv /etc/resolv.conf /etc/resolv.conf.backup
```
> Penjelasan: Mencadangkan berkas resolver lama.
```
ln -s /run/systemd/resolve/resolv.conf /etc/resolv.conf
```
> Penjelasan: Mengarahkan resolver ke berkas yang tidak memakai stub 127.0.0.53.
```
systemctl restart systemd-resolved
```
> Penjelasan: Menerapkan perubahan.
```
ss -tulpn | grep :53
```
> Penjelasan: Memeriksa: tidak boleh ada program yang menahan port 53.

**BERKAS: /etc/systemd/resolved.conf** | Bagian yang perlu ada

```
 1 [Resolve]
 2 DNSStubListener=no
Memasang AdGuard Home
```

**TERMINAL (login sebagai root)** | SSH ke STB

```
U=https://raw.githubusercontent.com/AdguardTeam/AdGuardHome/master/scripts
curl -s -S -L "$U/install.sh" | sh -s -- -v
```
> Penjelasan: Mengunduh dan menjalankan skrip instalasi resmi. AdGuard dipasang di /opt/AdGuardHome dan dijalankan sebagai layanan.
```
/opt/AdGuardHome/AdGuardHome -s status
```
> Penjelasan: Memeriksa layanan berjalan.
Wizard awal (http://192.168.88.253:3000)
AdGuard Home - Setup (langkah 2 dari 5)
1 Admin Web Interface: listen All interfaces
1 Admin Web Interface: port 80
2 DNS server: listen All interfaces
2 DNS server: port 53
Back Next
Gambar 12.1 - Ilustrasi wizard AdGuard. (1) Antarmuka admin di port 80. (2) Server DNS di port 53 pada semua interface.
1. Buka http://192.168.88.253:3000 dari laptop, klik Get Started.
> Penjelasan: Port 3000 hanya dipakai wizard awal.
2. Langkah 2: Admin Web Interface All interfaces, port 80. DNS server All interfaces, port 53. Klik
Next.
> Penjelasan: Port 80 untuk web admin, port 53 untuk layanan DNS.
3. Langkah 3: buat username dan password admin.
> Penjelasan: Dipakai untuk login ke antarmuka admin.
4. Langkah 4: baca petunjuk, klik Next; langkah 5: Open Dashboard.
> Penjelasan: Setelah ini admin ada di http://192.168.88.253 (port 80).
Konfigurasi di AdGuard Home
1. Settings &gt; DNS settings &gt; Upstream DNS servers: isi https://dns10.quad9.net/dns-query dan
1.1.1.1, atau pilih satu penyedia. Pilih Parallel requests.
> Penjelasan: Upstream adalah DNS tempat AdGuard bertanya untuk situs yang tidak diblokir. Parallel requests
mengambil jawaban tercepat.
2. Bootstrap DNS servers: 1.1.1.1, 9.9.9.9.
> Penjelasan: Dipakai hanya untuk mengetahui alamat upstream bertipe nama (DoH).
3. Filters &gt; DNS blocklists &gt; Add blocklist &gt; Choose from the list: aktifkan daftar yang disarankan.
> Penjelasan: Daftar blokir memuat ribuan domain iklan dan pelacak.
4. Settings &gt; General settings: aktifkan statistik dan log kueri (retensi 24 jam sampai 7 hari).
> Penjelasan: Agar terlihat siapa meminta apa. Retensi pendek menghemat disk STB.
5. Filters &gt; DNS rewrites: akan dipakai di Bab 19 untuk nama lokal.
Tes AdGuard

**COMMAND PROMPT WINDOWS** | Windows (laptop)

```
nslookup google.com 192.168.88.253
```
> Penjelasan: Tes jawaban normal: harus menampilkan alamat IP.
```
nslookup doubleclick.net 192.168.88.253
```
> Penjelasan: Tes blokir: harus menjawab 0.0.0.0 (domain iklan diblokir).
Konfigurasi di MikroTik

**TERMINAL MIKROTIK** | WinBox &gt; New Terminal

```
/ip dhcp-server network set 0 dns-server=192.168.88.253
```
> Penjelasan: Membagikan AdGuard sebagai DNS ke seluruh klien DHCP.
```
/ip dns set servers=192.168.88.253 allow-remote-requests=no
```
> Penjelasan: DNS untuk router sendiri.

**COMMAND PROMPT WINDOWS** | Windows (laptop)

```
ipconfig /renew
```
> Penjelasan: Meminta DHCP ulang agar laptop memakai DNS baru.
```
ipconfig /all
```
> Penjelasan: Memeriksa baris DNS Servers: harus 192.168.88.253.
Backup AdGuard

**POWERSHELL WINDOWS** | PowerShell (laptop)

```
scp root@192.168.88.253:/opt/AdGuardHome/AdGuardHome.yaml .
```
> Penjelasan: Menyalin berkas konfigurasi lengkap ke folder aktif di laptop. Atau pakai WinSCP.

## 12.4 Instal dan konfigurasi Tailscale

Tailscale membuat jaringan privat antar perangkat Anda tanpa membuka port di router. Dengan subnet
router, STB membuat seluruh jaringan 192.168.88.0/24 dapat dijangkau dari HP/laptop di mana saja:
halaman MikroTik, Proxmox, Nextcloud, dan lainnya.
Instalasi pada STB

**TERMINAL (login sebagai root)** | SSH ke STB (root)

```
curl -fsSL https://tailscale.com/install.sh | sh
```
> Penjelasan: Mengunduh dan memasang Tailscale resmi untuk Debian/Armbian.
```
echo 'net.ipv4.ip_forward = 1' > /etc/sysctl.d/99-tailscale.conf
```
> Penjelasan: Mengaktifkan penerusan paket IPv4 agar STB dapat berfungsi sebagai router.
```
echo 'net.ipv6.conf.all.forwarding = 1' >> /etc/sysctl.d/99-tailscale.conf
```
> Penjelasan: Mengaktifkan penerusan IPv6.
```
sysctl -p /etc/sysctl.d/99-tailscale.conf
```
> Penjelasan: Menerapkan pengaturan tanpa reboot.
```
tailscale up --advertise-routes=192.168.88.0/24 --accept-dns=false
```
> Penjelasan: Menghubungkan STB ke akun Tailscale dan mengumumkan jaringan rumah.
--accept-dns=false mencegah Tailscale mengubah DNS di STB yang menjalankan AdGuard.
Login dan persetujuan rute
1. Perintah terakhir menampilkan tautan login. Buka di browser laptop dan masuk (akun Google,
Microsoft, atau GitHub).
> Penjelasan: Mendaftarkan STB ke akun Anda.
2. Buka login.tailscale.com/admin/machines. Pada baris STB klik ... &gt; Edit route settings, centang
192.168.88.0/24, Save.
> Penjelasan: Rute yang diumumkan tidak aktif sebelum Anda menyetujuinya.
3. Pada menu ... yang sama pilih Disable key expiry.
> Penjelasan: Agar STB tidak terputus saat kunci kedaluwarsa (default sekitar 180 hari).
4. Opsional: di DNS &gt; Add nameserver &gt; Custom isi 192.168.88.253 dan aktifkan Override local
DNS.
> Penjelasan: Perangkat Anda di luar rumah memakai AdGuard rumah, sehingga iklan terblokir di mana saja.
Menyambungkan HP dan laptop
1. Pasang aplikasi Tailscale (HP, Windows, macOS) dan login dengan akun yang sama.
> Penjelasan: Windows, Android, dan iOS menerima rute subnet secara otomatis. Linux perlu tailscale up
--accept-routes.
2. Matikan WiFi di HP (pakai data seluler) dan buka http://192.168.88.1 atau
https://192.168.88.10:8006.
> Penjelasan: Jika halaman terbuka, akses jarak jauh sudah bekerja.

**TERMINAL (login sebagai root)** | SSH ke STB

```
tailscale status
```
> Penjelasan: Menampilkan perangkat dalam jaringan Tailscale dan statusnya.
```
tailscale ip -4
```
> Penjelasan: Menampilkan alamat Tailscale STB (100.x.y.z).
Konfigurasi di MikroTik
CATATAN
Tidak ada rute atau port forward yang perlu ditambahkan di MikroTik. Tailscale mengubah alamat sumber paket
(SNAT) sehingga perangkat rumah membalas langsung ke STB. Cukup pastikan STB mendapat IP tetap (12.2).
PERINGATAN
Jangan membuka port 8006, 22, atau 80 MikroTik ke internet. Seluruh akses jarak jauh cukup lewat Tailscale.
Cadangan dan masalah umum
• Subnet router cadangan bisa dipasang di LXC Proxmox (Bab 13.8) untuk berjaga jika STB mati.
• Bila subnet tidak terjangkau dari luar: pastikan rute disetujui, sysctl net.ipv4.ip_forward bernilai
1, dan jaringan tempat Anda berada tidak memakai subnet yang sama (192.168.88.0/24).
• Jika STB mati, akses jarak jauh dan DNS utama berhenti: itu sebabnya DNS kedua (Bab 13) penting.
KASUS NYATA - Subnet tidak bisa dijangkau dari luar rumah
Gejala: Setelah tailscale up, alamat 192.168.88.x tidak terbuka dari HP.
Penyebab: Rute belum disetujui, IP forwarding belum aktif, atau jaringan tempat Anda berada memakai subnet
yang sama.
Solusi: Setujui rute di konsol admin, cek sysctl net.ipv4.ip_forward, dan bila bentrok subnet
pertimbangkan mengganti rentang jaringan rumah.
KASUS NYATA - AdGuard gagal start karena port 53 dipakai
Gejala: Wizard atau layanan menolak karena address already in use pada port 53.
Penyebab: systemd-resolved memakai 127.0.0.53:53.
Solusi: Atur DNSStubListener=no (12.3), restart systemd-resolved, lalu restart AdGuard.


<!-- SOURCE: docs/bab/edisi2/13-adguard-pihole-failover.md -->

# Bab 13. Pemblokir Iklan: AdGuard atau Pi-hole, dan Rancangan 3 Server

Bab ini menjawab dua pertanyaan: mana yang cocok, AdGuard Home atau Pi-hole, dan apakah ide
memakai 3 aplikasi (2 bekerja, 1 sebagai balancer) masuk akal. Setelah itu dipasang pasangan
AdGuard di Proxmox dan failover-nya.

## 13.1 AdGuard Home vs Pi-hole

Keduanya adalah DNS sinkhole: perangkat bertanya alamat sebuah domain ke mereka, dan domain
iklan/pelacak dijawab 0.0.0.0 sehingga iklan tidak termuat.
Aspek AdGuard Home Pi-hole
Pemasangan Satu berkas program (Go); skrip resmi satu
baris
Skrip instalasi; memasang beberapa
komponen (FTL berbasis dnsmasq)
Antarmuka Modern, satu halaman, banyak pengaturan Sederhana, berfokus pada statistik dan
daftar blokir
DNS terenkripsi ke upstream
(DoH/DoT/DoQ)
Bawaan Perlu tambahan (misalnya Unbound atau
cloudflared)
Pengaturan per
perangkat/klien
Bawaan, mudah (aturan, kategori, jadwal) Ada lewat Groups, lebih manual
Server DHCP bawaan Ada Ada
Daftar blokir dan aturan
kustom
Ya, sintaks aturan mirip filter adblock Ya, daftar domain dan regex
Pemakaian sumber daya Sangat ringan Ringan
Sinkronisasi dua server adguardhome-sync (pihak ketiga) Gravity Sync atau Nebula Sync (pihak
ketiga)
Komunitas dan dokumentasi Besar Sangat besar dan lama
Cocok untuk Pemula sampai menengah yang ingin fitur
lengkap
Yang ingin sederhana dan sangat teruji
TIPS
Rekomendasi untuk proyek ini: AdGuard Home. Sudah berjalan di STB, sangat ringan, punya DoH/DoT
bawaan dan pengaturan per klien. Memakai satu jenis di kedua server juga membuat sinkronisasi pengaturan
lebih mudah. Pi-hole tetap pilihan bagus; cara memasangnya ada di 13.9.

## 13.2 Memikirkan ide: 3 aplikasi, 2 bekerja dan 1 sebagai balancer

Ada tiga cara menyusun lebih dari satu server DNS. Ide Anda sesuai Opsi 3.
Opsi 1 (disarankan)
DHCP memberi 2 DNS
Klien
Opsi 2
DNS + IP virtual (keepalived)
Klien
Opsi 3 (ide balancer)
3 server, 1 sebagai pembagi
Klien
AdGuard 1
STB
AdGuard 2
LXC
Klien memakai kedua DNS
Satu mati, yang lain jalan
IP virtual 192.168.88.5
AdGuard 1
MASTER
AdGuard 2
BACKUP
IP pindah otomatis
dnsdist (pembagi)
AdGuard 1
STB
AdGuard 2
LXC
Jika pembagi mati,
semua DNS ikut mati
Gambar 13.1 - Tiga cara menyusun server DNS.
Opsi Cara kerja Kelebihan Kekurangan
1. Dua DNS di
DHCP
MikroTik membagikan dua
alamat DNS; klien memakai
salah satunya
Sederhana, tanpa komponen
tambahan, tidak ada titik gagal
baru
Bukan pembagian beban yang
sempurna; sebagian klien
butuh beberapa detik beralih
saat server mati
2. IP virtual
(keepalived)
Dua server berbagi satu IP; IP
pindah ke server yang hidup
Satu IP tetap; peralihan cepat Perlu keepalived di kedua
server; kadang tidak stabil di
WiFi
3. Balancer
(dnsdist)
Server ketiga menerima semua
kueri lalu membagi ke dua
AdGuard
Pembagian beban nyata,
pemeriksaan kesehatan,
cache, latihan bagus
Balancer itu sendiri menjadi
titik gagal tunggal; statistik
AdGuard hanya melihat IP
balancer; tambahan latensi
Kesimpulan
• Untuk rumah: Opsi 1. Dua AdGuard sudah memberi ketahanan, tanpa menambah komponen.
• Opsi 3 tepat sebagai latihan (konsep load balancing dan health check). Di rumah, balancer yang mati
justru mematikan seluruh DNS, sehingga hasilnya lebih rapuh dari Opsi 1, kecuali balancer sendiri
dibuat redundan (dua dnsdist + keepalived).
• Gabungan yang masuk akal: STB (AdGuard utama) + LXC (AdGuard kedua) + dua DNS di DHCP,
dan opsional dnsdist di LXC untuk latihan.
CATATAN
Pada Opsi 3, AdGuard akan menganggap semua kueri datang dari alamat dnsdist, sehingga statistik per
perangkat dan pengaturan per klien tidak lagi berguna.

## 13.3 Memasang AdGuard Home kedua (LXC 101)

1. Buat CT 101 adguard2 (Bab 10), IP 192.168.88.11 lewat static lease.
> Penjelasan: Container ringan cocok untuk DNS.
2. Masuk konsol CT 101 sebagai root.
> Penjelasan: Tanpa sudo.

**TERMINAL (login sebagai root)** | Console CT 101 (root)

```
apt update && apt install -y curl
```
> Penjelasan: Memasang curl (jika belum).
```
U=https://raw.githubusercontent.com/AdguardTeam/AdGuardHome/master/scripts
curl -s -S -L "$U/install.sh" | sh -s -- -v
```
> Penjelasan: Memasang AdGuard Home di /opt/AdGuardHome.
```
ss -tulpn | grep :53
```
> Penjelasan: Memeriksa apakah port 53 sudah dipakai program lain. Jika ya, bebaskan seperti di Bab 12.3.
1. Buka http://192.168.88.11:3000 dan jalankan wizard seperti di Gambar 12.1 (admin port 80, DNS
port 53).
2. Atur upstream dan blocklist sama persis dengan AdGuard di STB (12.3).
> Penjelasan: Agar kedua server memblokir hal yang sama. Otomatisnya dengan adguardhome-sync (13.4).

## 13.4 Menyamakan pengaturan dengan adguardhome-sync

adguardhome-sync menyalin daftar blokir, aturan kustom, klien, dan DNS rewrites dari server utama
(origin) ke server cadangan (replica). Dijalankan di Docker pada VM Debian 13 (Bab 14); jalankan bagian
ini setelah Docker terpasang.

**BERKAS: /opt/stacks/adguard-sync/compose.yaml** | VM Debian 13 (192.168.88.20)

```
services:
  adguardhome-sync:
    image: ghcr.io/bakito/adguardhome-sync:latest
    container_name: adguardhome-sync
    command: run
    restart: unless-stopped
    environment:
      - ORIGIN_URL=http://192.168.88.253
      - ORIGIN_USERNAME=admin
      - ORIGIN_PASSWORD=GANTI
      - REPLICA1_URL=http://192.168.88.11
      - REPLICA1_USERNAME=admin
      - REPLICA1_PASSWORD=GANTI
      - CRON=*/15 * * * *
      - RUNONSTART=true
```

**TERMINAL (login sebagai root)** | VM Debian 13 (root)

```
mkdir -p /opt/stacks/adguard-sync && cd /opt/stacks/adguard-sync
```
> Penjelasan: Membuat folder untuk stack ini.
```
nano compose.yaml
```
> Penjelasan: Tempel isi di atas. Ganti password.
```
docker compose up -d
```
> Penjelasan: Menjalankan layanan sinkronisasi.
```
docker compose logs -f
```
> Penjelasan: Melihat log. Harus ada baris sinkronisasi sukses.
TIPS
Pada pemakaian jangka panjang, tulis versi image yang tetap (bukan latest) lalu biarkan Renovate (Bab 22)
mengusulkan pembaruannya.

## 13.5 Opsi 1: dua DNS di DHCP MikroTik

**TERMINAL MIKROTIK** | WinBox &gt; New Terminal

```
/ip dhcp-server network print
```
> Penjelasan: Melihat nomor baris jaringan DHCP (biasanya 0).
```
/ip dhcp-server network set 0 dns-server=192.168.88.253,192.168.88.11
```
> Penjelasan: Mengisi dua DNS: STB (utama) lalu LXC (cadangan).
```
/ip dns set servers=192.168.88.253,192.168.88.11 allow-remote-requests=no
```
> Penjelasan: DNS untuk router sendiri.

**COMMAND PROMPT WINDOWS** | Windows (laptop)

```
ipconfig /renew
```
> Penjelasan: Memperbarui lease DHCP di laptop.
```
ipconfig /all
```
> Penjelasan: Harus tampil dua DNS Server (.253 dan .11).
```
nslookup doubleclick.net 192.168.88.253
```
> Penjelasan: Tes AdGuard utama: jawaban 0.0.0.0.
```
nslookup doubleclick.net 192.168.88.11
```
> Penjelasan: Tes AdGuard kedua: jawaban 0.0.0.0.
Uji failover
1. Di Proxmox, Shutdown CT 101.
> Penjelasan: Mensimulasikan server cadangan mati.
2. Dari laptop buka beberapa situs baru.
> Penjelasan: Internet harus tetap normal lewat STB.
3. Nyalakan CT 101, lalu hentikan layanan AdGuard di STB (/opt/AdGuardHome/AdGuardHome -s
stop) dan ulangi uji.
> Penjelasan: Menguji arah sebaliknya. Jangan lupa menyalakan lagi (-s start).
PERINGATAN
Jangan menambahkan DNS publik (8.8.8.8) sebagai DNS ketiga di DHCP, karena sebagian klien akan lolos
dari pemblokiran iklan.

## 13.6 Opsi 2: IP virtual dengan keepalived

Hasilnya satu alamat (misalnya 192.168.88.5) yang selalu hidup. Pasang di STB dan di LXC 101, lalu klien
memakai 192.168.88.5 sebagai satu-satunya DNS.

**TERMINAL (login sebagai root)** | STB dan LXC 101 (root)

```
apt install -y keepalived
```
> Penjelasan: Memasang keepalived di kedua server.
```
ip -br a
```
> Penjelasan: Mencatat nama kartu jaringan (eth0 di LXC, end0/eth0 di STB).
```
nano /etc/keepalived/keepalived.conf
```
> Penjelasan: Membuat konfigurasi (isi di bawah).
```
systemctl enable --now keepalived
```
> Penjelasan: Menyalakan dan mengaktifkan setiap boot.
```
ip -br a
```
> Penjelasan: Pada server MASTER, alamat 192.168.88.5 harus muncul di kartu jaringan.

**BERKAS: /etc/keepalived/keepalived.conf** | STB = MASTER (priority 150), LXC 101 = BACKUP (priority 100)

```
vrrp_instance DNS_VIP {
state MASTER # di server cadangan ganti BACKUP
interface eth0 # nama kartu jaringan
virtual_router_id 51
priority 150 # di server cadangan pakai 100
advert_int 1
authentication {
auth_type PASS
auth_pass GANTI8
}
virtual_ipaddress {
192.168.88.5/24
}
}
```

**TERMINAL MIKROTIK** | WinBox &gt; New Terminal

```
/ip dhcp-server network set 0 dns-server=192.168.88.5
```
> Penjelasan: Membagikan IP virtual sebagai satu-satunya DNS.
CATATAN
VRRP kadang bermasalah di jaringan WiFi. Uji di jaringan kabel. Jika tidak stabil,
kembali ke Opsi 1.

## 13.7 Opsi 3: balancer dengan dnsdist (latihan)

Tujuan: LXC 104 dnsdist (alamat 192.168.88.13) menerima semua kueri lalu membaginya ke dua
AdGuard (STB dan LXC 101) dengan pemeriksaan kesehatan otomatis.
1. Buat CT 104 dnsdist (1 core, 256 MB, 4 GB), IP 192.168.88.13 lewat static lease.
2. Di dalam CT, pasang dnsdist dan atur konfigurasinya.
> Penjelasan: dnsdist adalah pembagi beban DNS resmi dari PowerDNS.

**TERMINAL (login sebagai root)** | Console CT 104 (root)

```
apt update && apt install -y dnsdist
```
> Penjelasan: Memasang dnsdist dari repository Debian.
```
nano /etc/dnsdist/dnsdist.conf
```
> Penjelasan: Mengisi konfigurasi (isi di bawah).
```
systemctl restart dnsdist
```
> Penjelasan: Menerapkan konfigurasi.
```
systemctl status dnsdist
```
> Penjelasan: Memastikan layanan berjalan (active).
```
dnsdist -c
```
> Penjelasan: Membuka konsol dnsdist. Ketik showServers() untuk melihat status tiap server, quit untuk
keluar.

**BERKAS: /etc/dnsdist/dnsdist.conf** | Konfigurasi dnsdist

```
setLocal("0.0.0.0:53")
addACL("192.168.88.0/24")
newServer({address="192.168.88.253:53", name="adguard-stb",
checkInterval=5, maxCheckFailures=3})
newServer({address="192.168.88.11:53", name="adguard-lxc",
checkInterval=5, maxCheckFailures=3})
setServerPolicy(leastOutstanding)
```

Baris Arti
setLocal(...) dnsdist mendengarkan di port 53 pada semua alamat.
addACL(...) Hanya jaringan 192.168.88.0/24 yang boleh bertanya (mencegah DNS
terbuka).
newServer(...) Mendaftarkan satu server tujuan (AdGuard) dan memeriksa
kesehatannya tiap 5 detik.
setServerPolicy(leastOutstanding) Mengirim kueri ke server yang paling sedikit antreannya. Alternatif:
roundrobin, firstAvailable.

**COMMAND PROMPT WINDOWS** | Windows (laptop)

```
nslookup doubleclick.net 192.168.88.13
```
> Penjelasan: Tes lewat dnsdist: harus menjawab 0.0.0.0.
```
nslookup google.com 192.168.88.13
```
> Penjelasan: Tes jawaban normal.

**TERMINAL MIKROTIK** | WinBox &gt; New Terminal

```
/ip dhcp-server network set 0 dns-server=192.168.88.13
```
> Penjelasan: Mengarahkan seluruh klien ke dnsdist.
PERINGATAN
Jika CT 104 mati, seluruh DNS rumah ikut mati karena hanya satu alamat yang dibagikan. Untuk menguji,
kembalikan DHCP ke Opsi 1 (dns-server=192.168.88.253,192.168.88.11) kapan saja. Jika port 53
sudah dipakai di LXC, bebaskan seperti di Bab 12.3.

## 13.8 Subnet router Tailscale cadangan (opsional)

Untuk berjaga bila STB mati, pasang Tailscale juga di container LXC (misalnya CT 103) dengan akses ke
perangkat TUN.

**TERMINAL (login sebagai root)** | Shell Proxmox

```
pct shutdown 103
```
> Penjelasan: Mematikan CT 103 sebelum mengubah konfigurasi.
```
nano /etc/pve/lxc/103.conf
```
> Penjelasan: Tambahkan dua baris di akhir berkas (isi di bawah).
```
pct start 103
```
> Penjelasan: Menyalakan kembali.

**BERKAS: /etc/pve/lxc/103.conf** | Tambahkan di akhir berkas

```
lxc.cgroup2.devices.allow: c 10:200 rwm
lxc.mount.entry: /dev/net/tun dev/net/tun none bind,create=file
```

Lalu di dalam CT 103 pasang Tailscale seperti Bab 12.4 dan setujui rute yang sama; Tailscale beralih
otomatis jika satu perangkat mati.

## 13.9 Memasang Pi-hole (jika memilih Pi-hole)

**TERMINAL (login sebagai root)** | Console CT (root), contoh CT 105 192.168.88.14

```
apt update && apt install -y curl
```
> Penjelasan: Memasang curl.
```
curl -sSL https://install.pi-hole.net | bash
```
> Penjelasan: Menjalankan installer resmi Pi-hole. Ikuti wizard teks: pilih interface, upstream DNS, blocklist, dan
catat password admin.
```
pihole setpassword
```
> Penjelasan: Mengubah password admin web.
Web admin di http://192.168.88.14/admin. Pengaturan MikroTik sama (isi DNS di DHCP). Jangan
menjalankan Pi-hole dan AdGuard di mesin yang sama karena bentrok port 53.

## 13.10 Opsional: mencegah perangkat memakai DNS lain

Sebagian aplikasi atau TV memakai DNS bawaan (misalnya 8.8.8.8) sehingga lolos dari pemblokiran.
MikroTik dapat memblokir permintaan DNS ke internet kecuali dari server AdGuard.

**TERMINAL MIKROTIK** | WinBox &gt; New Terminal (opsional)

```
/ip firewall address-list add list=dns-servers address=192.168.88.253
```
> Penjelasan: Daftar server DNS yang diizinkan: STB.
```
/ip firewall address-list add list=dns-servers address=192.168.88.11
```
```
/ip firewall filter add chain=forward action=drop protocol=udp dst-port=53 out-interface=ether1 src-address-list=!dns-servers place-before=0 comment="blok DNS UDP luar"
```
> Penjelasan: Menjatuhkan DNS UDP ke internet kecuali dari AdGuard.
```
/ip firewall filter add chain=forward action=drop protocol=tcp dst-port=53 out-interface=ether1 src-address-list=!dns-servers place-before=0 comment="blok DNS TCP luar"
```
> Penjelasan: Sama untuk DNS TCP.
PERINGATAN
Aturan ini memutus perangkat yang tidak memakai DNS dari DHCP. Uji dulu, dan siapkan cara membatalkan
(/ip firewall filter remove [find comment~"blok DNS"]). DNS-over-HTTPS (port 443) di browser
tidak terblokir oleh aturan ini.
KASUS NYATA - Satu perangkat masih menampilkan iklan
Gejala: Sebagian perangkat tidak memblokir iklan.
Penyebab: Perangkat memakai DNS sendiri (Secure DNS di browser, DNS tetap, lease lama).
Solusi: Matikan Secure DNS di browser, setel DNS otomatis, ipconfig /renew, atau gunakan aturan di
13.10.


<!-- SOURCE: docs/bab/edisi2/14-docker-portainer.md -->

# Bab 14. Docker dan Portainer

## 14.1 Ringkasan

Item Isi
Fungsi Docker menjalankan aplikasi dalam wadah terisolasi. Portainer adalah antarmuka web untuk
mengelola Docker.
Tempat VM Debian 13 (VM 201), alamat 192.168.88.20
Mengapa VM, bukan
LXC
Docker di dalam LXC sering bermasalah (izin, nesting, kernel). VM jauh lebih stabil.
Port Portainer 9443 (HTTPS) dan 8000

## 14.2 Instalasi Docker

Docker dipasang dari repository resmi Docker untuk Debian. Login sebagai root (su -), jadi perintah tanpa
sudo.

**TERMINAL (login sebagai root)** | VM Debian 13 (root)

```
apt update && apt install -y ca-certificates curl
```
> Penjelasan: Memasang paket yang dibutuhkan untuk mengunduh dan memverifikasi repository.
```
install -m 0755 -d /etc/apt/keyrings
```
> Penjelasan: Membuat folder penyimpanan kunci repository.
```
curl -fsSL https://download.docker.com/linux/debian/gpg -o /etc/apt/keyrings/docker.asc
```
> Penjelasan: Mengunduh kunci GPG Docker untuk memverifikasi paket.
```
chmod a+r /etc/apt/keyrings/docker.asc
```
> Penjelasan: Agar kunci bisa dibaca apt.
Lalu tambahkan repository Docker dalam format .sources:

**BERKAS: /etc/apt/sources.list.d/docker.sources** | Buat dengan: nano /etc/apt/sources.list.d/docker.sources

```
Types: deb
URIs: https://download.docker.com/linux/debian
Suites: trixie
Components: stable
Signed-By: /etc/apt/keyrings/docker.asc
```

**TERMINAL (login sebagai root)** | VM Debian 13 (root)

```
apt update
```
> Penjelasan: Memuat daftar paket Docker.
```
apt install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
```
> Penjelasan: Memasang Docker Engine dan plugin Compose.
```
docker run --rm hello-world
```
> Penjelasan: Menjalankan container uji. Harus menampilkan "Hello from Docker!".
```
docker compose version
```
> Penjelasan: Memastikan plugin Compose terpasang.
CATATAN
Karena Anda sudah root, tidak perlu menambahkan user ke grup docker. Jika ingin memakai user biasa:
usermod -aG docker NAMAUSER lalu login ulang.

## 14.3 Perintah Docker yang sering dipakai

Tujuan Perintah
Container berjalan docker ps (tambah -a untuk semua)
Lihat log docker logs -f NAMA
Masuk ke container docker exec -it NAMA sh
Naikkan stack docker compose up -d (di folder berisi compose.yaml)
Turunkan stack docker compose down
Perbarui image docker compose pull && docker compose up -d
Bersihkan yang tak terpakai docker system prune (hati-hati)
Biasakan satu folder per aplikasi di /opt/stacks/NAMA/compose.yaml. Dengan begitu mudah di-backup
dan nanti diserahkan ke Git (Bab 15).

## 14.4 Memasang Portainer

**TERMINAL (login sebagai root)** | VM Debian 13 (root)

```
docker volume create portainer_data
```
> Penjelasan: Membuat penyimpanan permanen untuk data Portainer.
```
docker run -d -p 8000:8000 -p 9443:9443 --name portainer --restart=always \
  -v /var/run/docker.sock:/var/run/docker.sock \
  -v portainer_data:/data portainer/portainer-ce:lts
```
> Penjelasan: Menjalankan Portainer CE. --restart=always agar hidup kembali setelah reboot. Akses ke docker.sock dibutuhkan agar Portainer bisa mengelola Docker.
```
docker ps
```
> Penjelasan: Memastikan container portainer berstatus Up.
1. Buka https://192.168.88.20:9443 dan lewati peringatan sertifikat.
> Penjelasan: Sertifikat dibuat sendiri oleh Portainer.
2. Buat user admin dengan password kuat dalam beberapa menit pertama.
> Penjelasan: Setelah beberapa menit tanpa pendaftaran, Portainer menutup halaman ini demi keamanan (lihat
kasus di bawah).
3. Pilih Get Started untuk mengelola Docker lokal. Menu: Containers, Images, Volumes, Networks,
Stacks.
> Penjelasan: Stacks adalah cara memasang aplikasi dari berkas compose.
4. Memasang aplikasi: Stacks &gt; Add stack, tempel isi compose.yaml, Deploy the stack.
> Penjelasan: Alternatif dari terminal docker compose up -d.
Konfigurasi di MikroTik dan jaringan
• Alamat 192.168.88.20 sudah direservasi (Bab 11.6). Tidak ada aturan firewall tambahan; akses hanya
dari jaringan lokal.
• Nama lokal portainer.lan dibuat di Bab 19 (DNS rewrites) lalu dipakai di dashboard.
• Akses dari luar rumah hanya lewat Tailscale.
Backup dan pemulihan
• Backup VM 201 lewat Proxmox (Bab 23) mencakup Docker, Portainer, dan semua volume.
• Data aplikasi ada di folder /opt/stacks/\* dan volume Docker (/var/lib/docker/volumes).
KASUS NYATA - Portainer: instance timed out for security
Gejala: Halaman meminta restart karena batas waktu pembuatan admin terlampaui.
Penyebab: Pendaftaran admin awal ditutup bila tidak diisi dalam beberapa menit.
Solusi: Jalankan docker restart portainer, buka lagi https://192.168.88.20:9443, dan segera buat
admin.
KASUS NYATA - docker: permission denied while trying to connect to the Docker daemon socket
Gejala: Perintah docker ... ditolak.
Penyebab: Dijalankan sebagai user biasa yang belum masuk grup docker.
Solusi: Jadilah root (su -), atau usermod -aG docker NAMAUSER lalu login ulang.


<!-- SOURCE: docs/bab/edisi2/15-forgejo.md -->

# Bab 15. Git Pribadi dengan Forgejo

## 15.1 Ringkasan

Item Isi
Fungsi Forgejo adalah layanan Git yang dijalankan sendiri (mirip GitHub) untuk menyimpan kode,
proyek, dan konfigurasi server.
Tempat Docker di VM Debian 13 (192.168.88.20)
Port Web 3000, SSH Git 2222
Sumber daya Sekitar 200-300 MB RAM; database SQLite cukup untuk pemakaian pribadi
Dokumentasi: forgejo.org.

## 15.2 Instalasi

**TERMINAL (login sebagai root)** | VM Debian 13 (root)

```
mkdir -p /opt/stacks/forgejo && cd /opt/stacks/forgejo
```
> Penjelasan: Membuat folder khusus aplikasi dan masuk ke dalamnya.
```
nano compose.yaml
```
> Penjelasan: Membuat berkas compose. Isinya ada di bawah.

**BERKAS: /opt/stacks/forgejo/compose.yaml** | Ganti &lt;VERSI-MAYOR&gt; dengan versi mayor terbaru (cek halaman rilis Forgejo)

```
services:
 server:
 image: codeberg.org/forgejo/forgejo:<VERSI-MAYOR>
 container_name: forgejo
 restart: always
 environment:
 - USER_UID=1000
 - USER_GID=1000
volumes:
 - ./forgejo:/data
 - /etc/timezone:/etc/timezone:ro
 - /etc/localtime:/etc/localtime:ro
 ports:
 - "3000:3000"
 - "2222:22"
```

Baris Arti
image: ... Image Forgejo. Pakai versi tetap (mis. 11) agar tidak berubah mendadak;
Renovate akan mengusulkan pembaruan.
restart: always Hidup kembali otomatis setelah reboot.
volumes: ./forgejo:/data Seluruh data (repo, database, konfigurasi) disimpan di folder forgejo di
samping compose.yaml.
3000:3000 Web Forgejo di port 3000 host.
Baris Arti
2222:22 SSH Git di port 2222 host (port 22 host dipakai SSH VM).

**TERMINAL (login sebagai root)** | Folder /opt/stacks/forgejo (root)

```
docker compose up -d
```
> Penjelasan: Menjalankan Forgejo di latar belakang.
```
docker compose logs -f
```
> Penjelasan: Memantau log sampai muncul pesan siap. Tekan Ctrl+C untuk berhenti melihat log.

## 15.3 Konfigurasi awal di web

Forgejo - Initial Configuration (http://192.168.88.20:3000)
Database Type SQLite3
Site Title Git Rumah
1 Server Domain 192.168.88.20
2 SSH Server Port 2222
Forgejo HTTP Listen Port 3000
3 Forgejo Base URL http://192.168.88.20:3000/
4 Administrator Account admin / password / email
Install Forgejo
Gambar 15.1 - Ilustrasi halaman instalasi. (1) Domain = IP VM. (2) Port SSH 2222 agar alamat clone benar. (3) Base URL.
(4) Akun administrator.
1. Buka http://192.168.88.20:3000. Halaman instalasi awal muncul.
> Penjelasan: Jika tidak terbuka, periksa docker compose logs.
2. Database Type: SQLite3.
> Penjelasan: Tidak perlu server database terpisah untuk pemakaian pribadi.
3. Server Domain: 192.168.88.20 (atau git.lan setelah Bab 19). Base URL:
http://192.168.88.20:3000/.
> Penjelasan: Dipakai Forgejo untuk membuat tautan.
4. SSH Server Port: ubah menjadi 2222.
> Penjelasan: Port yang benar-benar dibuka ke luar. Jika dibiarkan 22, alamat clone SSH akan salah.
5. Buka Administrator Account Settings, isi username, email, dan password. Klik Install Forgejo.
> Penjelasan: Akun ini adalah admin pertama.

## 15.4 Repository dan kunci SSH

**POWERSHELL WINDOWS** | PowerShell (laptop)

```
ssh-keygen -t ed25519 -C "email@contoh.com"
```
> Penjelasan: Membuat pasangan kunci SSH di laptop (tekan Enter untuk semua pertanyaan).
```
type $env:USERPROFILE\.ssh\id_ed25519.pub
```
> Penjelasan: Menampilkan kunci publik untuk ditempel di Forgejo.
1. Forgejo: foto profil &gt; Settings &gt; SSH / GPG Keys &gt; Add Key, tempel isi berkas .pub.
> Penjelasan: Memberi Forgejo kunci publik agar laptop bisa login tanpa password.
2. + &gt; New Repository: nama homelab, Create Repository.
> Penjelasan: Repository ini dipakai untuk GitOps (Bab 21).

**TERMINAL (user biasa)** | Git Bash / PowerShell (laptop)

```
git clone ssh://git@192.168.88.20:2222/USERNAME/homelab.git
```
> Penjelasan: Menyalin repository ke laptop. Ganti USERNAME. Perhatikan port 2222.
```
cd homelab
```
> Penjelasan: Masuk ke folder repository.
```
echo "# homelab" > README.md
```
> Penjelasan: Membuat berkas pertama.
```
git add . && git commit -m "awal" && git push
```
> Penjelasan: Menyimpan dan mengirim ke Forgejo.

## 15.5 Konfigurasi di MikroTik dan jaringan

• Tidak perlu aturan firewall; akses dari jaringan lokal. Alamat 192.168.88.20 sudah direservasi.
• Tambahkan DNS rewrite git.lan -&gt; 192.168.88.20 di AdGuard (Bab 19).
• Akses dari luar rumah hanya lewat Tailscale (ssh://git@192.168.88.20:2222/... tetap bisa
dipakai).

## 15.6 Backup

**TERMINAL (login sebagai root)** | VM Debian 13 (root)

```
cd /opt/stacks/forgejo && docker compose down
```
> Penjelasan: Menghentikan Forgejo agar data konsisten.
```
tar czf /root/forgejo-backup.tgz forgejo compose.yaml
```
> Penjelasan: Mengarsipkan folder data dan compose.
```
docker compose up -d
```
> Penjelasan: Menyalakan kembali.
Selain itu, backup seluruh VM 201 lewat Proxmox (Bab 23).
KASUS NYATA - Alamat clone SSH salah (port 22, bukan 2222)
Gejala: Forgejo menampilkan ssh://git@host/... tanpa port sehingga clone gagal.
Penyebab: Field SSH Server Port tidak diubah menjadi 2222 saat instalasi.
Solusi: Edit forgejo/gitea/conf/app.ini pada bagian [server]: SSH_PORT = 2222, lalu docker
compose restart.


<!-- SOURCE: docs/bab/edisi2/16-nextcloud.md -->

# Bab 16. Nextcloud

## 16.1 Ringkasan

Item Isi
Fungsi Cloud pribadi: sinkronisasi file, kalender, kontak, akses dari HP dan laptop (pengganti Google
Drive).
Tempat Docker di VM Debian 13 (192.168.88.20), port 8080
Komponen Nextcloud (web), MariaDB (database), Redis (cache)
Sumber daya 1 GB RAM atau lebih, ruang disk sesuai file Anda
CATATAN
Nextcloud (aplikasi cloud) berbeda dari TrueNAS (sistem operasi NAS dengan ZFS). Untuk lab, Nextcloud dan
Samba (Bab 17) cukup. TrueNAS dipasang di mesin asli.

## 16.2 Instalasi

**TERMINAL (login sebagai root)** | VM Debian 13 (root)

```
mkdir -p /opt/stacks/nextcloud && cd /opt/stacks/nextcloud
```
> Penjelasan: Membuat folder aplikasi.
```
nano .env
```
> Penjelasan: Berkas rahasia (password database). Isinya di bawah.
```
nano compose.yaml
```
> Penjelasan: Berkas compose utama (isi di bawah).

**BERKAS: /opt/stacks/nextcloud/.env** | Rahasia: jangan masukkan ke Git

```
DB_ROOT_PASSWORD=GANTI_ROOT
DB_PASSWORD=GANTI_DB
NC_HOST=192.168.88.20
```

**BERKAS: /opt/stacks/nextcloud/compose.yaml** | Pada pemakaian jangka panjang pin versi image (bukan `apache` tanpa versi)

```
services:
 db:
 image: mariadb:11.4
 restart: always
 command:
 - --transaction-isolation=READ-COMMITTED
 - --log-bin=binlog
 - --binlog-format=ROW
volumes:
 - ./db:/var/lib/mysql
 environment:
 - MYSQL_ROOT_PASSWORD=${DB_ROOT_PASSWORD}
 - MYSQL_PASSWORD=${DB_PASSWORD}
 - MYSQL_DATABASE=nextcloud
 - MYSQL_USER=nextcloud
 redis:
 image: redis:7-alpine
 restart: always
 app:
 image: nextcloud:apache
 container_name: nextcloud
 restart: always
 depends_on:
 - db
 - redis
 ports:
 - "8080:80"
volumes:
 - ./html:/var/www/html
 environment:
 - MYSQL_HOST=db
 - MYSQL_DATABASE=nextcloud
 - MYSQL_USER=nextcloud
 - MYSQL_PASSWORD=${DB_PASSWORD}
 - REDIS_HOST=redis
 - NEXTCLOUD_TRUSTED_DOMAINS=${NC_HOST} nextcloud.lan
```

Bagian Arti
db (MariaDB) Database; datanya di ./db. Perintah --transaction-isolation... wajib
untuk Nextcloud.
redis Cache untuk mempercepat dan mengunci file.
app (Nextcloud) Web Nextcloud di port 8080 host; seluruh aplikasi dan data di ./html.
${...} Nilai diambil dari berkas .env.
NEXTCLOUD_TRUSTED_DOMAINS Daftar alamat/nama yang boleh dipakai membuka Nextcloud.

**TERMINAL (login sebagai root)** | Folder /opt/stacks/nextcloud (root)

```
docker compose up -d
```
> Penjelasan: Menjalankan ketiga layanan.
```
docker compose logs -f app
```
> Penjelasan: Melihat log. Tunggu sampai Apache siap.

## 16.3 Konfigurasi di aplikasi

1. Buka http://192.168.88.20:8080 setelah log menunjukkan Apache siap.
> Penjelasan: Instalasi awal otomatis memakai database yang sudah terhubung.
2. Buat akun admin (username dan password kuat), lalu Install.
> Penjelasan: Biarkan database apa adanya.
3. Pasang aplikasi klien Nextcloud di Windows/HP, login dengan alamat server.
> Penjelasan: Sinkronisasi folder dan unggah foto otomatis dari HP.
4. Administration settings &gt; Basic settings &gt; Background jobs: pilih Cron.
> Penjelasan: Pekerjaan latar belakang berjalan stabil dan tidak bergantung pada pengunjung.

**TERMINAL (login sebagai root)** | VM Debian 13 (root)

```
crontab -e
```
> Penjelasan: Membuka daftar jadwal (pilih nano bila diminta). Tambahkan baris di bawah.

**BERKAS: crontab** | Tambahkan sebagai baris baru di crontab

```
*/5 * * * * docker exec -u www-data nextcloud php -f /var/www/html/cron.php
```

**TERMINAL (login sebagai root)** | VM Debian 13 (root)

```
docker exec -u www-data nextcloud php occ config:system:set trusted_domains 2 --value=nextcloud.lan
```
> Penjelasan: Menambah nama nextcloud.lan ke daftar domain tepercaya. Ulangi dengan angka 3, 4 untuk nama lain.

## 16.4 Konfigurasi di MikroTik dan jaringan

• Alamat 192.168.88.20 sudah direservasi (Bab 11.6).
• Tambahkan DNS rewrite nextcloud.lan -&gt; 192.168.88.20 di AdGuard (Bab 19). Port tetap 8080
(buka http://nextcloud.lan:8080).
• Jangan membuka port ke internet. Untuk akses dari luar rumah gunakan Tailscale (Bab 12.4).
• HTTPS di LAN: pasang reverse proxy (Caddy, Nginx Proxy Manager, atau Traefik) pada tahap
lanjutan.

## 16.5 Backup

**TERMINAL (login sebagai root)** | VM Debian 13 (root)

```
docker exec -u www-data nextcloud php occ maintenance:mode --on
```
> Penjelasan: Mengaktifkan mode pemeliharaan agar data tidak berubah saat dibackup.
```
cd /opt/stacks/nextcloud && docker compose down
```
> Penjelasan: Menghentikan layanan.
```
tar czf /root/nextcloud-backup.tgz db html compose.yaml .env
```
> Penjelasan: Mengarsipkan database, berkas, dan konfigurasi.
```
docker compose up -d
```
> Penjelasan: Menyalakan kembali.
```
docker exec -u www-data nextcloud php occ maintenance:mode --off
```
> Penjelasan: Mematikan mode pemeliharaan.
Cara paling mudah: backup VM 201 lewat Proxmox (Bab 23). Salin berkas backup keluar dari server.
KASUS NYATA - Access through untrusted domain
Gejala: Nextcloud menolak alamat yang dipakai di browser.
Penyebab: Alamat/nama itu belum masuk daftar trusted_domains.
Solusi: Jalankan perintah occ config:system:set trusted_domains ... di 16.3, lalu muat ulang
halaman.


<!-- SOURCE: docs/bab/edisi2/17-samba.md -->

# Bab 17. Folder Jaringan (Samba)

## 17.1 Ringkasan

Samba membuat folder di server tampil sebagai folder jaringan di Windows (\\192.168.88.12\share).
Dijalankan di container LXC kecil (CT 102 files, 192.168.88.12).

## 17.2 Instalasi

1. Buat CT 102 files (Bab 10): 1 core, 256 MB RAM, disk 8 GB, IP lewat static lease
192.168.88.12.
> Penjelasan: Samba sangat ringan.
2. Masuk konsol CT 102 sebagai root.

**TERMINAL (login sebagai root)** | Console CT 102 (root)

```
apt update && apt install -y samba
```
> Penjelasan: Memasang Samba.
```
mkdir -p /srv/share
```
> Penjelasan: Membuat folder yang akan dibagikan.
```
adduser --no-create-home --disabled-password --shell /usr/sbin/nologin userfile
```
> Penjelasan: Membuat user Linux khusus untuk Samba (tanpa login shell).
```
smbpasswd -a userfile
```
> Penjelasan: Membuat password Samba untuk user itu (dimasukkan dua kali).
```
chown -R userfile:userfile /srv/share
```
> Penjelasan: Menjadikan user itu pemilik folder.
```
nano /etc/samba/smb.conf
```
> Penjelasan: Menambahkan definisi share di akhir berkas (isi di bawah).
```
systemctl restart smbd
```
> Penjelasan: Menerapkan konfigurasi.

**BERKAS: /etc/samba/smb.conf** | Tambahkan di akhir berkas

```
[share]
path = /srv/share
browseable = yes
read only = no
valid users = userfile
```

## 17.3 Memakai dari Windows

1. File Explorer &gt; This PC &gt; Map network drive.
2. Folder: \\192.168.88.12\share, centang Connect using different credentials.
3. Login userfile dengan password Samba.
> Penjelasan: Drive jaringan muncul seperti disk biasa.

## 17.4 Folder di disk lain (bind mount)

**TERMINAL (login sebagai root)** | Shell Proxmox

```
pct set 102 -mp0 /mnt/data,mp=/srv/share
```
> Penjelasan: Memasang folder /mnt/data di host Proxmox ke dalam container sebagai /srv/share.
CATATAN
Pada container unprivileged, UID di dalam dan di host berbeda (offset 100000), jadi izin folder host perlu
disesuaikan agar user di dalam container bisa menulis.

## 17.5 MikroTik dan backup

• Reservasi 192.168.88.12 (Bab 3.5). Tidak perlu firewall tambahan; port 445 hanya di jaringan lokal.
• Tambahkan rewrite files.lan -&gt; 192.168.88.12 (Bab 19).
• Backup: vzdump 102 --storage local (container) dan salin folder data penting ke disk lain.


<!-- SOURCE: docs/bab/edisi2/18-home-assistant.md -->

# Bab 18. Home Assistant OS

## 18.1 Ringkasan

Item Isi
Fungsi Otomasi rumah: lampu, sensor, saklar, dan perangkat pintar lainnya.
Tempat VM sendiri di Proxmox (VM 202), alamat 192.168.88.21, web port 8123
Sumber daya 2 core, 2 GB RAM, disk 32 GB
Catatan Jika Proxmox mati, otomasi berhenti. Untuk tahap belajar itu aman.
Unduh image dari halaman Releases Home Assistant OS (berkas haos_ova-VERSI.qcow2.xz). Panduan
resmi: home-assistant.io/installation.

## 18.2 Instalasi

**TERMINAL (login sebagai root)** | Shell Proxmox (root)

```
cd /var/lib/vz/template/iso
```
> Penjelasan: Pindah ke folder ISO Proxmox.
```
V=<VERSI>
```
> Penjelasan: Menyimpan nomor versi rilis dalam variabel (ganti dengan nomor versi terbaru).
```
URL=https://github.com/home-assistant/operating-system/releases/download/$V
```
> Penjelasan: Alamat dasar unduhan.
```
wget $URL/haos_ova-$V.qcow2.xz
```
> Penjelasan: Mengunduh image HAOS.
```
xz -d haos_ova-$V.qcow2.xz
```
> Penjelasan: Mengekstrak berkas (hasilnya haos_ova-VERSI.qcow2).

**TERMINAL (login sebagai root)** | Shell Proxmox (root)

```
qm create 202 --name haos --memory 2048 --cores 2 --cpu host \
  --bios ovmf --machine q35 --ostype l26 --scsihw virtio-scsi-pci \
  --agent enabled=1 --net0 virtio,bridge=vmbr0
```
> Penjelasan: Membuat VM 202 kosong dengan UEFI (ovmf) dan jaringan VirtIO.
```
qm set 202 --efidisk0 local-lvm:1,efitype=4m,pre-enrolled-keys=0
```
> Penjelasan: Membuat disk UEFI tanpa kunci Secure Boot (wajib untuk HAOS).
```
qm importdisk 202 /var/lib/vz/template/iso/haos_ova-$V.qcow2 local-lvm
```
> Penjelasan: Mengimpor image sebagai disk VM.
```
qm config 202
```
> Penjelasan: Menampilkan konfigurasi. Cari baris unused0: local-lvm:vm-202-disk-1 (nama disk hasil
impor).
```
qm set 202 --scsi0 local-lvm:vm-202-disk-1,discard=on,ssd=1
```
> Penjelasan: Memasang disk impor sebagai disk boot (sesuaikan nama dengan baris unused0).
```
qm set 202 --boot order=scsi0
```
> Penjelasan: Mengatur boot dari disk itu.
```
qm start 202
```
> Penjelasan: Menyalakan VM.
PERINGATAN
HAOS tidak mau boot jika Secure Boot aktif. Opsi pre-enrolled-keys=0 memastikan hal itu.

## 18.3 Memberi IP tetap dan membuka web

1. Proxmox: VM 202 &gt; Hardware &gt; Network Device, salin MAC address.
2. MikroTik: reservasi 192.168.88.21, comment vm-haos (Bab 3.5).
3. Reboot VM 202. Tunggu 5 sampai 20 menit sampai konsol
menampilkan alamat IP.
> Penjelasan: HAOS mengunduh komponen saat boot pertama.
4. Buka http://192.168.88.21:8123 dan ikuti onboarding: nama, akun admin, lokasi, unit.
> Penjelasan: Perangkat di jaringan akan ditemukan otomatis.

## 18.4 Konfigurasi di Home Assistant

• Settings &gt; Devices & Services: tambahkan integrasi yang ditemukan otomatis (lampu, TV, printer,
dan sebagainya).
• Integrasi AdGuard Home (alamat 192.168.88.253) untuk melihat statistik dan mematikan
pemblokiran dari HA.
• Integrasi Tailscale, Proxmox VE (butuh API token), dan Uptime/Ping untuk memantau server.
• Aplikasi Home Assistant di HP: Settings &gt; Companion app. Dari luar rumah akses lewat Tailscale
(alamat 192.168.88.21).
• Perangkat USB (dongle Zigbee/Z-Wave): VM 202 &gt; Hardware &gt; Add &gt; USB Device.
Integrasi MikroTik (opsional)
Integrasi MikroTik di HA memakai API router. Pada Bab 3.8 layanan api dimatikan. Aktifkan hanya untuk
alamat HA dan buat user khusus read-only:

**TERMINAL MIKROTIK** | WinBox &gt; New Terminal

```
/user group add name=ha-readonly policy=read,api
```
> Penjelasan: Membuat grup hak akses read-only yang boleh memakai API.
```
/user add name=hass group=ha-readonly password=GANTI_KUAT address=192.168.88.21
```
> Penjelasan: Membuat user yang hanya boleh login dari 192.168.88.21.
```
/ip service set api address=192.168.88.21/32 disabled=no
```
> Penjelasan: Mengaktifkan API hanya untuk alamat HA.
CATATAN
Jika perintah grup ditolak karena versi RouterOS, buat grup lewat WinBox: System &gt; Users &gt; Groups, centang
hanya read dan api.

## 18.5 Backup

• Home Assistant: Settings &gt; System &gt; Backups &gt; Create backup; unduh berkasnya.
• Proxmox: backup VM 202 (Bab 23).
KASUS NYATA - HAOS tidak boot atau tidak muncul alamat IP
Gejala: Layar tertahan di UEFI atau tidak menemukan disk.
Penyebab: Disk belum menjadi boot device, atau efidisk memuat kunci Secure Boot.
Solusi: Periksa qm config 202: boot: order=scsi0 dan bios: ovmf. Buat ulang efidisk dengan
pre-enrolled-keys=0.


<!-- SOURCE: docs/bab/edisi2/19-dashboard-dan-domain-lokal.md -->

# Bab 19. Dashboard Pintasan dan Nama Domain Lokal

Dua hal membuat pengalaman memakai server jauh lebih nyaman: dashboard (satu halaman berisi
tombol ke semua layanan, termasuk MikroTik dan TP-Link) dan nama domain lokal (mikrotik.lan,
proxmox.lan) sehingga tidak perlu menghafal IP dan port.
Home Server Lab 17 Okt 2026 | CPU 12% RAM 41%
Jaringan
MikroTik
klik untuk membuka
TP-Link AP
klik untuk membuka
TP-Link penerima
klik untuk membuka
AdGuard
klik untuk membuka
Server
Proxmox
klik untuk membuka
Portainer
klik untuk membuka
Forgejo
klik untuk membuka
Nextcloud
klik untuk membuka
Rumah
Home Assistant
klik untuk membuka
Dashboard
klik untuk membuka
k3s
klik untuk membuka
Tailscale
klik untuk membuka
Gambar 19.1 - Contoh tampilan dashboard Homepage (ilustrasi). Setiap kartu adalah pintasan yang membuka halaman
layanan.

## 19.1 Memasang dashboard Homepage

Homepage (gethomepage.dev) ringan, memakai berkas YAML, dan menampilkan status layanan.
Dijalankan di Docker pada VM Debian 13 dan dibuka di http://home.lan.

**TERMINAL (login sebagai root)** | VM Debian 13 (root)

```
mkdir -p /opt/stacks/homepage/config && cd /opt/stacks/homepage
```
> Penjelasan: Membuat folder aplikasi dan folder konfigurasi.
```
nano compose.yaml
```
> Penjelasan: Berkas compose (isi di bawah).

**BERKAS: /opt/stacks/homepage/compose.yaml** | Pin versi image pada pemakaian jangka panjang

```
services:
  homepage:
    image: ghcr.io/gethomepage/homepage:latest
    container_name: homepage
    restart: unless-stopped
    ports:
      - "80:3000"
    environment:
      - HOMEPAGE_ALLOWED_HOSTS=192.168.88.20,home.lan
volumes:
  - ./config:/app/config
```

Baris Arti
80:3000 Dashboard dibuka di port 80 (http://home.lan tanpa mengetik port).
HOMEPAGE_ALLOWED_HOSTS Nama/alamat yang boleh dipakai membuka dashboard. Wajib agar tidak ditolak.
./config:/app/config Folder berkas konfigurasi YAML di host.

## 19.2 Berkas konfigurasi

Buat empat berkas di /opt/stacks/homepage/config. Berkas services.yaml berisi semua pintasan:
jaringan (MikroTik, TP-Link), server, dan aplikasi.
BERKAS: /opt/stacks/homepage/config/settings.yaml
 1 title: Home Server Lab
 2 theme: dark
 3 color: slate
 4 headerStyle: boxed
 5 layout:
 6 Jaringan:
 7 style: row
 8 columns: 4
 9 Server:
10 style: row
11 columns: 4
12 Aplikasi:
13 style: row
14 columns: 4

**BERKAS: /opt/stacks/homepage/config/widgets.yaml** | Widget di bagian atas: penggunaan sumber daya VM dan jam

```
- resources:
cpu: true
memory: true
disk: /
- datetime:
text_size: xl
format:
timeStyle: short
dateStyle: medium
```

**BERKAS: /opt/stacks/homepage/config/services.yaml** | Bagian 1 dari services.yaml (grup Jaringan)

```
- Jaringan:
- MikroTik:
href: http://192.168.88.1
description: Router utama (WebFig)
ping: 192.168.88.1
- TP-Link penerima:
href: http://192.168.0.1
description: TL-WR840N mode WISP
- TP-Link AP:
href: http://192.168.88.2
description: TL-WR820N Access Point
ping: 192.168.88.2
- AdGuard utama:
href: http://192.168.88.253
description: DNS pemblokir iklan (STB)
ping: 192.168.88.253
widget:
type: adguard
url: http://192.168.88.253
username: admin
password: GANTI
```

**BERKAS: /opt/stacks/homepage/config/services.yaml (lanjutan)** | Bagian 2: lanjutkan di berkas yang sama (grup Server dan Aplikasi)

```
- Server:
- Proxmox:
href: https://192.168.88.10:8006
description: Hypervisor
ping: 192.168.88.10
- Portainer:
href: https://192.168.88.20:9443
description: Manajemen Docker
- Forgejo:
href: http://192.168.88.20:3000
description: Git pribadi
- AdGuard kedua:
href: http://192.168.88.11
description: DNS cadangan (LXC 101)
ping: 192.168.88.11
- Aplikasi:
- Nextcloud:
href: http://192.168.88.20:8080
description: Cloud pribadi
- Home Assistant:
href: http://192.168.88.21:8123
description: Otomasi rumah
ping: 192.168.88.21
- Folder jaringan:
href: file://192.168.88.12/share
description: Samba (buka dari Explorer)
- Tailscale:
href: https://login.tailscale.com/admin/machines
description: Konsol admin
```

Kunci Arti
href Alamat yang dibuka saat kartu diklik. Ganti dengan nama .lan setelah 19.4.
description Keterangan di bawah nama.
ping Menandai status hidup/mati (titik hijau/merah). Dipakai untuk perangkat yang tidak punya web,
dan untuk situs HTTPS bersertifikat buatan sendiri.
widget Menampilkan statistik langsung dari aplikasi (contoh AdGuard: jumlah kueri dan iklan terblokir).

**TERMINAL (login sebagai root)** | Folder /opt/stacks/homepage (root)

```
nano config/settings.yaml
```
> Penjelasan: Membuat berkas pengaturan. Tempel isinya. Ulangi untuk widgets.yaml dan services.yaml
(gabungkan dua bagiannya).
```
docker compose up -d
```
> Penjelasan: Menjalankan dashboard.
```
docker compose logs -f
```
> Penjelasan: Memeriksa pesan error konfigurasi YAML (spasi harus tepat).
Buka http://192.168.88.20. Konfigurasi dibaca ulang otomatis saat berkas diubah; cukup muat ulang
halaman.
PERINGATAN
YAML sensitif terhadap spasi (indentasi). Gunakan spasi, bukan Tab, dan pertahankan lekukan seperti contoh.
TIPS
Alternatif dashboard: Homarr (antarmuka drag-and-drop), Dashy, atau Heimdall. Pintasan MikroTik/TP-Link
cukup berupa kartu berisi alamat webnya.

## 19.3 MikroTik dan WinBox

WinBox adalah aplikasi desktop, bukan halaman web, jadi tidak bisa dibuka dari dashboard. Untuk web,
MikroTik menyediakan WebFig (http://192.168.88.1) yang dibuat dari layanan www.

**TERMINAL MIKROTIK** | WinBox &gt; New Terminal

```
/ip service print
```
> Penjelasan: Memeriksa layanan www (port 80) aktif dan tidak dimatikan.

## 19.4 Nama domain lokal dengan AdGuard (DNS rewrites)

Fitur DNS rewrites AdGuard menjawab nama lokal dengan alamat IP yang Anda tentukan.
AdGuard Home - Filters &gt; DNS rewrites &gt; Add DNS rewrite
1 Domain mikrotik.lan
2 Enter the IP address or domain name 192.168.88.1
Cancel Save
Gambar 19.2 - Ilustrasi penambahan DNS rewrite. (1) Nama. (2) Alamat IP tujuan.
1. Buka AdGuard &gt; Filters &gt; DNS rewrites &gt; Add DNS rewrite.
2. Isi Domain dan IP address sesuai tabel, lalu Save.
3. Ulangi untuk setiap nama. Di AdGuard kedua, buat rewrites yang sama (atau biarkan
adguardhome-sync menyalinnya).
> Penjelasan: Agar nama tetap bekerja saat salah satu server mati.
4. Tes: nslookup mikrotik.lan 192.168.88.253, lalu buka http://mikrotik.lan.
> Penjelasan: Harus menjawab 192.168.88.1.
Domain IP Fungsi
mikrotik.lan 192.168.88.1 MikroTik (WebFig)
ap.lan 192.168.88.2 TP-Link AP
proxmox.lan 192.168.88.10 Proxmox (buka https://proxmox.lan:8006)
adguard.lan 192.168.88.253 AdGuard utama
adguard2.lan 192.168.88.11 AdGuard kedua
home.lan 192.168.88.20 Dashboard
git.lan 192.168.88.20 Forgejo (http://git.lan:3000)
nextcloud.lan 192.168.88.20 Nextcloud (http://nextcloud.lan:8080)
portainer.lan 192.168.88.20 Portainer (https://portainer.lan:9443)
ha.lan 192.168.88.21 Home Assistant (http://ha.lan:8123)
files.lan 192.168.88.12 Samba
TIPS
Gunakan akhiran .lan atau .home.arpa. Hindari .local karena bentrok dengan mDNS di sebagian
perangkat. Setelah nama dibuat, ganti href di services.yaml dengan nama .lan.
CATATAN
Router MikroTik juga bisa menjawab nama statis (/ip dns static add name=mikrotik.lan
address=192.168.88.1) untuk keperluan router sendiri, tetapi klien memakai AdGuard sehingga rewrites
AdGuard yang menentukan.
KASUS NYATA - Dashboard menolak dibuka: Host validation failed
Gejala: Halaman Homepage menampilkan error tentang host.
Penyebab: Nama/alamat yang dipakai tidak ada di HOMEPAGE_ALLOWED_HOSTS.
Solusi: Tambahkan alamat dan namanya (misalnya 192.168.88.20,home.lan) pada compose.yaml, lalu
docker compose up -d.


<!-- SOURCE: docs/bab/edisi2/20-k3s.md -->

# Bab 20. Kubernetes dengan k3s

## 20.1 Ringkasan

Item Isi
Fungsi k3s adalah Kubernetes ringan (satu berkas program) untuk belajar mengelola aplikasi dalam
cluster.
Tempat VM sendiri: VM 203 k3s, Debian 13, 2 core, 3-4 GB RAM, 20 GB disk, alamat 192.168.88.22
Cara membuat VM Dari ISO (Bab 11.2 sampai 11.6) atau dari template cloud-init (Bab 11.7)
Port API Kubernetes 6443

## 20.2 Instalasi

**TERMINAL (login sebagai root)** | VM 203 (root)

```
curl -sfL https://get.k3s.io | sh -
```
> Penjelasan: Mengunduh dan memasang k3s sebagai layanan. Selesai dalam beberapa menit.
```
k3s kubectl get nodes
```
> Penjelasan: Memeriksa node: harus berstatus Ready dalam 1-2 menit.
```
systemctl status k3s
```
> Penjelasan: Memastikan layanan k3s aktif (running).
Contoh hasil yang benar
NAME STATUS ROLES AGE VERSION
k3s Ready control-plane,master 2m v1.3x.x+k3s1
k3s membawa Traefik (ingress controller) dan penyimpanan lokal bawaan.

## 20.3 Mengakses dari laptop

1. Di VM salin isi /etc/rancher/k3s/k3s.yaml.
> Penjelasan: Berisi alamat dan kunci akses cluster.
2. Di laptop simpan sebagai %USERPROFILE%\.kube\config, lalu ubah server:
https://127.0.0.1:6443 menjadi https://192.168.88.22:6443.
> Penjelasan: Agar kubectl di laptop menunjuk ke VM.
3. Pasang kubectl di Windows, lalu jalankan kubectl get nodes.

**POWERSHELL WINDOWS** | PowerShell (laptop)

```
winget install Kubernetes.kubectl
```
> Penjelasan: Memasang kubectl.
```
kubectl get nodes
```
> Penjelasan: Memastikan laptop bisa berbicara dengan cluster.

## 20.4 Konsep dasar

Istilah Penjelasan singkat
Pod Satuan terkecil, berisi satu atau beberapa container.
Deployment Menjaga jumlah pod tertentu dan mengatur pembaruan.
Service Alamat tetap untuk mengakses sekumpulan pod (ClusterIP, NodePort).
Ingress Aturan masuk HTTP/HTTPS berdasarkan nama host (dilayani Traefik pada k3s).
Namespace Pengelompokan sumber daya.
ConfigMap / Secret Konfigurasi dan data rahasia untuk aplikasi.

## 20.5 Latihan pertama

**TERMINAL (login sebagai root)** | Laptop atau VM 203

```
kubectl create namespace belajar
```
> Penjelasan: Membuat ruang kerja baru.
```
kubectl -n belajar create deployment web --image=nginx:stable --replicas=2
```
> Penjelasan: Menjalankan 2 pod nginx.
```
kubectl -n belajar expose deployment web --port=80 --type=NodePort
```
> Penjelasan: Membuka layanan lewat port tinggi di node.
```
kubectl -n belajar get pods,svc
```
> Penjelasan: Melihat pod dan nomor NodePort (contoh 31234).
```
kubectl -n belajar scale deployment web --replicas=3
```
> Penjelasan: Menambah menjadi 3 pod.
```
kubectl delete namespace belajar
```
> Penjelasan: Membersihkan latihan.
Buka http://192.168.88.22:NODEPORT untuk melihat halaman nginx.

## 20.6 MikroTik, backup, dan masalah umum

• Reservasi 192.168.88.22 (Bab 3.5). Tidak perlu firewall; API 6443 hanya untuk jaringan lokal.
• Backup: backup VM 203 lewat Proxmox (Bab 23). Konfigurasi aplikasi sebaiknya ada di Git (Bab 21).
KASUS NYATA - Node NotReady atau VM terasa berat
Gejala: kubectl get nodes menunjukkan NotReady, atau semua perintah lambat.
Penyebab: RAM VM terlalu kecil atau terlalu banyak VM berjalan di HDD.
Solusi: Beri VM k3s minimal 3 GB RAM, matikan VM lain yang tidak dipakai, periksa journalctl -u k3s -n
50.


<!-- SOURCE: docs/bab/edisi2/21-flux-gitops.md -->

# Bab 21. GitOps dengan Flux

GitOps berarti Git adalah sumber kebenaran: kondisi cluster dideskripsikan dalam berkas YAML di
repository, dan agen di cluster (Flux) menyamakan cluster dengan isi repository. Mengubah aplikasi cukup
dengan commit.
Langkah Pelaku
1. Tulis atau ubah YAML, commit, push ke Forgejo Anda
2. Memantau repository tiap beberapa menit Flux (di k3s)
3. Menerapkan perbedaan ke cluster Flux
4. Mengusulkan versi image baru lewat pull request Renovate (Bab 22)

## 21.1 Struktur repository

Pakai repository homelab di Forgejo (Bab 15.4). Strukturnya:
BERKAS: struktur folder repository homelab
 1 homelab/
 2 clusters/
 3 home/
 4 apps.yaml &lt;- memberi tahu Flux folder apps/ harus diterapkan
 5 flux-system/ &lt;- dibuat otomatis oleh flux bootstrap
 6 apps/
 7 web/
 8 namespace.yaml
 9 deployment.yaml
10 service.yaml
11 kustomization.yaml
12 renovate.json

## 21.2 Memasang Flux (bootstrap)

**TERMINAL (login sebagai root)** | VM 203 (root)

```
curl -s https://fluxcd.io/install.sh | bash
```
> Penjelasan: Memasang perintah flux di VM 203.
```
export KUBECONFIG=/etc/rancher/k3s/k3s.yaml
```
> Penjelasan: Memberi tahu flux dan kubectl letak berkas akses cluster k3s.
```
flux check --pre
```
> Penjelasan: Memeriksa prasyarat cluster. Harus berakhir "prerequisites checks passed".
```
flux bootstrap git --url=ssh://git@192.168.88.20:2222/USERNAME/homelab.git \
  --branch=main --path=clusters/home
```
> Penjelasan: Memasang Flux di cluster dan menyimpan konfigurasinya di repository. Ganti USERNAME.
1. Perintah bootstrap menampilkan kunci publik. Tambahkan di repository: Settings &gt; Deploy
Keys &gt; Add, centang Enable Write Access.
> Penjelasan: Flux perlu menulis ke repository untuk menyimpan konfigurasinya sendiri.
2. Kembali ke terminal, tekan y untuk melanjutkan.
> Penjelasan: Flux memasang komponennya di namespace flux-system.
3. Periksa dengan flux get all dan kubectl -n flux-system get pods.
> Penjelasan: Semua pod harus Running.

## 21.3 Aplikasi pertama (contoh web)

BERKAS: apps/web/namespace.yaml
 1 apiVersion: v1
 2 kind: Namespace
 3 metadata:
 4 name: web
BERKAS: apps/web/deployment.yaml
 1 apiVersion: apps/v1
 2 kind: Deployment
 3 metadata:
 4 name: web
 5 namespace: web
 6 spec:
 7 replicas: 2
 8 selector:
 9 matchLabels:
10 app: web
11 template:
12 metadata:
13 labels:
14 app: web
15 spec:
16 containers:
17 - name: nginx
18 image: nginx:1.27
19 ports:
20 - containerPort: 80
BERKAS: apps/web/service.yaml
 1 apiVersion: v1
 2 kind: Service
 3 metadata:
 4 name: web
 5 namespace: web
 6 spec:
 7 type: NodePort
 8 selector:
 9 app: web
10 ports:
11 - port: 80
12 targetPort: 80
13 nodePort: 30080
BERKAS: apps/web/kustomization.yaml
 1 apiVersion: kustomize.config.k8s.io/v1beta1
 2 kind: Kustomization
 3 resources:
 4 - namespace.yaml
 5 - deployment.yaml
 6 - service.yaml

**BERKAS: clusters/home/apps.yaml** | Memberi tahu Flux untuk menerapkan apps/web setiap 5 menit

```
apiVersion: kustomize.toolkit.fluxcd.io/v1
kind: Kustomization
metadata:
name: apps
namespace: flux-system
spec:
interval: 5m
path: ./apps/web
prune: true
sourceRef:
kind: GitRepository
name: flux-system
```

**TERMINAL (user biasa)** | Laptop / VM 203

```
git add . && git commit -m "tambah aplikasi web" && git push
```
> Penjelasan: Mengirim perubahan ke Forgejo (dari laptop atau VM).
```
flux reconcile source git flux-system
```
> Penjelasan: Memaksa Flux menarik perubahan sekarang (tanpa menunggu 5 menit).
```
flux get kustomizations
```
> Penjelasan: Status penerapan; kolom READY harus True.
```
kubectl -n web get pods
```
> Penjelasan: Memastikan 2 pod nginx berjalan.
Ubah replicas: 2 menjadi 3, commit dan push: jumlah pod menjadi tiga. Jika Anda mengubah lewat
kubectl scale, Flux mengembalikannya sesuai isi Git.

## 21.4 Rahasia di Git dengan SOPS dan age

Jangan menyimpan password atau token apa adanya di repository. Pakai SOPS dengan kunci age agar
berkas rahasia terenkripsi di Git dan hanya didekripsi di dalam cluster.

**TERMINAL (login sebagai root)** | VM 203 (root)

```
age-keygen -o age.agekey
```
> Penjelasan: Membuat kunci age. Salin kunci publik (age1...) dari keluarannya.
```
kubectl create secret generic sops-age --namespace=flux-system \
  --from-file=age.agekey=age.agekey
```
> Penjelasan: Menyimpan kunci privat di cluster. Jangan masukkan age.agekey ke Git.

**BERKAS: .sops.yaml** | Di akar repository

```
creation_rules:
- path_regex: .*\.secret\.yaml$
encrypted_regex: ^(data|stringData)$
age: <KUNCI-PUBLIK-AGE>
```

**BERKAS: tambahan pada Kustomization Flux** | Untuk Kustomization yang berisi rahasia

```
spec:
decryption:
provider: sops
secretRef:
name: sops-age
```

Enkripsi berkas dengan sops --encrypt --in-place nama.secret.yaml sebelum commit. Cadangkan
age.agekey di password manager; bila hilang, rahasia tidak bisa dibuka.
KASUS NYATA - Flux bootstrap gagal: permission denied (publickey)
Gejala: Bootstrap berhenti dengan error SSH.
Penyebab: Deploy key belum ditambahkan atau tidak punya izin tulis.
Solusi: Tambahkan kunci publik di Settings &gt; Deploy Keys repo homelab dengan Write Access, lalu ulangi
bootstrap.
KASUS NYATA - Perubahan di Git tidak muncul di cluster
Gejala: Setelah push, pod tidak berubah.
Penyebab: Flux belum menarik, path salah, atau YAML tidak valid.
Solusi: Jalankan flux reconcile source git flux-system dan flux get kustomizations; baca
kolom Message; kubectl -n flux-system logs deploy/kustomize-controller.


<!-- SOURCE: docs/bab/edisi2/22-renovate.md -->

# Bab 22. Renovate: Pembaruan Otomatis

Renovate memindai repository, menemukan versi lama (image Docker, chart, dependensi), lalu membuat
pull request pembaruan otomatis. Dengan GitOps, menerima PR (merge) cukup untuk memperbarui
aplikasi.

## 22.1 Menyiapkan akun bot

1. Di Forgejo buat user renovate-bot (Site Administration &gt; User Accounts &gt; Create).
> Penjelasan: Akun terpisah agar PR dari bot mudah dikenali.
2. Tambahkan bot sebagai Collaborator dengan izin Write pada repo homelab.
> Penjelasan: Agar bot boleh membuat cabang dan PR.
3. Login sebagai bot &gt; Settings &gt; Applications: buat access token dengan izin repository (read dan
write), user (read), dan issue (read dan write). Simpan tokennya.
4. Buat token GitHub read-only tanpa izin (untuk membaca catatan rilis tanpa batas laju).
> Penjelasan: Opsional tetapi disarankan.

## 22.2 Menjalankan Renovate

**BERKAS: /opt/renovate/env** | VM Debian 13; pada Renovate lama gunakan RENOVATE_PLATFORM=gitea

```
RENOVATE_PLATFORM=forgejo
RENOVATE_ENDPOINT=http://192.168.88.20:3000/api/v1/
RENOVATE_TOKEN=TOKEN_BOT_FORGEJO
RENOVATE_GIT_AUTHOR=Renovate Bot <renovate@lab.local>
RENOVATE_AUTODISCOVER=true
RENOVATE_GITHUB_COM_TOKEN=TOKEN_GITHUB_READONLY
LOG_LEVEL=info
```

**TERMINAL (login sebagai root)** | VM Debian 13 (root)

```
mkdir -p /opt/renovate && chmod 700 /opt/renovate
```
> Penjelasan: Membuat folder dan membatasi aksesnya.
```
nano /opt/renovate/env
```
> Penjelasan: Isi berkas variabel (di atas) lalu simpan.
```
chmod 600 /opt/renovate/env
```
> Penjelasan: Hanya root yang boleh membaca token.
```
docker run --rm --env-file /opt/renovate/env renovate/renovate:<VERSI>
```
> Penjelasan: Menjalankan Renovate satu kali (ganti &lt;VERSI&gt; dengan versi terbaru). Baca log di layar.

**TERMINAL (login sebagai root)** | VM Debian 13 (root)

```
crontab -e
```
> Penjelasan: Menjadwalkan agar berjalan berkala. Tambahkan baris di bawah.

**BERKAS: crontab** | Setiap 6 jam

```
0 */6 * * * docker run --rm --env-file /opt/renovate/env renovate/renovate:<VERSI>
```

## 22.3 Berkas renovate.json di repository

**BERKAS: renovate.json** | Di akar repository

```
{
"$schema": "https://docs.renovatebot.com/renovate-schema.json",
"extends": ["config:recommended"],
"schedule": ["before 6am on saturday"],
"prConcurrentLimit": 5
}
```

Setelah Renovate berjalan, repository akan mendapat PR Configure Renovate (jika perlu), lalu PR
pembaruan seperti Update nginx to v1.28. Tinjau, merge, dan Flux menerapkannya ke cluster.
TIPS
Pin versi image (jangan latest) pada compose dan manifest. Renovate hanya bisa mengusulkan pembaruan
bila versi tertulis eksplisit. Berkas compose.yaml Docker juga dipindai otomatis.
KASUS NYATA - Renovate tidak membuat PR sama sekali
Gejala: Log berakhir tanpa PR, atau tidak ada repository ditemukan.
Penyebab: Bot belum jadi collaborator, token kurang izin, atau tidak ada dependensi dikenali.
Solusi: Periksa log: cari repositories dan No repositories found; tambahkan bot ke repo, periksa izin
token, dan pastikan versi image tertulis.


<!-- SOURCE: docs/bab/edisi2/23-backup-restore-instal-ulang.md -->

# Bab 23. Backup, Restore, dan Instal Ulang

Tujuan: bila Proxmox perlu diinstal ulang (disk rusak, upgrade besar, atau mesin diganti), semua VM dan container dapat dipulihkan dari backup.

## 23.1 Backup VM dan container

1. Pilih VM atau CT di panel kiri &gt; tab Backup &gt; Backup now.
2. Storage: local (hasil di /var/lib/vz/dump). Mode: Stop untuk yang boleh dimatikan sesaat,
Snapshot untuk yang harus tetap hidup. Compression: ZSTD.
> Penjelasan: Mode Stop paling konsisten; Snapshot tidak mematikan layanan.
3. Klik Backup dan tunggu TASK OK.
4. Jadwal otomatis: Datacenter &gt; Backup &gt; Add, pilih hari, jam, VM/CT, dan jumlah salinan
(Retention).
> Penjelasan: Backup yang dijadwalkan lebih andal daripada yang diingat.

**TERMINAL (login sebagai root)** | Shell Proxmox

```
vzdump 101 102 201 --storage local --mode snapshot --compress zstd
```
> Penjelasan: Backup beberapa VM/CT sekaligus dari terminal.
```
ls -lh /var/lib/vz/dump/
```
> Penjelasan: Melihat berkas backup yang dihasilkan.

## 23.2 Menyalin backup keluar dari server

Backup yang hanya ada di disk server ikut hilang saat Proxmox diinstal ulang. Salin keluar.
1. Pasang WinSCP di laptop (Bab 2.2).
2. Koneksi baru: File protocol SFTP, Host name 192.168.88.10, Port 22, user root, password root
Proxmox. Klik Login.
> Penjelasan: WinSCP menampilkan berkas laptop di kiri dan Proxmox di kanan.
3. Buka /var/lib/vz/dump di kanan, seret berkas vzdump-\* ke folder di HDD laptop (misalnya
G:\Backup-Proxmox).
> Penjelasan: Salinan di HDD aman dari kerusakan VM.
4. Simpan satu salinan lagi di tempat lain (flashdisk atau cloud) untuk data penting.

## 23.3 Menyimpan konfigurasi host Proxmox

Backup VM tidak menyimpan pengaturan tingkat host. Simpan berkas berikut:

**TERMINAL (login sebagai root)** | Shell Proxmox

```
tar czf /root/pve-host-config.tgz /etc/network/interfaces /etc/hosts \
  /etc/resolv.conf /etc/pve/storage.cfg /etc/pve/user.cfg \
  /etc/pve/jobs.cfg /etc/pve/firewall /etc/apt/sources.list.d
```
> Penjelasan: Mengarsipkan konfigurasi jaringan, storage, user, jadwal backup, firewall, dan repository.
```
ls -lh /root/pve-host-config.tgz
```
> Penjelasan: Memastikan arsip terbentuk.
Salin berkas .tgz ini keluar dengan WinSCP seperti 23.2.

## 23.4 Restore

**TERMINAL (login sebagai root)** | Shell Proxmox

```
qmrestore /var/lib/vz/dump/vzdump-qemu-201-TANGGAL.vma.zst 201 --storage local-lvm
```
> Penjelasan: Memulihkan VM 201 dari backup ke storage local-lvm.
```
pct restore 101 /var/lib/vz/dump/vzdump-lxc-101-TANGGAL.tar.zst \
  --storage local-lvm
```
> Penjelasan: Memulihkan container 101.
Lewat web: pilih storage tempat berkas, buka Backups, pilih berkas, klik Restore, tentukan ID dan
storage.

## 23.5 Prosedur instal ulang dan restore

Langkah Rincian
1. Backup lengkap Semua VM/CT di-backup dan disalin keluar; simpan pve-host-config.tgz dan Lampiran B.
2. Instal bersih Instal Proxmox di mesin dengan IP 192.168.88.10 (Bab 6 dan 8).
3. Jaringan Cek nama kartu (ip -br link) dan sesuaikan bridge-ports bila berubah.
4. Repository dan update Bab 9.5 dan 9.6.
5. Storage Buat storage dengan nama yang sama (lihat storage.cfg lama) agar restore menemukan targetnya.
6. Restore Unggah berkas backup ke /var/lib/vz/dump (WinSCP), restore tiap VM/CT dengan ID yang sama.
7. Periksa hardware Re-add perangkat USB (dongle Zigbee) pada HAOS; sesuaikan RAM/CPU; aktifkan Start at boot.
8. MikroTik dan DNS MAC address VM/LXC hasil restore sama, jadi static lease tetap berlaku.
Mengaktifkan Start at boot
Pilih VM/CT &gt; Options &gt; Start at boot &gt; Yes. Atur urutan di Start/Shutdown order: container AdGuard
order=1, VM lain setelahnya.
CATATAN
Untuk lingkungan lebih serius, pertimbangkan Proxmox Backup Server (PBS): backup incremental,
deduplikasi, dan verifikasi, dijalankan di mesin/disk terpisah.
KASUS NYATA - Restore berhasil tetapi tidak ada jaringan
Gejala: VM/CT hasil restore tidak mendapat IP di mesin baru.
Penyebab: Nama kartu fisik berbeda sehingga vmbr0 tidak terhubung ke LAN.
Solusi: Periksa /etc/network/interfaces, ubah bridge-ports ke kartu yang benar, lalu ifreload -a.


<!-- SOURCE: docs/bab/edisi2/24-katalog-masalah.md -->

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

| Gejala | Penyebab | Solusi | Rujukan |
|---|---|---|---|
| [Nyata] Tidak bisa membuka `https://192.168.100.2:8006` | IP Proxmox beda jaringan dengan laptop | Sesuaikan alamat/gateway di `interfaces` dan `hosts`; verifikasi dari konsol sebelum reboot | Bab 9.3 |
| [Nyata] Layar nano kosong saat mengedit jaringan | Nama berkas salah | Keluar tanpa menyimpan, lalu buka `/etc/network/interfaces` | Bab 9.3 |
| [Nyata] Setelah pindah jaringan, Proxmox tidak bisa dijangkau / DNS APT gagal | Interface bridge, alamat, gateway, atau DNS tidak sesuai jaringan aktif | Kumpulkan `ip -br link`, `ip -br address`, `ip route`, dan `/etc/resolv.conf`; cocokkan `bridge-ports` dengan interface Ethernet yang benar dan gunakan gateway/DNS dari subnet aktif. Jangan menyalin `bridge-ports all` atau alamat jaringan lama tanpa verifikasi | Bab 9.1, 9.3-9.4 |
| [Nyata] `apt update`: Temporary failure resolving | DNS kosong atau salah | Periksa System > DNS dan uji resolusi nama | Bab 9.4 |
| [Nyata] Tidak menemukan menu Repositories | Menu berada di bawah Updates | Buka Node > Updates > Repositories | Bab 9.5 |
| [Nyata] Refresh sangat lambat (9 KB/s) | Internet lambat atau uplink WiFi | Gunakan kabel LAN, mirror terdekat, atau waktu sepi | Bab 9.6 |
| [Nyata] Perintah `sudo` tidak terbaca | Sudah root; sudo tidak dipasang | Jangan gunakan sudo; di Debian masuk root dengan `su -` | Bab 1.7 |
| [Nyata] `ipconfig /release` memutus WiFi | IP dilepas tanpa diminta kembali | Jalankan `ipconfig /renew` | Bab 3.9 |
| [Nyata] STB punya dua instalasi Armbian | Instalasi lama di eMMC dan baru di SD | Periksa `lsblk` dan `findmnt /`; tentukan satu media | Bab 12.2 |
| [Nyata] Double NAT / router di belakang router lain | Urutan perangkat salah | Ikuti topologi jaringan terbaru | Bab 3.9 dan docs/02 |
| USB tidak muncul di boot menu | Mode boot, Secure Boot, atau penulisan USB | Periksa mode penulisan USB dan pengaturan boot sesuai panduan M710q | Bab 6.4, 27.5 |
| Layanan web Proxmox mati setelah ganti IP | `/etc/hosts` masih memuat IP lama | Perbarui `hosts`, lalu periksa hostname dan `pveproxy` | Bab 9.3 |
| Error 401 pada repository | Repository enterprise aktif | Nonaktifkan enterprise dan aktifkan no-subscription sesuai panduan | Bab 9.5 |
| Container tidak mendapat IP | Reservasi, bridge, atau DHCP bermasalah | Periksa lease MikroTik, bridge, dan alamat yang ditetapkan | Bab 10.5 |
| VM gagal start: KVM tidak tersedia | VT-x belum aktif | Aktifkan VT-x di BIOS; tanpa monitor, lihat thinklmi jika tersedia. Verifikasi `lscpu` dan `/dev/kvm` | Bab 11, 27.5 |
| Peringatan cdrom saat `apt update` | Sumber instalasi masih tersisa | Nonaktifkan baris cdrom di sumber APT | Bab 11.5 |
| Port 53 dipakai systemd-resolved | DNS stub memakai port yang dibutuhkan AdGuard | Atur `DNSStubListener=no`, lalu mulai ulang layanan terkait | Bab 12.3 |
| Subnet Tailscale tidak terjangkau | Rute belum disetujui atau IP forwarding mati | Setujui rute dan periksa `ip_forward=1` | Bab 26 |
| Satu perangkat masih menampilkan iklan | DNS sendiri atau lease lama | Periksa Secure DNS, perbarui lease, lalu evaluasi aturan firewall | Bab 13.10 |
| Portainer timeout saat setup | Admin awal terlambat dibuat | Mulai ulang Portainer dan segera selesaikan setup | Bab 14.4 |
| Docker permission denied | Pengguna bukan root atau tidak punya izin socket | Jalankan sebagai root; jika memakai grup docker, pahami dampak hak aksesnya | Bab 14.4 |
| Forgejo: clone SSH gagal | Port SSH Git salah | Pastikan `SSH_PORT = 2222` di konfigurasi Forgejo | Bab 15 |
| Nextcloud: untrusted domain | Domain belum terdaftar | Tambahkan domain tepercaya melalui `occ` | Bab 16.3 |
| Home Assistant OS tidak boot | Secure Boot atau urutan boot salah | Periksa konfigurasi EFI dan urutan disk VM | Bab 18 |
| Dashboard: Host validation failed | Host belum diizinkan | Tambahkan nama host pada `ALLOWED_HOSTS` | Bab 19 |
| k3s NotReady | RAM kurang atau sumber daya terbatas | Periksa RAM dan matikan VM yang tidak dipakai | Bab 20 |
| Flux: permission denied (publickey) | Deploy key tidak punya izin tulis | Tambahkan deploy key dengan izin yang diperlukan | Bab 21 |
| Renovate tidak membuat PR | Izin bot atau image tidak dipatok | Periksa izin akun bot dan tag versi image | Bab 22 |
| Restore sukses tetapi jaringan gagal | Nama kartu jaringan fisik berubah | Cocokkan `bridge-ports` dengan nama kartu aktual sebelum menerapkan konfigurasi | Bab 23 |

## 24.3 Cara meminta bantuan dengan efektif

• Apa yang dilakukan dan pesan error persis (salin teks).
• Keluaran ip a, ip route, dan cat /etc/resolv.conf dari server bermasalah.
• ipconfig dari laptop untuk masalah jaringan.
• Log: klik dua kali tugas di panel Tasks Proxmox, atau journalctl -u NAMA -n 50.
• Foto layar konsol server atau tangkapan layar Proxmox (Hardware dan Network).


<!-- SOURCE: docs/bab/edisi2/lampiran-a-ringkasan-perintah.md -->

# Lampiran A. Ringkasan Perintah

A.1 Proxmox (Shell, root)
Tujuan Perintah
Versi Proxmox pveversion
Daftar VM / CT qm list / pct list
Start / stop VM qm start 201 / qm shutdown 201
Start / stop CT pct start 101 / pct shutdown 101
Konfigurasi VM qm config 201
Terapkan jaringan ifreload -a
Backup vzdump 201 --storage local --mode snapshot
Restore VM / CT qmrestore berkas 201 / pct restore 101 berkas
Update apt update && apt full-upgrade
Status web systemctl status pveproxy
A.2 MikroTik (terminal)
Tujuan Perintah
Backup konfigurasi /system backup save name=NAMA dan /export file=NAMA
Daftar lease DHCP /ip dhcp-server lease print
Reservasi IP /ip dhcp-server lease add address=IP mac-address=MAC
comment=NAMA
DNS untuk klien /ip dhcp-server network set 0 dns-server=A,B
DNS router /ip dns set servers=A,B allow-remote-requests=no
Ping dari router /ping 192.168.88.10 count=3
Lihat layanan /ip service print
Tabel ARP /ip arp print
A.3 Docker, Kubernetes, Flux
Tujuan Perintah
Container berjalan / log docker ps / docker logs -f NAMA
Naik / turun stack docker compose up -d / docker compose down
Perbarui image docker compose pull && docker compose up -d
Node / pod / service kubectl get nodes / kubectl get pods -A / kubectl get svc
-A
Tujuan Perintah
Status Flux flux get all
Paksa sinkron Flux flux reconcile source git flux-system
A.4 Windows dan jaringan
Tujuan Perintah
Lihat IP ipconfig /all
Perbarui lease DHCP ipconfig /renew
Tes DNS nslookup domain alamat-dns
Cek hash ISO certutil -hashfile berkas.iso SHA256
SSH ssh root@192.168.88.10


<!-- SOURCE: docs/bab/edisi2/lampiran-b-rencana-ip-dan-id.md -->

# Lampiran B. Rencana IP dan ID

Perangkat / layanan ID IP Port / akses Catatan
MikroTik RB750GL - 192.168.88.1 80 (WebFig), WinBox
TL-WR820N (AP) - 192.168.88.2 80
TL-WR840N (penerima) - 192.168.0.1 80 Jaringan di atas MikroTik
Proxmox - 192.168.88.10 8006 IP statis
AdGuard #2 (LXC) 101 192.168.88.11 80, 53 Static lease
Samba (LXC) 102 192.168.88.12 445 Static lease
Tailscale cadangan (LXC) 103 - Opsional
dnsdist (LXC) 104 192.168.88.13 53 Opsional (latihan)
Pi-hole (LXC) 105 192.168.88.14 80, 53 Opsional
VM Debian 13 201 192.168.88.20 80, 3000, 2222, 8080,
9443
Dashboard, Forgejo,
Nextcloud, Portainer
VM Home Assistant 202 192.168.88.21 8123 Static lease
VM k3s 203 192.168.88.22 6443 Static lease
Template Debian 9000 - -
STB (AdGuard + Tailscale) - 192.168.88.253 80, 53 Static lease


<!-- SOURCE: docs/bab/edisi2/lampiran-c-daftar-periksa.md -->

# Lampiran C. Daftar Periksa

• RAM terpasang sesuai rencana dan lulus MemTest86 (Bab 27.1).
• BIOS diatur: VT-x, VT-d, UEFI, Secure Boot mati, AHCI, WoL, After Power Loss (Bab 27.5).
• ISO diverifikasi dan USB bootable dibuat (Bab 6.3).
• Kabel LAN dari mesin ke MikroTik, monitor dan keyboard terpasang.
• HDD 2 TB dilepas selama instalasi (hindari salah pilih disk).
C.2 Setelah Proxmox hidup
• Web terbuka di https://192.168.88.10:8006, login berhasil.
• pveversion, /dev/kvm, dan jumlah vmx lebih dari 0.
• Ping gateway, 8.8.8.8, dan deb.debian.org berhasil.
• Repository enterprise mati, no-subscription aktif, upgrade selesai.
• sensors dan smartctl -H /dev/nvme0 menampilkan data.
C.3 Sebelum instal ulang atau perubahan besar
• Semua VM/CT di-backup dan salinannya ada di luar Proxmox.
• pve-host-config.tgz tersimpan.
• Lampiran B terisi lengkap.
• Password dan kunci (age.agekey, token, password) tersimpan di password manager.
• Static lease MikroTik dan DNS rewrites AdGuard dicatat atau diekspor.


<!-- SOURCE: docs/bab/edisi2/lampiran-d-glosarium.md -->

# Lampiran D. Glosarium

Istilah Arti
Proxmox VE Sistem operasi server untuk menjalankan banyak VM dan container dengan antarmuka
web.
VM / LXC Komputer virtual penuh / container Linux ringan berbagi kernel.
Bridge (vmbr0) Saklar virtual Proxmox yang menghubungkan VM dan container ke jaringan LAN.
DHCP / Static lease Pembagian IP otomatis / IP tetap berdasarkan MAC.
DNS / DNS sinkhole Penerjemah nama situs / DNS yang menjawab 0.0.0.0 untuk domain iklan.
WISP Router menerima internet lewat WiFi lalu membagikannya lewat kabel.
NAT / Masquerade Berbagi satu alamat IP publik untuk banyak perangkat.
Docker / Compose Wadah aplikasi / berkas yang mendefinisikan beberapa container sekaligus.
Portainer Antarmuka web untuk mengelola Docker.
Failover / Load balancing Berpindah ke cadangan saat mati / membagi beban ke beberapa server.
keepalived / VIP Penyedia IP virtual yang berpindah antar server (VRRP).
Kubernetes / k3s Orkestrasi container / versi ringannya.
GitOps / Flux Mengelola infrastruktur dengan Git sebagai sumber kebenaran / agen yang
menyinkronkannya.
Renovate Bot yang membuat pull request pembaruan versi otomatis.
Subnet router Perangkat Tailscale yang membuat seluruh jaringan rumah dapat dijangkau dari luar.
SOPS / age Alat enkripsi berkas rahasia agar aman disimpan di Git.
vzdump Alat backup VM dan container bawaan Proxmox.
Snapshot Titik simpan kondisi VM yang bisa dikembalikan.
Buku Panduan Home Server Lab


<!-- SOURCE: docs/bab/suplemen/bagian-1-00-pengantar.md -->

# Bagian 1. Keamanan dan Akses Jarak Jauh (pengantar)

Bagian 1. Keamanan dan Akses Jarak Jauh
Asal: Suplemen 1. Bab 25-26.
Suplemen ini adalah tambahan untuk Buku Panduan Home Server Lab Edisi 2. Isi Edisi 2 tidak ditulis ulang.
Setiap suplemen berisi bab baru bernomor lanjutan (mulai Bab 25) dan satu lembar pembaruan di bagian akhir
yang menunjukkan bab lama mana yang berubah.
Isi Suplemen 1
Bab Isi Hasil akhir
25. Keamanan dasar
server
Backup sebelum mengubah, akun admin Proxmox
terpisah + 2FA, SSH hanya kunci, firewall Proxmox,
pengerasan VM Debian (UFW, update otomatis),
pengerasan MikroTik, checklist uji.
Server tidak bisa dimasuki dengan
password saja, hanya LAN yang boleh
mengakses panel admin, dan ada jalan
keluar bila terkunci.
26. Tailscale Cara kerja, memilih perangkat subnet router,
pemasangan di sisi server, sisi laptop Windows, sisi HP
(Android dan iPhone), kebijakan akses, DNS, uji dari
luar jaringan.
Panel Proxmox, SSH, dan layanan lain
dapat dibuka dari mana saja lewat
Tailscale, tanpa membuka satu port pun ke
internet.
Prasyarat
• Proxmox VE sudah terpasang dan web UI terbuka di https://192.168.88.10:8006 (Edisi 2 Bab 8 dan 9).
• VM Debian 13 sudah berjalan di 192.168.88.20 dengan pengguna biasa dan password root (Bab 11).
• MikroTik RB750GL sudah dikonfigurasi dasar dan dapat dibuka lewat WinBox (Bab 3).
• Laptop Windows berada di jaringan MikroTik (192.168.88.0/24) saat mengerjakan bab ini.
• Satu akun email (Google, Microsoft, Apple, atau GitHub) yang sudah memakai verifikasi dua langkah, untuk
Tailscale di Bab 26.
Alamat jaringan yang dipakai (sama dengan Edisi 2 Bab 3.2)
Alamat Perangkat Catatan
192.168.88.1 MikroTik RB750GL Gateway, firewall
192.168.88.2 TL-WR820N (Access Point)
192.168.88.10 Proxmox VE Mesin asli (ThinkCentre M710q)
192.168.88.11 / .12 LXC AdGuard kedua / LXC Samba Edisi 2 Bab 13 dan 17
192.168.88.20 VM Debian 13 Docker, Portainer, Git, Nextcloud
192.168.88.253 STB HG680 (AdGuard) DNS utama
192.168.88.250 (usulan) STB 2 (subnet router Tailscale) Belum tiba; buat reservasi di MikroTik saat
tiba
CATATAN
Seperti Edisi 2 Bab 1.7, perintah di buku ini tidak memakai sudo. Untuk VM Debian, masuk SSH sebagai pengguna
biasa lalu jalankan su - sehingga prompt menjadi # dan perintah berikutnya tanpa sudo. Teks seperti &lt;USER&gt;
adalah placeholder yang harus diganti dengan nilai Anda.
PERINGATAN - Risiko terkunci
Bab 25 mengubah cara login ke server. Selalu ikuti urutan langkah, biarkan satu sesi SSH lama tetap terbuka saat
menguji sesi baru, dan siapkan jalur darurat (Bab 25.2) sebelum mulai.


<!-- SOURCE: docs/bab/suplemen/25-keamanan-dasar.md -->

# Bab 25. Keamanan Dasar Server

PENEMPATAN - SEMUA GUEST
Tempat: Dikerjakan di setiap VM/LXC dan di host Proxmox, sesuai bagian bab. VM baru mewarisinya dari templat
VM 200 (Suplemen 7 Bab 49).
Perhatian: UFW di dalam VM tidak mengatur port yang dipublikasikan oleh Docker. Pemisah antar-VM yang bisa
diandalkan adalah firewall Proxmox (Suplemen 7 Bab 51).
Bab ini membuat server rumah lebih sulit dimasuki dan lebih mudah dipulihkan. Tujuannya bukan keamanan
sempurna, melainkan beberapa lapisan sederhana yang saling menutup kelemahan. Semua langkah ditulis untuk
pemula, dengan penjelasan setiap perintah dan cara kembali bila terjadi kesalahan.

## 25.1 Prinsip dan peta keamanan

Ada lima prinsip yang dipakai di seluruh buku: (1) kecilkan pintu masuk, hanya buka yang perlu; (2) akses dari
luar hanya lewat Tailscale; (3) login memakai kunci dan 2FA, bukan password saja; (4) perbarui rutin; (5)
cadangkan dan uji pemulihan.
1 Internet
tidak dipercaya; tidak ada port yang dibuka dari rumah
2 WISP TL-WR840N + IndiHome
NAT berlapis, tanpa port forwarding
3 MikroTik RB750GL
firewall input dan forward, layanan admin dibatasi ke LAN
4 Tailscale
satu-satunya jalan masuk dari luar, dengan kebijakan akses
5 Proxmox dan VM
firewall, akun admin terpisah, 2FA, SSH hanya kunci
6 Aplikasi dan data
update otomatis, backup 3-2-1, uji pemulihan
Gambar 25.1 - Enam lapisan keamanan. Penyerang harus menembus lapisan dari luar ke dalam.
Ancaman yang realistis di rumah
Ancaman Contoh Pertahanan di buku ini
Orang di internet mencoba
masuk
Memindai port di alamat IP publik Tidak ada port yang dibuka. Akses luar hanya lewat
Tailscale.
Perangkat di LAN yang tidak
tepercaya
HP tamu, perangkat IoT, laptop
terinfeksi
Firewall Proxmox, UFW di VM, akun admin dengan
2FA. Pemisahan jaringan (VLAN) dibahas sebagai opsi
nanti.
Password ditebak atau bocor Login root SSH dengan password Kunci SSH, 2FA, password manager (Suplemen 4).
Celah pada perangkat lunak
lama
Paket Debian atau Proxmox belum
diperbarui
Update rutin dan update keamanan otomatis.
Kesalahan sendiri Salah ubah konfigurasi, salah
hapus
Backup, snapshot, Safe Mode MikroTik, jalur darurat.
Perangkat hilang atau dicuri HP atau laptop berisi akses
Tailscale
Hapus perangkat dari konsol Tailscale, 2FA di akun
email.
Yang sudah ada di Edisi 2 dan yang ditambahkan
Area Sudah ada (Edisi 2) Ditambahkan di Suplemen 1
MikroTik Layanan tak terpakai dimatikan, WinBox dan SSH
dibatasi LAN, MAC server dimatikan (Bab 3.8)
Aturan firewall input dan forward, WebFig dibatasi
LAN, mematikan layanan tambahan, Safe Mode,
backup
Proxmox Repository no-subscription, update (Bab 9) Akun admin terpisah, 2FA TOTP, SSH hanya kunci,
firewall datacenter
VM Debian Login root lewat konsol, sudo tidak dipasang (Bab
1.7, 11)
Login SSH pengguna biasa + kunci, root SSH
dimatikan, UFW, update keamanan otomatis
STB AdGuard Home, backup AdGuardHome.yaml (Bab
12)
SSH kunci, kebijakan update hati-hati
Akses luar Tailscale subnet router (Bab 12.4, 13.8) Bab 26: kebijakan akses, DNS, klien laptop dan HP

## 25.2 Persiapan: backup dan jalur darurat

Sebelum mengubah apa pun, simpan keadaan yang masih bekerja. Dengan begitu kesalahan apa pun bisa
dibatalkan. Langkah ini hanya sekali dan memakan waktu beberapa menit.

**TERMINAL MIKROTIK** | WinBox &gt; New Terminal

```
/export file=sebelum-suplemen1
```
> Penjelasan: Menyimpan seluruh konfigurasi sebagai berkas teks yang dapat dibaca.
```
/system backup save name=sebelum-suplemen1
```
> Penjelasan: Membuat backup biner yang bisa dipulihkan ke router yang sama.
Lalu unduh kedua berkas ke laptop: di WinBox buka menu Files, seret sebelum-suplemen1.rsc dan
sebelum-suplemen1.backup ke folder di laptop.

**TERMINAL PROXMOX** | Shell Proxmox (root)

```
mkdir -p /root/cadangan-sebelum-suplemen1
```
> Penjelasan: Membuat folder untuk salinan konfigurasi.
```
cp -a /etc/ssh /root/cadangan-sebelum-suplemen1/ssh
```
> Penjelasan: Menyalin konfigurasi SSH lama agar bisa dikembalikan.
```
tar czf /root/cadangan-sebelum-suplemen1/etc-pve.tgz /etc/pve
```
> Penjelasan: Mengarsipkan konfigurasi Proxmox (pengguna, firewall, definisi VM). Berkas ini berisi data sensitif,
simpan di tempat aman.
```
ls -lh /root/cadangan-sebelum-suplemen1
```
> Penjelasan: Memastikan arsip terbentuk dan ukurannya tidak nol.

**POWERSHELL WINDOWS** | PowerShell (laptop)

```
scp -r root@192.168.88.10:/root/cadangan-sebelum-suplemen1 .
```
> Penjelasan: Menyalin folder cadangan dari Proxmox ke folder aktif di laptop. Salinan di luar server adalah intinya.
Snapshot VM Debian
1. Di web Proxmox, klik VM Debian di panel kiri, lalu buka tab Snapshots.
2. Klik Take Snapshot, beri nama sebelum-suplemen1, jangan centang Include RAM, klik Take Snapshot.
3. Tunggu status Task OK. Bila tombol Take Snapshot abu-abu, penyimpanan VM tidak mendukung snapshot;
gunakan Backup &gt; Backup now sebagai gantinya (Edisi 2 Bab 23).
Jalur darurat (catat sebelum mulai)
Perangkat Bila terkunci, masuk lewat Syarat
Proxmox (mesin asli) Monitor dan keyboard langsung Login root dan password lokal
VM Debian Tab Console di web Proxmox Login root dan password lokal
MikroTik WinBox lewat kabel ke ether2 (IP 192.168.88.1);
tombol reset sebagai pilihan terakhir
Backup dari langkah di atas
STB (Armbian) Monitor HDMI dan keyboard, atau PuTTY dari LAN Login root
TIPS
Konsol fisik Proxmox dan konsol web VM tidak memakai SSH, jadi aturan SSH yang dikeraskan di bab ini tidak mengunci jalur
darurat tersebut.

## 25.3 Akun admin Proxmox terpisah dan 2FA

Secara bawaan satu-satunya akun Proxmox adalah root@pam, akun yang sama dengan root di Linux. Siapa pun
yang menebak password-nya menguasai seluruh server. Kita buat akun admin terpisah, lalu pasang 2FA (kode 6
digit dari aplikasi autentikator) untuk kedua akun.
Membuat akun admin
1. Buka Datacenter &gt; Permissions &gt; Users lalu klik Add.
2. Isi User name (contoh: adminlab), Realm pilih Proxmox VE authentication server, isi password yang kuat
dan panjang, pastikan Enabled tercentang, klik Add.
3. Buka Datacenter &gt; Permissions lalu klik Add &gt; User Permission.
4. Isi Path = /, User = adminlab@pve, Role = Administrator, centang Propagate, klik Add.
5. Klik nama pengguna di kanan atas &gt; Logout. Masuk lagi dengan adminlab, Realm Proxmox VE
authentication server.
CATATAN
Akun ini hanya ada di Proxmox, bukan akun Linux. Karena itu ia tidak bisa dipakai untuk SSH, dan itu memang
disengaja: SSH tetap lewat root dengan kunci (Bab 25.4).
Memasang 2FA (TOTP)
1. Pasang aplikasi autentikator di HP (misalnya Google Authenticator, Microsoft Authenticator, atau Aegis di
Android).
2. Buka Datacenter &gt; Permissions &gt; Two Factor lalu klik Add &gt; TOTP. (Pada beberapa versi, menu yang
sama juga ada di nama pengguna kanan atas &gt; TFA.)
3. Pilih User adminlab@pve, isi Description (contoh: HP utama), pindai kode QR dengan aplikasi autentikator.
4. Ketik kode 6 digit yang muncul di aplikasi pada kolom Verify Code, isi Current Password (password akun
itu), klik Add.
5. Klik Add &gt; Recovery Keys, simpan seluruh kode yang tampil di password manager atau cetak dan simpan
fisik. Kode ini satu-satunya jalan bila HP hilang.
6. Ulangi langkah 2 sampai 5 untuk root@pam, supaya akun darurat juga terlindungi di web.
7. Logout dan login lagi: sekarang setelah password diminta kode 6 digit.
PERINGATAN
2FA hanya melindungi login web. Login SSH dan konsol tidak memakai TOTP. Simpan Recovery Keys sebelum
menutup halaman; tanpa itu dan tanpa HP, Anda harus memakai jalur darurat (Bab 25.11).
KASUS NYATA
Gejala: Kode TOTP selalu ditolak padahal benar. Penyebab: jam server menyimpang, misalnya NTP belum sinkron setelah mesin lama mati.
Solusi: jalankan timedatectl status dan pastikan "System clock
synchronized: yes"; bila tidak, tunggu sinkronisasi atau mulai ulang layanan waktu, lalu coba lagi.

## 25.4 SSH Proxmox hanya dengan kunci

Kunci SSH berpasangan: kunci privat tinggal di laptop dan tidak pernah dikirim, kunci publik dipasang di server.
Penyerang yang hanya tahu password tidak bisa masuk. Pasangan kunci sudah dibuat di Edisi 2 Bab 15.4; bila
belum, langkah 1 di bawah membuatnya.

**POWERSHELL WINDOWS** | PowerShell (laptop)

```
ssh-keygen -t ed25519 -C "laptop-rumah"
```
> Penjelasan: Membuat pasangan kunci. Jika sudah ada, jawab n saat ditanya menimpa berkas. Disarankan
mengisi passphrase agar kunci tercuri pun tidak langsung bisa dipakai.
```
type $env:USERPROFILE\.ssh\id_ed25519.pub
```
> Penjelasan: Menampilkan kunci publik (satu baris yang diawali ssh-ed25519). Salin seluruh baris itu.

**TERMINAL PROXMOX** | SSH atau Shell Proxmox (root)

```
mkdir -p /root/.ssh
```
> Penjelasan: Memastikan folder kunci ada.
```
echo 'TEMPEL-KUNCI-PUBLIK-DI-SINI' >> /root/.ssh/authorized_keys
```
> Penjelasan: Menambahkan kunci publik. Ganti teks dalam tanda petik dengan baris yang disalin tadi. Perhatikan
tanda &gt;&gt; (dua), jangan satu, agar kunci lain tidak terhapus.
```
chmod 600 /root/.ssh/authorized_keys
```
> Penjelasan: Membatasi izin berkas: hanya pemilik yang boleh membaca.
TIPS
Di Proxmox, /root/.ssh/authorized_keys tertaut ke /etc/pve/priv/authorized_keys, jadi perintah di atas
tetap berlaku. Pengguna PuTTY: buka PuTTYgen, Load kunci privat id_ed25519, Save private key (.ppk), lalu pakai di
Connection &gt; SSH &gt; Auth &gt; Credentials.
Uji login memakai kunci sebelum mematikan password

**POWERSHELL WINDOWS** | Jendela PowerShell BARU

```
ssh root@192.168.88.10
```
> Penjelasan: Harus langsung masuk tanpa meminta password (atau hanya meminta passphrase kunci). Jika masih
meminta password server, kunci belum terpasang benar; jangan lanjut.
Setelah berhasil, buat berkas pengaturan tambahan. Nama berkas berawalan 00- sengaja dipilih karena
OpenSSH memakai nilai pertama yang dibacanya.

**TERMINAL PROXMOX** | Shell Proxmox (root)

```
grep -n Include /etc/ssh/sshd_config
```
> Penjelasan: Memeriksa bahwa sshd_config memuat folder sshd_config.d (baris "Include
/etc/ssh/sshd_config.d/\*.conf").
```
nano /etc/ssh/sshd_config.d/00-hardening.conf
```
> Penjelasan: Membuat berkas baru. Isi seperti kotak di bawah.

**/etc/ssh/sshd_config.d/00-hardening.conf** | Isi berkas

```
PasswordAuthentication no
KbdInteractiveAuthentication no
PermitRootLogin prohibit-password
MaxAuthTries 3
LoginGraceTime 30
```

Simpan di nano dengan Ctrl+O, Enter, lalu keluar dengan Ctrl+X. Arti barisnya: password dimatikan, login
interaktif lain dimatikan, root hanya boleh dengan kunci, maksimal 3 percobaan, dan waktu login 30 detik.

**TERMINAL PROXMOX** | Shell Proxmox (root)

```
sshd -t
```
> Penjelasan: Memeriksa sintaks. Tidak ada keluaran berarti benar. Jika ada pesan error, perbaiki berkas dulu.
```
systemctl reload ssh
```
> Penjelasan: Menerapkan pengaturan tanpa memutus sesi yang sedang berjalan.
```
sshd -T | grep -Ei "passwordauthentication|permitrootlogin|kbdinteractive"
```
> Penjelasan: Menampilkan nilai yang benar-benar berlaku. Harus: passwordauthentication no,
kbdinteractiveauthentication no, permitrootlogin without-password.

**POWERSHELL WINDOWS** | PowerShell (laptop)

```
ssh -o PubkeyAuthentication=no root@192.168.88.10
```
> Penjelasan: Uji penolakan: memaksa login tanpa kunci. Hasil yang benar: "Permission denied (publickey)".
BAHAYA
Jangan tutup sesi SSH lama sebelum uji login kunci di jendela baru berhasil. Bila terkunci, masuk lewat konsol (Bab
25.2) dan hapus berkas dengan rm /etc/ssh/sshd_config.d/00-hardening.conf lalu systemctl reload
ssh.

## 25.5 Firewall Proxmox

Firewall Proxmox mati secara bawaan. Setelah dinyalakan, semua lalu lintas ke host diblokir kecuali web (8006)
dan SSH (22) dari jaringan lokal. Kita nyalakan lalu menuliskan aturan yang eksplisit agar maksudnya jelas dan
tidak berubah bila jaringan berubah.
PERINGATAN
Buka satu sesi SSH ke Proxmox sebelum menyalakan firewall (disarankan oleh dokumentasi Proxmox). Bila terputus,
sesi itu masih hidup dan firewall dapat dimatikan dari sana.

**TERMINAL PROXMOX** | Shell Proxmox (root)

```
pve-firewall localnet
```
> Penjelasan: Menampilkan jaringan yang dianggap "lokal". Harus memuat 192.168.88.0/24. Jika tampil jaringan
lain (misalnya 192.168.100.0/24 dari kasus Bab 9.11), sesuaikan aturan di bawah.
```
pve-firewall status
```
> Penjelasan: Memeriksa status layanan firewall sebelum diubah (mati atau stopped).
Menyalakan dan menulis aturan
1. Buka Datacenter &gt; Firewall &gt; Rules lalu klik Add. Isi: Direction in, Action ACCEPT, Protocol tcp, Source
192.168.88.0/24, Dest. port 8006, Comment "web Proxmox dari LAN", centang Enable, klik Add.
2. Ulangi dengan Dest. port 22, Comment "SSH dari LAN".
3. Ulangi dengan Protocol icmp (tanpa port) agar ping tetap bekerja, Comment "ping dari LAN".
4. Buka Datacenter &gt; Firewall &gt; Options, pilih baris Firewall, klik Edit, centang, OK. Pastikan Input Policy
bernilai DROP dan Output Policy ACCEPT.
5. Buka pve (node) &gt; Firewall &gt; Options dan pastikan Firewall bernilai yes.
6. Dari laptop, buka ulang https://192.168.88.10:8006 dan SSH baru. Keduanya harus tetap berfungsi.

**TERMINAL PROXMOX** | Shell Proxmox (root)

```
pve-firewall status
```
> Penjelasan: Harus menampilkan status enabled/running.
```
pve-firewall compile | head -40
```
> Penjelasan: Opsional: melihat aturan yang dihasilkan, untuk memastikan aturan 8006 dan 22 ada.
KEAMANAN
Akses dari luar rumah lewat Tailscale tetap lolos aturan ini karena router Tailscale mengubah alamat sumber menjadi
alamat LAN-nya (192.168.88.x). Bila suatu saat Tailscale dipasang langsung di Proxmox, tambahkan aturan dengan
Source 100.64.0.0/10.
BAHAYA
Terkunci dari firewall: dari konsol (Bab 25.2) jalankan pve-firewall stop. Perintah ini menghapus semua aturan
Proxmox dan membuat host tak terlindungi sampai pve-firewall start dijalankan. Alternatif: ubah enable: 1
menjadi enable: 0 di /etc/pve/firewall/cluster.fw, bagian [OPTIONS].
CATATAN
Firewall tingkat VM dan container sengaja belum dinyalakan. Perlindungan VM Debian dikerjakan di dalam VM
dengan UFW (Bab 25.6) agar mudah dipahami satu per satu.

## 25.6 Mengeraskan VM Debian

VM Debian (192.168.88.20) menjalankan Docker, Portainer, Git, dan Nextcloud, jadi ia target paling menarik.
Empat langkah: login SSH dengan kunci sebagai pengguna biasa, root SSH dimatikan, firewall UFW, dan update
keamanan otomatis. Perintah tetap tanpa sudo: setelah login, jalankan su -.
A. Login SSH pengguna biasa dengan kunci

**POWERSHELL WINDOWS** | PowerShell (laptop)

```
ssh <USER>@192.168.88.20
```
> Penjelasan: Masuk sebagai pengguna biasa yang dibuat saat instalasi Debian (Bab 11.3). Ganti &lt;USER&gt; dengan
nama pengguna Anda. Saat ini masih memakai password.
```
type $env:USERPROFILE\.ssh\id_ed25519.pub
```
> Penjelasan: Tampilkan kunci publik untuk disalin (di jendela PowerShell lain).

**TERMINAL VM DEBIAN** | SSH sebagai pengguna biasa

```
mkdir -p ~/.ssh
```
> Penjelasan: Membuat folder kunci milik pengguna ini.
```
chmod 700 ~/.ssh
```
> Penjelasan: Hanya pemilik yang boleh masuk folder.
```
echo 'TEMPEL-KUNCI-PUBLIK-DI-SINI' >> ~/.ssh/authorized_keys
```
> Penjelasan: Menambahkan kunci publik (ganti teksnya).
```
chmod 600 ~/.ssh/authorized_keys
```
> Penjelasan: Membatasi izin berkas kunci.

**POWERSHELL WINDOWS** | Jendela PowerShell BARU

```
ssh <USER>@192.168.88.20
```
> Penjelasan: Harus masuk tanpa password VM. Jika berhasil, lanjut ke bagian B.
B. Mematikan login root dan password lewat SSH

**TERMINAL VM DEBIAN** | SSH sebagai pengguna biasa

```
su -
```
> Penjelasan: Menjadi root (masukkan password root). Prompt berubah menjadi #. Mulai di sini tanpa sudo.
```
nano /etc/ssh/sshd_config.d/00-hardening.conf
```
> Penjelasan: Membuat berkas pengaturan. Isi seperti kotak di bawah.

**/etc/ssh/sshd_config.d/00-hardening.conf** | Isi berkas

```
PasswordAuthentication no
KbdInteractiveAuthentication no
PermitRootLogin no
MaxAuthTries 3
LoginGraceTime 30
```

**TERMINAL VM DEBIAN** | Sebagai root (setelah su -)

```
sshd -t
```
> Penjelasan: Memeriksa sintaks; tanpa keluaran berarti benar.
```
systemctl reload ssh
```
> Penjelasan: Menerapkan pengaturan.
```
sshd -T | grep -Ei "passwordauthentication|permitrootlogin"
```
> Penjelasan: Harus menampilkan passwordauthentication no dan permitrootlogin no.

**POWERSHELL WINDOWS** | PowerShell (laptop)

```
ssh root@192.168.88.20
```
> Penjelasan: Harus ditolak (Permission denied). Itu hasil yang diharapkan.
```
ssh <USER>@192.168.88.20
```
> Penjelasan: Pengguna biasa dengan kunci tetap harus bisa masuk.
C. Firewall UFW
UFW adalah antarmuka sederhana untuk firewall Linux. Aturan dasarnya: tolak semua yang masuk, terima yang
keluar, lalu izinkan SSH hanya dari LAN.

**TERMINAL VM DEBIAN** | Sebagai root

```
apt update && apt install -y ufw
```
> Penjelasan: Memasang UFW.
```
ufw default deny incoming
```
> Penjelasan: Semua koneksi masuk ditolak kecuali yang diizinkan.
```
ufw default allow outgoing
```
> Penjelasan: Koneksi keluar (update, Docker pull) tetap diizinkan.
```
ufw allow from 192.168.88.0/24 to any port 22 proto tcp
```
> Penjelasan: Mengizinkan SSH hanya dari LAN. Wajib sebelum mengaktifkan UFW.
```
ufw enable
```
> Penjelasan: Mengaktifkan UFW. Jawab y bila diminta. Sesi SSH yang berjalan tetap hidup karena aturan SSH
sudah ada.
```
ufw status verbose
```
> Penjelasan: Memeriksa: Status active, Default deny (incoming), allow (outgoing), dan aturan SSH.
PERINGATAN - Perlu dipahami
Docker melewati UFW. Port yang dipublikasikan Docker (misalnya -p 9443:9443 untuk Portainer) dipasang Docker
langsung di firewall sehingga tetap terbuka dari seluruh LAN walau UFW menolaknya. UFW di sini melindungi layanan
milik VM sendiri (SSH), bukan port container.
Karena itu rumah Anda mengandalkan tiga hal: tidak ada port forwarding di MikroTik, akses luar hanya lewat Tailscale,
dan nanti reverse proxy (Suplemen 3) yang menjadi pintu tunggal. Untuk melihat apa yang terbuka sekarang, jalankan
ss -tlnp di VM dan catat setiap port selain 22. Hasilnya dipakai di audit Bab 38.
D. Update keamanan otomatis

**TERMINAL VM DEBIAN** | Sebagai root

```
apt install -y unattended-upgrades apt-listchanges
```
> Penjelasan: Memasang paket yang memasang update keamanan Debian secara otomatis.
```
nano /etc/apt/apt.conf.d/20auto-upgrades
```
> Penjelasan: Membuat berkas pengaktif. Isi seperti kotak di bawah.

**/etc/apt/apt.conf.d/20auto-upgrades** | Isi berkas

```
APT::Periodic::Update-Package-Lists "1";
APT::Periodic::Unattended-Upgrade "1";
```

**TERMINAL VM DEBIAN** | Sebagai root

```
unattended-upgrade --dry-run --debug 2>&1 | tail -15
```
> Penjelasan: Uji tanpa mengubah apa pun. Harus menampilkan asal paket yang diizinkan (Debian security) dan
tanpa error.
```
systemctl status apt-daily-upgrade.timer --no-pager
```
> Penjelasan: Memastikan penjadwal harian aktif (active waiting).
```
[ -f /var/run/reboot-required ] && echo PERLU-REBOOT || echo aman
```
> Penjelasan: Memeriksa apakah ada update yang menunggu reboot.
CATATAN
Hanya update keamanan dari repositori Debian yang otomatis, dan VM tidak mulai ulang sendiri. Paket dari repositori
lain (termasuk Docker dan Tailscale) dan image container tidak ikut. Perbarui itu manual sebulan sekali dengan apt
update && apt full-upgrade dan docker compose pull, setelah backup.

## 25.7 STB Armbian: SSH kunci dan kebijakan update

STB (192.168.88.253) menjalankan AdGuard Home dan menjadi DNS seluruh rumah, sehingga stabilitasnya
lebih penting dari fiturnya. Dua tindakan saja: SSH hanya dengan kunci, dan tidak memakai update otomatis.

**POWERSHELL WINDOWS** | PowerShell (laptop)

```
type $env:USERPROFILE\.ssh\id_ed25519.pub
```
> Penjelasan: Tampilkan kunci publik untuk disalin.

**TERMINAL STB** | SSH ke 192.168.88.253 (root)

```
mkdir -p /root/.ssh
```
> Penjelasan: Memastikan folder kunci ada.
```
echo 'TEMPEL-KUNCI-PUBLIK-DI-SINI' >> /root/.ssh/authorized_keys
```
> Penjelasan: Menambahkan kunci publik.
```
chmod 600 /root/.ssh/authorized_keys
```
> Penjelasan: Membatasi izin.
```
grep -n Include /etc/ssh/sshd_config
```
> Penjelasan: Jika ada baris Include .../sshd_config.d/\*.conf, buat berkas seperti di Bab 25.4. Jika tidak ada, ubah
langsung baris terkait di /etc/ssh/sshd_config.
Setelah uji login kunci dari jendela baru berhasil, isi pengaturan sama dengan Proxmox (PermitRootLogin
prohibit-password dan PasswordAuthentication no), lalu sshd -t dan systemctl reload ssh.
KEAMANAN
Jangan memasang unattended-upgrades di STB. Pembaruan kernel atau berkas boot pada box Amlogic dapat
membuat STB gagal boot (pengalaman eMMC di Edisi 2 Bab 12.2). Perbarui AdGuard Home dari menunya sendiri
dan perbarui sistem secara manual hanya setelah backup AdGuardHome.yaml dan bila Anda siap menghadapi STB
yang tidak boot.

## 25.8 Mengeraskan MikroTik

Edisi 2 Bab 3.8 sudah mematikan layanan tak terpakai dan membatasi WinBox dan SSH. Tambahannya adalah
aturan firewall yang menutup akses ke router dari sisi WAN (jaringan TL-WR840N), pembatasan WebFig, dan
beberapa layanan tersembunyi.
PERINGATAN - Selalu pakai Safe Mode
Aktifkan Safe Mode sebelum mengubah firewall: klik tombol Safe Mode di WinBox (atau tekan Ctrl+X di terminal). Bila
koneksi Anda terputus karena aturan salah, RouterOS membatalkan perubahan otomatis. Matikan Safe Mode setelah
semua uji berhasil.

**TERMINAL MIKROTIK** | WinBox &gt; New Terminal (RouterOS 6.49)

```
/ip firewall filter print
```
> Penjelasan: Melihat aturan yang sudah ada. Jika sudah ada aturan "drop all not coming from LAN" atau drop dari
ether1, jangan menambah aturan serupa (langkah 2 sampai 5); cukup periksa urutannya.
```
/ip firewall filter add chain=input action=accept connection-state=established,related place-before=0 comment="terima koneksi berjalan"
```
> Penjelasan: Menerima balasan dari koneksi yang sudah berjalan. Harus paling atas.

```
/ip firewall filter add chain=input action=drop connection-state=invalid place-before=1 comment="buang paket tidak valid"
```
> Penjelasan: Membuang paket yang tidak sah.

```
/ip firewall filter add chain=input action=drop in-interface=ether1 place-before=2 comment="tutup router dari sisi WAN"
```
> Penjelasan: Menutup seluruh akses ke router dari arah internet/WR840N. Router tetap terbuka dari LAN.

```
/ip firewall filter add chain=forward action=drop in-interface=ether1 connection-state=new connection-nat-state=!dstnat comment="tolak koneksi baru dari WAN ke LAN"
```
> Penjelasan: Menolak koneksi baru dari arah WAN ke jaringan rumah.
```
/ip firewall filter print
```
> Penjelasan: Memeriksa urutan: terima koneksi berjalan, buang tidak valid, tutup WAN, lalu forward.

**TERMINAL MIKROTIK** | WinBox &gt; New Terminal

```
/ip service set www address=192.168.88.0/24
```
> Penjelasan: Membatasi WebFig ke LAN. Akses dari luar rumah tetap bisa lewat Tailscale, karena router Tailscale
tampil di router sebagai alamat LAN.
```
/ip proxy set enabled=no
```
> Penjelasan: Mematikan web proxy bawaan.
```
/ip socks set enabled=no
```
> Penjelasan: Mematikan SOCKS proxy.
```
/ip upnp set enabled=no
```
> Penjelasan: Mematikan UPnP (perangkat tidak boleh membuka port sendiri).
```
/tool bandwidth-server set enabled=no
```
> Penjelasan: Mematikan server uji bandwidth.
```
/ip cloud set ddns-enabled=no
```
> Penjelasan: Mematikan layanan DDNS bawaan MikroTik.
```
/ip ssh set strong-crypto=yes
```
> Penjelasan: Memakai algoritma SSH yang lebih kuat.
```
/user print
```
> Penjelasan: Memeriksa daftar pengguna. Pastikan hanya akun Anda dan tidak ada akun asing.

**TERMINAL MIKROTIK** | WinBox &gt; New Terminal

```
/export file=setelah-suplemen1
```
> Penjelasan: Menyimpan konfigurasi baru setelah semua uji berhasil.
```
/system backup save name=setelah-suplemen1
```
> Penjelasan: Backup biner baru.
CATATAN
Pemisahan jaringan (VLAN) untuk memisahkan server, tamu, dan perangkat IoT sangat berguna tetapi bergantung
pada kemampuan switch RB750GL dan perlu dicoba dulu. Itu dibahas sebagai opsi di suplemen berikutnya,
bukan di sini.

## 25.9 Backup dan pemulihan pengaturan keamanan

Yang disimpan Cara Simpan di
Kunci privat SSH (id_ed25519) dan
passphrase
Salin ke flashdisk terenkripsi atau password
manager
Di luar laptop
Recovery Keys 2FA Proxmox Dicetak atau di password manager Di luar server
Konfigurasi MikroTik (.rsc dan .backup) Langkah di Bab 25.2 dan 25.8 Laptop dan HDD 2 TB
/etc/pve dan /etc/ssh Proxmox Langkah di Bab 25.2 Laptop dan HDD 2 TB
Snapshot VM Debian Tab Snapshots; hapus bila sudah tak dipakai Penyimpanan Proxmox
AdGuardHome.yaml Edisi 2 Bab 12 Laptop
Cadangan yang tidak pernah diuji belum berarti. Satu kali saja, praktikkan memulihkan snapshot VM Debian ke
keadaan sebelum bab ini dan pastikan semua layanan hidup lagi.

## 25.10 Checklist uji keamanan

No Uji Cara Hasil yang diharapkan
1 SSH Proxmox tanpa kunci ditolak ssh -o PubkeyAuthentication=no
root@192.168.88.10
Permission denied (publickey)
2 SSH Proxmox dengan kunci jalan ssh root@192.168.88.10 Masuk
3 Root VM Debian ditolak ssh root@192.168.88.20 Permission denied
4 Pengguna biasa VM masuk
dengan kunci
ssh &lt;USER&gt;@192.168.88.20 Masuk tanpa password
5 Web Proxmox meminta kode 2FA Login adminlab dan root@pam Kode 6 digit diminta
6 Firewall Proxmox aktif pve-firewall status enabled/running
7 UFW VM aktif ufw status verbose Status: active
8 Update otomatis siap unattended-upgrade --dry-run --debug Tanpa error
9 MikroTik tertutup dari WAN /ip firewall filter print Aturan drop
in-interface=ether1-gateway ada
10 Layanan masih jalan Buka Portainer, Nextcloud, AdGuard Semua terbuka dari LAN
11 Backup baru ada Berkas di laptop rsc, backup, etc-pve.tgz

## 25.11 Masalah dan solusi

KASUS NYATA
Gejala: Setelah mengubah SSH, muncul "Permission denied (publickey)" untuk akun yang benar. Penyebab: kunci
publik belum masuk, salah izin berkas, atau salah akun. Solusi: masuk lewat konsol, cek ls -l
~/.ssh/authorized_keys (izin 600) dan isi barisnya; sementara waktu hapus berkas 00-hardening.conf dan
systemctl reload ssh.
KASUS NYATA
Gejala: Tidak bisa membuka web Proxmox setelah menyalakan firewall. Penyebab: alamat laptop di luar "jaringan
lokal" menurut Proxmox. Solusi: dari konsol jalankan pve-firewall stop, periksa pve-firewall localnet,
koreksi Source pada aturan 8006 dan 22, lalu pve-firewall start.
KASUS NYATA
Gejala: Kode 2FA ditolak dan Recovery Keys tidak ada. Solusi: dari konsol Proxmox (root) hapus faktor kedua akun
itu, misalnya pveum user tfa delete root@pam; jika perintah tidak dikenali, periksa pveum help user. Lalu
pasang 2FA baru dan simpan Recovery Keys.
KASUS NYATA
Gejala: Port container tetap bisa dibuka dari laptop padahal UFW menolaknya. Penyebab: Docker memasang aturan
sendiri yang mendahului UFW. Solusi: ini perilaku normal; ikuti catatan Bab 25.6 dan audit Bab 38.
KASUS NYATA
Gejala: Terputus dari MikroTik setelah menambah aturan firewall. Solusi: bila Safe Mode aktif, perubahan otomatis
dibatalkan; bila tidak, sambungkan kabel ke ether2, buka WinBox lewat 192.168.88.1, hapus aturan terakhir, atau
pulihkan backup.


<!-- SOURCE: docs/bab/suplemen/26-tailscale.md -->

# Bab 26. Tailscale: Akses Aman dari Mana Saja

PENEMPATAN - BARU - LXC sendiri, bukan VM Docker
Tempat: LXC CT103 ts-router (dibuat di Edisi 2 Bab 13.8), tidak di VM 201. Nama Tailscale tetap router-vm.
Alasan: Tailscale adalah pintu masuk dari luar. Bila digabung dengan Docker, kebobolan salah satu membuka yang
lain. LXC ringan, hidup terpisah, dan nanti pindah ke STB 2.
Perubahan: Pada tabel 26.2, pilihan B (VM 192.168.88.20) tidak dipakai lagi; pakai C. Langkah di bawah sama; LXC
perlu perangkat /dev/net/tun (Edisi 2 Bab 13.8). Tailscale tetap tidak dipasang di host Proxmox.
Tailscale membuat jaringan privat antarperangkat melalui internet tanpa membuka port di router. Bab ini menjelaskan rancangan akses jarak jauh, pemilihan subnet router, konfigurasi server dan klien, kebijakan akses, DNS, serta pengujian dari luar rumah. **Status proyek: Tailscale belum diterapkan; STB 1 tetap khusus AdGuard Home.**

## 26.1 Cara kerja dalam satu gambar

Setiap perangkat yang diberi Tailscale masuk ke satu jaringan privat bernama tailnet dan mendapat alamat
100.x.y.z. Satu perangkat di rumah dijadikan subnet router: ia meneruskan lalu lintas dari tailnet ke seluruh
jaringan 192.168.88.0/24. Dengan begitu Proxmox, MikroTik, dan VM tidak perlu dipasangi Tailscale satu per
satu.
Rumah (jaringan 192.168.88.0/24)
HP / Laptop
di luar rumah, Tailscale aktif
Server koordinasi Tailscale
hanya bertukar kunci
Subnet router
STB 2 / VM Debian / LXC
Perangkat di LAN
MikroTik .1 Proxmox .10
VM Debian .20 STB .253
terowongan WireGuard
(langsung, atau lewat relay)
meneruskan
Tidak ada port yang dibuka
di router rumah.
Gambar 26.1 - HP atau laptop di luar rumah menjangkau LAN lewat subnet router.
Istilah Arti sederhana
Tailnet Jaringan privat milik akun Anda; hanya perangkat Anda di dalamnya.
Subnet router Perangkat di rumah yang menjadi pintu ke seluruh LAN (dipakai di buku ini).
WireGuard Teknologi enkripsi di balik terowongan; isi lalu lintas tidak terbaca pihak lain.
Relay (DERP) Jalur cadangan lewat server Tailscale bila koneksi langsung tidak bisa dibuat (umum pada NAT
berlapis seperti WISP dan IndiHome). Lebih lambat tetapi tetap terenkripsi.
MagicDNS Nama otomatis untuk perangkat Tailscale, misalnya router-vm.
Tag Label pada perangkat server (tag:router) agar aturan akses bisa dibedakan dari perangkat
pribadi.
Grants / ACL Aturan siapa boleh menjangkau apa di dalam tailnet.
Istilah Arti sederhana
Split DNS Hanya nama domain tertentu yang dijawab oleh DNS rumah (AdGuard) saat Anda di luar.

## 26.2 Memilih perangkat subnet router

Subnet router harus hidup terus agar akses luar bekerja. Pilihan Anda saat ini:
Pilihan Kapan Kelebihan Kekurangan
A. STB 2 (target) Setelah STB 2 tiba Selalu hidup, terpisah dari Proxmox,
STB 1 khusus AdGuard (keputusan
Anda)
Perlu perangkat, Armbian, dan IP
tetap
B. VM Debian
192.168.88.20
(sementara)
Sekarang, selama
STB 2 belum ada
Tanpa perangkat baru, langkah
sama dengan A
Hidup hanya selama Proxmox
hidup
C. LXC CT103 (Edisi 2
Bab 13.8)
Sebagai cadangan
permanen
Ringan; Tailscale beralih otomatis
bila router lain mati
Ikut mati bila Proxmox mati
D. STB 1 (Edisi 2 Bab
12.4)
Tidak disarankan
sekarang
Sudah selalu hidup STB 1 seharusnya khusus AdGuard
agar DNS rumah stabil
CATATAN
Rancangan proyek: gunakan CT103 sebagai subnet router bila akses Tailscale diperlukan sebelum STB 2 tersedia; setelah STB 2 siap, pindahkan peran utama ke STB 2 dan CT103 dapat dipertahankan sebagai cadangan. Proxmox kini sudah berjalan, tetapi CT103 dan Tailscale belum dibuat. Pastikan jaringan host/guest final dan perangkat pilihan sebelum menerapkan langkah server. Dua router dapat mengiklankan rute yang sama hanya setelah failover dikonfigurasi dan diuji.
KEAMANAN
Tailscale tidak dipasang di host Proxmox. Host virtualisasi sebaiknya tidak memiliki jalan masuk tambahan; akses
ke Proxmox cukup lewat subnet router.

## 26.3 Menyiapkan akun dan konsol admin

1. Buka login.tailscale.com dan masuk memakai akun Google, Microsoft, Apple, atau GitHub Anda. Tailscale
tidak menyimpan password sendiri; keamanan tailnet mengikuti akun ini.
2. Aktifkan verifikasi dua langkah di akun email itu. Siapa pun yang menguasai akun tersebut menguasai
tailnet Anda.
3. Kenali empat halaman konsol admin: Machines (daftar perangkat), Access controls (aturan akses), DNS,
dan Settings (kunci dan kedaluwarsa perangkat).
4. Buka Settings &gt; Keys dan lihat berapa lama kunci perangkat berlaku sebelum kedaluwarsa. Perangkat
pribadi sebaiknya tetap kedaluwarsa berkala; perangkat server tidak (lihat 26.6).
KEAMANAN
Catat alamat email yang dipakai di password manager nanti (Suplemen 4). Jangan memakai akun bersama atau akun
tanpa verifikasi dua langkah.

## 26.4 Sisi server: memasang subnet router

Contoh memakai VM Debian (pilihan B). Untuk STB 2 (Armbian) dan LXC langkahnya sama; khusus LXC baca
Edisi 2 Bab 13.8 untuk izin /dev/net/tun. Semua perintah sebagai root.

**TERMINAL VM DEBIAN** | Sebagai root (setelah su -)

```
apt update && apt install -y curl
```
> Penjelasan: Memastikan curl terpasang.
```
curl -fsSL https://tailscale.com/install.sh | sh
```
> Penjelasan: Mengunduh dan memasang Tailscale resmi untuk Debian. Skrip menambahkan repositori sehingga
pembaruan ikut apt.
```
echo 'net.ipv4.ip_forward = 1' > /etc/sysctl.d/99-tailscale.conf
```
> Penjelasan: Mengaktifkan penerusan paket IPv4. Tanpa ini perangkat tidak bisa menjadi pintu ke LAN.
```
echo 'net.ipv6.conf.all.forwarding = 1' >> /etc/sysctl.d/99-tailscale.conf
```
> Penjelasan: Mengaktifkan penerusan IPv6 (dua tanda &gt;&gt;, menambah baris).
```
sysctl -p /etc/sysctl.d/99-tailscale.conf
```
> Penjelasan: Menerapkan pengaturan tanpa reboot.
```
tailscale up --advertise-routes=192.168.88.0/24 --accept-dns=false --hostname=router-vm
```
> Penjelasan: Menghubungkan ke akun dan mengumumkan LAN. --accept-dns=false menjaga DNS lokal agar
tidak diubah Tailscale. --hostname memberi nama yang mudah dikenali.
Perintah terakhir menampilkan sebuah alamat https://login.tailscale.com/a/.... Buka di browser laptop, masuk
dengan akun yang sama, dan setujui perangkat. Lalu setujui rute di konsol:
1. Buka Machines, temukan router-vm (tertulis "Subnet router" dengan tanda peringatan).
2. Klik ... di barisnya &gt; Edit route settings, centang 192.168.88.0/24, klik Save.
3. Klik ... &gt; Disable key expiry agar router tidak perlu login ulang berkala (otomatis terpenuhi setelah diberi tag
di 26.6).

**TERMINAL VM DEBIAN** | Sebagai root

```
tailscale status
```
> Penjelasan: Menampilkan perangkat di tailnet dan statusnya. router-vm harus tertulis hidup.
```
tailscale ip -4
```
> Penjelasan: Menampilkan alamat Tailscale perangkat ini (100.x.y.z).
TIPS
Untuk mengubah pengaturan Tailscale di kemudian hari gunakan tailscale set (misalnya tailscale set
--advertise-routes=192.168.88.0/24). Mengulang tailscale up tanpa seluruh opsi sebelumnya akan ditolak
dengan pesan yang meminta semua opsi disebut ulang.
KASUS NYATA
Gejala: Rute disetujui tetapi 192.168.88.x tidak terjangkau dari luar. Penyebab umum: penerusan paket belum aktif,
atau firewall VM menolak penerusan. Solusi: jalankan sysctl net.ipv4.ip_forward (harus 1). Bila UFW aktif,
lihat ip -br a untuk nama kartu jaringan (misalnya ens18), lalu coba ufw route allow in on tailscale0 out
on ens18 dan ufw allow in on tailscale0. Tailscale memasang aturan penerusan sendiri; aturan UFW ini
hanya bila masih terblokir.

## 26.5 Sisi klien: laptop Windows dan HP

Setiap perangkat yang dipakai mengakses server dari luar harus memasang aplikasi Tailscale dan masuk ke
akun yang sama. Windows, Android, dan iPhone menerima rute subnet secara bawaan (Edisi 2 Bab 12.4); bila
192.168.88.x tidak terjangkau, periksa opsi Use Tailscale subnets di pengaturan aplikasi.
A. Laptop Windows
1. Unduh pemasang Windows dari tailscale.com/download dan jalankan sampai selesai.
2. Ikon Tailscale muncul di area notifikasi (dekat jam). Klik ikon &gt; Log in; browser terbuka, masuk dengan akun
yang sama.
3. Klik ikon lagi: status harus Connected, dan nama router-vm terlihat di daftar perangkat.
4. Biarkan opsi Run Tailscale when I log in aktif agar otomatis berjalan.

**POWERSHELL WINDOWS** | PowerShell (laptop)

```
tailscale status
```
> Penjelasan: Menampilkan perangkat tailnet. Jika perintah tidak dikenali, tutup lalu buka PowerShell baru.
```
tailscale ping router-vm
```
> Penjelasan: Menguji jalur ke router. Hasilnya menyebut "via DERP" (relay) atau alamat langsung (direct).
```
ping 192.168.88.10
```
> Penjelasan: Menguji Proxmox lewat rute subnet (bermakna saat laptop di luar rumah atau di jaringan lain).
CATATAN
Saat laptop berada di rumah, di jaringan 192.168.88.0/24 yang sama, Tailscale tidak diperlukan. Bila ada akses yang
aneh di rumah, pilih Disconnect dulu untuk membedakan sumber masalahnya.
B. HP Android
1. Pasang Tailscale dari Google Play Store.
2. Buka aplikasi, ketuk Get Started, lalu masuk dengan akun yang sama.
3. Saat muncul permintaan koneksi VPN dari sistem, ketuk OK. Ini wajib; Tailscale bekerja sebagai VPN lokal di
HP.
4. Geser sakelar ke aktif. Ikon kunci/VPN muncul di bilah status, dan router-vm tampil di daftar.
5. Buka Pengaturan &gt; Jaringan &gt; VPN, ketuk ikon roda gigi di Tailscale, aktifkan VPN selalu aktif. Jangan
aktifkan "Blokir koneksi tanpa VPN" agar internet tetap hidup bila Tailscale mati. (Nama menu berbeda antar
merek HP.)
6. Buka Pengaturan &gt; Aplikasi &gt; Tailscale &gt; Baterai dan pilih Tidak dibatasi agar tidak dimatikan sistem
untuk menghemat daya.
C. iPhone
1. Pasang Tailscale dari App Store.
2. Buka aplikasi dan masuk dengan akun yang sama.
3. Saat iOS meminta izin menambahkan konfigurasi VPN, ketuk Allow dan konfirmasi dengan Face ID atau
kode.
4. Aktifkan sakelar. Indikator VPN muncul di bilah status, dan router-vm tampil di daftar.
PERINGATAN
Android dan iPhone hanya bisa menjalankan satu VPN pada satu waktu. Bila Anda memakai VPN lain, matikan dulu
sebelum menyalakan Tailscale.
KEAMANAN
Kunci layar HP dan laptop wajib aktif. Perangkat yang terhubung ke Tailscale yang hilang harus segera dihapus dari
konsol (Bab 26.9).

## 26.6 Kebijakan akses dan tag

Secara bawaan semua perangkat di tailnet boleh menghubungi semua perangkat lain. Kita batasi supaya
perangkat server (router) tidak bisa memulai koneksi ke HP dan laptop Anda. Jika router suatu hari diretas,
penyerang tidak otomatis mendapat jalan ke perangkat pribadi Anda.
CATATAN
Pada tailnet satu pengguna, manfaat utamanya adalah mengurung perangkat ber-tag. Aturan ini juga menjadi dasar
bila kelak ada anggota keluarga yang diberi akses sebagian.
1. Buka Access controls. Salin seluruh isi editor ke berkas teks di laptop sebagai cadangan.
2. Tambahkan anggota Anda ke `group:home-admins`, setel `tagOwners`, dan gabungkan aturan `grants` di kotak bawah dengan kebijakan yang sudah ada. Jika bagian `groups` atau `grants` sudah ada, gabungkan isinya; jangan membuat kunci tingkat atas duplikat. Gunakan alamat akun Tailscale Anda sendiri.
3. Klik Save. Editor menolak penyimpanan bila ada kesalahan sintaks.

**Access controls (potongan)** | tailnet policy file (HuJSON)

```
 // Hanya akun admin yang Anda masukkan ke grup ini boleh mengakses LAN rumah.
 "groups": {
 "group:home-admins": ["EMAIL-ADMIN-ANDA@example.com"],
 },
 // Siapa yang boleh memberi tag router pada perangkat
 "tagOwners": {
 "tag:router": ["group:home-admins"],
 },
 // Grup admin boleh menjangkau router dan LAN rumah; anggota lain tidak mendapat akses LAN otomatis.
 "grants": [
 {
 "src": ["group:home-admins"],
 "dst": ["tag:router", "192.168.88.0/24"],
 "ip": ["*"],
 },
 {
 "src": ["group:home-admins"],
 "dst": ["autogroup:self"],
 "ip": ["tcp:443"],
 },
 ],
```

1. Buka Machines, klik ... pada router-vm &gt; Edit ACL tags, pilih tag:router, Save.
2. Periksa ulang rute: Edit route settings harus masih tercentang. Perangkat ber-tag otomatis tidak
kedaluwarsa kuncinya.
3. Uji dari HP (data seluler): buka https://192.168.88.10:8006. Harus tetap berhasil.
TIPS
Jika editor menolak dst berupa rentang IP pada grants, pakai sintaks lama yang juga didukung: "acls": [{ "action":
"accept", "src": ["group:home-admins"], "dst": ["tag:router:*", "192.168.88.0/24:*"] }].
KEAMANAN
Editor kebijakan dibuka lewat situs web Tailscale, bukan lewat tailnet, sehingga kesalahan aturan tidak mengunci jalur
Anda untuk memperbaikinya. Tetap simpan salinan JSON lama.

## 26.7 DNS: nama dan pemblokir iklan dari luar rumah

Ada tiga tingkat, dari paling aman ke paling berpengaruh. Mulailah dari A dan B; C opsional.
A. MagicDNS
1. Buka halaman DNS di konsol admin dan pastikan MagicDNS aktif.
2. Uji dari laptop: tailscale ping router-vm memakai nama, bukan alamat.
B. Split DNS: nama lokal dijawab AdGuard
Dengan ini, nama berakhiran lab.local dijawab oleh AdGuard di rumah saat Anda di luar. Fondasi ini dipakai di
Suplemen 3 untuk nama layanan.
1. Di AdGuard Home (http://192.168.88.253) buka Filters &gt; DNS rewrites &gt; Add DNS rewrite: Domain
pve.lab.local, IP 192.168.88.10.
2. Di konsol Tailscale buka DNS &gt; Nameservers &gt; Add nameserver &gt; Custom.
3. Isi 192.168.88.253, aktifkan Restrict to domain, isi domain lab.local, Save.
4. Dari HP (data seluler, Tailscale aktif) buka https://pve.lab.local:8006. Harus terbuka.
CATATAN
Pertanyaan DNS dari HP tiba di AdGuard dengan alamat router Tailscale, bukan alamat HP. Statistik per perangkat di
AdGuard tidak akan menampilkan HP saat di luar rumah.
C. Opsional: pemblokir iklan di HP saat di luar rumah
Di DNS &gt; Nameservers tambahkan 192.168.88.253 sebagai nameserver global dan aktifkan Override DNS
servers (di sebagian tampilan disebut Override local DNS). Seluruh pertanyaan DNS perangkat Anda lewat
AdGuard rumah.
PERINGATAN
Risiko: bila rumah mati listrik atau IndiHome putus, AdGuard tidak terjangkau dan HP Anda terlihat "tidak ada internet"
selama Tailscale aktif. Menambah nameserver kedua (misalnya 1.1.1.1) sebagai cadangan mengurangi risikonya,
tetapi urutan pemilihan nameserver tidak dijamin sehingga iklan bisa tidak terblokir sesekali.
Saran: mulai dari A dan B saja. Aktifkan C hanya bila Anda siap mematikan Tailscale ketika internet terasa mati.

## 26.8 Uji dari luar jaringan

Membuktikan akses dari luar tidak bisa dilakukan dari dalam rumah. Pakai data seluler HP, bukan WiFi rumah.
No Perangkat dan jaringan Uji Hasil yang diharapkan
1 HP, data seluler, Tailscale aktif Buka https://192.168.88.10:8006 Peringatan sertifikat (normal, sertifikat
buatan sendiri), lalu login dan kode 2FA
2 HP, data seluler Buka http://192.168.88.1 Halaman WebFig MikroTik
3 HP, data seluler Buka http://192.168.88.253 Halaman AdGuard Home
4 HP, data seluler Buka https://pve.lab.local:8006
(setelah 26.7B)
Halaman Proxmox
5 HP, Tailscale mati Buka alamat nomor 1 Gagal. Ini membuktikan tidak ada port
yang terbuka ke internet.
6 Laptop di jaringan lain (hotspot
HP kedua)
ssh root@192.168.88.10 Masuk dengan kunci
7 Laptop atau HP tailscale ping router-vm Hasil direct atau via DERP; keduanya
berfungsi

## 26.9 Operasional harian

Perintah atau tindakan Fungsi
tailscale status Daftar perangkat dan keadaannya
tailscale ping &lt;nama&gt; Menguji jalur; menunjukkan direct atau via DERP
tailscale netcheck Memeriksa kualitas koneksi dan jarak ke server relay
tailscale version Versi terpasang
apt update && apt install -y --only-upgrade tailscale Memperbarui Tailscale di server Debian
Machines &gt; ... &gt; Delete Menghapus perangkat yang hilang atau tidak dipakai lagi
Machines &gt; ... &gt; Disable key expiry Hanya untuk perangkat server, bukan HP atau laptop
KEAMANAN
Bila HP atau laptop hilang: segera buka Machines dan Delete perangkat itu, lalu ganti password akun email dan
periksa verifikasi dua langkahnya. Tinjau daftar Machines sebulan sekali dan hapus yang tidak dikenal.

## 26.10 Checklist pengerasan Tailscale

Item Status yang diharapkan
Verifikasi dua langkah pada akun email Aktif
Subnet route hanya 192.168.88.0/24 Tidak ada rute lain yang disetujui
Exit node Tidak dipakai
Perangkat router memakai tag:router Ya, tanpa kedaluwarsa kunci
Kebijakan akses Bukan lagi "semua ke semua"
Tailscale di Proxmox host Tidak dipasang
Port forwarding di MikroTik Tidak ada
Daftar Machines Semua perangkat dikenali

## 26.11 Masalah dan solusi

Gejala Penyebab Solusi
192.168.88.x tidak terjangkau dari
HP
Rute belum disetujui; penerusan
paket mati; klien menonaktifkan
subnet
Setujui rute di konsol, sysctl net.ipv4.ip_forward
harus 1, cek Use Tailscale subnets di klien
Koneksi lambat dari luar Memakai relay (DERP) karena NAT
berlapis, atau upload IndiHome
terbatas
tailscale ping untuk melihat direct atau DERP;
tunggu beberapa menit untuk koneksi langsung;
kecepatan dibatasi upload rumah
Internet HP mati setelah DNS
global
AdGuard tidak terjangkau Matikan Override DNS servers atau tambah
nameserver cadangan (26.7C)
Pesan Key expired Kunci perangkat habis masa berlaku Login ulang; untuk server pakai tag:router agar
tidak kedaluwarsa
tailscale up ditolak karena opsi Opsi sebelumnya tidak disebut ulang Pakai tailscale set, atau sebutkan semua opsi
Tailscale gagal di LXC /dev/net/tun tidak tersedia Ikuti Edisi 2 Bab 13.8
Web Proxmox ditolak dari luar Sumber lalu lintas bukan LAN, atau
firewall Proxmox menolak
Cek pve-firewall localnet dan aturan Source
192.168.88.0/24 (Bab 25.5)
Tailscale tidak bisa menyala di HP VPN lain aktif Matikan VPN lain, hanya satu VPN pada satu
waktu
Layanan terbuka dari luar tanpa
Tailscale
Tidak ada port forwarding, jadi
seharusnya tidak mungkin
Periksa MikroTik: /ip firewall nat print dan
pastikan tidak ada dst-nat

## 26.12 Pindah ke STB 2 dan cara menghapus

Rencana lengkap pemindahan ada di Suplemen 6. Ringkasnya, saat STB 2 tiba: pasang Tailscale dengan
langkah 26.4 (hostname router-stb2), setujui rute, beri tag:router, uji, lalu kosongkan rute di VM Debian.

**TERMINAL VM DEBIAN** | Sebagai root

```
tailscale set --advertise-routes=
```
> Penjelasan: Mengosongkan rute yang diumumkan VM setelah STB 2 aktif.
Untuk menghapus Tailscale sepenuhnya dari sebuah server:

**TERMINAL VM DEBIAN** | Sebagai root

```
tailscale down
```
> Penjelasan: Memutus dari tailnet.
```
tailscale logout
```
> Penjelasan: Melepas perangkat dari akun.
```
apt purge -y tailscale
```
> Penjelasan: Menghapus paket.
```
rm /etc/sysctl.d/99-tailscale.conf
```
> Penjelasan: Menghapus pengaturan penerusan paket.
Lalu hapus perangkatnya dari halaman Machines bila masih tampil.


<!-- SOURCE: docs/bab/suplemen/bagian-1-99-penutup.md -->

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


<!-- SOURCE: docs/bab/suplemen/bagian-2-00-pengantar.md -->

# Bagian 2. Proxmox di Mesin Asli (ThinkCentre M710q) (pengantar)

Bagian ini memasang Proxmox VE di **Lenovo ThinkCentre M710q**. Model A (VMware) dan Model C (instal ke disk dulu) pada Edisi 3 sudah dihapus pada Revisi 3.

| Bab | Isi | Hasil akhir |
|---|---|---|
| 27. Mesin M710q | Spesifikasi aktual, RAM yang dilaporkan 16+8 GB (24 GB), NVMe terpasang, BIOS | Mesin siap diinstal setelah RAM/disk diverifikasi dan MemTest lulus |
| 28. Instal langsung | Unduh dan verifikasi ISO, USB bootable, boot, layar installer, masalah umum | Proxmox hidup di 192.168.88.10:8006 |
| 29. (dihapus) | Penanda | - |
| 30. Pasca-instalasi | BIOS, sensor, SMART, Wake-on-LAN, pemulihan backup, keamanan | Server stabil, bisa dinyalakan dari STB |

Urutan: Bab 27, Bab 6 (USB), Bab 8 dan 28 (instalasi), Bab 9 (konfigurasi awal), Bab 30. Lalu ulangi Bab 25 dan 26 di mesin ini.

**PERINGATAN.** Instalasi Proxmox menghapus seluruh isi disk yang dipilih. Salin dulu data penting dari NVMe (bila ada isinya) dan lepaskan HDD 2 TB berisi data selama instalasi.

| Alamat | Perangkat |
|---|---|
| 192.168.88.1 | MikroTik RB750GL |
| 192.168.88.10 | Proxmox (ThinkCentre M710q) |
| 192.168.88.20 | VM Debian 13 (docker-core) |
| 192.168.88.253 | STB HG680 (AdGuard); juga pengirim Wake-on-LAN (Bab 30.5) |


<!-- SOURCE: docs/bab/suplemen/27-mesin-m710q.md -->

# Bab 27. Mesin Anda: Lenovo ThinkCentre M710q

PENEMPATAN - HOST FISIK. Template Debian 13 VM 200 dan CT 100 sudah ada; belum ada guest layanan yang dilaporkan. Bab ini fokus pada perangkat keras M710q.

Mesin server Anda adalah **Lenovo ThinkCentre M710q (Tiny)**. Bab ini mencatat spesifikasi, rencana RAM dan disk, dan pengaturan BIOS-nya. Menu BIOS bisa berbeda antar versi; nama di bawah adalah patokan, cocokkan dengan layar Anda.

## 27.1 Spesifikasi dan kebutuhan

| Komponen | Kebutuhan | M710q Anda | Status |
|---|---|---|---|
| CPU | 64-bit dengan VT-x/AMD-V, 4 core disarankan | Core i5-6500T, 4 core / 4 thread | VT-x/KVM aktif setelah perbaikan; VT-d Disabled |
| RAM | 16 GB atau lebih | 16 GB + 8 GB (24 GB fisik) | Linux melaporkan 23 GiB; BIOS/MemTest86 belum diperiksa |
| Disk sistem | SSD 120 GB atau lebih | NVMe Samsung MZALQ512HALU-000L2 | Proxmox berjalan; terdeteksi sebesar 476,9 GB |
| Disk data / backup | HDD/SSD terpisah | 2 × HDD Seagate Surveillance 2 TB, 3,5 inci | Belum tersambung; enclosure single-bay lama ditemukan tetapi belum diuji; HDD kedua ditunda |
| Jaringan | 1 port LAN kabel | 1 Gigabit Ethernet (Intel) | Lulus |

Spesifikasi di atas adalah patokan umum model M710q; **cek label RAM, tipe slot, dan ketebalan disk pada unit Anda sendiri** sebelum membeli atau memasang.

### Rencana RAM

| Pilihan | Total | Catatan |
|---|---|---|
| 16 GB | 16 GB | Profil konservatif Bab 56 |
| **16 GB + 8 GB (konfigurasi saat ini)** | **24 GB** | Diharapkan terpasang; periksa BIOS dan uji MemTest86. Gunakan profil konservatif sambil memantau beban. |
| 16 GB + 16 GB | 32 GB | Opsi peningkatan di masa depan; tetap ukur beban nyata, jangan anggap semua VM aman menyala bersamaan. |

RAM sudah dilaporkan diganti: modul pertama 8 GB diganti dengan 16 GB, sementara modul 8 GB lainnya tetap terpasang. Jadi total fisiknya 24 GB; Proxmox melaporkan 23 GiB yang dapat digunakan. BIOS dan MemTest86 belum diperiksa. Jalankan **MemTest86 dari USB sampai 1-2 putaran penuh tanpa error** sebelum menaruh beban kerja penting; RAM bermasalah dapat merusak VM secara diam-diam.

## 27.2 Memeriksa spesifikasi dari Windows

Selagi M710q masih menjalankan Windows, buka PowerShell di komputer itu dan jalankan perintah
berikut. Catat hasilnya; ini akan dipakai untuk memilih disk dan ukuran VM.

**POWERSHELL WINDOWS** | PowerShell di M710q

```powershell
Get-CimInstance Win32_Processor | Select-Object Name, NumberOfCores, NumberOfLogicalProcessors, VirtualizationFirmwareEnabled
```
> Penjelasan: Menampilkan CPU, jumlah core, dan apakah virtualisasi sudah aktif di BIOS (True atau False).
```
Get-CimInstance Win32_PhysicalMemory | Select Capacity,Speed,Manufacturer
```
> Penjelasan: Menampilkan setiap keping RAM. Jumlahkan kapasitasnya (satuan byte; 8589934592 = 8 GB).
```
Get-PhysicalDisk | Select FriendlyName,MediaType,Size,HealthStatus
```
> Penjelasan: Menampilkan disk, jenis (SSD atau HDD), ukuran, dan status kesehatan dasar.
```
Get-NetAdapter | Select Name,InterfaceDescription,LinkSpeed
```
> Penjelasan: Menampilkan kartu jaringan. Catat merek chipset (Intel, Realtek) dan kecepatan (1 Gbps).
TIPS
Jika VirtualizationFirmwareEnabled bernilai False, bukan berarti CPU tidak mampu; biasanya hanya belum dinyalakan
di BIOS (Bab 27.5). Cek juga merek dan model CPU di internet untuk memastikan ada VT-x atau AMD-V.

## 27.3 Memeriksa kesehatan komputer

M710q bisa menyimpan masalah tersembunyi. Dua jam pemeriksaan sekarang menghemat berhari-hari
kemudian.
Yang diperiksa Alat Lulus jika Bila gagal
Kesehatan disk CrystalDiskInfo (gratis,
Windows)
Status "Baik"; tidak ada Reallocated
atau Pending sector; SSD sisa umur
masih tinggi
Ganti disk. Disk rusak adalah
penyebab kehilangan data
nomor satu
RAM MemTest86 dari USB, 1
sampai 2 putaran penuh
Nol error Cabut keping bergantian, ganti
yang rusak
Suhu dan kipas HWiNFO atau cek manual Suhu diam di bawah 60 derajat,
kipas berputar dan tidak berisik
berlebihan
Bersihkan debu, ganti pasta
termal
Port LAN Colok kabel ke MikroTik Lampu LAN menyala dan IP didapat Pakai adaptor USB-LAN
sebagai cadangan (kurang
ideal)
Baterai laptop Lihat fisik Tidak menggembung Lepas baterai, pakai tanpa
baterai
Tombol power dan
layar
Coba nyalakan Berfungsi Layar rusak tidak masalah bila
HDMI jalan


## 27.4 Memutuskan disk dan sistem berkas

| Disk | Peran | Sistem berkas | Catatan |
|---|---|---|---|
| NVMe Samsung MZALQ512HALU-000L2 (476,9 GB) | Sistem Proxmox + disk VM (local-lvm) | ext4 | Proxmox sudah berjalan; `local` dan `local-lvm` aktif |
| HDD Seagate Surveillance 2 TB (unit 1) | Calon disk data / datastore PBS | Belum dipilih | Belum tersambung; enclosure lama ditemukan tetapi belum diuji. Identifikasi model/kondisi sebelum dipakai |
| HDD Seagate Surveillance 2 TB (unit 2) | Ditunda | — | Enclosure yang tersedia hanya single-bay; peran unit ini belum ditentukan |

**Anggaran ruang NVMe 500 GB.** Disk VM dibuat tipis (thin), jadi ruang terpakai mengikuti isi, bukan ukuran yang diminta. Tetap hitung: sekitar 10-15 VM dengan sistem 4-8 GB aktual, ditambah image Docker dan data aplikasi. Contoh di bab layanan memakai disk data besar (musik 200 GiB di Bab 53, foto 300 GiB di Bab 55, datastore PBS 200 GiB di Bab 50). **Jangan menaruh semuanya di NVMe.** Saran:

| Data | Tempat | Ukuran awal |
|---|---|---|
| Sistem VM / container | NVMe (local-lvm) | sesuai bab |
| Foto Immich (disk kedua VM 214) | NVMe, ukuran dikecilkan (contoh 150 GiB) lalu diperbesar bila perlu | 150 GiB |
| Pustaka musik (VM 211) | NVMe atau HDD, 80-100 GiB | 80 GiB |
| Datastore PBS (VM 212) | **HDD 2 TB** | 1-1,5 TB |

**Menghubungkan HDD pertama.** Anda memiliki dua HDD Seagate Surveillance 2 TB berukuran 3,5 inci; keduanya dinyatakan aman. Satu HDD belum diformat sehingga sebelumnya tidak muncul di Windows. M710q Tiny hanya menyediakan satu bay SATA 2,5", jadi HDD 3,5 inci akan dipakai melalui koneksi luar. Enclosure yang tersedia single-bay dan belum diuji; rencana sementara memakai satu HDD dahulu dan menunda yang kedua. Pastikan enclosure memiliki catu daya sendiri. Pilih peruntukan disk setelah model dan kondisi diverifikasi. Jangan mencabut disk saat backup berjalan. Catat model (dan serial secara lokal, jangan di repo) agar tidak salah pilih saat menyiapkan storage.

> Disk tunggal bukan backup. Backup VM ke HDD 2 TB (Bab 50), ditambah satu salinan lagi di media lain (Bab 50.13).

## 27.5 Pengaturan BIOS/UEFI lengkap (ThinkCentre)

Masuk BIOS: tekan **F1** berulang saat logo Lenovo muncul. Menu boot sekali pakai: **F12**. (Tombol Novo/Enter menu opsional pada beberapa varian.)

| Pengaturan | Nilai | Mengapa |
|---|---|---|
| Intel Virtualization Technology (VT-x) | Enabled | Wajib agar VM berjalan dengan akselerasi KVM |
| Intel VT-d | Opsional; saat ini Disabled | Hanya diperlukan untuk kebutuhan passthrough perangkat PCI tertentu |
| SATA Controller Mode | AHCI | Agar disk 2,5" terbaca; NVMe tidak terpengaruh |
| Boot Mode | UEFI (CSM/Legacy dimatikan) | Instalasi bersih dan boot stabil |
| Secure Boot | Disabled | Mengurangi masalah saat instalasi |
| After Power Loss (Power) | Power On | Menyala sendiri setelah listrik padam dan kembali |
| Wake on LAN | Automatic / Enabled | Agar bisa dinyalakan dari STB (Bab 30.5) |
| Enhanced Power Saving Mode / ErP | Disabled | Mode hemat daya ini memutus daya kartu LAN dan membuat Wake-on-LAN gagal |
| Fast Boot | Disabled | Menghindari USB terlewat saat instalasi |
| Startup Sequence | USB di atas NVMe saat instalasi, lalu NVMe | Setelah instalasi, NVMe di urutan pertama |
| Supervisor password | Isi (opsional) | Mencegah perubahan BIOS oleh orang lain; simpan di Vaultwarden |

Nama menu persis berbeda antar versi BIOS (mis. "Power > Automatic Power On" untuk Wake on LAN dan After Power Loss). Bila ragu, cari kata kunci "Virtualization", "Wake", dan "Power Loss". Memperbarui BIOS lewat situs dukungan Lenovo disarankan sebelum instalasi.

### BIOS Lenovo tanpa layar: gunakan thinklmi hanya bila tersedia

Kasus nyata pada M710q (31 Oktober 2026): VM gagal dinyalakan karena VT-x mati, dan pengguna tidak memiliki monitor untuk masuk BIOS. Host memiliki `/sys/class/firmware-attributes/thinklmi`, sehingga nilai Intel Virtualization Technology bisa diaktifkan lewat antarmuka firmware Linux. Dukungan ini bergantung pada model, BIOS, kernel, dan driver; jangan menganggap folder `thinklmi` tersedia pada setiap mesin.

> **Peringatan:** perubahan firmware berisiko membuat mesin tidak dapat boot. Gunakan hanya jika benar-benar perlu dan siapkan akses lokal/pemulihan. Jangan ubah atribut selain VT-x. Jangan mengirim password BIOS ke chat. Jika folder/atribut tidak ada, jangan membuatnya; gunakan monitor dan F1 atau dokumentasi Lenovo.

**TERMINAL HOST PROXMOX** | Shell host, sebagai root

```
ls /sys/class/firmware-attributes/
```
> Penjelasan: Pastikan keluaran memuat `thinklmi`. Jika tidak ada, berhenti dan gunakan cara BIOS biasa.

```
ls "/sys/class/firmware-attributes/thinklmi/attributes"
```
> Penjelasan: Cari nama atribut virtualization yang memang ada pada mesin. Jangan menyalin nama dari model lain bila tidak cocok.

```
cat "/sys/class/firmware-attributes/thinklmi/attributes/Intel(R) Virtualization Technology/current_value"
cat "/sys/class/firmware-attributes/thinklmi/attributes/Intel(R) Virtualization Technology/possible_values"
```
> Penjelasan: Pastikan atribut yang dipilih adalah Intel Virtualization Technology dan `Enabled` tercantum sebagai nilai yang diizinkan. Pada unit yang diuji, nilai awal `Disabled` dan pilihan `Disabled;Enabled`.

```
echo "Enabled" > "/sys/class/firmware-attributes/thinklmi/attributes/Intel(R) Virtualization Technology/current_value"
```
> Penjelasan: Mengubah hanya VT-x ke Enabled. Pada unit pengguna, perubahan bertahan setelah reboot; kebutuhan menulis `save_settings` belum dipastikan dan bukan bagian langkah ini.

```
reboot
```
> Penjelasan: Nyalakan ulang agar firmware menerapkan perubahan. Pastikan akses web/SSH tersedia kembali.

```
lscpu | grep -i virtualization
ls -l /dev/kvm
```
> Penjelasan: Hasil pada unit yang diuji adalah `Virtualization: VT-x` dan perangkat `/dev/kvm` tersedia. Jika tidak, jangan mulai membuat VM; cek BIOS/firmware secara lokal.

Intel VT-d boleh tetap `Disabled` sampai benar-benar ada kebutuhan passthrough PCI; VT-x diperlukan untuk akselerasi VM KVM.


<!-- SOURCE: docs/bab/suplemen/28-instal-langsung-m710q.md -->

# Bab 28. Instal Langsung di Lenovo ThinkCentre M710q

> **Pembaruan 31 Oktober 2026.** Bab ini adalah panduan instalasi langsung di **Lenovo ThinkCentre M710q**. SSD NVMe M.2 500 GB sudah terpasang di slot 1. RAM dilaporkan 16+8 GB (24 GB total), tetapi harus dikonfirmasi di BIOS dan lulus MemTest86 **sebelum** menginstal. Periksa isi/partisi NVMe dan cadangkan data penting sebelum memilih disk target. Kartu jaringan Intel biasanya bernama `enp0s31f6` (periksa dengan `ip -br link`); BIOS F1, menu boot F12.

PENEMPATAN - HOST - mesin fisik
Tempat: Langsung di ThinkCentre M710q (host Proxmox), bukan di dalam VM.
Aturan: Host hanya menjalankan Proxmox. Jangan memasang Docker atau aplikasi di host; semua aplikasi masuk
ke guest menurut Peta Penempatan (Suplemen 7 Bab 48).
Ini cara standar dan paling disarankan untuk ThinkCentre M710q Anda: Proxmox dipasang langsung ke disk
komputer itu. Bab ini memperluas Edisi 2 Bab 6 dengan langkah rinci, pilihan di installer, dan penanganan
masalah.

## 28.1 Gambaran alur dan waktu

Langkah Perkiraan waktu
Cadangkan data dan periksa komputer (Bab 27) 30 sampai 120 menit
Unduh dan verifikasi ISO 10 sampai 30 menit
Membuat USB bootable 10 menit
Mengatur BIOS dan boot dari USB 10 menit
Instalasi di layar 10 sampai 15 menit
Boot pertama, pemeriksaan, update 20 menit

## 28.2 Siapkan data ini sebelum mulai

Data Nilai Catatan
Alamat IP (CIDR) 192.168.88.10/24 Di luar rentang DHCP MikroTik (.100 sampai .254)
Gateway 192.168.88.1 MikroTik
DNS 192.168.88.253 AdGuard di STB; bila belum siap, 1.1.1.1
Hostname (FQDN) pve.lab.local Harus berformat nama.domain
Password root Kuat dan panjang Simpan di tempat aman; lupa berarti harus mode
rescue
Email administrator Email aktif Dipakai untuk notifikasi sistem
Kabel LAN Dari komputer ke MikroTik Wajib terhubung saat instalasi agar IP bisa diuji

## 28.3 Mengunduh dan memverifikasi ISO

1. Di laptop, buka proxmox.com/en/downloads dan unduh Proxmox VE ISO Installer versi 9 terbaru. Edisi 2
memakai proxmox-ve_9.2-1.iso; versi yang lebih baru juga boleh.
2. Di halaman yang sama catat nilai SHA256 milik berkas itu.

**POWERSHELL WINDOWS** | PowerShell (laptop)

```
Get-FileHash -Algorithm SHA256 $env:USERPROFILE\Downloads\proxmox-ve_9.2-1.iso
```
> Penjelasan: Menghitung sidik jari berkas. Ganti nama berkas sesuai unduhan Anda. Nilai Hash harus sama persis
dengan SHA256 di situs. Jika beda, unduh ulang; berkas rusak atau tidak asli.

## 28.4 Membuat USB bootable

Siapkan flashdisk minimal 8 GB. Semua isinya akan terhapus. ISO Proxmox adalah image hibrida, jadi cara
menulisnya harus mode image mentah.
Cara 1: Rufus (disarankan di Windows)
1. Unduh Rufus dari rufus.ie dan jalankan.
2. Pada Device, pilih flashdisk yang benar (periksa nama dan ukurannya; jangan memilih HDD).
3. Klik SELECT dan pilih berkas ISO Proxmox.
4. Partition scheme: GPT untuk komputer UEFI (MBR hanya untuk BIOS lama). Target system akan
menyesuaikan.
5. Klik START. Saat muncul pertanyaan mode penulisan, pilih Write in DD Image mode lalu OK. Dokumentasi
Proxmox menyebut mode DD wajib agar Rufus berfungsi.
6. Tunggu status READY, lalu cabut flashdisk dengan aman.
Cara 2: balenaEtcher
1. Pilih Flash from file dan pilih ISO.
2. Pilih Select target dan pilih flashdisk.
3. Klik Flash! dan tunggu selesai.
CATATAN
Ventoy praktis untuk banyak ISO tetapi pada sebagian komputer installer Proxmox bermasalah lewat Ventoy. Bila
instalasi aneh, ulangi dengan Rufus (mode DD) atau Etcher.

## 28.5 Boot dari USB

1. Colokkan flashdisk dan kabel LAN ke ThinkCentre M710q, lalu nyalakan sambil menekan tombol menu boot
berulang kali (tabel Bab 27.5).
2. Pilih flashdisk. Pilih entri yang berawalan UEFI: bila ada.
3. Menu Proxmox muncul. Pilih Install Proxmox VE (Graphical) dan tekan Enter.
4. Bila layar hitam, berkedip, atau rusak, restart dan pilih Install Proxmox VE (Terminal UI); urutan layarnya
sama.
TIPS
Menu juga memuat Advanced Options (mode debug dan Rescue Boot). Rescue Boot dipakai bila sistem terpasang
tetapi gagal boot (Bab 29.5).

## 28.6 Layar demi layar di mesin asli

Tampilan lengkap tiap layar ada di Edisi 2 Bab 8. Di bawah ini hal yang khusus untuk instalasi di mesin asli.
Layar Isi yang dipilih Perhatian di mesin asli
1. Lisensi Klik I agree -
2. Target Harddisk Pilih SSD NVMe 500 GB (nvme0n1). Klik Options untuk sistem berkas Periksa merek dan ukuran dengan teliti; disk ini
akan dihapus seluruhnya. Disk lain jangan
dipilih
3. Lokasi dan zona
waktu
Indonesia, Asia/Jakarta, keyboard US Zona waktu salah membuat jam dan 2FA
meleset
4. Password dan email Password root kuat, email aktif Simpan password di password manager
Layar Isi yang dipilih Perhatian di mesin asli
5. Jaringan manajemen Interface yang terhubung kabel, hostname
pve.lab.local, IP 192.168.88.10/24, gateway
192.168.88.1, DNS 192.168.88.253
Pilih interface yang statusnya terhubung; salah
pilih berarti web tidak bisa dibuka
6. Ringkasan Periksa semua isian, centang reboot otomatis Cabut USB saat mesin restart pertama
Opsi disk di layar 2 (tombol Options)
Opsi Arti Disarankan
Filesystem ext4, XFS, BTRFS (pratinjau), ZFS ext4 untuk satu SSD (Bab 27.4)
hdsize Ukuran disk yang dipakai installer Biarkan penuh, kecuali ingin menyisakan
ruang di disk
swapsize Ukuran swap Biarkan bawaan
maxroot Ukuran maksimum partisi sistem Biarkan bawaan
minfree Ruang kosong yang disisakan di grup volume Biarkan bawaan
maxvz Ukuran partisi data VM (local-lvm) Biarkan bawaan
PERINGATAN
Pada layar 2, jika ada beberapa disk (misalnya SSD dan HDD 2 TB), pilih hanya SSD. Sebaiknya lepaskan HDD
berisi data penting dari komputer selama instalasi untuk menghilangkan risiko salah pilih.

## 28.7 Boot pertama dan pemeriksaan

1. Saat mesin restart, cabut USB. Mesin boot ke Proxmox dan layar menampilkan alamat
https://192.168.88.10:8006.
2. Dari laptop yang terhubung ke jaringan MikroTik, buka alamat itu. Peringatan sertifikat itu normal; lanjutkan,
login root, Realm Linux PAM standard authentication.

**TERMINAL PROXMOX** | Konsol ThinkCentre M710q atau Shell web (root)

```
pveversion
```
> Penjelasan: Menampilkan versi Proxmox yang terpasang.
```
ip -br a
```
> Penjelasan: Memeriksa alamat. Pada vmbr0 harus ada 192.168.88.10/24.
```
lscpu | grep -E "Model name|Virtualization"
```
> Penjelasan: Memastikan VT-x atau AMD-V aktif (baris Virtualization tidak kosong).
```
lsblk -o NAME,SIZE,TYPE,MODEL
```
> Penjelasan: Daftar disk. Pastikan disk yang diharapkan terlihat, termasuk HDD data.
```
free -h
```
> Penjelasan: Memeriksa jumlah RAM yang terbaca.
```
ping -c 3 192.168.88.1
```
> Penjelasan: Menguji koneksi ke MikroTik.
Lanjutkan ke Edisi 2 Bab 9.2 sampai 9.6 (mencatat di MikroTik, DNS, repository no-subscription, update), lalu Bab
30 di suplemen ini.

## 28.8 Masalah umum dan solusi

Gejala Penyebab Solusi
Installer menyatakan tidak ada
disk (no hard disk found)
Mode SATA berupa RAID atau Intel
RST/VMD
Ubah SATA Mode ke AHCI di BIOS (Bab 27.5)
Flashdisk tidak muncul di menu
boot
Penulisan salah, Secure Boot, atau
mode boot tidak cocok
Tulis ulang dengan Rufus (DD), nonaktifkan
Secure Boot, pilih entri UEFI:
Layar hitam atau rusak saat
installer
Masalah driver grafis installer Pilih Install Proxmox VE (Terminal UI)
Tidak ada interface jaringan di
layar 5
Kartu LAN tidak dikenali kernel atau
kabel tidak terpasang
Pastikan kabel terpasang; ganti ke adaptor
USB-LAN sementara; cari dukungan chipset
(sebagian Realtek 2.5G butuh driver tambahan)
Web tidak terbuka setelah
instalasi
IP, gateway, atau interface salah Ikuti Edisi 2 Bab 9.3: periksa
/etc/network/interfaces dan /etc/hosts
Mesin kembali ke installer terus USB belum dicabut Cabut USB dan restart
Tidak mau boot tanpa keyboard BIOS menahan karena error keyboard Matikan Halt on keyboard error di BIOS


<!-- SOURCE: docs/bab/suplemen/30-pasca-instalasi-wol.md -->

# Bab 30. Pasca-Instalasi di Mesin Asli, Wake-on-LAN, dan Memindahkan Isi Lab

PENEMPATAN - HOST. Tempat: pengaturan setelah instalasi dilakukan di host Proxmox (ThinkCentre M710q). Aplikasi tetap di guest.

## 30.1 Urutan kerja

| Urutan | Tindakan | Rujukan |
|---|---|---|
| 1 | Pasang RAM tambahan, uji MemTest86 | Bab 27.1 |
| 2 | Atur BIOS | Bab 27.5 |
| 3 | Instal Proxmox dari USB | Bab 6, 8, 28 |
| 4 | Pengaturan awal: DNS, repository no-subscription, update | Bab 9.4 sampai 9.6 |
| 5 | Sensor suhu dan kesehatan disk | Bab 30.4 |
| 6 | Wake-on-LAN dari STB | Bab 30.5 |
| 7 | Pasang HDD 2 TB sebagai disk data/backup | Bab 27.4 |
| 8 | Keamanan (akun admin, 2FA, SSH kunci, firewall) dan Tailscale | Bab 25 dan 26 |
| 9 | Templat VM 200 dan layanan | Bab 49 dan seterusnya |
| 10 | PBS dan backup terjadwal, uji pulih | Bab 50 |

## 30.2 Pengaturan dasar mesin asli

Kerjakan Bab 9.4 sampai 9.8 (DNS, repository, update, antarmuka, kebiasaan baik) seperti biasa.

## 30.3 Penempatan fisik, kipas, dan suhu

M710q adalah PC kecil tanpa baterai dan tanpa layar, jadi tidak ada pengaturan "tutup layar". Yang perlu diperhatikan:

- Letakkan di tempat berventilasi, jauhkan dari tumpukan barang; jangan ditutup. Boleh berdiri atau rebah sesuai dudukan.
- Pantau suhu CPU dan NVMe (Bab 30.4). Sebagai pedoman, di atas 80 derajat berarti perlu pembersihan debu atau perbaikan aliran udara.
- Pakai catu daya bawaan (adaptor eksternal) dan colokkan ke stabilizer/UPS kecil bila ada (monitor listrik ada di daftar rencana).
- Beri label di mesin: nama, IP 192.168.88.10, dan MAC kartu LAN.

## 30.4 Sensor suhu dan kesehatan disk

**TERMINAL PROXMOX** | Shell Proxmox (root)

```
apt install -y lm-sensors
```
> Penjelasan: Memasang pembaca sensor suhu dan kipas.
```
sensors-detect --auto
```
> Penjelasan: Mendeteksi sensor yang tersedia dan menerima pilihan bawaan.
```
sensors
```
> Penjelasan: Menampilkan suhu CPU dan kipas. Catat suhu saat diam; sebagai pedoman, di atas 80 derajat berarti
perlu pembersihan atau pendinginan.
```
smartctl -H /dev/sda
```
> Penjelasan: Memeriksa kesehatan SSD atau HDD. Hasil yang diharapkan: PASSED. Untuk NVMe pakai
/dev/nvme0.
```
smartctl -a /dev/sda | head -40
```
> Penjelasan: Melihat detail SMART, termasuk jam pemakaian dan sektor bermasalah.
CATATAN
smartmontools biasanya sudah terpasang di Proxmox; jika perintah tidak dikenali, jalankan apt install -y
smartmontools. Data suhu inilah yang nanti dibaca oleh Beszel atau Prometheus di suplemen monitoring (suhu tidak
terbaca di VM).

## 30.5 Wake-on-LAN: menyalakan Proxmox dari STB

Wake-on-LAN (WoL) menyalakan komputer yang mati dengan mengirim paket khusus (magic packet) ke kartu
LAN-nya. STB yang selalu hidup bisa menjadi pengirimnya. Paket WoL berupa broadcast, jadi pengirim harus
berada di LAN yang sama; dari luar rumah, Anda masuk ke STB lewat Tailscale lalu menjalankan perintahnya di
STB.
CATATAN
WoL tidak sama dengan menyala otomatis setelah listrik padam. Itu pengaturan BIOS Restore on AC Power Loss
(Bab 27.5). Keduanya sebaiknya aktif.
A. Di BIOS ThinkCentre M710q
Aktifkan Wake on LAN atau Power On by PCI-E, dan nonaktifkan ErP/Deep Sleep (Bab 27.5). Pada laptop,
WoL hanya bekerja lewat kabel LAN, tidak lewat WiFi, dan sebagian laptop tidak mendukungnya saat mati total.
B. Di Proxmox: mengaktifkan WoL pada kartu LAN

**TERMINAL PROXMOX** | Shell Proxmox (root)

```
apt install -y ethtool
```
> Penjelasan: Memasang alat pengatur kartu jaringan.
```
ip -br link
```
> Penjelasan: Mencari nama kartu LAN (contoh enp0s31f6). Catat juga alamat MAC-nya
(AA:BB:CC:DD:EE:FF), dibutuhkan nanti.
```
ethtool enp0s31f6 | grep -i wake
```
> Penjelasan: Ganti enp0s31f6 dengan nama kartu Anda. "Supports Wake-on" harus memuat huruf g, dan "Wake-on: d"
berarti masih mati.
```
ethtool -s enp0s31f6 wol g
```
> Penjelasan: Menyalakan WoL sekarang (tidak permanen sampai reboot).
```
nano /etc/network/interfaces
```
> Penjelasan: Menambahkan baris agar WoL aktif setiap kali menyala. Edit blok kartu fisik seperti kotak di bawah.

**/etc/network/interfaces (bagian kartu fisik)** | Ganti enp0s31f6 sesuai nama kartu

```
iface enp0s31f6 inet manual
 post-up /usr/sbin/ethtool -s enp0s31f6 wol g
```

**TERMINAL PROXMOX** | Shell Proxmox (root)

```
ifreload -a
```
> Penjelasan: Menerapkan konfigurasi.
```
ethtool enp0s31f6 | grep "Wake-on"
```
> Penjelasan: Harus menampilkan "Wake-on: g".
C. Di STB: mengirim magic packet

**TERMINAL STB** | SSH ke 192.168.88.253 (root)

```
apt update && apt install -y wakeonlan
```
> Penjelasan: Memasang pengirim magic packet.
```
nano /usr/local/bin/nyalakan-proxmox
```
> Penjelasan: Membuat skrip singkat. Isi seperti kotak di bawah; ganti MAC dengan milik Proxmox.

**/usr/local/bin/nyalakan-proxmox** | Isi berkas

```
#!/bin/sh
wakeonlan AA:BB:CC:DD:EE:FF
```

**TERMINAL STB** | SSH ke 192.168.88.253 (root)

```
chmod +x /usr/local/bin/nyalakan-proxmox
```
> Penjelasan: Membuat skrip dapat dijalankan.
D. Uji
1. Di web Proxmox pilih node, klik Shutdown. Tunggu sampai komputer benar-benar mati (lampu mati; LED
LAN biasanya tetap redup).
2. Di STB jalankan nyalakan-proxmox.
3. Komputer harus menyala dalam beberapa detik dan web Proxmox terbuka lagi setelah satu sampai dua
menit.
KASUS NYATA
Gejala: WoL berhasil dari kondisi tidur tetapi gagal dari mati total. Penyebab: kartu LAN diputus dayanya (ErP atau
Deep Sleep aktif) atau driver mereset pengaturan saat mati. Solusi: nonaktifkan ErP/Deep Sleep di BIOS, pastikan
Wake-on: g setelah boot, dan ulangi uji. Bila tetap gagal, perangkat keras komputer itu mungkin tidak mendukung WoL
dari mati total.
KEAMANAN
Magic packet tidak memakai password dan hanya berlaku di LAN. Karena itu perintah penyalaan dijalankan dari STB
(akses SSH-nya sudah berkunci, Bab 25.7), bukan dengan membuka layanan WoL ke internet.
TIPS
Dari HP, aplikasi SSH seperti Termius (Android dan iPhone) bisa menjalankan nyalakan-proxmox lewat Tailscale ke
192.168.88.253. Nanti perintah ini dapat dipasang sebagai tombol di Home Assistant atau alur n8n.


## 30.6 Memulihkan backup setelah instal ulang

Bila Proxmox diinstal ulang (disk rusak atau upgrade besar), pulihkan VM dan container dari backup. Prosedur lengkap ada di Bab 23.5; bila memakai PBS, restore dari antarmuka Proxmox (Datacenter > Storage > pbs-home) seperti di Bab 50.12. **Kunci enkripsi backup** wajib ada, atau backup tidak bisa dipulihkan.

Setelah restore, MAC VM tetap sama sehingga reservasi IP di MikroTik (192.168.88.20 dan seterusnya) tetap berlaku.

## 30.7 Mengulang keamanan di mesin asli

Kerjakan Bab 25.3 sampai 25.5 (akun admin, 2FA, SSH kunci, firewall Proxmox), 25.6 untuk setiap VM, dan Bab 26 untuk Tailscale. Pengaturan akun, 2FA, dan firewall tersimpan di mesin, bukan di buku.

## 30.8 Checklist dan masalah umum

| No | Uji | Hasil yang diharapkan |
|---|---|---|
| 1 | Web Proxmox terbuka dari laptop | Login root berhasil |
| 2 | `lscpu` menunjukkan Virtualization | VT-x terdeteksi |
| 3 | `free -h` | 16 GB (atau 32 GB setelah RAM ditambah) terbaca |
| 4 | `sensors` menampilkan suhu | Suhu diam wajar |
| 5 | `smartctl -H /dev/nvme0` | PASSED |
| 6 | Wake-on-LAN dari STB | Mesin menyala setelah Shutdown |
| 7 | Mesin menyala sendiri setelah listrik padam | After Power Loss = Power On bekerja |
| 8 | HDD 2 TB terbaca di Node > Disks | Muncul dengan ukuran benar |


<!-- SOURCE: docs/bab/suplemen/bagian-2-99-penutup.md -->

# Bagian 2. Proxmox di Mesin Asli (ThinkCentre M710q): Lembar Pembaruan dan Syarat Lulus Fase 2

## Lembar pembaruan

| Bab sebelumnya | Perubahan | Rujukan |
|---|---|---|
| Edisi 2, Bab 4 | Hanya satu model: mesin asli | Bab 4 |
| Edisi 2, Bab 5 dan 7; Bab 29 | Dihapus (penanda singkat) | - |
| Edisi 2, Bab 6 | Khusus ThinkCentre M710q | Bab 6 |
| Edisi 2, Bab 9 | 9.10 (open-vm-tools) dihapus; snapshot dan disk data disesuaikan | Bab 9 |
| Edisi 2, Bab 23 | Dari "pindah ke mesin asli" menjadi "instal ulang dan restore" | Bab 23 |
| Bab 56 | Tambah 56.7 untuk RAM 32 GB | Bab 56.7 |

## Syarat lulus Fase 2

| No | Poin | Ya / Tidak |
|---|---|---|
| 1 | RAM yang terpasang dikenali BIOS dan lulus MemTest86 (24 GB dilaporkan; konfirmasi aktual) | |
| 2 | BIOS diatur (VT-x, VT-d, UEFI, Secure Boot mati, AHCI, WoL, After Power Loss) | |
| 3 | Proxmox terpasang di NVMe dan web terbuka di 192.168.88.10:8006 | |
| 4 | `sensors` dan `smartctl -H /dev/nvme0` menampilkan data | |
| 5 | HDD 2 TB terbaca sebagai disk data/backup | |
| 6 | Wake-on-LAN dari STB menyalakan mesin | |
| 7 | Bab 25 dan 26 (keamanan dan Tailscale) dikerjakan di mesin ini | |


<!-- SOURCE: docs/bab/suplemen/31-docker-compose-fondasi.md -->

# Bab 31. Fondasi Docker Compose yang Rapi dan Aman

PENEMPATAN - GABUNG - berlaku di setiap VM Docker
Tempat: Struktur /opt/stacks dan pola compose berlaku di setiap VM Docker. Jaringan Docker proxy hanya dibuat di
VM 201 docker-core (192.168.88.20).
Alasan: Jaringan Docker tidak melintasi VM. Layanan di VM lain dijangkau Caddy lewat alamat IP:port, bukan nama
container (Suplemen 7 Bab 48.3).
Semua aplikasi di suplemen berikutnya dipasang dengan cara yang sama. Bab singkat ini menetapkan cara itu
sekali, sehingga tiap bab aplikasi cukup menyebut isi berkasnya.

## 31.1 Struktur folder

Setiap aplikasi punya satu folder berisi berkas compose.yaml, berkas .env bila ada rahasia, dan folder data.
Seluruh folder inilah yang dicadangkan.

**Struktur** | Susunan folder di VM Debian

```
/opt/stacks/
 uptime-kuma/
 compose.yaml
 data/
 gotify/
 compose.yaml
 .env
 data/
 beszel/
 compose.yaml
 beszel_data/
```

## 31.2 Aturan yang dipakai di buku ini

Aturan Alasan
Satu folder per aplikasi di /opt/stacks Mudah dicari, dicadangkan, dan dihapus
restart: unless-stopped Aplikasi menyala kembali setelah reboot, tetapi tidak bila sengaja
dimatikan
Versi image: tag mayor bila ada (misalnya :2); latest
hanya untuk layanan monitoring ringan
Menghindari lompatan versi besar yang merusak; backup dulu
sebelum update
Rahasia (password) di berkas .env dengan izin 600 Tidak tercecer di compose.yaml yang mungkin dibagikan
Data di folder lokal (bind mount) bukan volume
tersembunyi
Folder bisa dilihat dan dicadangkan langsung
Port dicatat di tabel alokasi (31.3) Mencegah bentrok antar aplikasi

## 31.3 Alokasi port dan catatan firewall

Layanan Port host Alamat akses
Uptime Kuma 3001 http://192.168.88.20:3001
Gotify 8070 (di container 80) http://192.168.88.20:8070
Beszel hub 8090 http://192.168.88.20:8090
Beszel agent (mesin yang dipantau) 45876 (hanya bila hub yang
menghubungi agen)
Tidak dibuka bila memakai token universal
(Bab 33)
PERINGATAN - Docker dan UFW
Port yang dipublikasikan Docker (kolom port host di atas) melewati UFW (Suplemen 1 Bab 25.6) dan terbuka dari
seluruh LAN. Ini dapat diterima selama semua perangkat di LAN tepercaya dan tidak ada port forwarding. Nanti
reverse proxy (suplemen berikutnya) menjadi pintu tunggal.

## 31.4 Memeriksa Docker dan menyiapkan folder

**TERMINAL VM DEBIAN** | Sebagai root (setelah su -)

```
docker --version
```
> Penjelasan: Memastikan Docker terpasang.
```
docker compose version
```
> Penjelasan: Memastikan plugin Compose terpasang (perintahnya "docker compose", dengan spasi).
```
mkdir -p /opt/stacks
```
> Penjelasan: Membuat folder induk untuk semua aplikasi.
```
ss -tlnp | grep -E ":(3001|8070|8090)\b" || echo port-bebas
```
> Penjelasan: Memastikan port 3001, 8070, dan 8090 belum dipakai. Hasil port-bebas berarti aman.

## 31.5 Perintah rutin (tempel di catatan Anda)

Tujuan Perintah (dijalankan di folder aplikasi)
Menyalakan atau menerapkan perubahan docker compose up -d
Melihat status docker compose ps
Melihat log docker compose logs -f --tail=50
Memperbarui image docker compose pull && docker compose up -d
Mematikan tanpa menghapus data docker compose stop
Menghapus kontainer (data di folder tetap ada) docker compose down


<!-- SOURCE: docs/bab/suplemen/bagian-3-00-pengantar.md -->

# Bagian 3. Monitoring dan Notifikasi (pengantar)

Bagian 3. Monitoring dan Notifikasi
Asal: Suplemen 3. Bab 31-34.
Suplemen ini memasang tiga hal yang menjawab permintaan awal Anda: memantau uptime seluruh layanan,
memantau CPU, RAM, disk, dan suhu, dan mengirim peringatan ke HP. Dua alat utamanya ringan dan cocok
untuk pemula: Uptime Kuma (apakah layanan hidup) dan Beszel (seberapa sehat mesinnya), dengan Gotify
sebagai pengirim notifikasi.
Bab Isi Hasil akhir
31. Fondasi Docker
Compose
Struktur folder, aturan versi dan port, perintah rutin Cara seragam memasang semua aplikasi
berikutnya
32. Uptime Kuma dan
Gotify
Pasang, tambah monitor, notifikasi ke HP (Android,
iPhone)
Notifikasi di HP saat layanan mati atau
hidup kembali
33. Beszel Hub dan agen di VM, Proxmox, dan STB; suhu,
Docker, peringatan
Grafik CPU, RAM, disk, suhu, dengan
peringatan
34. Menyatukan dan
menguji
Alur peringatan, kartu dashboard, backup, uji
menyeluruh, batas monitoring
Sistem pemantau teruji dan tercadangkan
Prasyarat
• VM Debian 13 di 192.168.88.20 dengan Docker dan Docker Compose (Edisi 2 Bab 14).
• Disarankan: Suplemen 1 (keamanan dan Tailscale) dan Suplemen 2 (Proxmox di mesin asli) sudah dikerjakan.
Suhu CPU terbaca di mesin asli (ThinkCentre M710q).
• Bila UFW aktif di VM (Suplemen 1 Bab 25.6), ikuti catatan port di Bab 31.3.
• Satu akun Telegram bila ingin kanal notifikasi kedua (opsional, disarankan untuk iPhone).
CATATAN
Prometheus dan Grafana tidak dipasang di sini. Untuk kebutuhan Anda (CPU, RAM, disk, suhu, uptime) Beszel dan
Uptime Kuma sudah cukup, memakai RAM jauh lebih sedikit, dan lebih mudah dirawat pemula. Prometheus dan
Grafana tetap bisa ditambahkan belakangan bila butuh grafik yang sangat khusus.
PERINGATAN
Pemantau yang berjalan di mesin yang sama dengan yang dipantau ikut mati saat mesin itu mati. Pada tahap ini
semua dipasang di VM Debian; saat STB 2 atau mesin kedua tersedia, Uptime Kuma sebaiknya dipindah ke sana
(Bab 34.6).


<!-- SOURCE: docs/bab/suplemen/32-uptime-kuma-gotify.md -->

# Bab 32. Uptime Kuma dan Gotify

PENEMPATAN - GABUNG - ke docker-core
Tempat: Uptime Kuma dan Gotify di VM 201 docker-core (192.168.88.20).
Alasan: Keduanya ringan, saling bergantung, dan harus bisa menjangkau semua guest. Gotify juga menerima
peringatan dari Proxmox dan PBS (Bab 50).
Port: Gotify memakai port 8070 di VM ini; guest lain mengaksesnya lewat 192.168.88.20:8070 (dibuka firewall, Bab
51).
Gotify adalah server notifikasi pribadi: aplikasi lain mengirim pesan ke Gotify, dan aplikasi Gotify di HP
menampilkannya. Uptime Kuma mengecek layanan secara berkala dan mengirim pesan lewat Gotify (dan
Telegram) saat sesuatu mati atau hidup kembali.

## 32.1 Memasang Gotify

**TERMINAL VM DEBIAN** | Sebagai root

```
mkdir -p /opt/stacks/gotify/data && cd /opt/stacks/gotify
```
> Penjelasan: Membuat folder aplikasi dan pindah ke dalamnya.
```
nano compose.yaml
```
> Penjelasan: Membuat berkas Compose. Isi seperti kotak pertama di bawah.

**/opt/stacks/gotify/compose.yaml** | Isi berkas

```
services:
  gotify:
    image: gotify/server:latest
    container_name: gotify
    restart: unless-stopped
    ports:
      - "8070:80"
    environment:
      - TZ=Asia/Jakarta
      - GOTIFY_DEFAULTUSER_NAME=admin
      - GOTIFY_DEFAULTUSER_PASS=${GOTIFY_ADMIN_PASS}
    volumes:
      - ./data:/app/data
```

**TERMINAL VM DEBIAN** | Sebagai root di /opt/stacks/gotify

```
nano .env
```
> Penjelasan: Membuat berkas rahasia. Isi satu baris seperti kotak di bawah; ganti dengan password kuat Anda
sendiri.

**/opt/stacks/gotify/.env** | Isi berkas

```
GOTIFY_ADMIN_PASS=GANTI-DENGAN-PASSWORD-KUAT
```

**TERMINAL VM DEBIAN** | Sebagai root di /opt/stacks/gotify

```
chmod 600 .env
```
> Penjelasan: Hanya root yang boleh membaca berkas rahasia.
```
docker compose up -d
```
> Penjelasan: Mengunduh image dan menyalakan Gotify di latar belakang.
```
docker compose ps
```
> Penjelasan: Status harus running (Up).
1. Buka http://192.168.88.20:8070 dari laptop. Login: admin dan password dari berkas .env.
2. Buka Users, ubah password admin bila perlu, dan simpan di password manager.
3. Buka Apps &gt; Create Application, nama Uptime Kuma. Salin token-nya (kode panjang); dipakai di 32.4.
4. Ulangi: buat aplikasi kedua bernama Beszel dan salin tokennya (dipakai di Bab 33).
Aplikasi Gotify di HP
Android (HP Anda)
1. Pasang aplikasi Gotify dari Google Play Store atau F-Droid.
2. Buka aplikasi, isi Server URL: http://192.168.88.20:8070, lalu login dengan akun admin.
3. Alamat ini hanya terjangkau bila HP di WiFi rumah atau Tailscale aktif (Suplemen 1 Bab 26). Pastikan VPN
selalu aktif di pengaturan Android.
4. Buka Pengaturan &gt; Aplikasi &gt; Gotify &gt; Baterai dan pilih Tidak dibatasi. Gotify menjaga koneksi
terus-menerus; tanpa ini Android bisa mematikannya.
5. Biarkan notifikasi "Gotify foreground service" tampil. Itu penanda aplikasi sedang menerima.
6. Uji: di web Gotify klik Push Message pada sebuah aplikasi, kirim pesan, dan pastikan muncul di HP.
iPhone
Gotify tidak memiliki aplikasi resmi di App Store (periksa lagi saat Anda memasang). Untuk iPhone pakai
Telegram sebagai kanal utama (32.4B), atau aplikasi pihak ketiga yang kompatibel dengan Gotify bila Anda
menemukannya.

## 32.2 Memasang Uptime Kuma

**TERMINAL VM DEBIAN** | Sebagai root

```
mkdir -p /opt/stacks/uptime-kuma/data && cd /opt/stacks/uptime-kuma
```
> Penjelasan: Membuat folder aplikasi.
```
nano compose.yaml
```
> Penjelasan: Membuat berkas Compose. Isi seperti kotak di bawah.

**/opt/stacks/uptime-kuma/compose.yaml** | Isi berkas

```
services:
  uptime-kuma:
    image: louislam/uptime-kuma:2
    container_name: uptime-kuma
    restart: unless-stopped
    ports:
      - "3001:3001"
    volumes:
      - ./data:/app/data
```

**TERMINAL VM DEBIAN** | Sebagai root di /opt/stacks/uptime-kuma

```
docker compose up -d
```
> Penjelasan: Menyalakan Uptime Kuma. Tag :2 mengikuti versi mayor 2 yang resmi.
```
docker compose ps
```
> Penjelasan: Status harus running.
1. Buka http://192.168.88.20:3001. Pada kunjungan pertama, buat akun admin (nama dan password kuat).
2. Buka Settings &gt; Security dan aktifkan 2FA (pindai kode QR dengan aplikasi autentikator; simpan kode
cadangan).
3. Buka Settings &gt; General dan atur Display Timezone ke Asia/Jakarta.

## 32.3 Menambah monitor

Klik Add New Monitor untuk tiap baris tabel berikut. Atur Heartbeat Interval 60 detik dan Retries 3, supaya satu
kegagalan sesaat tidak langsung menimbulkan alarm.
Nama Tipe Target Catatan
Proxmox web HTTP(s) https://192.168.88.10:8006 Centang Ignore TLS/SSL error (sertifikat
buatan sendiri)
MikroTik Ping 192.168.88.1
AdGuard STB (web) HTTP(s) http://192.168.88.253 Sesuaikan port bila AdGuard tidak di port
80
AdGuard STB (DNS) DNS Hostname example.com, Resolver
192.168.88.253, port 53
Menguji DNS benar-benar menjawab,
bukan hanya web hidup
VM Debian Ping 192.168.88.20
SSH VM Debian TCP Port 192.168.88.20, port 22
Portainer HTTP(s) https://192.168.88.20:9443 Ignore TLS error; sesuaikan bila port
berbeda
Internet (IndiHome) Ping 1.1.1.1 Menunjukkan apakah internet putus;
berguna sebagai bukti gangguan
TIPS
Gunakan Group untuk mengelompokkan (Jaringan, Server, Aplikasi). Layanan lain (Nextcloud, Forgejo, Home
Assistant) ditambahkan dengan cara yang sama setiap kali sebuah layanan baru dipasang.

## 32.4 Notifikasi ke HP

A. Gotify (Android dan kanal utama Anda)
1. Di Uptime Kuma buka Settings &gt; Notifications &gt; Setup Notification.
2. Notification Type: Gotify. Application Token: token aplikasi Uptime Kuma dari 32.1. Server URL:
http://192.168.88.20:8070. Priority: 8.
3. Centang Default enabled dan Apply on all existing monitors. Klik Test; pesan harus muncul di HP. Klik
Save.
B. Telegram (kanal kedua; utama untuk iPhone)
1. Di Telegram cari @BotFather, kirim /newbot, ikuti petunjuknya, dan salin token bot.
2. Kirim satu pesan apa saja ke bot baru Anda. Lalu cari @userinfobot dan kirim pesan ke sana untuk
mendapat Chat ID Anda.
3. Di Uptime Kuma tambah notifikasi tipe Telegram: isi Bot Token dan Chat ID, klik Test, lalu Save. Aktifkan juga
Default enabled.
KEAMANAN
Token Gotify dan token bot Telegram setara kunci. Simpan di password manager, jangan dibagikan, dan bila bocor,
buat ulang (hapus aplikasi di Gotify atau gunakan /revoke di BotFather).

## 32.5 Jendela pemeliharaan

Saat Anda sengaja mematikan atau mereboot server, Uptime Kuma akan mengirim alarm palsu. Buka menu
Maintenance &gt; Add Maintenance, pilih monitor yang terdampak dan waktunya, supaya tidak ada notifikasi
selama jendela itu.

## 32.6 Backup Uptime Kuma dan Gotify

**TERMINAL VM DEBIAN** | Sebagai root

```
cd /opt/stacks/uptime-kuma && docker compose stop
```
> Penjelasan: Menghentikan sejenak agar basis data tidak sedang ditulis.
```
tar czf /root/uptime-kuma-$(date +%F).tgz -C /opt/stacks uptime-kuma
```
> Penjelasan: Mengarsipkan seluruh folder aplikasi (compose dan data).
```
docker compose start
```
> Penjelasan: Menyalakan kembali.
```
cd /opt/stacks/gotify && docker compose stop && tar czf /root/gotify-$(date +%F).tgz -C /opt/stacks gotify && docker compose start
```
> Penjelasan: Mengarsipkan Gotify dalam satu baris. Arsip berisi .env (rahasia), simpan di tempat aman.
Salin arsip ke laptop atau HDD 2 TB (scp seperti di Suplemen 2 Bab 30.6). Pemulihan: ekstrak arsip ke
/opt/stacks lalu docker compose up -d di folder aplikasinya.

## 32.7 Masalah dan solusi

Gejala Penyebab Solusi
Notifikasi Gotify tidak muncul di HP HP di luar rumah tanpa Tailscale, atau
Android membatasi aplikasi
Aktifkan Tailscale; atur baterai Tidak dibatasi
Uptime Kuma gagal mengirim ke
Gotify (connection refused)
Alamat atau port salah Pakai http://192.168.88.20:8070; cek docker
compose ps di folder Gotify
Monitor HTTPS selalu merah Sertifikat buatan sendiri Centang Ignore TLS/SSL error
Banyak alarm palsu Interval terlalu sensitif Retries 3 dan interval 60 detik; gunakan
jendela pemeliharaan
Halaman 3001 tidak terbuka Container belum jalan atau port bentrok docker compose ps dan docker compose logs
--tail=50
Telegram Test gagal Bot belum menerima pesan pertama
atau Chat ID salah
Kirim pesan ke bot dulu, periksa ulang Chat ID


<!-- SOURCE: docs/bab/suplemen/33-beszel.md -->

# Bab 33. Beszel: CPU, RAM, Disk, dan Suhu

PENEMPATAN - GABUNG hub, BARU agen per guest
Tempat: Hub Beszel di VM 201 docker-core (192.168.88.20). Agen dipasang di setiap VM saat VM itu dibuat (dan di
host Proxmox bila diinginkan).
Alasan: Satu dasbor, satu agen per mesin. Hub menghubungi tiap agen, sehingga firewall Proxmox harus
mengizinkan 192.168.88.20 ke port agen (Bab 51).
Beszel terdiri dari hub (halaman web dengan grafik dan pengaturan peringatan) dan agen kecil di setiap mesin
yang dipantau. Agen membaca CPU, RAM, disk, jaringan, suhu, dan statistik Docker. Beszel dibuat ringan,
dengan agen yang memakai RAM sangat sedikit.
Mesin Cara pasang agen Yang terbaca
VM Debian (192.168.88.20) Docker (sekaligus lokasi hub) CPU, RAM, disk VM, statistik tiap container; suhu tidak
ada (VM)
Proxmox (192.168.88.10) Binary (skrip pemasang) CPU, RAM, disk, jaringan, suhu (mesin asli)
STB (192.168.88.253) Binary (opsional) CPU, RAM, disk, suhu SoC
MikroTik Tidak bisa dipasangi agen Dipantau lewat ping di Uptime Kuma

## 33.1 Memasang hub

**TERMINAL VM DEBIAN** | Sebagai root

```
mkdir -p /opt/stacks/beszel/beszel_data && cd /opt/stacks/beszel
```
> Penjelasan: Membuat folder aplikasi.
```
nano compose.yaml
```
> Penjelasan: Membuat berkas Compose. Isi seperti kotak di bawah.

**/opt/stacks/beszel/compose.yaml** | Isi berkas

```
services:
  beszel:
    image: henrygd/beszel:latest
    container_name: beszel
    restart: unless-stopped
    extra_hosts:
      - host.docker.internal:host-gateway
    ports:
      - "8090:8090"
    volumes:
      - ./beszel_data:/beszel_data
```

**TERMINAL VM DEBIAN** | Sebagai root di /opt/stacks/beszel

```
docker compose up -d
```
> Penjelasan: Menyalakan hub.
```
docker compose ps
```
> Penjelasan: Status harus running.
1. Buka http://192.168.88.20:8090. Kunjungan pertama meminta Anda membuat akun admin (email, password
kuat). Email boleh berupa alamat apa saja, misalnya admin@lab.local.
2. Setelah login, klik Add System. Dialog menampilkan Public Key hub dan perintah pemasangan agen.
Biarkan dialog terbuka atau salin kuncinya; dipakai di bawah.
CATATAN
Hub membuat pasangan kunci sendiri saat pertama dijalankan. Kunci publiknya dipakai agen untuk memastikan
hanya hub Anda yang boleh meminta data.

## 33.2 Agen di VM Debian (Docker)

Agen perlu mode jaringan host agar dapat membaca statistik kartu jaringan. Hub dan agen berada di mesin yang
sama tetapi di jaringan Docker berbeda, karena itu hub menjangkau agen lewat nama host.docker.internal.

**TERMINAL VM DEBIAN** | Sebagai root

```
mkdir -p /opt/stacks/beszel-agent && cd /opt/stacks/beszel-agent
```
> Penjelasan: Folder terpisah untuk agen.
```
nano compose.yaml
```
> Penjelasan: Isi seperti kotak di bawah; ganti KUNCI dengan Public Key dari dialog Add System. Sebaiknya salin
isi Compose dari dialog langsung bila tampilannya berbeda dengan contoh.

**/opt/stacks/beszel-agent/compose.yaml** | Isi berkas

```
services:
  beszel-agent:
    image: henrygd/beszel-agent:latest
    container_name: beszel-agent
    restart: unless-stopped
    network_mode: host
    volumes:
      - ./beszel_agent_data:/var/lib/beszel-agent
      - /var/run/docker.sock:/var/run/docker.sock:ro
    environment:
      PORT: "45876"
      KEY: "ssh-ed25519 AAAA...GANTI-DENGAN-KUNCI-DARI-HUB"
```

**TERMINAL VM DEBIAN** | Sebagai root di /opt/stacks/beszel-agent

```
docker compose up -d
```
> Penjelasan: Menyalakan agen.
```
ufw allow from 172.16.0.0/12 to any port 45876 proto tcp
```
> Penjelasan: Hanya bila UFW aktif: mengizinkan hub (yang berada di jaringan Docker 172.x) menjangkau agen.
Tanpa ini hub akan gagal terhubung.
1. Di dialog Add System isi Name: vm-debian, Host / IP: host.docker.internal, Port: 45876, lalu klik Add
system.
2. Dalam beberapa detik sistem berubah menjadi hijau dan grafik mulai muncul. Klik namanya untuk melihat
CPU, RAM, disk, jaringan, dan daftar container.
KEAMANAN
Agen memakai docker.sock (hanya baca) untuk membaca statistik container. Walau hanya baca, akses ini membuka
informasi seluruh container; pasang hanya agen resmi dan perbarui rutin.

## 33.3 Agen di Proxmox (mesin asli)

1. Di hub klik Add System. Isi Name: proxmox, Host / IP: 192.168.88.10, Port: 45876. Pilih tab Binary dan salin
perintah pemasangan yang tampil (jangan klik Add system dulu).
2. Buka Shell Proxmox (root) dan tempel perintah itu. Skrip mengunduh agen, membuat pengguna khusus
bernama beszel, dan menyalakannya sebagai layanan. Bentuk umumnya: curl -sL https://get.beszel.dev -o
/tmp/install-agent.sh && chmod +x /tmp/install-agent.sh && /tmp/install-agent.sh diikuti opsi kunci dan
port dari dialog.

**TERMINAL PROXMOX** | Shell Proxmox (root)

```
systemctl status beszel-agent --no-pager
```
> Penjelasan: Memastikan layanan agen aktif (active running).
```
ss -tlnp | grep 45876
```
> Penjelasan: Memastikan agen mendengarkan di port 45876.
1. Karena firewall Proxmox aktif (Suplemen 1 Bab 25.5), buka Datacenter &gt; Firewall &gt; Rules &gt; Add: Direction
in, Action ACCEPT, Protocol tcp, Source 192.168.88.20, Dest. port 45876, Comment "Beszel hub", Enable,
Add.
2. Kembali ke dialog di hub dan klik Add system. Proxmox muncul hijau. Buka halamannya dan cari panel
Temperature.
CATATAN
Suhu hanya muncul bila mesin memiliki sensor yang terbaca. Pastikan sensors menampilkan data (Suplemen 2 Bab
30.4).
TIPS
Bila tidak ingin membuka port masuk, hub mendukung token universal: aktifkan di Settings &gt; Tokens &
Fingerprints (versi baru), dan agen menyambung keluar ke hub tanpa aturan firewall masuk. Gunakan perintah yang
disediakan hub; tampilan bisa berbeda antar versi.

## 33.4 Agen di STB (opsional)

STB adalah DNS seluruh rumah, jadi tambahkan hal baru dengan hati-hati. Agen Beszel sangat kecil, tetapi bila
Anda ragu, lewati dan biarkan Uptime Kuma memantau STB lewat ping dan DNS (Bab 32.3).
1. Di hub klik Add System: Name stb, Host / IP 192.168.88.253, Port 45876, tab Binary, salin perintah.
2. SSH ke STB (root, dengan kunci) dan tempel perintah itu. Periksa dengan systemctl status beszel-agent
--no-pager.
3. Klik Add system di hub. STB tidak memiliki firewall bawaan di buku ini, jadi tidak ada aturan tambahan.

## 33.5 Peringatan

1. Di hub buka Settings &gt; Notifications dan tambahkan alamat notifikasi (format Shoutrrr) dari kotak di bawah.
Gunakan tombol uji bila tersedia.
2. Buka halaman sebuah sistem, klik ikon lonceng, lalu aktifkan peringatan sesuai tabel. Ulangi untuk tiap
sistem.
Alamat notifikasi (Shoutrrr) | Pilih salah satu atau keduanya; ganti nilai huruf besar
gotify://192.168.88.20:8070/TOKEN-APLIKASI-BESZEL?DisableTLS=yes
telegram://TOKEN-BOT@telegram?channels=CHAT-ID
Peringatan Nilai awal Jika terpicu
Status (sistem mati) Aktif Cek mesin dan jaringan
CPU Di atas 80% selama 10 menit Cari proses atau container yang rakus
Memori Di atas 90% selama 10 menit Kurangi VM atau tambah RAM
Peringatan Nilai awal Jika terpicu
Disk Di atas 85% Bersihkan atau tambah disk; jangan biarkan
100%
Suhu Di atas 80 derajat Bersihkan debu, perbaiki ventilasi
CATATAN
Bila alamat Gotify ditolak karena parameter, ikuti dokumentasi Shoutrrr untuk layanan Gotify, atau pakai Telegram.
Perhatikan huruf besar kecil pada nama parameter.

## 33.6 Memperbarui dan masalah umum

**TERMINAL VM DEBIAN** | Sebagai root

```
cd /opt/stacks/beszel && docker compose pull && docker compose up -d
```
> Penjelasan: Memperbarui hub. Backup folder dulu (Bab 34.3).
```
cd /opt/stacks/beszel-agent && docker compose pull && docker compose up -d
```
> Penjelasan: Memperbarui agen di VM.
Agen binary di Proxmox dan STB dapat diperbarui dengan menjalankan ulang skrip pemasang atau perintah
update agen yang dijelaskan di dokumentasi Beszel.
Gejala Penyebab Solusi
Sistem tetap abu-abu atau merah di
hub
Port 45876 terblokir (UFW atau firewall
Proxmox)
Tambahkan aturan Bab 33.2 dan 33.3; uji:
telnet alamat 45876
Hub gagal menjangkau agen di VM
yang sama
Memakai 192.168.88.20 bukannya
host.docker.internal
Gunakan host.docker.internal pada Host / IP
Tidak ada panel suhu VM, atau sensor tidak terbaca Periksa sensors di mesin asli; VM memang
tidak punya suhu
Tidak ada statistik container docker.sock tidak terpasang pada agen Pastikan baris /var/run/docker.sock ada di
compose
Peringatan tidak sampai Alamat Shoutrrr salah Uji alamat; bandingkan dengan format
dokumentasi


<!-- SOURCE: docs/bab/suplemen/34-menyatukan-dan-menguji.md -->

# Bab 34. Menyatukan, Menguji, dan Memahami Batasnya

PENEMPATAN - TIDAK ADA GUEST
Tempat: Bab ini menyatukan dan menguji layanan Suplemen 3 yang berada di docker-core.

## 34.1 Alur peringatan

Layanan dan mesin
Proxmox, VM, STB, MikroTik
Uptime Kuma
hidup atau mati?
Beszel
CPU, RAM, disk, suhu
Gotify
dan Telegram
HP Anda
notifikasi
Gambar 34.1 - Uptime Kuma dan Beszel mengirim peringatan lewat Gotify atau Telegram ke HP.
Pertanyaan Dijawab oleh
Apakah layanan hidup dan menjawab? Uptime Kuma
Apakah internet rumah putus? Uptime Kuma (ping 1.1.1.1)
Apakah CPU, RAM, disk, atau suhu mendekati batas? Beszel
Container mana yang memakai sumber daya terbanyak? Beszel (halaman sistem vm-debian)
Apakah disk mulai rusak? Pemeriksaan bulanan: smartctl -H (Suplemen 2 Bab
30.4)

## 34.2 Kartu di dashboard Homepage

Konfigurasi contoh di repo sudah memuat kartu monitoring ini. Jika Anda membuat Homepage dari awal, tambahkan entri berikut ke services.yaml, lalu muat ulang halaman. Gunakan nama HTTPS lokal setelah Caddy aktif.

**services.yaml (tambahan)** | Hati-hati dengan spasi; YAML sensitif terhadap indentasi

```
- Monitoring:
    - Uptime Kuma:
        href: https://kuma.home.arpa
        description: Uptime semua layanan
    - Beszel:
        href: https://beszel.home.arpa
        description: CPU, RAM, disk, suhu
    - Gotify:
        href: https://gotify.home.arpa
        description: Notifikasi ke HP
```

## 34.3 Backup dan rutinitas bulanan

Kapan Tindakan
Sebulan sekali Update image: di tiap folder /opt/stacks/\*, docker compose pull lalu up -d (backup dulu)
Sebulan sekali apt update dan apt full-upgrade di VM dan Proxmox; cek /var/run/reboot-required
Sebulan sekali smartctl -H pada semua disk; tinjau riwayat peringatan di Uptime Kuma dan Beszel
Sebulan sekali Tinjau daftar Machines Tailscale (hapus perangkat tak dikenal)
Tiga bulan sekali Uji pemulihan: ekstrak arsip backup ke folder uji dan pastikan aplikasi dapat menyala
Folder yang dicadangkan: seluruh /opt/stacks (compose, .env, data). Hentikan container sebentar saat
mengarsipkan agar basis data konsisten, seperti di Bab 32.6.

## 34.4 Uji menyeluruh

No Skenario Cara Hasil yang diharapkan
1 Layanan mati docker stop portainer (lalu docker start portainer
setelah alarm)
Notifikasi DOWN lalu UP di HP
dalam beberapa menit
2 Beban CPU apt install -y stress-ng, lalu stress-ng --cpu 0 --timeout
900s (turunkan sementara ambang CPU ke 2 menit)
Peringatan CPU dari Beszel
3 Mesin mati Matikan VM Debian dari web Proxmox (pakai jendela
pemeliharaan bila perlu)
Beszel: sistem down; Uptime
Kuma: monitor VM merah
4 Notifikasi di luar rumah Matikan WiFi HP, Tailscale aktif, ulangi uji 1 Notifikasi tetap tiba
5 Pemulihan backup Ekstrak arsip Uptime Kuma ke folder lain dan jalankan Monitor dan riwayat muncul
PERINGATAN
Setelah uji nomor 2, kembalikan ambang CPU ke nilai normal (10 menit).

## 34.5 Batas yang perlu Anda pahami

KASUS NYATA
Pemantau di dalam rumah tidak bisa memberi tahu saat rumah kehilangan internet atau listrik. Pesan Gotify
dan Telegram butuh jaringan. Bila IndiHome mati, Anda tidak menerima apa pun, dan baru tahu saat tidak bisa
mengakses.
Solusi opsional: layanan pihak luar seperti Healthchecks.io (periksa ketentuan paket gratisnya). Server rumah
mengirim sinyal berkala ke layanan itu, dan layanan itulah yang memperingatkan Anda bila sinyal berhenti. Pada VM
tambahkan satu baris cron berisi perintah curl ke alamat ping yang diberikan layanan itu.
KEAMANAN
Kanal Telegram adalah satu-satunya yang melewati internet publik. Isinya hanya status layanan; jangan mengirim
password atau data pribadi lewat notifikasi.

## 34.6 Langkah berikutnya untuk ketahanan

• Pindahkan Uptime Kuma ke mesin lain (STB 2 atau mini PC) begitu tersedia, agar tetap bisa melaporkan saat
Proxmox mati.
• Tambahkan monitor untuk setiap layanan baru pada hari yang sama layanan itu dipasang.
• Pertimbangkan UPS kecil agar mati listrik tidak mematikan server tanpa shutdown (rencana monitor listrik
Anda).


<!-- SOURCE: docs/bab/suplemen/bagian-3-99-penutup.md -->

# Bagian 3. Monitoring dan Notifikasi: Lembar Pembaruan dan Syarat Lulus Fase 3

Lembar Pembaruan dan Syarat Lulus
Bab sebelumnya Perubahan Rujukan
Edisi 2, Bab 19 (Dashboard) Tambahkan kartu Uptime Kuma, Beszel, Gotify Bab 34.2
Edisi 2, Bab 23 (Backup) Tambahkan /opt/stacks ke daftar backup, termasuk .env Bab 32.6 dan 34.3
Edisi 2, Bab 24 (Masalah) Tambahkan tabel masalah Gotify, Uptime Kuma, dan Beszel Bab 32.7 dan 33.6
Suplemen 1, Bab 25.5 (firewall
Proxmox)
Tambahkan aturan masuk tcp 45876 dari 192.168.88.20 untuk
agen Beszel
Bab 33.3
Suplemen 1, Bab 25.6 (UFW) Tambahkan aturan 172.16.0.0/12 ke port 45876 bila agen
Beszel di VM
Bab 33.2
Suplemen 2, Bab 30.4 (sensor) Data sensors kini dibaca Beszel untuk panel suhu Bab 33.3
Syarat lulus Fase 3
No Poin Ya / Tidak
1 Gotify, Uptime Kuma, dan Beszel berjalan (docker compose ps)
2 Notifikasi uji tiba di HP (Gotify di Android, Telegram di iPhone atau cadangan)
3 Monitor Proxmox, MikroTik, AdGuard, VM, dan internet aktif
4 Beszel menampilkan vm-debian dan Proxmox; panel suhu muncul di mesin asli
5 Peringatan CPU, RAM, disk, suhu, dan status dikonfigurasi
6 Uji skenario 1 dan 3 berhasil; notifikasi tiba juga dari luar rumah (Tailscale)
7 Backup /opt/stacks sudah dibuat dan disalin ke luar server
Berikutnya (Suplemen 4): reverse proxy lokal dengan sertifikat SSL, sehingga layanan diakses lewat nama
(misalnya kuma.lab.local) dan bukan IP:port, dengan sisi klien (memasang sertifikat di laptop, Android, dan
iPhone).


<!-- SOURCE: docs/bab/suplemen/bagian-4-00-pengantar.md -->

# Bagian 4. Reverse Proxy dan Sertifikat SSL Lokal (pengantar)

Bagian 4. Reverse Proxy dan Sertifikat SSL
Lokal
Asal: Suplemen 4. Bab 35-38.
Sampai Suplemen 3, setiap layanan dibuka lewat alamat IP dan port (misalnya 192.168.88.20:3001) dan tanpa
HTTPS. Suplemen ini memasang reverse proxy: satu pintu yang menerima semua permintaan, memberi
sertifikat HTTPS, dan meneruskannya ke layanan yang tepat. Hasilnya, Anda cukup membuka
https://kuma.home.arpa.
Bab Isi Hasil akhir
35. Konsep dan keputusan Cara kerja, tiga jalur sertifikat, memilih nama domain
lokal
Tahu jalur yang dipakai dan alasannya
36. Memasang Caddy DNS, jaringan Docker, Caddy, memindahkan
layanan ke belakang proxy
Layanan terbuka lewat nama dengan
HTTPS
37. Sertifikat di perangkat Mengambil sertifikat akar dan memasangnya di
Windows, Android, iPhone
Gembok hijau tanpa peringatan di semua
perangkat
38. Jalur opsional: domain
asli
Sertifikat tepercaya tanpa memasang apa pun di
perangkat
Alternatif bila aplikasi HP menolak
sertifikat lokal
Mengapa HTTPS di jaringan sendiri?
• Banyak aplikasi web (Vaultwarden, AFFiNE, kamera, notifikasi, dan kunci sandi/passkey) mensyaratkan
HTTPS agar fitur penting bekerja.
• Satu pintu lebih mudah dijaga: port aplikasi bisa ditutup dan yang terbuka hanya 80 dan 443.
• Alamat berupa nama lebih mudah diingat daripada IP dan port.
• Lalu lintas lewat Tailscale sudah terenkripsi; HTTPS menambah kompatibilitas aplikasi, bukan menggantikan
Tailscale.
Prasyarat
• VM Debian dengan Docker Compose dan struktur /opt/stacks (Suplemen 3, Bab 31).
• AdGuard Home di STB (Edisi 2 Bab 12) dengan alamat 192.168.88.253.
• Tailscale dengan Split DNS (Suplemen 1 Bab 26.7) bila ingin memakai nama dari luar rumah.
PERINGATAN
Suplemen ini mengubah file Compose layanan yang sudah berjalan (Uptime Kuma, Beszel, Gotify). Buat backup
/opt/stacks lebih dulu (Suplemen 3 Bab 34.3).


<!-- SOURCE: docs/bab/suplemen/35-reverse-proxy-konsep.md -->

# Bab 35. Reverse Proxy Lokal dan Sertifikat SSL: Konsep

PENEMPATAN - TIDAK ADA GUEST
Tempat: Bab konsep. Caddy dipasang di Bab 36.

## 35.1 Cara kerja

Perangkat Anda bertanya ke AdGuard: "di mana kuma.home.arpa?". AdGuard menjawab 192.168.88.20, alamat
VM Debian. Di sana Caddy menerima koneksi HTTPS di port 443, menunjukkan sertifikat untuk nama itu, lalu
meneruskan ke layanan yang sesuai di dalam Docker.
HP / Laptop
ketik kuma.home.arpa
AdGuard (DNS)
\*.home.arpa = 192.168.88.20
Caddy
port 443, sertifikat CA lokal
Uptime Kuma
Beszel
Gotify
Proxmox
AdGuard
HTTPS
Gambar 35.1 - Nama diterjemahkan AdGuard, Caddy memberi HTTPS dan meneruskan ke layanan.

## 35.2 Tiga jalur untuk sertifikat

Sertifikat HTTPS harus dipercaya oleh perangkat Anda. Untuk alamat yang hanya ada di jaringan rumah, ada tiga
cara:
Jalur Cara Kelebihan Kekurangan
1. CA lokal Caddy
(dipakai di Bab 36 dan 37)
Caddy membuat otoritas
sertifikat sendiri; sertifikat
akarnya dipasang di tiap
perangkat
Gratis, tanpa domain, tanpa
akun luar, sertifikat otomatis
diperbarui
Sertifikat akar harus dipasang di
setiap perangkat; sebagian
aplikasi HP menolaknya
2. Domain asli + DNS-01
(Bab 38, opsional)
Membeli domain; Caddy
membuktikan kepemilikan lewat
catatan DNS di Cloudflare
Dipercaya semua perangkat
dan aplikasi tanpa
memasang apa pun
Biaya domain tahunan, perlu
akun Cloudflare dan token API
3. HTTPS bawaan
Tailscale
Sertifikat untuk nama \*.ts.net
dari Tailscale
Tanpa domain, tepercaya Satu nama per perangkat
sehingga kurang cocok untuk
banyak layanan; nama tampil di
catatan sertifikat publik
CATATAN
Pilihan buku ini: Jalur 1 dikerjakan penuh karena tidak butuh biaya. Jalur 2 disediakan di Bab 38 bila nanti Anda
membeli domain. Keduanya dapat hidup berdampingan di Caddy yang sama.
PERINGATAN
Batasan Android yang perlu Anda tahu: Chrome di Android mempercayai sertifikat yang Anda pasang, tetapi sejak
Android 7 banyak aplikasi hanya mempercayai sertifikat bawaan sistem. Aplikasi seperti Gotify, DAVx5, atau
Bitwarden bisa menolak CA buatan sendiri, atau punya pengaturan sertifikat sendiri. Karena itu Gotify tetap dibiarkan
terbuka lewat IP dan port (Bab 36.5), dan Jalur 2 menjadi jalan keluar untuk aplikasi lain.

## 35.3 Memilih nama domain lokal

Edisi 2 memakai lab.local (misalnya pve.lab.local). Akhiran .local dicadangkan untuk mDNS (penemuan nama
otomatis), sehingga sebagian perangkat, terutama iPhone dan macOS, bisa lambat atau gagal menanyakannya
ke DNS biasa. Standar yang disiapkan khusus untuk jaringan rumah adalah home.arpa. Layanan baru memakai
home.arpa; pve.lab.local lama tetap berfungsi seperti sebelumnya.
Layanan Nama baru Tujuan di belakang Caddy
Uptime Kuma kuma.home.arpa container uptime-kuma, port 3001
Beszel beszel.home.arpa container beszel, port 8090
Gotify (web) gotify.home.arpa container gotify, port 80
Proxmox proxmox.home.arpa https://192.168.88.10:8006 (sertifikat Proxmox diabaikan)
Portainer portainer.home.arpa https://192.168.88.20:9443 (sertifikat diabaikan)
AdGuard adguard.home.arpa http://192.168.88.253:80


<!-- SOURCE: docs/bab/suplemen/36-caddy.md -->

# Bab 36. Memasang Caddy dan Memindahkan Layanan

PENEMPATAN - GABUNG - ke docker-core
Tempat: Caddy di VM 201 docker-core (192.168.88.20) sebagai satu-satunya gerbang HTTPS.
Aturan baru: Layanan di VM lain ditulis reverse_proxy IP:port, bukan nama container. Hanya layanan di docker-core
yang memakai jaringan proxy.

## 36.1 DNS: nama menuju VM Debian

1. Buka AdGuard Home (http://192.168.88.253) &gt; Filters &gt; DNS rewrites &gt; Add DNS rewrite.
2. Isi Domain: \*.home.arpa, Answer: 192.168.88.20, simpan. Tanda bintang membuat semua nama di bawah
home.arpa mengarah ke VM.
3. Ulangi aturan yang sama di AdGuard kedua (LXC 192.168.88.11, Edisi 2 Bab 13) agar nama tetap dikenali
bila STB mati.
4. Agar nama berfungsi dari luar rumah: di konsol Tailscale DNS &gt; Nameservers tambahkan nameserver
Custom 192.168.88.253 dengan Restrict to domain bernilai home.arpa (cara seperti Suplemen 1 Bab
26.7B).

**POWERSHELL WINDOWS** | PowerShell (laptop)

```
nslookup kuma.home.arpa 192.168.88.253
```
> Penjelasan: Menanyakan langsung ke AdGuard. Jawaban harus 192.168.88.20.

## 36.2 Jaringan Docker bersama

Caddy dan container yang berada di VM 201 harus bergabung ke jaringan Docker `proxy` agar Caddy dapat memanggilnya memakai nama container. Jaringan Docker ini hanya berlaku di VM 201; layanan pada VM lain dijangkau memakai alamat IP dan port yang diizinkan firewall Proxmox.

**TERMINAL VM DEBIAN** | Sebagai root (setelah su -)

```
docker network create proxy
```
> Penjelasan: Membuat jaringan bernama proxy. Cukup sekali.
```
ss -tlnp | grep -E ":(80|443)\b" || echo port-bebas
```
> Penjelasan: Memastikan port 80 dan 443 di VM belum dipakai. Jika dipakai (biasanya Homepage Edisi 2),
pindahkan dulu portnya; lihat peringatan di bawah.
PERINGATAN
Homepage dari Edisi 2 Bab 19 memakai ports "80:3000" dan merebut port 80 yang dibutuhkan Caddy. Ubah ke
"3002:3000" dan perbarui HOMEPAGE_ALLOWED_HOSTS sebelum Caddy dinyalakan (Suplemen 7 Bab 48.8). Port
3001 tidak bisa dipakai karena sudah milik Uptime Kuma.

## 36.3 Memasang Caddy

**TERMINAL VM DEBIAN** | Sebagai root

```
mkdir -p /opt/stacks/caddy/data /opt/stacks/caddy/config && cd /opt/stacks/caddy
```
> Penjelasan: Membuat folder aplikasi. Folder data akan menyimpan sertifikat dan otoritas lokal.
```
nano compose.yaml
```
> Penjelasan: Isi seperti kotak di bawah.

**/opt/stacks/caddy/compose.yaml** | Isi berkas

```
services:
  caddy:
    image: caddy:2
    container_name: caddy
    restart: unless-stopped
    ports:
      - "80:80"
      - "443:443"
      - "443:443/udp"
    volumes:
      - ./Caddyfile:/etc/caddy/Caddyfile:ro
      - ./data:/data
      - ./config:/config
    networks:
      - proxy
networks:
  proxy:
    external: true
```

**TERMINAL VM DEBIAN** | Sebagai root di /opt/stacks/caddy

```
nano Caddyfile
```
> Penjelasan: Berkas pengaturan Caddy. Isi seperti kotak di bawah.

**/opt/stacks/caddy/Caddyfile** | Isi berkas

```
{
  local_certs
}

kuma.home.arpa {
  reverse_proxy uptime-kuma:3001
}

beszel.home.arpa {
  reverse_proxy beszel:8090
}

gotify.home.arpa {
  reverse_proxy gotify:80
}

proxmox.home.arpa {
  reverse_proxy https://192.168.88.10:8006 {
    transport http {
      tls_insecure_skip_verify
    }
  }
}

portainer.home.arpa {
  reverse_proxy https://192.168.88.20:9443 {
    transport http {
      tls_insecure_skip_verify
    }
  }
}

adguard.home.arpa {
  reverse_proxy 192.168.88.253:80
}

dash.home.arpa {
  reverse_proxy 192.168.88.20:3002
}

git.home.arpa {
  reverse_proxy 192.168.88.23:3000
}

affine.home.arpa {
  reverse_proxy 192.168.88.25:3010
}

nextcloud.home.arpa {
  header Strict-Transport-Security "max-age=15552000"
  redir /.well-known/carddav /remote.php/dav/ 301
  redir /.well-known/caldav /remote.php/dav/ 301
  reverse_proxy 192.168.88.26:8080
}

n8n.home.arpa {
  reverse_proxy 192.168.88.27:5678
}

wp.home.arpa {
  reverse_proxy 192.168.88.28:8081
}

web.home.arpa {
  reverse_proxy 192.168.88.28:8082
}
```

Opsi global `local_certs` memerintahkan Caddy memakai otoritas sertifikat lokal untuk nama-nama ini. `tls_insecure_skip_verify` hanya dipakai untuk Proxmox dan Portainer karena sertifikat bawaan mereka ditandatangani sendiri; koneksi tetap berada di LAN.

## 36.4 Menyiapkan layanan agar berada di belakang Caddy

Untuk container di VM 201 yang hanya diakses melalui Caddy, hapus publikasi port dan hubungkan container ke jaringan `proxy`; Caddy dapat mengaksesnya lewat nama container. Gotify tetap memublikasikan port 8070 untuk klien dan pengirim notifikasi. Homepage tetap diakses lewat port 3002. Container di VM lain tidak dapat bergabung ke jaringan Docker ini: pertahankan port layanan di LAN VM dan batasi sumbernya dengan firewall Proxmox.

**TERMINAL VM DEBIAN** | Sebagai root

```
cd /opt/stacks/uptime-kuma && nano compose.yaml
```
> Penjelasan: Ubah menjadi seperti kotak di bawah: baris ports dihapus, ditambah jaringan proxy.

**/opt/stacks/uptime-kuma/compose.yaml** | Contoh setelah diubah

```
services:
  uptime-kuma:
    image: louislam/uptime-kuma:2
    container_name: uptime-kuma
    restart: unless-stopped
    volumes:
      - ./data:/app/data
    networks:
      - proxy
networks:
  proxy:
    external: true
```

Layanan Perubahan pada compose.yaml Alasan
Uptime Kuma Hapus ports, tambah networks proxy (seperti contoh) Hanya lewat Caddy
Beszel hub Hapus ports, tambah networks proxy; extra_hosts
tetap
Agen terhubung lewat host.docker.internal
sehingga tidak butuh port hub
Gotify Tetap ports "8070:80", tambah networks proxy Aplikasi Android memakai
http://192.168.88.20:8070 lewat Tailscale;
monitor Uptime Kuma juga
Homepage Tetap ports "3002:3000" (bukan 80); tidak perlu
networks proxy
Caddy menjangkaunya lewat
192.168.88.20:3002 seperti Portainer
TIPS
Bila agen Beszel Anda memakai token universal (Suplemen 3 Bab 33.3), agen menyambung ke port hub.
Pertahankan baris ports 8090 pada hub dalam kasus itu.

**TERMINAL VM DEBIAN** | Sebagai root

```
cd /opt/stacks/uptime-kuma && docker compose up -d
```
> Penjelasan: Menerapkan perubahan; container dibuat ulang dengan jaringan baru. Data aman di folder data.
```
cd /opt/stacks/beszel && docker compose up -d
```
> Penjelasan: Hal yang sama untuk Beszel (setelah mengubah compose.yaml-nya).
```
cd /opt/stacks/gotify && docker compose up -d
```
> Penjelasan: Hal yang sama untuk Gotify.

## 36.5 Menyalakan Caddy dan memeriksa

**TERMINAL VM DEBIAN** | Sebagai root

```
cd /opt/stacks/caddy && docker compose up -d
```
> Penjelasan: Menyalakan Caddy.
```
docker compose logs --tail=40
```
> Penjelasan: Melihat log. Cari baris yang menyebut pembuatan sertifikat lokal untuk nama-nama tadi dan tidak ada
error.
```
docker exec caddy caddy validate --config /etc/caddy/Caddyfile
```
> Penjelasan: Memeriksa sintaks Caddyfile. Hasil yang benar: Valid configuration.
Dari laptop buka https://kuma.home.arpa. Sebelum sertifikat akar dipasang (Bab 37), browser akan
menampilkan peringatan. Itu normal. Jika halaman Uptime Kuma tampil setelah memilih lanjut, jalur proxy sudah
benar.
KEAMANAN
Folder /opt/stacks/caddy/data berisi kunci privat otoritas sertifikat lokal Anda. Siapa pun yang memilikinya bisa
membuat sertifikat yang dipercaya perangkat Anda. Jangan dibagikan, jangan disajikan lewat web, dan sertakan
dalam backup yang tersimpan aman.

## 36.6 Menambah layanan baru ke depannya

1. Pastikan layanan bergabung ke jaringan proxy dan catat nama container serta port di dalamnya.
2. Tambahkan satu blok di Caddyfile: nama.home.arpa { reverse_proxy nama-container:port }.
3. Muat ulang tanpa memutus layanan: docker exec caddy caddy reload --config /etc/caddy/Caddyfile.
Tidak perlu menambah DNS karena \*.home.arpa sudah mencakupnya.

## 36.7 Memperbarui monitor dan dashboard

Di Uptime Kuma ubah target monitor ke nama baru (centang Ignore TLS/SSL error karena container Kuma
belum mempercayai CA lokal). Di Homepage (Edisi 2 Bab 19 dan Suplemen 3 Bab 34.2) ganti tautan kartu ke
alamat https yang baru. Homepage sendiri kini dibuka di https://dash.home.arpa.


<!-- SOURCE: docs/bab/suplemen/37-sertifikat-akar-perangkat.md -->

# Bab 37. Memasang Sertifikat Akar di Perangkat

PENEMPATAN - TIDAK ADA GUEST
Tempat: Langkah di perangkat klien. Tidak ada VM/LXC baru.
Caddy menandatangani sertifikat layanan dengan otoritas lokal-nya. Agar perangkat percaya, sertifikat akar
otoritas itu dipasang sekali di tiap perangkat. Yang dipasang hanya sertifikat akar (berkas root.crt, publik), bukan
kunci privat.

## 37.1 Mengambil sertifikat akar dari server

**TERMINAL VM DEBIAN** | Sebagai root

```
cp /opt/stacks/caddy/data/caddy/pki/authorities/local/root.crt /root/caddy-root.crt
```
> Penjelasan: Menyalin hanya berkas root.crt ke lokasi mudah. Jangan menyalin berkas root.key di folder yang
sama; itu kunci privat.
```
ls -l /root/caddy-root.crt
```
> Penjelasan: Memastikan berkas ada dan ukurannya tidak nol.

**POWERSHELL WINDOWS** | PowerShell (laptop)

```
scp <USER>@192.168.88.20:/root/caddy-root.crt .
```
> Penjelasan: Karena login root SSH dimatikan (Suplemen 1), ambil berkas lewat pengguna biasa; salin dulu
berkasnya ke home pengguna itu bila izin menolak. Alternatif: ambil lewat Portainer atau WinSCP dengan akun
pengguna biasa.
TIPS
Jika izin menolak, jalankan di VM: cp /root/caddy-root.crt /home/&lt;USER&gt;/ && chown &lt;USER&gt;
/home/&lt;USER&gt;/caddy-root.crt, lalu scp berkas itu dari folder home.
Setelah berkas ada di laptop, kirim ke HP: lewat kabel USB (Android), email ke diri sendiri, Google Drive atau
iCloud Drive, atau Telegram. Berkas ini aman dikirim karena hanya berisi sertifikat publik.

## 37.2 Laptop Windows

Cara A: dengan antarmuka
1. Klik dua kali caddy-root.crt &gt; Install Certificate.
2. Pilih Local Machine (butuh izin administrator) atau Current User, klik Next.
3. Pilih Place all certificates in the following store &gt; Browse &gt; Trusted Root Certification Authorities &gt; OK
&gt; Next &gt; Finish.
4. Konfirmasi peringatan keamanan dengan Yes. Tutup lalu buka ulang browser.
Cara B: dengan PowerShell

**POWERSHELL WINDOWS** | PowerShell sebagai Administrator

```powershell
Import-Certificate -FilePath "$env:USERPROFILE\caddy-root.crt" -CertStoreLocation Cert:\LocalMachine\Root
```
> Penjelasan: Memasang sertifikat akar ke penyimpanan tepercaya Windows. Sesuaikan lokasi berkas. Chrome
dan Edge memakai penyimpanan ini.
CATATAN
Firefox memiliki penyimpanan sendiri. Impor di Settings &gt; Privacy & Security &gt; Certificates &gt; View Certificates &gt;
Authorities &gt; Import lalu centang "Trust this CA to identify websites".

## 37.3 HP Android

1. Salin caddy-root.crt ke HP (folder Download).
2. Pastikan HP memakai kunci layar (PIN, pola, atau sidik jari); Android mewajibkannya untuk memasang
sertifikat.
3. Buka Pengaturan &gt; Keamanan dan privasi &gt; Keamanan lainnya &gt; Enkripsi dan kredensial &gt; Instal
sertifikat &gt; Sertifikat CA. (Nama menu berbeda antar merek HP; cari kata "Install a certificate" atau "Instal
sertifikat".)
4. Muncul peringatan bahwa jaringan bisa dipantau. Ketuk Instal saja dan pilih berkas caddy-root.crt.
5. Buka Chrome dan kunjungi https://kuma.home.arpa (Tailscale aktif bila di luar rumah). Gembok harus tampil
tanpa peringatan.
PERINGATAN
Android akan menampilkan pemberitahuan tetap "Jaringan mungkin dipantau" selama sertifikat pengguna terpasang.
Itu normal untuk CA yang Anda pasang sendiri.
Sertifikat ini dipercaya oleh browser. Aplikasi lain (Gotify, DAVx5, Bitwarden) bisa menolaknya; uji satu per satu.
Untuk Gotify, tetap pakai http://192.168.88.20:8070. Jika sebuah aplikasi bersikeras, pertimbangkan Jalur 2 (Bab 38).
37.4 iPhone
1. Kirim caddy-root.crt ke iPhone (iCloud Drive, email ke diri sendiri, atau AirDrop dari Mac). Buka dari aplikasi
Files atau email dan ketuk berkasnya.
2. Muncul "Profile Downloaded". Buka Pengaturan &gt; Umum &gt; VPN & Manajemen Perangkat, ketuk profil yang
diunduh, lalu Pasang dan masukkan kode.
3. Langkah yang sering terlewat: buka Pengaturan &gt; Umum &gt; Tentang &gt; Pengaturan Kepercayaan
Sertifikat dan aktifkan sakelar untuk "Caddy Local Authority - ... Root". Tanpa ini sertifikat terpasang tetapi
belum dipercaya.
4. Buka Safari ke https://kuma.home.arpa (Tailscale aktif bila di luar rumah). Gembok harus tampil tanpa
peringatan.

## 37.5 Memeriksa dan merawat

Hal Penjelasan
Masa berlaku Sertifikat akar Caddy berlaku sangat lama (sekitar 10 tahun); sertifikat layanan diperbarui otomatis
oleh Caddy. Anda tidak perlu mengurusnya.
Backup Folder /opt/stacks/caddy/data wajib dicadangkan. Jika hilang, Caddy membuat otoritas baru dan
semua perangkat harus memasang akar baru.
Perangkat hilang Hapus sertifikat akar dari perangkat lain bukan keharusan, tetapi jangan biarkan kunci privat bocor
dari server.
Memeriksa penerbit Di browser buka detail sertifikat: penerbit tertulis Caddy Local Authority.


<!-- SOURCE: docs/bab/suplemen/38-domain-asli-cloudflare.md -->

# Bab 38. Jalur Opsional: Domain Asli dengan Sertifikat Tepercaya

PENEMPATAN - GABUNG - ke docker-core
Tempat: Caddy yang sama di VM 201 docker-core (192.168.88.20); hanya mengubah sumber sertifikat.
Jalur ini cocok bila Anda tidak ingin memasang sertifikat akar di setiap perangkat atau ada aplikasi HP yang
menolak CA lokal. Anda membeli sebuah domain (misalnya contoh.com), dan Caddy meminta sertifikat asli dari
Let's Encrypt dengan membuktikan kepemilikan lewat catatan DNS, tanpa membuka port apa pun ke internet.

## 38.1 Cara kerja dan apa yang terlihat publik

Hal Penjelasan
Pembuktian Caddy membuat catatan TXT sementara di DNS Cloudflare (DNS-01). Let's Encrypt
memeriksa, lalu sertifikat diterbitkan.
Alamat IP rumah Tidak dibuat catatan A publik. Nama seperti kuma.lab.contoh.com hanya dijawab oleh
AdGuard di rumah dan mengarah ke 192.168.88.20.
Sertifikat wildcard Satu sertifikat \*.lab.contoh.com menutupi semua layanan sehingga nama tiap layanan tidak
tercatat satu per satu di catatan sertifikat publik.
Biaya Hanya domain tahunan (harga bervariasi antar penyedia, periksa sebelum membeli).
Cloudflare gratis untuk kebutuhan ini.

## 38.2 Langkah di Cloudflare

1. Beli domain dari penyedia pilihan Anda. Buat akun Cloudflare (gratis) dan tambahkan domain itu.
2. Cloudflare memberi dua alamat nameserver. Pasang keduanya di pengaturan domain pada penyedia tempat
membeli, lalu tunggu domain aktif di Cloudflare.
3. Di Cloudflare buka My Profile &gt; API Tokens &gt; Create Token. Pilih templat Edit zone DNS, batasi pada zona
domain Anda saja, dan buat token. (Bila Caddy melaporkan kurang izin, tambahkan izin Zone Read.)
4. Salin token itu sekali; Cloudflare tidak menampilkannya lagi. Simpan di password manager.

## 38.3 Membangun Caddy dengan modul Cloudflare

Caddy bawaan tidak membawa modul DNS Cloudflare. Image dibangun sendiri dari dua baris Dockerfile. Ini
menggantikan image: caddy:2 pada Bab 36.3.

**TERMINAL VM DEBIAN** | Sebagai root

```
cd /opt/stacks/caddy && nano Dockerfile
```
> Penjelasan: Isi seperti kotak pertama di bawah.

**/opt/stacks/caddy/Dockerfile** | Isi berkas

```
FROM caddy:builder AS builder
RUN xcaddy build --with github.com/caddy-dns/cloudflare
FROM caddy:2
COPY --from=builder /usr/bin/caddy /usr/bin/caddy
```

**TERMINAL VM DEBIAN** | Sebagai root di /opt/stacks/caddy

```
nano .env
```
> Penjelasan: Berkas rahasia; isi satu baris seperti kotak di bawah.

**/opt/stacks/caddy/.env** | Isi berkas

```
CF_API_TOKEN=TEMPEL-TOKEN-CLOUDFLARE-DI-SINI
```

**TERMINAL VM DEBIAN** | Sebagai root di /opt/stacks/caddy

```
chmod 600 .env
```
> Penjelasan: Hanya root yang boleh membaca token.
```
nano compose.yaml
```
> Penjelasan: Ganti baris image: caddy:2 menjadi build: . dan tambahkan env_file: .env di bawah
container_name.

**/opt/stacks/caddy/Caddyfile (jalur domain asli)** | Ganti contoh.com dengan domain Anda; tambah blok handle untuk layanan

```
lain
*.lab.contoh.com {
 tls {
 dns cloudflare {env.CF_API_TOKEN}
 resolvers 1.1.1.1
 }
 @kuma host kuma.lab.contoh.com
 handle @kuma {
 reverse_proxy uptime-kuma:3001
 }
 @gotify host gotify.lab.contoh.com
 handle @gotify {
 reverse_proxy gotify:80
 }
 handle {
 abort
 }
}
```

**TERMINAL VM DEBIAN** | Sebagai root di /opt/stacks/caddy

```
docker compose up -d --build
```
> Penjelasan: Membangun image dengan modul Cloudflare lalu menyalakan Caddy. Pembangunan pertama
memakan beberapa menit.
```
docker compose logs --tail=50
```
> Penjelasan: Cari pesan sertifikat berhasil diperoleh untuk \*.lab.contoh.com. Pesan kesalahan token atau izin
muncul di sini.
CATATAN
resolvers 1.1.1.1 penting: tanpa itu Caddy memeriksa catatan DNS lewat AdGuard rumah, yang punya rewrite sendiri
untuk nama yang sama, dan pembuktian bisa gagal.
Bila Caddy yang sama sedang melayani \*.home.arpa (Jalur 1), tempatkan kedua grup alamat di Caddyfile yang sama;
keduanya dapat berdampingan.

## 38.4 DNS dan klien untuk jalur ini

1. AdGuard (dan AdGuard kedua): DNS rewrite \*.lab.contoh.com menjadi 192.168.88.20.
2. Tailscale: tambah nameserver Custom 192.168.88.253 dengan Restrict to domain lab.contoh.com agar
nama berfungsi dari luar rumah.
3. Tidak ada yang dipasang di laptop, Android, atau iPhone. Buka https://kuma.lab.contoh.com dan gembok
langsung tampil, termasuk di aplikasi yang menolak CA lokal.
KEAMANAN
Token Cloudflare sebaiknya hanya untuk satu zona dan disimpan di .env berizin 600. Jika bocor, cabut di Cloudflare
lalu buat yang baru. Aktifkan verifikasi dua langkah di akun Cloudflare dan akun penyedia domain.


<!-- SOURCE: docs/bab/suplemen/bagian-4-99-penutup.md -->

# Bagian 4. Reverse Proxy dan Sertifikat SSL Lokal: Uji, Masalah Umum, Lembar Pembaruan, Syarat Lulus Fase 4

Uji, Masalah Umum, dan Lembar Pembaruan
Uji menyeluruh
No Uji Hasil yang diharapkan
1 nslookup kuma.home.arpa 192.168.88.253 Jawaban 192.168.88.20
2 Laptop: buka https://kuma.home.arpa setelah Bab 37 Halaman Uptime Kuma, gembok tanpa peringatan
3 Buka https://proxmox.home.arpa Halaman login Proxmox; konsol VM berfungsi (bila tidak,
buka lewat IP:8006)
4 HP Android (Chrome), WiFi rumah Gembok tanpa peringatan
5 HP Android, data seluler, Tailscale aktif Nama terbuka dari luar rumah
6 iPhone (Safari), setelah mengaktifkan kepercayaan
sertifikat
Gembok tanpa peringatan
7 Notifikasi Gotify dari Uptime Kuma tetap tiba Ya (Gotify tetap lewat 192.168.88.20:8070)
8 Port lama 3001 dan 8090 dari laptop Tidak lagi terbuka (hanya Caddy 80 dan 443)
Masalah dan solusi
Gejala Penyebab Solusi
Nama tidak ditemukan DNS rewrite belum ada, atau
perangkat memakai DNS lain
Periksa AdGuard (Bab 36.1); di Android matikan
Private DNS yang menimpa DNS jaringan; Tailscale
split DNS bila di luar rumah
Peringatan sertifikat tetap
muncul
Sertifikat akar belum dipasang atau
belum dipercaya
Ulangi Bab 37; iPhone: aktifkan di Pengaturan
Kepercayaan Sertifikat; Firefox: impor terpisah
Error 502 Bad Gateway Layanan tidak berada di jaringan
proxy atau nama container salah
docker network inspect proxy; samakan nama
container di Caddyfile
Caddy gagal start Kesalahan sintaks atau port 80/443
terpakai
docker exec caddy caddy validate ... ; ss -tlnp | grep
-E ":(80|443)"
Konsol VM Proxmox putus Proxy dan WebSocket Buka Proxmox langsung lewat
https://192.168.88.10:8006 untuk konsol
Aplikasi Android menolak
sertifikat
Aplikasi tidak mempercayai CA
pengguna
Pakai IP:port untuk aplikasi itu atau beralih ke Jalur 2
(Bab 38)
Setelah reinstal semua
perangkat menolak
Folder data Caddy hilang sehingga
CA baru dibuat
Pulihkan backup /opt/stacks/caddy/data, atau pasang
akar baru di semua perangkat
Lembar pembaruan
Bab sebelumnya Perubahan Rujukan
Suplemen 1, Bab 25.6 Setelah layanan dipindah ke belakang Caddy, port aplikasi tidak
lagi dipublikasikan; hanya 80 dan 443
Bab 36.4
Suplemen 1, Bab 26.7 Tambahkan Split DNS untuk home.arpa selain lab.local Bab 36.1
Suplemen 3, Bab 32.3 dan 34.2 Ganti target monitor dan tautan Homepage ke nama https baru
(Gotify tetap IP:port)
Bab 36.7
Edisi 2, Bab 19 Tautan kartu dashboard memakai nama baru Bab 36.7
Edisi 2, Bab 23 dan Suplemen 3
Bab 34.3
Tambahkan /opt/stacks/caddy (termasuk data berisi kunci CA)
ke backup
Bab 36.5
Syarat lulus Fase 4
No Poin Ya / Tidak
1 AdGuard (dan AdGuard kedua) memiliki rewrite \*.home.arpa ke 192.168.88.20
2 Caddy berjalan; kuma, beszel, gotify, proxmox, portainer, adguard terbuka lewat https
3 Sertifikat akar terpasang di laptop, Android, dan iPhone; gembok tanpa peringatan
4 Dari luar rumah (Tailscale) nama tetap terbuka
5 Port aplikasi lama tertutup kecuali Gotify 8070
6 Backup folder Caddy (data) tersimpan di luar server
Berikutnya (Suplemen 5): hosting web (situs statis dan WordPress) dan n8n di belakang Caddy yang sama,
lengkap dengan sisi klien. Setelah itu Proxmox Backup Server, SSO, Immich, dan opsional AMP, Ollama, sesuai
daftar Anda.


<!-- SOURCE: docs/bab/suplemen/bagian-5-00-pengantar.md -->

# Bagian 5. Hosting Web dan n8n (pengantar)

Bagian 5. Hosting Web dan n8n
Asal: Suplemen 5. Bab 39-43.
Suplemen 4 membuat satu pintu HTTPS (Caddy). Suplemen ini memasang tiga hal di belakang pintu itu: situs
web statis, WordPress, dan n8n (otomasi alur kerja). Satu bab opsional menunjukkan cara membuka situs
statis ke internet dengan Cloudflare Tunnel tanpa membuka port di router.
Bab Isi Hasil akhir
39. Konsep dan keputusan Jalur privat vs publik, mengapa tunnel, apa dipasang
di mana
Tahu mana yang privat dan mana yang
boleh publik
40. Situs statis Folder situs, blok Caddy, unggah dari laptop https://web.home.arpa tampil di semua
perangkat
41. WordPress WordPress + MariaDB, pemasangan, pengamanan
dasar
https://wp.home.arpa dengan HTTPS
benar
42. n8n n8n + Postgres, uji webhook ke Gotify, webhook luar https://n8n.home.arpa dan notifikasi uji
tiba
43. Cloudflare Tunnel
(opsional)
Situs statis publik lewat koneksi keluar Situs terbuka dari internet tanpa port
forwarding
Prasyarat
• Caddy dan jaringan Docker proxy dari Suplemen 4 (Bab 36) sudah berjalan; Gotify dan Uptime Kuma dari
Suplemen 3.
• Sertifikat akar Caddy terpasang di perangkat (Suplemen 4 Bab 37) bila ingin gembok tanpa peringatan.
• VM 208 n8n, 209 web, dan 210 web-public dibuat dari templat VM 200 (Suplemen 7 Bab 48-49). Caddy tetap
di VM 201 docker-core.
• Semua perintah dijalankan sebagai root setelah su - (tanpa sudo), di guest yang ditunjuk Kotak
Penempatan di awal tiap bab.
PERINGATAN
Suplemen 1 sampai 4 belum Anda uji. Suplemen ini bergantung langsung pada Caddy (Suplemen 4). Saran urutan:
uji dulu Bab 36 dan 37, baru kerjakan Bab 40 dan seterusnya. Bila Caddy bermasalah, kesalahan di sini sulit
dibedakan dari kesalahan di sana.
CATATAN
Hal yang tidak bisa saya pastikan dari dokumentasi ditandai [BELUM PASTI] di teks dan dikumpulkan di tabel pada
halaman penutup. Laporkan hasil uji per bab agar bisa dikoreksi.


<!-- SOURCE: docs/bab/suplemen/39-hosting-web-konsep.md -->

# Bab 39. Hosting Web di Rumah: Konsep dan Keputusan

PENEMPATAN - TIDAK ADA GUEST
Tempat: Bab konsep. Penempatan: situs statis dan WordPress di VM 209 web, n8n di VM 208, situs publik di VM 210.

## 39.1 Dua jalur: privat dan publik

Sampai Suplemen 4 semua layanan hanya bisa dibuka dari jaringan rumah atau lewat Tailscale. Itu jalur privat
dan tetap menjadi jalur utama buku ini. Jalur publik berarti siapa pun di internet bisa membuka alamat Anda.
Jalur A - privat (bab 40, 41, 42)
Jalur B - publik, opsional (bab 43, hanya situs statis)
HP / Laptop
Tailscale / Wi-Fi
AdGuard
nama \*.home.arpa
Caddy :443
HTTPS CA lokal
Layanan
WordPress, n8n, situs
Pengunjung
internet
Cloudflare
HTTPS publik
cloudflared
koneksi KELUAR dari VM
web-public
situs statis saja
Gambar 39.1 - Jalur privat (Tailscale + Caddy) dan jalur publik opsional (Cloudflare Tunnel).
Jalur A: privat Jalur B: publik (opsional)
Siapa bisa membuka Perangkat Anda (rumah atau Tailscale) Siapa saja di internet
Sertifikat CA lokal Caddy (pasang akar di perangkat) Sertifikat publik dari Cloudflare, tanpa pemasangan
Risiko Rendah Ada: serangan otomatis, beban, kesalahan
konfigurasi
Biaya Gratis Perlu domain milik sendiri (biaya tahunan); Tunnel
sendiri gratis [BELUM PASTI] cek halaman harga
Cloudflare
Cocok untuk WordPress, n8n, alat pribadi Situs statis kecil (portofolio, halaman info)

## 39.2 Mengapa tunnel, bukan port forwarding

Internet Anda melewati beberapa lapis jaringan: router IndiHome, TL-WR840N dalam mode WISP, lalu MikroTik.
Membuka port ke dalam berarti menembus setiap lapis (dan router IndiHome mungkin tidak bisa Anda atur).
Alamat IP publik IndiHome juga bisa berubah atau berbagi [BELUM PASTI]. Cloudflare Tunnel membalik arah:
program cloudflared di VM membuat koneksi keluar ke Cloudflare, sehingga tidak ada port yang dibuka ke
dalam.
KEAMANAN
Tunnel menghindari port forwarding, tetapi tidak membuat aplikasi yang Anda publikasikan menjadi aman.
Karena itu hanya situs statis (tanpa login, tanpa database) yang dipublikasikan di buku ini.

## 39.3 Keputusan: apa dipasang di mana

Layanan Alamat Guest Proxmox Jalur Alasan
Situs statis (privat) web.home.arpa VM 209 web (.28) A Hanya berkas HTML;
permukaan serangan kecil
WordPress wp.home.arpa VM 209 web (.28) A saja Halaman login, plugin, dan
pembaruan rutin sering jadi
sasaran serangan
n8n n8n.home.arpa VM 208 n8n (.27) A saja Menyimpan kredensial ke
layanan lain; kebocoran
berdampak besar
Situs statis (publik) domain Anda (Bab 43) VM 210 web-public (.29) B opsional Satu-satunya yang menghadap
internet; VM paling terisolasi
Setiap layanan berjalan di VM sendiri atau VM web bersama sesuai Peta Penempatan (Suplemen 7 Bab 48).
Caddy di docker-core hanya meneruskan permintaan ke alamat IP:port VM tujuan.
PERINGATAN
Alamat WordPress tersimpan di databasenya. Bila Anda memasang dengan wp.home.arpa lalu pindah ke domain
publik, alamat harus diganti (Pengaturan atau alat WP-CLI). Putuskan alamat akhir sebelum Bab 41.

## 39.4 Sumber daya dan persiapan

WordPress dengan MariaDB dan n8n dengan Postgres masing-masing menjalankan dua container. Sebagai
gambaran kasar, tiap pasangan memakai beberapa ratus MB RAM [BELUM PASTI] (perkiraan, bukan angka
resmi), ditambah RAM sistem operasi VM-nya sendiri. Periksa juga RAM total host Proxmox (free -h di shell
host) karena kini ada tiga VM tambahan. Pantau di Beszel (Suplemen 3) setelah dipasang dan sesuaikan RAM
VM di Proxmox bila perlu.

**TERMINAL VM DOCKER-CORE** | VM docker-core (192.168.88.20), sebagai root (setelah su -)

```
free -h && df -h /
```
> Penjelasan: Melihat RAM dan ruang disk VM ini (lakukan juga di host Proxmox).
```
tar czf /root/stacks-sebelum-s5.tgz /opt/stacks
```
> Penjelasan: Backup seluruh /opt/stacks sebelum mengubah Caddy (berkas ini berisi kunci CA, simpan aman,
jangan dibagikan).
```
docker ps --format "table {{.Names}}\t{{.Status}}"
```
> Penjelasan: Memastikan caddy, gotify, uptime-kuma berjalan sebelum mulai.


<!-- SOURCE: docs/bab/suplemen/40-situs-statis.md -->

# Bab 40. Situs Web Statis dengan Caddy

PENEMPATAN - GABUNG - ke VM web
Tempat: VM 209 web (192.168.88.28). Dibuat dari templat VM 200: qm clone 200 209 --name web --full 1
(Suplemen 7 Bab 49).
Alasan: Situs statis dan WordPress sama-sama konten web privat dengan data kecil, jadi boleh serumah. Caddy di
docker-core hanya meneruskan ke VM ini.
Dipisahkan dari: n8n (VM 208), situs publik (VM 210), dan semua layanan lain.
Mode hemat: Boleh digabung ke VM 206 (apps).
Situs statis adalah kumpulan berkas (HTML, CSS, gambar). Berkasnya disajikan oleh sebuah Caddy kecil di VM
web; Caddy besar di docker-core hanya menjadi gerbang HTTPS yang meneruskan ke sana. VM web juga akan
menampung WordPress (Bab 41).

## 40.1 Membuat VM web

**TERMINAL HOST PROXMOX** | Shell node Proxmox (host), sebagai root

```
qm clone 200 209 --name web --full 1
```
> Penjelasan: Membuat VM 209 bernama web sebagai salinan penuh dari templat VM 200 (Suplemen 7 Bab 49).
```
qm set 209 --memory 1536 --cores 2
```
> Penjelasan: Mengatur RAM (MB) dan jumlah inti. Angka awal adalah perkiraan [BELUM PASTI]; pantau di Beszel
lalu sesuaikan.
```
qm start 209
```
> Penjelasan: Menyalakan VM. Lakukan penyiapan awal di Suplemen 7 Bab 49.4 (nama host, kunci SSH, alamat
192.168.88.28), lalu kembali ke sini.

## 40.2 Sisi server: situs di VM web

**TERMINAL VM WEB** | VM web (192.168.88.28), sebagai root (setelah su -)

```
mkdir -p /opt/stacks/web/sites/halo && cd /opt/stacks/web
```
> Penjelasan: Folder induk semua situs; satu subfolder per situs.
```
chown -R <USER>: /opt/stacks/web/sites
```
> Penjelasan: Menjadikan folder ini milik pengguna biasa Anda (ganti &lt;USER&gt;) agar bisa diunggah dari laptop lewat
scp tanpa login root.
```
nano sites/halo/index.html
```
> Penjelasan: Isi seperti kotak di bawah sebagai halaman uji.

**/opt/stacks/web/sites/halo/index.html** | Isi berkas

```
<!doctype html>
<html lang="id">
<head><meta charset="utf-8"><title>Halo</title>
<meta name="viewport" content="width=device-width, initial-scale=1"></head>
<body><h1>Halo dari home server</h1><p>Situs statis ini disajikan oleh Caddy.</p></body>
</html>
```

**TERMINAL VM WEB** | VM web, sebagai root di /opt/stacks/web

```
nano Caddyfile
```
> Penjelasan: Caddy kecil: HTTP saja, memilih folder situs menurut nama host. Isi seperti kotak di bawah.

**/opt/stacks/web/Caddyfile** | Isi berkas

```
{
 auto_https off
}
http://web.home.arpa {
 root * /srv/sites/halo
 encode gzip
 file_server
}
```

**TERMINAL VM WEB** | VM web, sebagai root di /opt/stacks/web

```
nano compose.yaml
```
> Penjelasan: Isi seperti kotak di bawah.

**/opt/stacks/web/compose.yaml** | Isi berkas

```
services:
  sites:
    image: caddy:2
    container_name: sites
    restart: unless-stopped
    volumes:
      - ./Caddyfile:/etc/caddy/Caddyfile:ro
      - ./sites:/srv/sites:ro
    ports:
      - "8082:80"
```

**TERMINAL VM WEB** | VM web, sebagai root di /opt/stacks/web

```
docker compose up -d
```
> Penjelasan: Menyalakan Caddy kecil. Port 8082 dibuka untuk LAN; firewall Proxmox (Suplemen 7 Bab 51) hanya
mengizinkan docker-core menjangkaunya.
```
docker exec sites caddy validate --config /etc/caddy/Caddyfile
```
> Penjelasan: Memeriksa sintaks. Hasil benar: Valid configuration.

## 40.3 Gerbang HTTPS di docker-core

**TERMINAL VM DOCKER-CORE** | VM docker-core (192.168.88.20), sebagai root

```
nano /opt/stacks/caddy/Caddyfile
```
> Penjelasan: Tambahkan blok di bawah ini di akhir berkas. Volume Caddy tidak perlu diubah.

**/opt/stacks/caddy/Caddyfile (tambahan)** | Tambahan

```
web.home.arpa {
 reverse_proxy 192.168.88.28:8082
}
```

**TERMINAL VM DOCKER-CORE** | VM docker-core, sebagai root

```
docker exec caddy caddy validate --config /etc/caddy/Caddyfile
```
> Penjelasan: Memeriksa sintaks seluruh Caddyfile.
```
docker exec caddy caddy reload --config /etc/caddy/Caddyfile
```
> Penjelasan: Memuat blok baru tanpa memutus layanan lain.
CATATAN
Nama web.home.arpa sudah terjawab oleh rewrite \*.home.arpa di AdGuard (Suplemen 4 Bab 36.1) dan mengarah ke
docker-core. Caddy meneruskan nama host asli ke VM web, sehingga Caddy kecil memilih folder yang benar. Bila
halaman tidak muncul, lihat tabel masalah di halaman penutup.

## 40.4 Sisi klien: Windows

1. Buka browser ke https://web.home.arpa. Halaman "Halo dari home server" harus tampil dengan gembok
(setelah Suplemen 4 Bab 37).
Mengunggah situs dari laptop (OpenSSH sudah ada di Windows 10 dan 11) langsung ke VM web:

**POWERSHELL WINDOWS** | PowerShell (laptop), di folder situs Anda

```
scp -r .\* <USER>@192.168.88.28:/opt/stacks/web/sites/halo/
```
> Penjelasan: Menyalin semua isi folder saat ini ke folder situs di VM web. Ganti &lt;USER&gt;. Berkas lama dengan
nama sama akan tertimpa.
TIPS
Bila lebih suka antarmuka grafis, WinSCP memakai akun dan jalur yang sama. Berkas baru langsung disajikan; tidak
perlu restart.

## 40.5 Sisi klien: Android dan iPhone

1. Di rumah: buka https://web.home.arpa di Chrome (Android) atau Safari (iPhone). Di luar rumah nyalakan
Tailscale lebih dulu.
2. Gembok tanpa peringatan bergantung pada sertifikat akar (Suplemen 4 Bab 37.3 dan 37.4). Di iPhone jangan
lupa mengaktifkan kepercayaan sertifikat.
3. Opsional: Android Chrome &gt; Menu &gt; Tambahkan ke layar utama; iPhone Safari &gt; Bagikan &gt; Tambah ke
Layar Utama agar situs punya ikon sendiri.
CATATAN
Mengedit berkas situs langsung dari HP tidak dibahas di sini; lakukan dari laptop. Editor berbasis web (code studio)
ada di daftar rencana Anda untuk suplemen berikutnya.

## 40.6 Menambah situs kedua

1. Di VM web: buat folder mkdir /opt/stacks/web/sites/blog dan isi dengan berkas.
2. Di VM web: tambah blok http://blog.home.arpa { root \* /srv/sites/blog file_server } ke
/opt/stacks/web/Caddyfile, lalu docker exec sites caddy reload --config /etc/caddy/Caddyfile.
3. Di docker-core: tambah blok blog.home.arpa { reverse_proxy 192.168.88.28:8082 } ke Caddyfile gerbang
dan muat ulang seperti 40.3.


<!-- SOURCE: docs/bab/suplemen/41-wordpress.md -->

# Bab 41. WordPress dengan MariaDB

PENEMPATAN - GABUNG - ke VM web (sudah ada dari Bab 40)
Tempat: VM 209 web (192.168.88.28), berdampingan dengan situs statis. Tidak membuat VM baru.
Alasan: Database WordPress berada di jaringan Docker internal VM ini dan tidak terjangkau VM lain.
Mode hemat: Boleh digabung ke VM 206 (apps).
WordPress memakai image resmi dari Docker Hub (varian apache) dan MariaDB sebagai database, keduanya di
VM web (VM 209). Database ditaruh di jaringan Docker internal VM itu sehingga tidak terjangkau dari VM lain;
hanya port 8081 WordPress yang dibuka, dan firewall Proxmox membatasinya untuk docker-core.

## 41.1 Menyiapkan folder dan kata sandi

**TERMINAL VM WEB** | VM web (192.168.88.28), sebagai root

```
mkdir -p /opt/stacks/wordpress && cd /opt/stacks/wordpress
```
> Penjelasan: Folder aplikasi.
```
echo "WP_DB_PASSWORD=$(openssl rand -hex 16)" > .env
```
> Penjelasan: Membuat kata sandi database acak. Nilainya tidak tercatat di riwayat perintah.
```
echo "WP_DB_ROOT_PASSWORD=$(openssl rand -hex 16)" >> .env
```
> Penjelasan: Kata sandi root MariaDB, juga acak.
```
chmod 600 .env
```
> Penjelasan: Hanya root yang boleh membaca berkas ini.
```
nano compose.yaml
```
> Penjelasan: Isi seperti kotak di bawah.

**/opt/stacks/wordpress/compose.yaml** | Isi berkas

```
services:
  wp-db:
    image: mariadb:11
    container_name: wp-db
    restart: unless-stopped
    environment:
      MARIADB_DATABASE: wordpress
      MARIADB_USER: wordpress
      MARIADB_PASSWORD: ${WP_DB_PASSWORD}
      MARIADB_ROOT_PASSWORD: ${WP_DB_ROOT_PASSWORD}
    volumes:
      - ./db:/var/lib/mysql
    networks:
      - wp-internal
  wordpress:
    image: wordpress:6-apache
    container_name: wordpress
    restart: unless-stopped
    depends_on:
      - wp-db
    environment:
      WORDPRESS_DB_HOST: wp-db
      WORDPRESS_DB_USER: wordpress
      WORDPRESS_DB_PASSWORD: ${WP_DB_PASSWORD}
      WORDPRESS_DB_NAME: wordpress
    volumes:
      - ./html:/var/www/html
    ports:
      - "8081:80"
    networks:
      - wp-internal
networks:
  wp-internal:
```

Tag image: wordpress:6-apache dan mariadb:11 mengikuti pola tag Docker Hub yang umum [BELUM PASTI] -
periksa daftar tag di halaman Docker Hub wordpress dan mariadb sebelum memakainya; jika tag ditolak, pilih tag
varian apache yang tertera di sana.

## 41.2 Menyalakan dan menyambungkan ke Caddy

**TERMINAL VM WEB** | VM web, sebagai root di /opt/stacks/wordpress

```
docker compose up -d && docker compose ps
```
> Penjelasan: Mengunduh image dan menyalakan kedua container. Tunggu satu menit pada kali pertama.
Sekarang daftarkan WordPress di gerbang, yang berada di VM lain (docker-core):

**TERMINAL VM DOCKER-CORE** | VM docker-core (192.168.88.20), sebagai root

```
nano /opt/stacks/caddy/Caddyfile
```
> Penjelasan: Tambahkan blok di bawah ini.

**/opt/stacks/caddy/Caddyfile (tambahan)** | Tambahan

```
wp.home.arpa {
 reverse_proxy 192.168.88.28:8081
}
```

**TERMINAL VM DOCKER-CORE** | VM docker-core, sebagai root

```
docker exec caddy caddy reload --config /etc/caddy/Caddyfile
```
> Penjelasan: Memuat blok baru tanpa memutus layanan lain.

**TERMINAL VM WEB** | Kembali ke VM web, sebagai root

```
docker exec wordpress grep -n FORWARDED_PROTO /usr/src/wordpress/wp-config-docker.php
```
> Penjelasan: Memeriksa bahwa image sudah menangani header X-Forwarded-Proto (Caddy mengirimnya
otomatis). Jika ada baris hasil, WordPress akan mengenali HTTPS. Jika kosong, lihat tabel masalah di halaman
penutup.

## 41.3 Pemasangan lewat browser

1. Buka https://wp.home.arpa. Pilih bahasa.
2. Isi judul situs. Nama pengguna jangan admin; pakai nama lain. Gunakan kata sandi panjang dari pengelola
kata sandi, dan email yang bisa Anda akses.
3. Setelah masuk ke dasbor buka Settings &gt; General dan pastikan WordPress Address dan Site Address
berawalan https://wp.home.arpa.
4. Buka Settings &gt; Permalinks, pilih Post name, simpan.
5. Buka Dashboard &gt; Updates dan terapkan semua pembaruan.

## 41.4 Pengamanan dasar

• Tetap privat: jangan publikasikan WordPress lewat tunnel di buku ini.
• Pasang plugin seperlunya; setiap plugin menambah risiko. Hapus yang tidak dipakai (bukan sekadar
menonaktifkan).
• Aktifkan pembaruan otomatis untuk plugin dan tema dari Plugins &gt; Installed Plugins.
• Pertimbangkan autentikasi dua langkah lewat plugin yang Anda pilih sendiri setelah membaca ulasannya.
• Biarkan pengelola Docker (bukan WordPress) yang menangani sistem: jangan beri akses SSH ke container.

## 41.5 Sisi klien

Perangkat Cara Catatan
Windows Browser ke https://wp.home.arpa dan /wp-admin Gembok setelah sertifikat akar terpasang (Suplemen
4 Bab 37.2)
Android Chrome ke https://wp.home.arpa/wp-admin;
Tailscale aktif di luar rumah
Aplikasi resmi WordPress untuk Android mungkin
menolak CA lokal [BELUM PASTI]; pakai Chrome
bila gagal
iPhone Safari ke alamat yang sama; aktifkan kepercayaan
sertifikat
Aplikasi resmi WordPress iOS dengan CA lokal:
[BELUM PASTI]; Safari adalah jalur yang pasti

## 41.6 Backup WordPress

**TERMINAL VM WEB** | VM web (192.168.88.28), sebagai root

```
mkdir -p /opt/stacks/wordpress/backup
```
> Penjelasan: Folder hasil dump.
```
docker exec wp-db sh -c 'exec mariadb-dump -uroot -p"$MARIADB_ROOT_PASSWORD" --all-databases' > /opt/stacks/wordpress/backup/wp-$(date +%F).sql
```
> Penjelasan: Dump database ke berkas SQL bertanggal. Folder /opt/stacks/wordpress/html (berisi tema, plugin,
unggahan) ikut dibackup bersama folder lain.


<!-- SOURCE: docs/bab/suplemen/42-n8n.md -->

# Bab 42. n8n: Otomasi Alur Kerja

PENEMPATAN - BARU - VM sendiri
Tempat: VM 208 n8n (192.168.88.27): qm clone 200 208 --name n8n --full 1.
Alasan: n8n menyimpan kredensial ke layanan lain. Dipisahkan agar kebobolan di aplikasi web atau catatan tidak
membuka kunci n8n, dan sebaliknya.
Mode hemat: Boleh digabung ke VM 206 (apps).
n8n menghubungkan layanan lewat alur kerja visual (misalnya: terima webhook, lalu kirim notifikasi ke Gotify).
Pemasangan di sini mengikuti dokumentasi resmi n8n untuk Docker dan reverse proxy, dengan Postgres
sebagai database.
CATATAN
Panduan Compose resmi n8n yang terbaru memuat tumpukan sandbox untuk n8n Assistant (container privileged
Docker-in-Docker, disarankan minimal 4 GB RAM dan 2 vCPU). Bagian itu sengaja tidak dipakai di sini: berat, dan
container privileged setara akses root ke host. Hanya n8n dan Postgres yang dipasang; fitur n8n Assistant tidak aktif.

## 42.1 Membuat VM n8n, menyiapkan folder dan rahasia

**TERMINAL HOST PROXMOX** | Shell node Proxmox (host), sebagai root

```
qm clone 200 208 --name n8n --full 1
```
> Penjelasan: Membuat VM 208 bernama n8n sebagai salinan penuh dari templat VM 200 (Suplemen 7 Bab 49).
```
qm set 208 --memory 1536 --cores 2
```
> Penjelasan: RAM (MB) dan inti. Angka awal adalah perkiraan [BELUM PASTI]; sesuaikan setelah memantau di
Beszel.
```
qm start 208
```
> Penjelasan: Menyalakan. Lakukan penyiapan awal di Suplemen 7 Bab 49.4 (nama host, kunci SSH, alamat
192.168.88.27), lalu lanjut di bawah.
Langkah berikut dijalankan di VM n8n:

**TERMINAL VM N8N** | VM n8n (192.168.88.27), sebagai root (setelah su -)

```
mkdir -p /opt/stacks/n8n/data /opt/stacks/n8n/db /opt/stacks/n8n/backup
cd /opt/stacks/n8n
```
> Penjelasan: Folder aplikasi, data n8n, database, dan hasil backup.
```
chown -R 1000:1000 data
```
> Penjelasan: n8n berjalan sebagai pengguna node (uid 1000) di dalam container; tanpa ini muncul error izin pada
folder data.
```
echo "POSTGRES_PASSWORD=$(openssl rand -hex 16)" > .env
```
> Penjelasan: Kata sandi Postgres acak.
```
echo "N8N_ENCRYPTION_KEY=$(openssl rand -hex 32)" >> .env
```
> Penjelasan: Kunci enkripsi yang melindungi kredensial tersimpan di n8n. Simpan salinannya di luar server;
tanpa kunci ini kredensial tidak bisa dibuka lagi.
```
nano .env
```
> Penjelasan: Tambahkan baris versi di bawah isi yang sudah ada: N8N_VERSION=&lt;nomor versi stabil&gt; (lihat
catatan di bawah).
```
chmod 600 .env
```
> Penjelasan: Hanya root yang boleh membaca.
PERINGATAN
Nomor versi: dokumentasi n8n meminta Anda mengambil nomor rilis stabil terbaru dari halaman rilis di GitHub
(n8n-io/n8n). Sumber pihak ketiga yang saya temukan menyebut 2.29.10 sebagai contoh, tetapi itu belum saya
konfirmasi di halaman rilis resmi [BELUM PASTI]. Gunakan nomor yang tertera di halaman rilis pada hari Anda
memasang.

## 42.2 Berkas compose

**TERMINAL VM N8N** | VM n8n, sebagai root di /opt/stacks/n8n

```
nano compose.yaml
```
> Penjelasan: Isi seperti kotak di bawah.

**/opt/stacks/n8n/compose.yaml** | Isi berkas

```
services:
  n8n-db:
    image: postgres:18
    container_name: n8n-db
    restart: unless-stopped
    environment:
      POSTGRES_USER: n8n
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
      POSTGRES_DB: n8n
      PGDATA: /var/lib/postgresql/18/docker
    volumes:
      - ./db:/var/lib/postgresql
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -h localhost -U n8n -d n8n"]
      interval: 5s
      timeout: 5s
      retries: 10
    networks:
      - n8n-internal
  n8n:
    image: docker.n8n.io/n8nio/n8n:${N8N_VERSION}
    container_name: n8n
    restart: unless-stopped
    depends_on:
      n8n-db:
        condition: service_healthy
    environment:
      N8N_HOST: n8n.home.arpa
      N8N_PROTOCOL: https
      N8N_PORT: "5678"
      WEBHOOK_URL: https://n8n.home.arpa/
      N8N_PROXY_HOPS: "1"
      N8N_ENCRYPTION_KEY: ${N8N_ENCRYPTION_KEY}
      GENERIC_TIMEZONE: Asia/Jakarta
      TZ: Asia/Jakarta
      DB_TYPE: postgresdb
      DB_POSTGRESDB_HOST: n8n-db
      DB_POSTGRESDB_PORT: "5432"
      DB_POSTGRESDB_DATABASE: n8n
      DB_POSTGRESDB_USER: n8n
      DB_POSTGRESDB_PASSWORD: ${POSTGRES_PASSWORD}
    volumes:
      - ./data:/home/node/.n8n
    ports:
      - "5678:5678"
    networks:
      - n8n-internal
networks:
  n8n-internal:
```

Pengaturan Fungsi Sumber
WEBHOOK_URL (dengan garis
miring akhir)
Alamat webhook yang ditampilkan n8n dan didaftarkan ke
layanan luar; wajib di belakang reverse proxy
Dokumentasi resmi
n8n
N8N_PROXY_HOPS=1 Memberi tahu n8n bahwa ada satu proxy (Caddy) di depannya Dokumentasi resmi
n8n
N8N_ENCRYPTION_KEY Mengenkripsi kredensial tersimpan Dokumentasi resmi
n8n
GENERIC_TIMEZONE, TZ Zona waktu jadwal (Schedule trigger) Dokumentasi resmi
n8n
Pengaturan Fungsi Sumber
PostgreSQL 18 memakai direktori data versi khusus. Pertahankan nilai `PGDATA` dan mount volume induk ini; jangan menggantinya dengan pola PostgreSQL 17 ke bawah.
Dokumentasi image PostgreSQL resmi
Port 5678 dibuka untuk LAN dari VM ini; firewall Proxmox (Suplemen 7 Bab 51) hanya mengizinkan docker-core
menjangkaunya, sehingga n8n tetap hanya terbuka lewat Caddy. Caddy meneruskan WebSocket secara
otomatis, yang dibutuhkan editor n8n.

## 42.3 Menyalakan dan menyambungkan ke Caddy

**TERMINAL VM N8N** | VM n8n, sebagai root di /opt/stacks/n8n

```
docker compose up -d && docker compose ps
```
> Penjelasan: Menyalakan Postgres dan n8n. n8n baru mulai setelah Postgres berstatus healthy.
```
docker compose logs --tail=30 n8n
```
> Penjelasan: Mencari kalimat bahwa n8n siap dan tidak ada error database atau izin.
Daftarkan n8n di gerbang yang berada di VM docker-core:

**TERMINAL VM DOCKER-CORE** | VM docker-core (192.168.88.20), sebagai root

```
nano /opt/stacks/caddy/Caddyfile
```
> Penjelasan: Tambahkan blok di bawah ini.

**/opt/stacks/caddy/Caddyfile (tambahan)** | Tambahan

```
n8n.home.arpa {
 reverse_proxy 192.168.88.27:5678
}
```

**TERMINAL VM DOCKER-CORE** | VM docker-core, sebagai root

```
docker exec caddy caddy reload --config /etc/caddy/Caddyfile
```
> Penjelasan: Memuat blok n8n.
Buka https://n8n.home.arpa. Halaman pertama meminta pembuatan akun pemilik: isi email, nama, dan kata
sandi kuat. Itu satu-satunya akun yang punya kendali penuh.

## 42.4 Uji: webhook yang mengirim notifikasi ke Gotify

Alur uji ini membuktikan tiga hal sekaligus: n8n berjalan, Caddy meneruskan webhook, dan n8n dapat memanggil
Gotify di VM lain lewat LAN (VM n8n ke docker-core, diizinkan firewall Proxmox).
1. Di Gotify (https://gotify.home.arpa atau http://192.168.88.20:8070) buat aplikasi baru bernama n8n dan salin
tokennya.
2. Di n8n buat workflow baru. Tambah node Webhook: Method POST, Path uji.
3. Tambah node HTTP Request setelahnya: Method POST, URL http://192.168.88.20:8070/message (Gotify di
docker-core). Aktifkan pengiriman Header dengan nama X-Gotify-Key dan nilai token tadi. Body bertipe
JSON dengan field title (isi: Uji n8n) dan message (isi: Halo dari n8n).
4. Klik Listen for test event pada node Webhook, lalu kirim permintaan uji dari laptop (di bawah).

**POWERSHELL WINDOWS** | PowerShell (laptop)

```powershell
Invoke-RestMethod -Method Post -Uri "https://n8n.home.arpa/webhook-test/uji" -ContentType "application/json" -Body '{"pesan":"halo"}'
```
> Penjelasan: Mengirim POST ke alamat uji (webhook-test) n8n. Notifikasi "Uji n8n" harus tiba di aplikasi Gotify di HP Anda. Invoke-RestMethod dipakai karena kutip JSON di curl.exe sering rusak di PowerShell.
1. Bila berhasil, simpan workflow dan aktifkan sakelar Active. Alamat produksi berganti dari /webhook-test/uji
menjadi /webhook/uji.
TIPS
Jalur "test" hanya hidup selama Anda menekan Listen for test event; jalur produksi hanya hidup ketika workflow Active.
Kebingungan antara keduanya adalah sumber galat paling umum.

## 42.5 Keamanan n8n

• Pada node Webhook produksi, atur Authentication (Header Auth atau Basic Auth) agar tidak sembarang
perangkat di jaringan dapat memicu alur.
• Kredensial layanan lain disimpan terenkripsi dengan N8N_ENCRYPTION_KEY. Backup kunci itu terpisah
dari backup data.
• Jangan menaruh token penting dalam teks workflow; simpan lewat fitur Credentials.
• Tetap privat. Pembahasan webhook dari layanan luar ada di 42.7.

## 42.6 Sisi klien

Perangkat Cara memakai Catatan
Windows Browser ke https://n8n.home.arpa. Opsional:
Chrome/Edge Menu &gt; Instal sebagai aplikasi agar
punya jendela sendiri
Tempat terbaik untuk menyusun workflow
Android Chrome ke alamat yang sama, lalu Menu &gt; Tambahkan
ke layar utama. Tailscale aktif di luar rumah
Cocok untuk memantau eksekusi, kurang
nyaman untuk menyusun alur
iPhone Safari ke alamat yang sama, lalu Bagikan &gt; Tambah ke
Layar Utama. Aktifkan kepercayaan sertifikat
Sama seperti Android
Memicu dari HP Android: aplikasi HTTP Shortcuts. iPhone: aplikasi
Pintasan (Shortcuts), aksi "Get Contents of URL" ke
alamat webhook
Apakah kedua aplikasi menerima CA lokal
[BELUM PASTI] - uji; bila ditolak, picu dari
browser atau dari alur lain

## 42.7 Webhook dari layanan luar (Telegram, GitHub, dan sejenisnya)

Layanan luar harus bisa mencapai n8n lewat HTTPS dengan sertifikat publik. Alamat n8n.home.arpa tidak
dikenal di internet dan memakai CA lokal, jadi layanan seperti Telegram tidak akan bisa mengirim webhook ke
sana. Ada tiga pilihan:
Pilihan Penjelasan Penilaian
1. Picu dengan jadwal atau
polling
n8n yang menanyakan ke layanan luar secara berkala
(Schedule trigger atau node polling), tanpa jalur masuk
Dipilih buku ini: tanpa membuka
apa pun
2. Hostname tunnel khusus
untuk jalur webhook
Memublikasikan sebagian n8n lewat Cloudflare Tunnel Tidak dibahas: menambah risiko
pada layanan yang menyimpan
kredensial [BELUM PASTI] (praktik
pembatasan jalur belum saya
verifikasi)
3. Layanan relay di VPS
publik
Server kecil di luar rumah yang menerima webhook lalu
diteruskan lewat Tailscale
Butuh biaya dan perawatan
tambahan; di luar cakupan

## 42.8 Backup dan pembaruan

**TERMINAL VM N8N** | VM n8n, sebagai root di /opt/stacks/n8n

```
docker exec n8n-db pg_dump -U n8n n8n > backup/n8n-$(date +%F).sql
```
> Penjelasan: Dump database (berisi workflow, kredensial terenkripsi, riwayat). Simpan N8N_ENCRYPTION_KEY
terpisah dari berkas .env di luar server.
```
nano .env
```
> Penjelasan: Untuk memperbarui: ubah N8N_VERSION ke versi baru setelah membaca catatan rilis di GitHub.
```
docker compose pull && docker compose up -d
```
> Penjelasan: Mengunduh image baru dan membuat ulang container. Lakukan dump database terlebih dulu.


<!-- SOURCE: docs/bab/suplemen/43-cloudflare-tunnel.md -->

# Bab 43. Opsional: Situs Statis Publik dengan Cloudflare Tunnel

PENEMPATAN - BARU - VM sendiri, paling terisolasi
Tempat: VM 210 web-public (192.168.88.29): qm clone 200 210 --name web-public --full 1.
Alasan: Satu-satunya yang menghadap internet. Bila dibobol, penyerang tidak boleh punya jalan ke LAN: firewall
Proxmox memblokir keluar ke LAN (Bab 51.4).
Tidak boleh: Digabung dengan layanan lain, termasuk situs statis privat di VM 209.
PERINGATAN
Bab ini opsional. Kerjakan hanya bila Anda memang ingin situs bisa dibuka siapa pun. Yang dipublikasikan hanya
situs statis dalam container terpisah. Jangan memublikasikan WordPress, n8n, Portainer, Proxmox, atau Gotify.

## 43.1 Prasyarat dan cara kerja

• Akun Cloudflare dan domain milik sendiri yang DNS-nya dikelola Cloudflare (dokumentasi menyebut langkah
membuat catatan DNS untuk aplikasi). Biaya domain tahunan ada di luar buku ini.
• Langkah resmi: membuat tunnel di dasbor Cloudflare, menjalankan cloudflared dengan token, lalu menambah
published application route berisi hostname dan Service URL.
• Nama menu dasbor Cloudflare berubah dari waktu ke waktu [BELUM PASTI]; ikuti halaman Setup pada
developers.cloudflare.com/tunnel bila tampilan berbeda dari tulisan di bawah.
Pengunjung
www.domain-anda
Cloudflare
HTTPS publik
cloudflared
di VM, koneksi keluar
web-public
situs statis
Jaringan Docker terpisah (publicweb): tidak terhubung ke proxy, WordPress, n8n, atau Gotify
Gambar 43.1 - cloudflared membuat koneksi keluar; tidak ada port yang dibuka di router.

## 43.2 Mencoba dulu tanpa domain (quick tunnel)

Dokumentasi Cloudflare menyediakan perintah satu baris yang membuat alamat acak trycloudflare.com untuk
mencoba. Alamatnya berubah setiap kali dijalankan dan cocok untuk uji, bukan untuk penggunaan tetap [BELUM
PASTI] (sifat batasannya belum saya baca di dokumentasi). Siapkan dulu situs publik (43.3, langkah 1 sampai 3),
lalu:

**TERMINAL VM WEB-PUBLIC** | VM web-public, sebagai root

```
docker run --rm --network publicweb cloudflare/cloudflared:latest tunnel --url http://web-public:80
```
> Penjelasan: Menjalankan quick tunnel sementara untuk uji. Tag `latest` di sini hanya untuk uji sekali jalan; jangan gunakan untuk konektor tunnel permanen. Perintah menampilkan alamat
https://....trycloudflare.com; buka dari HP dengan data seluler. Hentikan dengan Ctrl+C.

## 43.3 Server: VM web-public dan situs publik

**TERMINAL HOST PROXMOX** | Shell node Proxmox (host), sebagai root

```
qm clone 200 210 --name web-public --full 1
```
> Penjelasan: Membuat VM 210 sebagai salinan penuh dari templat VM 200 (Suplemen 7 Bab 49).
```
qm set 210 --memory 768 --cores 1
```
> Penjelasan: RAM (MB) dan inti. Angka awal adalah perkiraan [BELUM PASTI].
```
qm start 210
```
> Penjelasan: Menyalakan. Lakukan penyiapan awal di Suplemen 7 Bab 49.4 (alamat 192.168.88.29), lalu pasang
firewall Proxmox untuk VM ini (Bab 51.4) sebelum membuka tunnel ke internet.
Langkah berikut dijalankan di VM web-public. VM ini sengaja tidak berbagi apa pun dengan VM web privat (209):

**TERMINAL VM WEB-PUBLIC** | VM web-public (192.168.88.29), sebagai root (setelah su -)

```
mkdir -p /opt/stacks/tunnel-web/public && cd /opt/stacks/tunnel-web
```
> Penjelasan: Folder khusus situs publik. Isinya terpisah dari situs privat di VM web.
```
nano public/index.html
```
> Penjelasan: Isi halaman publik. Boleh meniru contoh HTML di Bab 40.2, tetapi jangan menyalin folder situs privat.
```
docker network create publicweb
```
> Penjelasan: Jaringan Docker khusus yang tidak dihubungkan ke jaringan proxy.
```
nano Caddyfile
```
> Penjelasan: Isi seperti kotak di bawah.

**/opt/stacks/tunnel-web/Caddyfile** | Isi berkas

```
:80 {
 root * /srv
 encode gzip
 file_server
}
```

**TERMINAL VM WEB-PUBLIC** | VM web-public, sebagai root di /opt/stacks/tunnel-web

```
nano compose.yaml
```
> Penjelasan: Isi seperti kotak di bawah. Token ditaruh di .env pada langkah 43.4, bukan di berkas ini.

**/opt/stacks/tunnel-web/compose.yaml** | Isi berkas

```
services:
  web-public:
    image: caddy:2
    container_name: web-public
    restart: unless-stopped
    volumes:
      - ./Caddyfile:/etc/caddy/Caddyfile:ro
      - ./public:/srv:ro
    networks:
      - publicweb
  cloudflared:
    image: cloudflare/cloudflared:${CLOUDFLARED_VERSION}
    container_name: cloudflared
    restart: unless-stopped
    command: tunnel --no-autoupdate run --token ${TUNNEL_TOKEN}
    depends_on:
      - web-public
    networks:
      - publicweb
networks:
  publicweb:
    external: true
```

Container web-public memakai Caddy tersendiri pada port 80 di dalam jaringan publicweb saja; ia tidak memublikasikan port ke host. Perintah tunnel --no-autoupdate run --token mengikuti contoh Docker Cloudflare. Sebelum menjalankan Compose, isi `CLOUDFLARED_VERSION` di `.env` dengan tag versi yang telah diperiksa pada dokumentasi/rilis resmi Cloudflare. Jangan biarkan variabel kosong dan jangan memakai `latest` untuk konektor permanen.

## 43.4 Membuat tunnel di dasbor Cloudflare

1. Masuk ke dasbor Cloudflare dan buka bagian pengelolaan Tunnels (di area Zero Trust / Cloudflare One; letak
menu [BELUM PASTI]).
2. Buat tunnel baru, pilih konektor cloudflared, beri nama (misalnya home-web), lalu pilih lingkungan Docker.
3. Dasbor menampilkan perintah docker run dengan token panjang. Salin hanya token (teks setelah --token).
4. Di server, edit `/opt/stacks/tunnel-web/.env` secara lokal. Isi `TUNNEL_TOKEN=...` dengan token dari dasbor dan `CLOUDFLARED_VERSION=...` dengan tag versi yang sudah diverifikasi. Jangan kirim token ke chat atau GitHub. Setelah disimpan, jalankan `chmod 600 .env`.
5. Di dasbor, tambah Route bertipe Published application: hostname (misalnya www.domain-anda), Service
URL http://web-public:80. Dasbor membuat catatan DNS yang diperlukan.

**TERMINAL VM WEB-PUBLIC** | VM web-public, sebagai root di /opt/stacks/tunnel-web

```
docker compose up -d && docker compose logs --tail=20 cloudflared
```
> Penjelasan: Menyalakan dan memeriksa log. Cari tanda koneksi tunnel terdaftar; di dasbor status tunnel berubah
menjadi sehat.
KEAMANAN
Token tunnel setara kunci: pemegangnya dapat menjalankan tunnel Anda. Jangan dibagikan atau dimasukkan ke
repositori. Bila bocor, ganti (rotasi) token di dasbor dan perbarui .env. Cloudflare menyediakan pembatasan akses
(Access) untuk menaruh login di depan alamat tertentu [BELUM PASTI] (tidak dikaji di sini).

## 43.5 Sisi klien

Perangkat Cara uji Hasil yang diharapkan
Windows Buka https://www.domain-anda di browser Halaman tampil dengan gembok; tidak perlu
sertifikat tambahan
Android Matikan Wi-Fi dan Tailscale, buka alamat di Chrome
lewat data seluler
Halaman tampil; membuktikan situs
benar-benar publik
iPhone Sama, di Safari lewat data seluler Halaman tampil tanpa langkah kepercayaan
sertifikat
Mengubah isi Dari laptop: scp ke
&lt;USER&gt;@192.168.88.29:/opt/stacks/tunnel-web/public
(ubah kepemilikan folder ke pengguna biasa seperti Bab
40.2)
Berkas baru langsung tampil, tanpa restart
CATATAN
Sertifikat HTTPS untuk jalur publik berasal dari Cloudflare, sehingga semua perangkat memercayainya tanpa
memasang apa pun. Ini berbeda dari jalur privat yang memakai CA lokal Caddy.


<!-- SOURCE: docs/bab/suplemen/44-jalur-sertifikat-tailscale-serve.md -->

# Bab 44. Jalur Sertifikat per Aplikasi dan Tailscale Serve

PENEMPATAN - BARU - VM vault dibuat di bab ini
Tempat: VM 205 vault (192.168.88.24), dibuat di Bab 44.3 dengan qm clone 200 205 --name vault --full 1. Node
tailnet lab-vault ada di dalamnya; tidak ada lagi node untuk docker-core.
Alasan: Setiap VM yang memakai Tailscale Serve mendapat nama .ts.net sendiri di port 443; tidak perlu port 8443,
8444, dan seterusnya.

## 44.1 Masalahnya: aplikasi HP tidak sama dengan browser

Di Suplemen 4 Anda memasang sertifikat akar Caddy di HP, dan browser mempercayainya. Tetapi aplikasi di
Android sering memakai daftar sertifikat sendiri atau sistem saja. Untuk Bitwarden, laporan pengguna di forum
Vaultwarden dan Bitwarden menyebut aplikasi Android gagal dengan galat "Trust anchor for certification path not
found" walau sertifikat sudah dipasang; solusi yang berhasil bagi mereka adalah sertifikat publik. Dokumentasi
Bitwarden sendiri menyatakan sertifikat buatan sendiri tidak dipercaya klien secara bawaan dan hanya disarankan
untuk uji. Ini bukti dari laporan pengguna, bukan jaminan untuk perangkat Anda [BELUM PASTI].
Aplikasi Yang diketahui tentang CA lokal Keputusan buku ini
Bitwarden (Android, iPhone,
ekstensi)
Laporan kegagalan di Android; klien memerlukan
kepercayaan sertifikat
Jalur 1: sertifikat tepercaya dari
Tailscale Serve
AFFiNE (desktop, Android,
iPhone)
Tidak ada informasi yang saya temukan [BELUM PASTI] Jalur 2 (CA lokal); pindah ke Jalur
1 bila aplikasi menolak
DAVx5 (kalender Android) Mendukung sertifikat buatan sendiri; catatan rilisnya
menyebut penanganan sertifikat khusus; ada laporan
pengguna berhasil dengan CA sendiri di Android 14
Jalur 2
Kalender iPhone bawaan Memakai kepercayaan sistem; sertifikat akar yang Anda
aktifkan di Bab 37.4 berlaku
Jalur 2
Thunderbird (Windows) Penyimpanan sertifikat sendiri; akar harus diimpor (lihat
47.6)
Jalur 2
Jalur 1 - Vaultwarden: sertifikat tepercaya dari Tailscale Serve
Jalur 2 - AFFiNE dan Nextcloud: CA lokal Caddy (Suplemen 4)
HP / Laptop
Tailscale aktif
Tailscale Serve
https://...ts.net
127.0.0.1:8081
hanya di dalam VM
Vaultwarden
kata sandi
HP / Laptop
rumah atau Tailscale
AdGuard
\*.home.arpa
Caddy :443
sertifikat CA lokal
Layanan
AFFiNE, Nextcloud
Gambar 44.1 - Dua jalur HTTPS: Serve untuk kata sandi, Caddy untuk layanan lain.

## 44.2 Tailscale Serve: HTTPS tepercaya tanpa membeli domain

Tailscale Serve memberi perangkat Anda sebuah nama di MagicDNS (berakhiran .ts.net), mengurus sertifikat
yang dipercaya semua perangkat, dan meneruskan permintaan ke port lokal. Menurut dokumentasi Tailscale,
Serve hanya dapat diakses anggota tailnet Anda dan tidak membuka layanan ke internet. Jangan dikacaukan
dengan Funnel, yang memang membuka ke internet. Di buku ini Funnel tidak pernah dipakai.
Hal Penjelasan
Syarat MagicDNS dan HTTPS Certificates aktif di halaman DNS konsol admin Tailscale
Alamat https://NAMA-PERANGKAT.NAMA-TAILNET.ts.net. Satu VM = satu nama. Karena setiap layanan
sensitif berada di VM sendiri (lab-vault, dan lab-affine bila perlu), semuanya memakai port 443 tanpa
port tambahan
Akses Hanya perangkat di tailnet Anda dengan Tailscale aktif, termasuk saat di rumah
Privasi Nama tailnet Anda tercantum di catatan sertifikat publik (Certificate Transparency); isi vault tidak ikut.
Seperti dicatat di Suplemen 4 Bab 35.2
Alternatif Tailscale Services memberi satu nama per layanan di port 443, tetapi membutuhkan pengaturan
tambahan di konsol admin [BELUM PASTI] dan tidak dipakai di sini

## 44.3 Membuat VM vault dan memasang Tailscale di dalamnya

Router-vm (CT103) hanya meneruskan LAN. Serve harus berjalan di mesin yang menjalankan layanannya, jadi
VM vault yang baru menjadi perangkat tailnet kedua dengan nama lab-vault. Perangkat ini tidak
mengumumkan rute. Buat VM-nya dulu:

**TERMINAL HOST PROXMOX** | Shell node Proxmox (host), sebagai root

```
qm clone 200 205 --name vault --full 1
```
> Penjelasan: Membuat VM 205 bernama vault sebagai salinan penuh dari templat VM 200 (Suplemen 7 Bab 49).
```
qm set 205 --memory 1024 --cores 1
```
> Penjelasan: RAM (MB) dan inti. Vaultwarden ringan; angka awal adalah perkiraan [BELUM PASTI].
```
qm start 205
```
> Penjelasan: Menyalakan. Lakukan penyiapan awal di Suplemen 7 Bab 49.4 (nama host vault, kunci SSH, alamat
192.168.88.24), lalu lanjut di bawah.

**TERMINAL VM VAULT** | VM vault (192.168.88.24), sebagai root (setelah su -)

```
curl -fsSL https://tailscale.com/install.sh | sh
```
> Penjelasan: Memasang Tailscale resmi (cara yang sama seperti Suplemen 1 Bab 26.3).
```
tailscale up --hostname=lab-vault --accept-dns=false
```
> Penjelasan: Menghubungkan ke akun dan memberi nama lab-vault. --accept-dns=false menjaga DNS server
tidak berubah. Buka tautan login yang tampil di browser laptop.
```
tailscale status
```
> Penjelasan: lab-vault harus muncul hidup. Catat nama panjangnya (NAMA.TAILNET.ts.net) dari konsol admin
pada halaman Machines.
1. Di konsol admin buka Machines, klik ... pada lab-vault &gt; Disable key expiry agar server tidak terputus ketika
kunci kedaluwarsa.
2. Buka halaman DNS: pastikan MagicDNS aktif dan aktifkan HTTPS Certificates (ada peringatan bahwa nama
tailnet menjadi publik di catatan sertifikat; baca lalu setujui).
3. Kebijakan terbaru di Suplemen 1 Bab 26.6 sudah memuat izin TCP 443 untuk node milik admin. Jika Anda memakai kebijakan lama, tambahkan aturan pada kotak berikut ke daftar `grants`; pastikan sumbernya hanya grup admin.

**Tambahan pada tailnet policy (di dalam "grants")** | Tambahan

```
 {
 "src": ["group:home-admins"],
 "dst": ["autogroup:self"],
 "ip": ["tcp:443"],
 },
```

Tanpa entri ini lab-vault tidak terjangkau dari HP. Aturan memakai `autogroup:self` untuk membatasi akses grup
admin ke node yang dimiliki anggotanya pada TCP 443. ACL lama dapat memakai bentuk berikut dengan sumber grup admin: "acls": [{
"action": "accept", "src": ["group:home-admins"], "dst": ["autogroup:self:443"] }]. Karena tiap VM punya
nama .ts.net sendiri di port 443, satu entri ini cukup untuk semua node Serve milik Anda.
KEAMANAN
Simpan salinan JSON kebijakan lama sebelum mengubah (Suplemen 1 Bab 26.6). Kesalahan kebijakan bisa
memutus akses Anda sendiri.

## 44.4 Sisi klien

Perangkat Yang perlu dipastikan
Windows Tailscale berjalan (ikon di dekat jam). Uji: buka https://lab-vault.NAMA-TAILNET.ts.net setelah Bab 45
Android Tailscale terpasang, VPN aktif (Suplemen 1 Bab 26.4). Biarkan aktif juga di rumah agar nama .ts.net
terjawab
iPhone Tailscale terpasang dan aktif (Suplemen 1 Bab 26.5). Aktif juga di rumah
CATATAN
Konsekuensinya: vault kata sandi hanya dapat disinkronkan saat Tailscale aktif. Aplikasi Bitwarden menyimpan
salinan vault di perangkat, sehingga mengisi kata sandi tetap bisa saat offline; yang tertunda hanya sinkronisasi.


<!-- SOURCE: docs/bab/suplemen/bagian-5-99-penutup.md -->

# Bagian 5. Hosting Web dan n8n: Uji, Masalah Umum, Lembar Pembaruan, Syarat Lulus Fase 5

Uji, Masalah Umum, dan Lembar Pembaruan
Uji menyeluruh
No Uji Hasil yang diharapkan
1 Caddy validate setelah semua blok ditambah Valid configuration
2 Laptop: https://web.home.arpa Halaman Halo, gembok tanpa peringatan
3 Laptop: https://wp.home.arpa, selesaikan pemasangan Dasbor WordPress; alamat Site dan WordPress
berawalan https
4 Laptop: https://n8n.home.arpa, buat akun pemilik Editor n8n terbuka
5 Webhook uji ke /webhook-test/uji Notifikasi tiba di Gotify di HP
6 Aktifkan workflow, panggil /webhook/uji dengan autentikasi Notifikasi tiba; tanpa kredensial ditolak
7 HP Android dan iPhone: tiga alamat privat (WiFi rumah) Terbuka dengan gembok
8 HP, data seluler, Tailscale aktif Tiga alamat privat tetap terbuka
9 Opsional: HP data seluler, Tailscale mati, alamat publik Situs statis publik tampil; alamat home.arpa tidak
terbuka
10 Uptime Kuma: tambah monitor untuk web, wp, dan n8n Semua hijau
Masalah dan solusi
Gejala Penyebab Solusi
502 Bad Gateway pada web,
wp, atau n8n
Container belum siap, port tidak
dibuka, atau firewall Proxmox
menolak docker-core
Di VM tujuan: docker compose ps; ss -tlnp. Dari
docker-core: timeout 3 bash -c '&lt;/dev/tcp/IP-VM/PORT' &&
echo terbuka
WordPress: "Error
establishing a database
connection"
MariaDB belum selesai inisialisasi
atau kata sandi .env berubah
setelah database dibuat
docker compose logs wp-db; bila kata sandi diubah
sesudah inisialisasi, hapus folder db hanya jika belum ada
data penting
WordPress: loop pengalihan
atau halaman tanpa gaya
WordPress tidak mengenali
HTTPS di belakang proxy
Ulangi pemeriksaan grep di 41.2; periksa Site Address
berawalan https; bila grep kosong, tambahkan
penanganan X-Forwarded-Proto lewat
WORDPRESS_CONFIG_EXTRA mengikuti dokumentasi
image
n8n: error izin pada
/home/node/.n8n
Folder data bukan milik uid 1000 chown -R 1000:1000 /opt/stacks/n8n/data
n8n: cookie aman / tidak bisa
login lewat IP
n8n menuntut HTTPS untuk
cookie
Selalu buka lewat https://n8n.home.arpa, bukan IP dan
port
n8n: alamat webhook tampil
localhost
WEBHOOK_URL salah atau
tanpa garis miring akhir
Perbaiki di compose, docker compose up -d
n8n: webhook produksi 404 Workflow belum Active, atau
memakai alamat webhook-test
Aktifkan workflow dan pakai /webhook/...
Postgres: data tidak bertahan
setelah container dibuat ulang
Volume tidak dipasang ke direktori induk PostgreSQL 18 atau PGDATA tidak sesuai
Gunakan ./db:/var/lib/postgresql dan PGDATA=/var/lib/postgresql/18/docker; backup sebelum naik versi mayor
Tunnel: halaman 502 atau
1033 di alamat publik
cloudflared tidak terhubung atau
Service URL salah
docker compose logs cloudflared; pastikan Service URL
http://web-public:80 dan kedua container di jaringan
publicweb
Lembar pembaruan
Bab sebelumnya Perubahan Rujukan
Suplemen 4, Bab 36.3 Tidak ada perubahan compose Caddy. Caddy tidak lagi
menyajikan berkas; hanya meneruskan
Bab 40.3
Suplemen 4, Bab 36.6 Caddyfile bertambah: web, wp, n8n sebagai reverse_proxy ke
IP:port VM masing-masing
Bab 40, 41, 42
Suplemen 7, Bab 48-51 Peta penempatan VM, templat VM 200, dan firewall Proxmox
yang membatasi port 8081, 8082, 5678
Suplemen 7
Suplemen 3, Bab 32 Tambah monitor Uptime Kuma untuk tiga alamat baru (Ignore
TLS error)
Uji no. 10
Suplemen 1, Bab 25 Jalur publik tidak membuka port masuk; firewall tidak berubah.
Jaringan Docker publicweb dipisah
Bab 43
Edisi 2, Bab 19 dan Suplemen 3
Bab 34.2
Tambah kartu dashboard Homepage untuk situs, WordPress, n8n Bab 40-42
Edisi 2, Bab 23 dan Suplemen 3
Bab 34.3
Backup tambahan: /opt/stacks/web, wordpress (html dan dump
SQL), n8n (dump SQL; kunci enkripsi disimpan terpisah),
tunnel-web (tanpa .env di tempat bersama)
Bab 41.6, 42.8
Daftar hal yang belum dipastikan
No Hal Cara memastikan
1 Tag wordpress:6-apache dan mariadb:11 ada di Docker Hub Cek halaman tag; bila tidak ada pilih tag apache
terdekat
2 Nomor versi n8n stabil terkini (contoh 2.29.10 dari sumber pihak
ketiga)
Ambil dari halaman rilis n8n-io/n8n
3 Perkiraan RAM WordPress dan n8n Ukur dengan Beszel
4 Aplikasi WordPress, HTTP Shortcuts, dan Pintasan menerima CA
lokal
Uji di perangkat; bila ditolak pakai browser
5 Letak menu dasbor Cloudflare (Tunnels) dan batasan quick tunnel Ikuti halaman Setup di
developers.cloudflare.com/tunnel
6 Biaya domain dan apakah Tunnel gratis untuk kebutuhan Anda Cek halaman harga Cloudflare dan pendaftar
domain
7 Pembatasan akses (Cloudflare Access) dan webhook sebagian jalur Tidak dikaji; baca dokumentasi sebelum
mencoba
8 Alamat IP publik IndiHome dinamis atau berbagi Tidak berpengaruh pada tunnel; hanya relevan
bila port forwarding
Syarat lulus Fase 5
No Poin Ya / Tidak
1 web.home.arpa, wp.home.arpa, n8n.home.arpa terbuka dengan HTTPS di laptop dan HP
2 WordPress terpasang, pembaruan diterapkan, akun bukan bernama admin
3 n8n berjalan di Postgres; webhook uji mengirim notifikasi ke Gotify
4 Webhook produksi memakai autentikasi
5 Dump SQL WordPress dan n8n serta kunci enkripsi n8n tersimpan di luar server
6 Bila bab 43 dikerjakan: situs publik tampil dari data seluler, layanan privat tidak terbuka
Berikutnya (Suplemen 6): AFFiNE, kalender Nextcloud, dan Vaultwarden, masing-masing dengan sisi klien
Windows, Android, dan iPhone. Vaultwarden dan AFFiNE sangat bergantung pada HTTPS yang benar; hasil uji
Suplemen 4 akan menentukan apakah jalur CA lokal cukup.


<!-- SOURCE: docs/bab/suplemen/bagian-6-00-pengantar.md -->

# Bagian 6. Vaultwarden, AFFiNE, dan Kalender Nextcloud (pengantar)

Bagian 6. Vaultwarden, AFFiNE, dan Kalender
Nextcloud
Asal: Suplemen 6. Bab 44-47.
Suplemen 6 memasang tiga layanan pribadi yang menyimpan data paling sensitif di server Anda: kata sandi
(Vaultwarden), catatan dan dokumen bergaya Notion (AFFiNE), dan kalender (Nextcloud). Ketiganya punya
aplikasi di HP, dan di situlah persoalan sertifikat HTTPS dari Suplemen 4 menjadi penting.
Bab Isi Hasil akhir
44. Jalur sertifikat per
aplikasi
Mengapa aplikasi HP bisa menolak CA lokal; Tailscale
Serve sebagai jalur tepercaya tanpa domain
Tahu aplikasi mana memakai jalur
mana
45. Vaultwarden Server kata sandi, akun, aplikasi Windows, Android,
iPhone, backup
Kata sandi tersinkron di semua
perangkat
46. AFFiNE Server catatan, aplikasi desktop dan HP, backup Catatan tersinkron di semua
perangkat
47. Nextcloud dan Kalender Server Nextcloud, aplikasi Calendar, sinkron ke
Thunderbird, Android (DAVx5), iPhone
Kalender pribadi pengganti Google
Calendar
Prasyarat
• Caddy, jaringan Docker proxy, dan sertifikat akar terpasang di perangkat (Suplemen 4); struktur /opt/stacks
(Suplemen 3).
• Tailscale dengan router-vm (Suplemen 1 Bab 26) dan kebijakan jaringan yang sudah Anda ubah di Bab 26.6.
• VM 205 vault, 206 affine, dan 207 nextcloud dibuat dari templat VM 200 (Suplemen 7 Bab 48-49). Caddy
tetap di VM 201 docker-core.
• Semua perintah server dijalankan sebagai root setelah su - (tanpa sudo), di guest yang ditunjuk Kotak
Penempatan di awal tiap bab.
PERINGATAN
Suplemen 1 sampai 5 belum Anda uji. Suplemen ini bergantung pada Tailscale (Suplemen 1), Caddy dan sertifikat
(Suplemen 4). Kerjakan Bab 44 setelah Tailscale dan Bab 37 terbukti jalan, dan laporkan hasilnya.
KEAMANAN
Data di sini tidak tergantikan (kata sandi, kalender, catatan). Backup yang tersimpan hanya di server yang sama
bukan backup. Proxmox Backup Server dibahas di Suplemen 7; sampai saat itu salin backup secara manual ke laptop
atau disk luar.
CATATAN
Hal yang belum bisa saya pastikan dari dokumentasi ditandai [BELUM PASTI] dan dikumpulkan di tabel pada
halaman penutup.


<!-- SOURCE: docs/bab/suplemen/45-vaultwarden.md -->

# Bab 45. Vaultwarden: Pengelola Kata Sandi

PENEMPATAN - VM vault dari Bab 44.3 (tidak membuat VM baru)
Tempat: VM 205 vault (192.168.88.24).
Alasan: Data paling sensitif. Hanya menjalankan Vaultwarden dan Tailscale; tanpa Caddy, tanpa port di LAN;
satu-satunya pintu adalah Tailscale Serve.
Tidak boleh: Digabung dengan layanan lain, termasuk pada mode hemat.
Vaultwarden adalah server yang kompatibel dengan klien Bitwarden resmi. Anda memakai aplikasi dan ekstensi
Bitwarden biasa, tetapi datanya tersimpan di server Anda. Vaultwarden dijalankan di VM vault sendiri (dibuat di
Bab 44.3) dan hanya lewat Tailscale Serve, tanpa Caddy dan tanpa port yang terbuka di LAN.
PERINGATAN
Tidak ada pemulihan kata sandi utama. Isi vault terenkripsi dengan kata sandi utama yang hanya Anda ketahui. Jika
lupa, data tidak dapat dibuka siapa pun, termasuk Anda dan saya. Tulis di kertas dan simpan di tempat aman.

## 45.1 Server

**TERMINAL VM VAULT** | VM vault (192.168.88.24), sebagai root

```
mkdir -p /opt/stacks/vaultwarden/data /opt/stacks/vaultwarden/backup
cd /opt/stacks/vaultwarden
```
> Penjelasan: Membuat folder aplikasi, data, dan hasil backup.
```
echo "TS_HOST=lab-vault.NAMA-TAILNET.ts.net" > .env
```
> Penjelasan: Ganti dengan nama panjang lab-vault dari konsol admin. Jangan ada spasi.
```
echo "VW_VERSION=TAG_RILIS_TER_VERIFIKASI" >> .env
```
> Penjelasan: Ganti nilai contoh dengan tag rilis tertentu yang telah diperiksa pada halaman rilis resmi Vaultwarden **sebelum** menjalankan Compose. Jangan gunakan `latest` untuk pengelola kata sandi; catat tag yang dipilih agar pembaruan dapat dikendalikan.
```
chmod 600 .env && nano compose.yaml
```
> Penjelasan: Isi seperti kotak di bawah.

**/opt/stacks/vaultwarden/compose.yaml** | Isi berkas

```
services:
  vaultwarden:
    image: vaultwarden/server:${VW_VERSION}
    container_name: vaultwarden
    restart: unless-stopped
    environment:
      DOMAIN: "https://${TS_HOST}"
      SIGNUPS_ALLOWED: "true"
      TZ: Asia/Jakarta
    volumes:
      - ./data:/data
    ports:
      - "127.0.0.1:8081:80"
```

Pengaturan Fungsi
DOMAIN Alamat tunggal yang dipakai Vaultwarden untuk tautan dan WebAuthn. Harus sama persis
dengan alamat yang dibuka klien (tanpa port tambahan, karena memakai 443)
SIGNUPS_ALLOWED Sementara true agar Anda bisa membuat akun sendiri; diubah ke false di 45.3
127.0.0.1:8081:80 Port hanya terbuka di dalam VM, tidak di LAN. Tailscale Serve meneruskan ke sini
Pengaturan Fungsi
Tanpa ADMIN_TOKEN Halaman admin /admin sengaja tidak aktif (dokumentasi Vaultwarden: halaman admin mati bila
ADMIN_TOKEN tidak diatur). Mengurangi permukaan serangan

**TERMINAL VM VAULT** | VM vault, sebagai root di /opt/stacks/vaultwarden

```
docker compose up -d && docker compose logs --tail=20
```
> Penjelasan: Menyalakan dan melihat log. Cari baris yang menyebut server mendengarkan di port 80 dan tidak ada
error.
```
tailscale serve --bg --https=443 8081
```
> Penjelasan: Mengaktifkan Serve: HTTPS port 443 di nama lab-vault diteruskan ke 127.0.0.1:8081. Pada kali
pertama sertifikat diminta dan butuh beberapa detik.
```
tailscale serve status
```
> Penjelasan: Memeriksa. Harus ada rute https://lab-vault....ts.net menuju proxy ke 8081.
KEAMANAN
Jangan pernah menjalankan tailscale funnel untuk layanan ini. Funnel membuka alamat ke internet; Serve tidak.

## 45.2 Membuat akun pertama

1. Dari laptop dengan Tailscale aktif, buka https://lab-vault.NAMA-TAILNET.ts.net. Halaman vault Bitwarden
harus tampil dengan gembok tanpa peringatan.
2. Klik Create account. Isi email, nama, dan kata sandi utama yang panjang (frasa beberapa kata lebih
mudah diingat dan lebih kuat).
3. Masuk, lalu buka Settings &gt; Security &gt; Two-step login dan aktifkan aplikasi autentikator (TOTP). Simpan
kode pemulihan di kertas.

## 45.3 Menutup pendaftaran

**TERMINAL VM VAULT** | VM vault, sebagai root di /opt/stacks/vaultwarden

```
sed -i 's/SIGNUPS_ALLOWED: "true"/SIGNUPS_ALLOWED: "false"/' compose.yaml
```
> Penjelasan: Mengubah pengaturan pendaftaran menjadi false: tidak ada akun baru yang bisa dibuat orang lain.
```
docker compose up -d
```
> Penjelasan: Menerapkan perubahan. Akun Anda tetap ada.
```
grep SIGNUPS compose.yaml
```
> Penjelasan: Memastikan nilainya false.

## 45.4 Sisi klien

Windows
1. Pasang ekstensi Bitwarden di Chrome, Edge, atau Firefox dari toko ekstensi resmi, dan opsional aplikasi
desktop dari bitwarden.com/download.
2. Pada layar login, ketuk pemilih wilayah/server (bertulis bitwarden.com) dan pilih Self-hosted. Di kolom
Server URL isi https://lab-vault.NAMA-TAILNET.ts.net, simpan.
3. Masuk dengan email dan kata sandi utama; masukkan kode autentikator.
Android
1. Pasang Bitwarden dari Google Play Store. Pastikan Tailscale aktif.
2. Di layar login ketuk pemilih server (bitwarden.com) &gt; Self-hosted &gt; isi Server URL yang sama &gt; Simpan.
3. Masuk. Aktifkan isi otomatis: Pengaturan &gt; Kata sandi dan akun (atau Isi otomatis) &gt; Layanan isi
otomatis &gt; Bitwarden. Nama menu berbeda antar merek HP.
iPhone
1. Pasang Bitwarden dari App Store. Pastikan Tailscale aktif.
2. Di layar login ketuk pemilih server &gt; Self-hosted &gt; isi Server URL yang sama &gt; Simpan, lalu masuk.
3. Aktifkan isi otomatis: Pengaturan &gt; Kata Sandi &gt; Opsi Kata Sandi &gt; Isi Otomatis Kata Sandi dan Kunci
Sandi &gt; Bitwarden. Nama menu bergantung versi iOS.
TIPS
Bila aplikasi HP gagal tersambung padahal browser berhasil membuka alamat yang sama, itu bukan masalah sertifikat
(Jalur 1 memakai sertifikat tepercaya). Periksa Tailscale aktif, alamat .ts.net yang benar (tanpa salah ketik), dan aturan
kebijakan Bab 44.3.

## 45.5 Backup Vaultwarden

Cara paling sederhana dan aman terhadap korupsi adalah menghentikan container sebentar, menyalin folder
data, lalu menyalakannya kembali. Vaultwarden mungkin menyediakan perintah backup daring bawaan [BELUM
PASTI] (belum saya verifikasi di dokumentasi), jadi cara ini yang dipakai.

**TERMINAL VM VAULT** | VM vault, sebagai root di /opt/stacks/vaultwarden

```
docker compose stop && tar czf backup/vw-$(date +%F).tgz data && docker compose start
```
> Penjelasan: Berhenti sebentar (beberapa detik), mengarsipkan seluruh folder data bertanggal, lalu menyala
kembali.
```
ls -l backup
```
> Penjelasan: Memastikan arsip ada.
PERINGATAN
Salin arsip ke luar server (laptop atau disk luar) secara berkala. Selain itu, dari aplikasi Bitwarden Anda dapat
mengekspor vault (Tools &gt; Export vault) ke berkas terenkripsi sebagai cadangan kedua; simpan berkas itu di tempat
aman karena berkas yang tidak terenkripsi berisi semua kata sandi dalam teks biasa.


<!-- SOURCE: docs/bab/suplemen/46-affine.md -->

# Bab 46. AFFiNE: Catatan dan Dokumen Bergaya Notion

PENEMPATAN - BARU - VM sendiri
Tempat: VM 206 affine (192.168.88.25): qm clone 200 206 --name affine --full 1.
Alasan: Berisi PostgreSQL, Redis, dan unggahan sendiri; siklus pembaruan berbeda dari layanan lain.
Mode hemat: Inilah VM 206 yang berganti nama menjadi apps dan menampung n8n serta web.
AFFiNE adalah aplikasi catatan, dokumen, dan papan tulis. Server self-host terdiri dari empat bagian menurut
dokumentasinya: aplikasi AFFiNE, tugas migrasi database sekali jalan, Redis, dan PostgreSQL dengan ekstensi
pgvector. Layanan ini lewat Caddy (Jalur 2, https://affine.home.arpa).
PERINGATAN
Nama image dan tata letak berkas compose resmi AFFiNE berubah antar versi. Sumber yang saya baca
menyebut ghcr.io/toeverything/affine dan ghcr.io/toeverything/affine-graphql [BELUM PASTI]. Karena itu di 46.1 ada
langkah membandingkan dengan berkas compose resmi dari rilis terbaru sebelum menyalakan.

## 46.1 Membuat VM affine dan menyiapkan server

**TERMINAL HOST PROXMOX** | Shell node Proxmox (host), sebagai root

```
qm clone 200 206 --name affine --full 1
```
> Penjelasan: Membuat VM 206 bernama affine sebagai salinan penuh dari templat VM 200 (Suplemen 7 Bab 49).
```
qm set 206 --memory 2048 --cores 2
```
> Penjelasan: RAM (MB) dan inti. Kebutuhan sebenarnya belum bisa saya pastikan [BELUM PASTI]; mulai dari
angka ini dan pantau di Beszel.
```
qm start 206
```
> Penjelasan: Menyalakan. Lakukan penyiapan awal di Suplemen 7 Bab 49.4 (nama host, kunci SSH, alamat
192.168.88.25), lalu lanjut di bawah.
Langkah berikut dijalankan di VM affine:

**TERMINAL VM AFFINE** | VM affine (192.168.88.25), sebagai root (setelah su -)

```
mkdir -p /opt/stacks/affine/{config,storage,db,backup} && cd /opt/stacks/affine
```
> Penjelasan: Folder konfigurasi, unggahan, database, dan backup.
```
curl -fsSL -o /root/affine-resmi.yml https://github.com/toeverything/AFFiNE/releases/latest/download/docker-compose.yml
grep -n "image:" /root/affine-resmi.yml
```
> Penjelasan: Mengunduh berkas compose resmi dari rilis terbaru hanya untuk dibandingkan. Bila nama image di
sana berbeda dari yang ada di kotak compose di bawah, pakai nama dari berkas resmi.
```
openssl rand -hex 16
```
> Penjelasan: Menampilkan kata sandi database acak. Salin untuk dipakai di langkah berikutnya.
```
nano .env
```
> Penjelasan: Isi seperti kotak di bawah dan tempel kata sandi tadi di dua tempat (DB_PASSWORD dan
DATABASE_URL). DATABASE_URL ditaruh di .env karena compose resmi merangkainya dari variabel yang
sama.
```
chmod 600 .env && nano compose.yaml
```
> Penjelasan: Isi compose seperti kotak berikutnya.

**/opt/stacks/affine/.env** | Isi berkas

```
AFFINE_REVISION=stable
DB_USERNAME=affine
DB_DATABASE=affine
DB_PASSWORD=TEMPEL-KATA-SANDI-DI-SINI
DATABASE_URL=postgresql://affine:TEMPEL-KATA-SANDI-DI-SINI@postgres:5432/affine
DB_DATA_LOCATION=./db
UPLOAD_LOCATION=./storage
CONFIG_LOCATION=./config
AFFINE_SERVER_EXTERNAL_URL=https://affine.home.arpa
AFFINE_SERVER_HTTPS=true
```

**/opt/stacks/affine/compose.yaml** | Bagian 1 dari 2 - disusun mengikuti struktur compose resmi

```
name: affine
services:
  affine:
    image: ghcr.io/toeverything/affine:${AFFINE_REVISION:-stable}
    container_name: affine_server
    restart: unless-stopped
    depends_on:
      redis:
        condition: service_healthy
      postgres:
        condition: service_healthy
      affine_migration:
        condition: service_completed_successfully
    volumes:
      - ${UPLOAD_LOCATION}:/root/.affine/storage
      - ${CONFIG_LOCATION}:/root/.affine/config
    env_file:
      - .env
    environment:
      - REDIS_SERVER_HOST=redis
      - AFFINE_INDEXER_ENABLED=false
    ports:
      - "3010:3010"
    networks:
      - affine-internal
  affine_migration:
    image: ghcr.io/toeverything/affine:${AFFINE_REVISION:-stable}
    container_name: affine_migration_job
    command: ['sh', '-c', 'node ./scripts/self-host-predeploy.js']
    volumes:
      - ${UPLOAD_LOCATION}:/root/.affine/storage
      - ${CONFIG_LOCATION}:/root/.affine/config
    env_file:
      - .env
    environment:
      - REDIS_SERVER_HOST=redis
      - AFFINE_INDEXER_ENABLED=false
    depends_on:
      redis:
        condition: service_healthy
      postgres:
        condition: service_healthy
    networks:
      - affine-internal
```

**/opt/stacks/affine/compose.yaml (lanjutan)** | Bagian 2 dari 2 - ketik tepat di bawah bagian 1

```
  redis:
    image: redis
    container_name: affine_redis
    restart: unless-stopped
    healthcheck:
      test: ['CMD', 'redis-cli', 'ping']
      interval: 10s
      timeout: 5s
      retries: 5
    networks:
      - affine-internal
  postgres:
    image: pgvector/pgvector:pg16
    container_name: affine_postgres
    restart: unless-stopped
    volumes:
      - ${DB_DATA_LOCATION}:/var/lib/postgresql/data
    environment:
      POSTGRES_USER: ${DB_USERNAME}
      POSTGRES_PASSWORD: ${DB_PASSWORD}
      POSTGRES_DB: ${DB_DATABASE:-affine}
      POSTGRES_INITDB_ARGS: '--data-checksums'
    healthcheck:
      test: ['CMD', 'pg_isready', '-U', "${DB_USERNAME}", '-d', "${DB_DATABASE:-affine}"]
      interval: 10s
      timeout: 5s
      retries: 5
    networks:
      - affine-internal
networks:
  affine-internal:
```

Port 3010 dibuka untuk LAN dari VM ini; firewall Proxmox (Suplemen 7 Bab 51) hanya mengizinkan docker-core
menjangkaunya. Indexer pencarian dimatikan (AFFINE_INDEXER_ENABLED=false) seperti pada compose
resmi; kebutuhan RAM total belum bisa saya pastikan [BELUM PASTI], pantau di Beszel.

**TERMINAL VM AFFINE** | VM affine, sebagai root di /opt/stacks/affine

```
docker compose up -d
```
> Penjelasan: Mengunduh image dan menyalakan. Migrasi database berjalan dulu dan berhenti sendiri; server
menyala sesudahnya.
```
docker compose ps -a
```
> Penjelasan: Memeriksa: affine_migration_job berstatus Exited (0), lainnya Up/healthy. Bila server tidak menyala,
lihat log migrasi: docker compose logs affine_migration.
Daftarkan AFFiNE di gerbang yang berada di VM docker-core:

**TERMINAL VM DOCKER-CORE** | VM docker-core (192.168.88.20), sebagai root

```
nano /opt/stacks/caddy/Caddyfile
```
> Penjelasan: Tambahkan blok di bawah ini.

**/opt/stacks/caddy/Caddyfile (tambahan)** | Tambahan

```
affine.home.arpa {
 reverse_proxy 192.168.88.25:3010
}
```

**TERMINAL VM DOCKER-CORE** | VM docker-core, sebagai root

```
docker exec caddy caddy reload --config /etc/caddy/Caddyfile
```
> Penjelasan: Memuat blok baru.

## 46.2 Akun admin pertama

1. Buka https://affine.home.arpa. Dokumentasi AFFiNE menyebut langkah Create the first Admin account
setelah pemasangan; ikuti halaman yang tampil (alamat halaman admin bisa /admin [BELUM PASTI]).
2. Isi email dan kata sandi kuat. Simpan di Vaultwarden (Bab 45).
3. Di panel admin cari pengaturan server dan pendaftaran pengguna; matikan pendaftaran terbuka bila ada
(nama opsi [BELUM PASTI]). Ganti nama server bila mau.
CATATAN
Bila masuk via email meminta tautan atau kode lewat surel dan Anda belum mengatur pengiriman email, atur SMTP
(dokumentasi AFFiNE: Email Notifications) atau pakai akun yang dibuat admin dengan kata sandi [BELUM PASTI].

## 46.3 Sisi klien

Perangkat Cara menyambung Catatan
Windows Pasang aplikasi desktop dari affine.pro. Klik area nama workspace
&gt; Add Server &gt; isi https://affine.home.arpa &gt; Connect &gt; masuk
dengan email
Mengandalkan sertifikat akar
terpasang (Suplemen 4 Bab 37.2).
Alternatif tanpa instalasi: browser ke
alamat yang sama
Android Pasang AFFiNE dari Google Play (app.affine.pro). Di layar edit
ketuk ikon Back di atas, isi Server URL, Connect, masuk
Jika menolak sertifikat, lihat 46.5
(pindah ke Jalur 1)
iPhone Pasang AFFiNE dari App Store. Langkah sama seperti Android Aktifkan kepercayaan sertifikat akar
(Suplemen 4 Bab 37.4) lebih dulu
Browser HP Chrome/Safari ke https://affine.home.arpa, lalu Tambahkan ke layar
utama
Cadangan bila aplikasi bermasalah
Langkah klien di atas berasal dari ulasan pihak ketiga (Gigazine, Mei 2026) dan dokumentasi AFFiNE tentang
menyambung ke server self-host; nama tombol bisa berbeda di versi Anda [BELUM PASTI]. Aplikasi dan server
harus berada pada versi yang saling cocok [BELUM PASTI] (menurut templat pihak ketiga); selalu perbarui server
dengan tag stable.

## 46.4 Backup AFFiNE

**TERMINAL VM AFFINE** | VM affine, sebagai root di /opt/stacks/affine

```
docker exec affine_postgres pg_dump -U affine affine > backup/affine-$(date +%F).sql
```
> Penjelasan: Dump database (dokumen, papan tulis, profil).
```
tar czf backup/affine-files-$(date +%F).tgz storage config
```
> Penjelasan: Mengarsipkan unggahan dan konfigurasi.

## 46.5 Bila aplikasi HP menolak sertifikat lokal

Pindahkan AFFiNE ke Jalur 1 (Bab 44), seperti Vaultwarden. Karena AFFiNE sudah punya VM sendiri, ia cukup
menjadi node tailnet sendiri bernama lab-affine di port 443. Hanya satu alamat yang berlaku, jadi Caddy tidak lagi
dipakai untuk AFFiNE:
1. Di VM affine pasang Tailscale seperti Bab 44.3 dengan tailscale up --hostname=lab-affine
--accept-dns=false. Nonaktifkan key expiry di konsol admin. Entri grants tcp:443 dari Bab 44.3 sudah
mencukupi.
2. Di .env ubah AFFINE_SERVER_EXTERNAL_URL menjadi https://lab-affine.NAMA-TAILNET.ts.net.
3. Jalankan docker compose up -d lalu tailscale serve --bg --https=443 3010 di VM affine (port 3010
sudah dibuka di compose).
4. Di docker-core hapus blok affine.home.arpa dari Caddyfile dan muat ulang Caddy. Sambungkan ulang
semua klien ke alamat baru.


<!-- SOURCE: docs/bab/suplemen/47-nextcloud-kalender.md -->

# Bab 47. Nextcloud dan Kalender Pribadi

PENEMPATAN - BARU - VM sendiri
Tempat: VM 207 nextcloud (192.168.88.26): qm clone 200 207 --name nextcloud --full 1.
Alasan: Akan tumbuh menjadi penyimpanan berkas (NAS) dengan disk besar; pembaruannya harus satu mayor demi
satu mayor; datanya perlu backup tersendiri.
Tidak boleh: Digabung dengan layanan lain.
Nextcloud menyediakan kalender yang dapat disinkronkan lewat standar CalDAV ke Android, iPhone, dan
Windows. Di sini Nextcloud dipasang untuk kalender dulu; pemakaian sebagai penyimpanan berkas (NAS,
rencana nomor 2 Anda) dan OnlyOffice menyusul di suplemen berikutnya, dan folder datanya dapat dipindah ke
disk besar saat itu.
PERINGATAN
Nextcloud hanya mendukung naik versi satu mayor sekaligus, jadi jangan memakai tag latest. Cek nomor mayor
yang didukung saat ini di Docker Hub (nextcloud) atau halaman rilis Nextcloud, lalu isi NEXTCLOUD_TAG di bawah
[BELUM PASTI]. Contoh bentuk: 31-apache (contoh dari sumber pihak ketiga, bukan versi terkini).

## 47.1 Membuat VM nextcloud dan menyiapkan server

**TERMINAL HOST PROXMOX** | Shell node Proxmox (host), sebagai root

```
qm clone 200 207 --name nextcloud --full 1
```
> Penjelasan: Membuat VM 207 bernama nextcloud sebagai salinan penuh dari templat VM 200 (Suplemen 7 Bab
49).
```
qm set 207 --memory 2048 --cores 2
```
> Penjelasan: RAM (MB) dan inti. Angka awal adalah perkiraan [BELUM PASTI]; pantau di Beszel.
```
qm start 207
```
> Penjelasan: Menyalakan. Lakukan penyiapan awal di Suplemen 7 Bab 49.4 (nama host, kunci SSH, alamat
192.168.88.26), lalu lanjut di bawah.
Langkah berikut dijalankan di VM nextcloud:

**TERMINAL VM NEXTCLOUD** | VM nextcloud (192.168.88.26), sebagai root (setelah su -)

```
mkdir -p /opt/stacks/nextcloud/{html,data,db,backup} && cd /opt/stacks/nextcloud
```
> Penjelasan: Folder aplikasi, data, database, dan backup.
```
echo "POSTGRES_PASSWORD=$(openssl rand -hex 16)" > .env
```
> Penjelasan: Kata sandi database acak.
```
echo "REDIS_PASSWORD=$(openssl rand -hex 16)" >> .env
```
> Penjelasan: Kata sandi Redis acak.
```
echo "NC_ADMIN_PASSWORD=$(openssl rand -hex 12)" >> .env
```
> Penjelasan: Kata sandi awal admin Nextcloud. Akan diganti setelah login pertama.
```
nano .env
```
> Penjelasan: Tambahkan dua baris: NC_ADMIN_USER=&lt;nama-admin-bukan-admin&gt; dan
NEXTCLOUD_TAG=&lt;nomor-mayor&gt;-apache (lihat peringatan di atas).
```
chmod 600 .env && nano compose.yaml
```
> Penjelasan: Isi seperti kotak di bawah.

**/opt/stacks/nextcloud/compose.yaml** | Bagian 1 dari 2

```
x-nc-env: &nc-env
  POSTGRES_HOST: nc-db
  POSTGRES_DB: nextcloud
  POSTGRES_USER: nextcloud
  POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
  REDIS_HOST: nc-redis
  REDIS_HOST_PASSWORD: ${REDIS_PASSWORD}
  NEXTCLOUD_TRUSTED_DOMAINS: nextcloud.home.arpa
  TRUSTED_PROXIES: 192.168.88.20
  OVERWRITEPROTOCOL: https
services:
  nc-db:
    image: postgres:16-alpine
    container_name: nc-db
    restart: unless-stopped
    environment:
      POSTGRES_DB: nextcloud
      POSTGRES_USER: nextcloud
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
    volumes:
      - ./db:/var/lib/postgresql/data
    networks:
      - nc-internal
  nc-redis:
    image: redis:7-alpine
    container_name: nc-redis
    restart: unless-stopped
    command: redis-server --requirepass ${REDIS_PASSWORD}
    networks:
      - nc-internal
```

**/opt/stacks/nextcloud/compose.yaml (lanjutan)** | Bagian 2 dari 2 - ketik tepat di bawah bagian 1

```
  nextcloud:
    image: nextcloud:${NEXTCLOUD_TAG}
    container_name: nextcloud
    restart: unless-stopped
    depends_on:
      - nc-db
      - nc-redis
    environment:
      <<: *nc-env
      NEXTCLOUD_ADMIN_USER: ${NC_ADMIN_USER}
      NEXTCLOUD_ADMIN_PASSWORD: ${NC_ADMIN_PASSWORD}
    volumes:
      - ./html:/var/www/html
      - ./data:/var/www/html/data
    ports:
      - "8080:80"
    networks:
      - nc-internal
  nc-cron:
    image: nextcloud:${NEXTCLOUD_TAG}
    container_name: nc-cron
    restart: unless-stopped
    entrypoint: /cron.sh
    depends_on:
      - nextcloud
    environment:
      <<: *nc-env
    volumes:
      - ./html:/var/www/html
      - ./data:/var/www/html/data
    networks:
      - nc-internal
networks:
  nc-internal:
```

Pengaturan Fungsi
NEXTCLOUD_TRUSTED_DO
MAINS
Nama yang boleh dipakai untuk membuka Nextcloud; di luar daftar ini muncul galat domain
tidak tepercaya
TRUSTED_PROXIES Alamat proxy yang dipercaya: Caddy di docker-core (192.168.88.20), yang kini berada di VM
lain. Permintaan tiba dari alamat itu
OVERWRITEPROTOCOL=http
s
Membuat Nextcloud selalu menulis tautan https walau di belakang proxy
nc-cron Menjalankan pekerjaan latar belakang (termasuk kalender dan notifikasi) lewat cron bawaan
image

**TERMINAL VM NEXTCLOUD** | VM nextcloud, sebagai root di /opt/stacks/nextcloud

```
docker compose up -d && docker compose logs -f nextcloud
```
> Penjelasan: Menyalakan. Pemasangan pertama memakan beberapa menit; tunggu sampai log tenang, lalu Ctrl+C
untuk keluar dari log.
```
grep NC_ADMIN .env
```
> Penjelasan: Menampilkan nama dan kata sandi awal admin untuk login pertama.
Daftarkan Nextcloud di gerbang yang berada di VM docker-core:

**TERMINAL VM DOCKER-CORE** | VM docker-core (192.168.88.20), sebagai root

```
nano /opt/stacks/caddy/Caddyfile
```
> Penjelasan: Tambahkan blok di bawah ini.

**/opt/stacks/caddy/Caddyfile (tambahan)** | Tambahan

```
nextcloud.home.arpa {
 header Strict-Transport-Security "max-age=15552000"
 redir /.well-known/carddav /remote.php/dav/ 301
 redir /.well-known/caldav /remote.php/dav/ 301
 reverse_proxy 192.168.88.26:8080
}
```

**TERMINAL VM DOCKER-CORE** | VM docker-core, sebagai root

```
docker exec caddy caddy reload --config /etc/caddy/Caddyfile
```
> Penjelasan: Memuat blok baru. Dua baris redir membantu klien kalender menemukan alamat CalDAV otomatis
(disarankan dokumentasi dan contoh Nextcloud).

## 47.2 Login pertama dan penyiapan

1. Buka https://nextcloud.home.arpa dan masuk dengan admin dari langkah terakhir. Segera ganti kata sandi
di Foto profil &gt; Personal settings &gt; Security dan simpan di Vaultwarden.
2. Buka Administration settings &gt; Basic settings dan pilih Cron pada Background jobs (sudah dijalankan
container nc-cron).
3. Buat akun harian terpisah: Foto profil &gt; Accounts &gt; New account. Pakai akun ini untuk kalender dan
perangkat; akun admin hanya untuk pengelolaan.
4. Buka Administration settings &gt; Overview dan baca peringatannya (misalnya indeks database, wilayah
telepon bawaan). Perintah perbaikan ada di 47.3.

## 47.3 Memasang aplikasi Calendar dan merapikan peringatan

**TERMINAL VM NEXTCLOUD** | VM nextcloud, sebagai root

```
docker exec -u www-data nextcloud php occ app:install calendar
```
> Penjelasan: Memasang aplikasi Calendar dari toko aplikasi Nextcloud. Bila sudah terpasang akan tertulis
demikian (itu normal).
```
docker exec -u www-data nextcloud php occ config:system:set default_phone_region --value=ID
```
> Penjelasan: Mengisi wilayah telepon bawaan (ID = Indonesia) untuk menghilangkan satu peringatan.
```
docker exec -u www-data nextcloud php occ db:add-missing-indices
```
> Penjelasan: Menambah indeks database yang disarankan.
```
docker exec -u www-data nextcloud php occ maintenance:repair --include-expensive
```
> Penjelasan: Menjalankan perbaikan pemeliharaan yang berat; aman dijalankan sekali setelah pemasangan.
Buka https://nextcloud.home.arpa/apps/calendar. Kalender bawaan bernama Personal sudah ada. Buat satu
acara uji.

## 47.4 Kata sandi aplikasi untuk perangkat

Jangan memakai kata sandi akun di HP atau Thunderbird. Buat kata sandi aplikasi terpisah per perangkat
sehingga satu perangkat yang hilang dapat dicabut tanpa mengganti kata sandi utama.
1. Login dengan akun harian &gt; Foto profil &gt; Personal settings &gt; Security &gt; bagian Devices & sessions.
2. Isi nama (misalnya HP-Android), klik Create new app password, salin kata sandi yang tampil (hanya muncul
sekali).
3. Ulangi untuk iPhone dan Thunderbird. Cabut dengan tombol hapus di daftar yang sama bila perangkat hilang.

## 47.5 Sisi klien: Android (DAVx5)

1. Pasang DAVx5 dari F-Droid atau Google Play (harga di Play Store [BELUM PASTI]). Beri izin yang diminta
(kalender, kontak, notifikasi).
2. Pastikan sertifikat akar Caddy sudah terpasang di Android (Suplemen 4 Bab 37.3). Tailscale aktif bila di luar
rumah.
3. Di DAVx5 ketuk + &gt; Login with URL and user name. Base URL: https://nextcloud.home.arpa, nama
pengguna akun harian, kata sandi = kata sandi aplikasi.
4. Bila muncul peringatan sertifikat, jangan lanjut sebelum yakin itu sertifikat Anda. Catatan rilis DAVx5
menyebut dukungan sertifikat buatan sendiri; perilaku persisnya di perangkat Anda [BELUM PASTI].
5. Pilih kalender yang disinkronkan (aktifkan sakelar di tab CalDAV). Buka aplikasi kalender di HP (Google
Calendar atau yang lain); kalender Nextcloud muncul di daftar akun.

## 47.6 Sisi klien: iPhone

1. Pastikan sertifikat akar terpasang dan kepercayaannya diaktifkan (Suplemen 4 Bab 37.4). Tailscale aktif bila
di luar rumah.
2. Buka Pengaturan &gt; Kalender &gt; Akun &gt; Tambah Akun &gt; Lainnya &gt; Tambah Akun CalDAV (nama menu
bergantung versi iOS).
3. Server: nextcloud.home.arpa, Nama Pengguna: akun harian, Kata Sandi: kata sandi aplikasi, Deskripsi
bebas. Ketuk Lanjut.
4. Aktifkan Kalender pada daftar yang muncul, lalu Simpan. Buka aplikasi Kalender dan lihat kalender baru.

## 47.7 Sisi klien: Windows

1. Paling sederhana: pakai kalender lewat browser di https://nextcloud.home.arpa/apps/calendar (sudah
dipercaya setelah Suplemen 4 Bab 37.2). Opsional: Chrome/Edge Menu &gt; Instal sebagai aplikasi.
Aplikasi kalender di desktop: Thunderbird. Thunderbird punya penyimpanan sertifikat sendiri, jadi akar Caddy
perlu diimpor lebih dulu [BELUM PASTI]:
1. Pasang Thunderbird dari thunderbird.net. Buka Settings &gt; Privacy & Security &gt; Certificates &gt; Manage
Certificates &gt; Authorities &gt; Import lalu pilih caddy-root.crt dan centang Trust this CA to identify websites.
2. Buka tab Calendar &gt; New Calendar &gt; On the Network &gt; CalDAV. Di Location isi
https://nextcloud.home.arpa/remote.php/dav/calendars/NAMA-PENGGUNA/personal/ (bagian personal
adalah kode kalender bawaan [BELUM PASTI]).
3. Saat diminta, masukkan nama pengguna dan kata sandi aplikasi (Windows), lalu beri nama kalender dan
selesaikan.

## 47.8 Backup Nextcloud

**TERMINAL VM NEXTCLOUD** | VM nextcloud, sebagai root di /opt/stacks/nextcloud

```
docker exec -u www-data nextcloud php occ maintenance:mode --on
```
> Penjelasan: Mode pemeliharaan agar data tidak berubah selama backup.
```
docker exec nc-db pg_dump -U nextcloud nextcloud > backup/nextcloud-$(date +%F).sql
```
> Penjelasan: Dump database (tempat kalender tersimpan).
```
tar czf backup/nextcloud-files-$(date +%F).tgz html/config data
```
> Penjelasan: Mengarsipkan konfigurasi (config.php berisi rahasia yang dibutuhkan untuk pemulihan) dan folder
data.
```
docker exec -u www-data nextcloud php occ maintenance:mode --off
```
> Penjelasan: Mengembalikan ke mode normal.
KEAMANAN
Arsip berisi config.php dengan rahasia instance. Perlakukan seperti kata sandi: jangan unggah ke layanan publik.


<!-- SOURCE: docs/bab/suplemen/bagian-6-99-penutup.md -->

# Bagian 6. Vaultwarden, AFFiNE, dan Kalender Nextcloud: Uji, Masalah Umum, Lembar Pembaruan, Syarat Lulus Fase 6

Uji, Masalah Umum, dan Lembar Pembaruan
Uji menyeluruh
No Uji Hasil yang diharapkan
1 tailscale status di VM vault; konsol admin Machines lab-vault hidup, kunci tidak kedaluwarsa
2 Laptop (Tailscale): https://lab-vault.NAMA-TAILNET.ts.net Vault Bitwarden, gembok tanpa peringatan
3 Buat akun, aktifkan TOTP, tutup pendaftaran Akun lain tidak bisa dibuat
4 Android dan iPhone: login Bitwarden ke server sendiri Login berhasil, item tersinkron antar perangkat
5 Android: Tailscale mati Mengisi kata sandi dari salinan lokal tetap bisa; sinkron
tertunda
6 Laptop: https://affine.home.arpa, akun admin, buat satu
halaman
Halaman tersimpan
7 Aplikasi AFFiNE Windows, Android, iPhone tersambung Halaman uji muncul di semua perangkat (atau catat
mana yang gagal)
8 Nextcloud: login, ganti kata sandi admin, Overview tanpa
peringatan penting
Cron aktif; hanya peringatan ringan
9 Acara dibuat di web; muncul di DAVx5/Android dan iPhone Sinkron dua arah: acara dari HP muncul di web
10 Backup dibuat untuk tiga layanan dan disalin ke luar server Arsip ada di laptop atau disk luar
Masalah dan solusi
Gejala Penyebab Solusi
Alamat .ts.net tidak terbuka dari
HP
Tailscale mati, atau kebijakan
jaringan belum mengizinkan port 443
Aktifkan Tailscale; periksa entri grants Bab 44.3;
tailscale serve status di VM vault
Serve: sertifikat belum tersedia HTTPS Certificates belum diaktifkan
di konsol admin
Aktifkan di halaman DNS konsol admin, ulangi
tailscale serve
Bitwarden: galat sertifikat di
aplikasi
Alamat diketik salah atau memakai
nama lain (misalnya lab-docker lama)
Samakan persis dengan DOMAIN di compose
Vaultwarden menolak
pendaftaran
SIGNUPS_ALLOWED false (normal) Buat akun hanya saat true; atau undang lewat
pengaturan yang Anda aktifkan sendiri
AFFiNE: server tidak menyala Migrasi database gagal atau nama
image salah
docker compose logs affine_migration; bandingkan
image dengan berkas resmi (46.1)
AFFiNE: tautan atau login
mengarah ke alamat salah
AFFINE_SERVER_EXTERNAL_URL
atau HTTPS tidak diatur
Periksa .env lalu docker compose up -d
Nextcloud: "Access through
untrusted domain"
Nama tidak ada di
NEXTCLOUD_TRUSTED_DOMAINS
Perbaiki compose; atau occ config:system:set
trusted_domains 1 --value=nextcloud.home.arpa
Nextcloud: loop pengalihan
atau http di tautan
OVERWRITEPROTOCOL atau proxy
tepercaya salah
Periksa compose (47.1) dan Caddyfile
DAVx5 tidak menemukan
kalender
Kata sandi aplikasi salah atau
.well-known belum dialihkan
Buat ulang kata sandi aplikasi; pastikan dua baris
redir ada di Caddyfile
iPhone: "Tidak dapat
memverifikasi identitas server"
Sertifikat akar belum dipercaya Aktifkan di Pengaturan Kepercayaan Sertifikat
(Suplemen 4 Bab 37.4)
Lembar pembaruan
Bab sebelumnya Perubahan Rujukan
Suplemen 1, Bab 26.6 Kebijakan tailnet bertambah satu entri grants untuk autogroup:self
pada tcp:443
Bab 44.3
Suplemen 1, Bab 26.3 VM vault (bukan VM Docker) menjadi perangkat tailnet kedua
(lab-vault), bukan penerus rute
Bab 44.3
Suplemen 4, Bab 36.6 Caddyfile bertambah: affine dan nextcloud sebagai reverse_proxy
ke IP:port VM masing-masing (Vaultwarden tidak lewat Caddy)
Bab 46, 47
Suplemen 7, Bab 48-51 Peta penempatan VM, templat VM 200, dan firewall Proxmox
yang membatasi port 3010, 8080
Suplemen 7
Suplemen 3, Bab 32 Monitor Uptime Kuma baru untuk affine dan nextcloud (Ignore
TLS error). Alamat pantau memakai IP:port VM
(192.168.88.25:3010, 192.168.88.26:8080). Vaultwarden hanya
terbuka lewat Tailscale; pantau dengan agen Beszel di VM vault;
titik pemeriksaan sehat [BELUM PASTI]
Uji menyeluruh
Edisi 2, Bab 23 dan Suplemen 3
Bab 34.3
Backup baru: vaultwarden (tar data), affine (sql dan files),
nextcloud (sql dan files). Wajib disalin ke luar server
Bab 45.5, 46.4, 47.8
Daftar hal yang belum dipastikan
No Hal Cara memastikan
1 Android Bitwarden dengan CA lokal (laporan gagal dari pengguna); Jalur
1 dipilih untuk menghindarinya
Tidak perlu diuji; Jalur 1 sudah
menghindarinya
2 Sintaks grants ip "tcp:443" dan autogroup:self; serve berjalan dengan
--accept-dns=false
Coba; gunakan bentuk acls lama bila
ditolak
3 Nama image AFFiNE (affine vs affine-graphql) dan tata letak compose
resmi
Bandingkan dengan berkas resmi (46.1)
4 Alamat halaman admin AFFiNE, nama opsi pendaftaran, login email
tanpa SMTP
Lihat dokumentasi AFFiNE After Installation
dan Email Notifications
5 AFFiNE di Android dan iPhone menerima CA lokal; langkah menu
aplikasi
Uji; bila gagal pakai 46.5
6 Nomor mayor Nextcloud terkini untuk NEXTCLOUD_TAG Cek Docker Hub nextcloud
7 DAVx5 menerima CA lokal dan harga di Play Store; Thunderbird
memakai penyimpanan sertifikat sendiri; kode kalender bawaan
"personal"
Uji di perangkat
8 Perintah backup daring Vaultwarden dan titik pemeriksaan sehat Baca wiki Vaultwarden; pakai cara stop dan
tar bila ragu
9 Kebutuhan RAM gabungan Ukur dengan Beszel
Syarat lulus Fase 6
No Poin Ya / Tidak
1 Vaultwarden hanya lewat Tailscale Serve; pendaftaran ditutup; TOTP aktif
2 Bitwarden tersinkron di Windows, Android, iPhone
3 AFFiNE berjalan; aplikasi desktop dan HP tersambung (atau Jalur 1 diterapkan)
4 Nextcloud berjalan dengan Cron; kalender tersinkron ke Android dan iPhone
5 Kata sandi aplikasi dipakai di perangkat, bukan kata sandi akun
6 Backup tiga layanan sudah disalin ke luar server
7 Funnel tidak pernah dijalankan (tailscale funnel status kosong)
Berikutnya (Suplemen 7): Proxmox Backup Server dan audit keamanan keseluruhan. Backup kata sandi dan
kalender di suplemen ini akan dipindahkan ke jadwal backup otomatis di sana.


<!-- SOURCE: docs/bab/suplemen/bagian-7-00-pengantar.md -->

# Bagian 7. Penempatan VM/LXC, Backup, dan Audit (pengantar)

Bagian 7. Penempatan VM/LXC, Backup, dan
Audit
Asal: Suplemen 7. Bab 48-52.
Suplemen 7 membuat satu keputusan besar: setiap layanan berjalan di VM atau container Proxmox yang
terpisah, kecuali beberapa layanan ringan yang sengaja digabung. Sesudah itu ia memasang Proxmox Backup
Server, firewall antar-guest, dan audit keamanan. Suplemen 1 sampai 6 diterbitkan ulang sebagai Revisi 2 agar
setiap bab pemasangan diawali Kotak Penempatan yang menyebut guest tujuan.
Bab Isi Hasil akhir
48. Peta penempatan Prinsip, daftar guest dan IP, aturan menerjemahkan bab
lama, mode hemat, penyesuaian Edisi 2
Tahu setiap layanan tinggal di
mana
49. Templat VM Debian +
Docker
Membuat templat, menyalin VM baru, penyiapan awal
tiap VM
VM baru jadi dalam beberapa
menit
50. Proxmox Backup Server VM pbs, datastore, pengguna, job backup, prune, uji
pulih, salinan kedua
Backup otomatis dan terbukti bisa
dipulihkan
51. Firewall Proxmox
antar-guest
Matriks akses, IPSet, aturan per VM, isolasi VM publik Hanya jalur yang diizinkan yang
terbuka
52. Audit keamanan Skrip audit baca-saja, Lynis, SSH kunci, laporan Daftar temuan dan keputusan
risiko
Urutan kerja yang disarankan
1. Baca Bab 48 lalu kerjakan Bab 49 (membuat templat VM 200).
2. Pasang layanan menurut Kotak Penempatan di Suplemen 3, 4, 5, 6 (Revisi 2), masing-masing di guest yang
ditunjuk.
3. Kerjakan Bab 50 setelah ada guest yang berisi data, lalu Bab 51, terakhir Bab 52.
PERINGATAN
Tidak ada suplemen yang sudah Anda uji. Karena belum ada yang terpasang, Anda tidak perlu memindahkan apa
pun: pasang langsung di guest tujuan. Bila sebagian sudah terpasang di satu VM Docker (192.168.88.20), jangan
memigrasi sekaligus; pindahkan satu layanan, uji, baru lanjut.
CATATAN
Angka RAM, nomor VMID, dan alamat IP di sini adalah rancangan yang bisa Anda ubah selama konsisten. Hal yang
belum bisa saya pastikan ditandai [BELUM PASTI] dan dikumpulkan di tabel pada halaman penutup.


<!-- SOURCE: docs/bab/suplemen/48-peta-penempatan.md -->

# Bab 48. Peta Penempatan: Siapa Tinggal di Mana

## 48.1 Mengapa dipisah, dan harganya

• Dampak kebobolan terbatas. Bila WordPress diretas, penyerang berada di VM web, bukan di VM yang berisi
kata sandi atau kredensial n8n.
• Backup dan pemulihan per layanan. PBS (Bab 50) mencadangkan dan memulihkan satu VM tanpa
menyentuh yang lain.
• Firewall per guest. Aturan di Proxmox (Bab 51) bisa menutup port satu VM dari VM lain.
• Pembaruan terpisah. Nextcloud harus naik satu mayor demi satu mayor; itu tidak boleh menahan layanan
lain.
Harganya: setiap VM membawa sistem operasinya sendiri (RAM dan disk), ada lebih banyak mesin untuk
diperbarui, dan Caddy tidak lagi menjangkau layanan lewat nama container tetapi lewat IP:port. Karena itu ada
kelompok yang sengaja digabung dan mode hemat di 48.6.

## 48.2 Empat pertanyaan penempatan

Pertanyaan Bila jawabannya ya Contoh
Memakai Docker? Guest berupa VM. Dokumentasi Proxmox menyarankan
menjalankan container aplikasi seperti Docker di dalam VM
QEMU, bukan di LXC atau di host
Semua layanan buku ini
Hanya layanan Linux ringan tanpa
Docker?
Boleh LXC (ringan, berbagi kernel host) Tailscale router (CT103),
AdGuard kedua (CT101),
Samba (CT102)
Menyimpan rahasia (kata sandi,
kredensial layanan lain)?
VM sendiri vault, n8n, git (token
Renovate, kunci deploy)
Menghadap internet? VM sendiri dan paling terisolasi web-public
Data besar atau siklus pembaruan
berbeda?
VM sendiri nextcloud, pbs
Ringan, saling bergantung, dan
harus menjangkau semua guest?
Gabung dalam satu VM infrastruktur Caddy, Gotify, Uptime
Kuma, Homepage,
Beszel hub, Portainer
CATATAN
Proxmox VE 9.1 menambah dukungan image OCI (Docker) sebagai container aplikasi di LXC, tetapi masih berstatus
tech preview menurut dokumentasi dan tulisan pihak ketiga. Buku ini tidak memakainya; VM tetap pilihan untuk
Docker. Host Proxmox tidak menjalankan Docker sama sekali.

## 48.3 Peta guest dan alamat

Host Proxmox (192.168.88.10) - tanpa Docker dan tanpa aplikasi
201 docker-core
.20 Caddy
204 git
.23 Forgejo
205 vault
.24 Vaultwarden
206 affine
.25 AFFiNE
207 nextcloud
.26 Nextcloud
213 sso
.32 Pocket ID
208 n8n
.27 n8n
209 web
.28 situs, WP
210 web-public
.29 internet
211 music
.31 Navidrome
212 pbs
.30 backup
214 immich
.33 Immich
CT103 ts-router
LXC, Tailscale (nanti STB 2)
STB 1 .253
AdGuard Home (perangkat sendiri)
VM 200 Template-VM
template VM Debian 13; paket dasar belum diverifikasi
CT 100 Template-CT
template CT Debian 13; dasar 1 CPU/512 MiB/512 MiB swap/8 GiB
Gambar 48.1 - Host Proxmox dengan guest terpisah (VM 202 HAOS, 203 k3s, CT101 dan CT102 dari Edisi 2 tidak digambar); STB 1
dan CT103 di luar kelompok VM Docker.
VMID Nama Jenis IP Isi Bab
200 Template-VM VM (templat) - Debian 13; paket dasar belum dicatat (beda dari templat cloud-init 9000 Edisi 2)
49
100 Template-CT LXC (templat) - Debian 13; 1 CPU, 512 MiB RAM, 512 MiB swap, disk 8 GiB 49
201 docker-core VM .20 Caddy (gerbang HTTPS), Portainer,
Gotify, Uptime Kuma, Beszel hub,
Homepage, adguardhome-sync
31-38
202 haos VM .21 Home Assistant OS Edisi 2
203 k3s VM .22 Kubernetes k3s + Flux Edisi 2
204 git VM .23 Forgejo + Renovate (pindah dari VM
201 Edisi 2)
Edisi 2,
48.8
205 vault VM .24 Vaultwarden + node Tailscale lab-vault 44-45
206 affine VM .25 AFFiNE (+ Postgres, Redis) 46
207 nextcloud VM .26 Nextcloud (+ Postgres, Redis, cron) 47
208 n8n VM .27 n8n (+ Postgres) 42
209 web VM .28 Situs statis privat, WordPress (+
MariaDB)
40-41
210 web-public VM .29 cloudflared + situs statis publik 43
211 music VM .31 Navidrome (streaming musik) + disk
pustaka
53
212 pbs VM .30 Proxmox Backup Server 50
213 sso VM .32 Pocket ID (SSO passkey) + node
Tailscale lab-sso
54
214 immich VM .33 Immich (foto) + disk foto kedua + node
Tailscale lab-immich
55
101 adguard2 LXC .11 AdGuard Home kedua (failover DNS) Edisi 2
102 files LXC .12 Samba (folder jaringan) Edisi 2
103 ts-router LXC (lihat Edisi 2) Tailscale subnet router (nanti pindah ke
STB 2)
26
- STB 1 perangkat .253 AdGuard Home (DNS rumah), terpisah
dari Proxmox
Edisi 2
Semua alamat berada di LAN 192.168.88.0/24 milik MikroTik. VM 201-210 mengikuti urutan alamat .20-.29; VM
211 (music, .31) dan 212 (pbs, .30) ditambahkan belakangan sehingga urutannya bertukar. CT101-105 dan
alamat .11-.14 tetap seperti Lampiran B Edisi 2. Ganti bila bentrok dengan VM lain Anda; yang penting konsisten
di semua bab.

## 48.4 Aturan menerjemahkan bab lama

Sebelum pemisahan, banyak bab menulis "VM Docker 192.168.88.20" dan memakai jaringan Docker proxy
bersama. Revisi 2 Suplemen 3 sampai 6 sudah memakai aturan di bawah. Gunakan tabel ini bila Anda
menambah layanan sendiri atau membaca bab lama yang belum direvisi.
Teks lama Ganti dengan Alasan
VM Docker 192.168.88.20 untuk
layanan X
Guest X menurut tabel 48.3 Setiap layanan punya tempatnya
networks: proxy (external) pada
layanan di VM lain
Hapus. Layanan hanya memakai jaringan
internalnya
Jaringan Docker tidak melintasi VM
reverse_proxy nama-container:port reverse_proxy IP-VM:port-yang-dibuka Caddy dan layanan berada di VM
berbeda
ports: 127.0.0.1:PORT:PORT ports: PORT:PORT (terbuka di LAN VM itu) Caddy di VM lain harus bisa
menjangkaunya; dikunci firewall
Proxmox (Bab 51)
TRUSTED_PROXIES: 172.16.0.0/12 TRUSTED_PROXIES: 192.168.88.20 Permintaan tiba dari alamat
docker-core
http://gotify:80 (dari layanan lain) http://192.168.88.20:8070 Gotify di VM lain
Monitor Uptime Kuma ke nama
container
Monitor ke IP:port VM atau ke alamat
Caddy
Kuma di docker-core
Agen Beszel hanya di satu VM Agen di setiap VM; hub menghubungi tiap
agen
Setiap VM dipantau sendiri
Contoh hasil akhir: Caddyfile di docker-core setelah semua layanan berpindah (blok gembok, header, dan redir
seperti di bab masing-masing):

**/opt/stacks/caddy/Caddyfile (ringkas)** | Gambaran akhir

```
web.home.arpa { reverse_proxy 192.168.88.28:8082 }
wp.home.arpa { reverse_proxy 192.168.88.28:8081 }
n8n.home.arpa { reverse_proxy 192.168.88.27:5678 }
affine.home.arpa { reverse_proxy 192.168.88.25:3010 }
git.home.arpa { reverse_proxy 192.168.88.23:3000 }
nextcloud.home.arpa {
 header Strict-Transport-Security "max-age=15552000"
 redir /.well-known/carddav /remote.php/dav/ 301
 redir /.well-known/caldav /remote.php/dav/ 301
 reverse_proxy 192.168.88.26:8080
}
```

CATATAN
Vaultwarden tidak muncul di Caddyfile: ia hanya terbuka lewat Tailscale Serve di VM vault. Navidrome (VM 211) juga
hanya lewat Tailscale Serve. Situs publik (VM 210) tidak lewat Caddy; ia keluar lewat Cloudflare Tunnel.

## 48.5 Pemetaan bab lama ke guest

Bab Layanan Guest Yang berubah dari teks asli
Edisi 2 AdGuard Home STB 1 (.253) Tidak ada: sengaja di luar Proxmox
Edisi 2 Debian + Docker, Portainer,
Homepage, adguardhome-sync
VM 201 (templat 200
dibuat di Bab 49)
VM Debian pertama menjadi
docker-core atau sumber templat
(Bab 49); Homepage pindah port
(48.8)
Edisi 2, Bab 15 dan
22
Forgejo, Renovate VM 204 (.23) Pindah dari VM 201; lihat 48.8
Edisi 2, Bab 16 Nextcloud Dilewati; pakai Suplemen 6
Bab 47 (VM 207)
Bab 16 Edisi 2 tidak dikerjakan; lihat
48.8
Edisi 2, Bab 17
sampai 21
Samba, Home Assistant, k3s,
Flux
CT102, VM 202, VM 203 Tidak ada; hanya alamat Forgejo di
Flux (48.8)
Suplemen 1, Bab 25 Pengerasan dasar Semua guest + host UFW tidak mengatur port Docker;
tambahkan firewall Proxmox (Bab 51)
Suplemen 1, Bab 26 Tailscale subnet router CT103 (LXC) Pilihan B (VM Docker) tidak dipakai;
pakai C
Suplemen 2, Bab
27-30
Proxmox di ThinkCentre M710q Host Tidak ada; host tanpa aplikasi
Suplemen 3, Bab
31-34
Uptime Kuma, Gotify, Beszel VM 201; agen Beszel di
semua VM
Agen dipasang saat VM dibuat
Suplemen 4, Bab
35-38
Caddy, sertifikat VM 201 Teruskan ke IP:port VM lain
Suplemen 5, Bab
39-43
Situs statis, WordPress, n8n,
tunnel
VM 209, 208, 210 Sudah ditulis ulang di Revisi 2
Suplemen 6, Bab
44-47
Vaultwarden, AFFiNE, Nextcloud VM 205, 206, 207 Sudah ditulis ulang di Revisi 2; node
Tailscale lab-vault, tcp:443
Suplemen 8, Bab 53 Navidrome (musik) VM 211 Baru; node Tailscale lab-music,
tcp:443
Suplemen 9, Bab
54-56
Pocket ID (SSO), Immich (foto),
profil RAM
VM 213, 214 Baru; node Tailscale lab-sso dan
lab-immich, tcp:443; profil untuk
mesin 16 GB di Bab 56

## 48.6 Mode hemat dan perkiraan RAM

Proxmox menjalankan sistem operasi lengkap per VM, jadi RAM total = jumlah RAM semua VM + kebutuhan
host. Angka awal di bawah adalah perkiraan saya [BELUM PASTI] dan bukan angka resmi; ukur dengan Beszel
lalu sesuaikan. Sisakan RAM untuk host Proxmox sendiri.
VM RAM awal (MB) Boleh digabung?
201 docker-core 2048 Inti; tidak digabung
204 git 1024 Tidak (menyimpan token dan kunci deploy)
205 vault 1024 Tidak pernah
206 affine 2048 Ya, ke "apps" (VM 206)
207 nextcloud 2048 Tidak (data besar, pembaruan sendiri)
208 n8n 1536 Ya, ke "apps" (VM 206)
209 web 1536 Ya, ke "apps" (VM 206)
210 web-public 768 Tidak pernah
211 music 1024 Ya, ke "apps" (VM 206)
VM RAM awal (MB) Boleh digabung?
212 pbs 2048 Tidak pernah (backup terpisah dari yang dicadangkan)
213 sso 1024 Tidak pernah (memegang kunci masuk ke layanan lain)
214 immich 6144 (4096 tanpa ML) Tidak (database vektor, ML, dan foto sendiri)
Jumlah (terpisah penuh) 22.272 MB (sekitar
21,8 GB)
Belum termasuk host Proxmox, HAOS, dan k3s
Mode hemat: apps 3072 MB
menggantikan 206+208+209+211
19.200 MB (sekitar
18,8 GB)
Menghemat sistem operasi tiga VM
Bersama VM Edisi 2 (HAOS 2048 MB,
k3s 3072 sampai 4096 MB)
27.392 sampai 28.416
MB (26,8 sampai 27,8
GB); mode hemat
24.320 sampai 25.344
MB
Edisi 2 membuat VM 201 dengan 4096 MB; 2048 MB
adalah sasaran setelah Forgejo dan Nextcloud pindah
[BELUM PASTI]
PERINGATAN
Mesin utama (ThinkCentre M710q, i5-6500T) dilaporkan memakai RAM 24 GB (16+8) per 31 Oktober 2026; BIOS dan MemTest86 belum dikonfirmasi (Bab 27.1).
Profil pemakaian lama disusun untuk 16 GB dan 32 GB. Pada 24 GB, gunakan baseline konservatif dan tambah beban bertahap sesuai Bab 56.8; jangan menyalakan semua VM sekaligus tanpa pemantauan.
Bila memakai mode hemat Perubahan
n8n, web, music, affine menjadi VM 206 "apps"
(192.168.88.25)
Ganti IP di Caddyfile: 8081, 8082, 5678, 3010 semuanya di
192.168.88.25; port sama, tidak ada bentrok
Kotak Penempatan bab 40, 41, 42, 46, 53 Jalankan langkah di VM apps, tanpa membuat VM 208, 209, dan 211
(disk musik menjadi disk kedua VM apps)
Firewall (Bab 51) Aturan untuk 206 menggabungkan port 3010, 5678, 8081, 8082 dari
192.168.88.20

## 48.7 Cara membaca Kotak Penempatan

Di awal setiap bab pemasangan Anda akan melihat kotak ungu seperti di bawah. Ia menjawab satu pertanyaan:
buat guest baru, atau gabung ke yang sudah ada?
PENEMPATAN - BARU - VM sendiri
Tempat: VM 208 n8n (192.168.88.27): qm clone 200 208 --name n8n --full 1.
Alasan: Satu kalimat mengapa dipisah atau digabung.
Mode hemat: Bila ada, guest mana yang boleh menampungnya bersama layanan lain.
Label di kotak Artinya
BARU Buat VM atau LXC baru (perintah qm clone atau pct create diberikan)
GABUNG Pasang di guest yang sudah ada; nama dan IP guest disebut
HOST Dikerjakan di host Proxmox; bukan di guest
TIDAK ADA GUEST Bab konsep, langkah klien, atau pengujian
SEMUA GUEST Dikerjakan di setiap guest (pengerasan, audit)

## 48.8 Penyesuaian Edisi 2

Edisi 2 (halaman 1-122) tidak diubah. Ia menaruh Docker, Portainer, Homepage, Forgejo, dan Nextcloud di satu
VM 201. Tiga keputusan di buku ini mengubah sebagian isinya: Forgejo dan Renovate pindah ke VM 204 git,
Nextcloud Edisi 2 Bab 16 dilewati dan diganti Suplemen 6 Bab 47, dan Homepage berpindah port sebelum
Caddy dipasang. Baca bagian Edisi 2 di bawah dengan nilai pada kolom kanan.
Bagian Edisi 2 Yang tertulis Dibaca sebagai
Bab 15.2 sampai 15.5
(Forgejo)
VM Debian di 192.168.88.20; Server
Domain, Base URL, dan alamat clone
memakai .20
VM 204 git (192.168.88.23) dari templat 200 (Bab
49.4). Compose dan folder /opt/stacks/forgejo
sama. Base URL http://192.168.88.23:3000/, clone
ssh://git@192.168.88.23:2222/USER/homelab.git
Bab 21.2 (flux bootstrap) ssh://git@192.168.88.20:2222/USERNA
ME/homelab.git
ssh://git@192.168.88.23:2222/USERNAME/homela
b.git
Bab 22.2 (Renovate) RENOVATE_ENDPOINT=http://192.168.
88.20:3000/api/v1/, dijalankan di VM
Debian
http://192.168.88.23:3000/api/v1/, dijalankan di VM
204 (Docker sudah ada dari templat)
Bab 16 (Nextcloud) Nextcloud, MariaDB, Redis di VM 201,
port 8080
Dilewati. Pasang dengan Suplemen 6 Bab 47 di
VM 207 (192.168.88.26). Migrasi data dari Bab 16
tidak dibahas
Bab 19.1 (Homepage) ports "80:3000"; HOMEPAGE_ALLOWE
D_HOSTS=192.168.88.20,home.lan
ports "3002:3000"; HOMEPAGE_ALLOWED_HOS
TS=192.168.88.20:3002,dash.home.arpa. Port 80
dan 443 dikosongkan untuk Caddy
Bab 19.2 dan 19.4 (kartu,
DNS)
Kartu dan rewrite Forgejo serta Nextcloud
menunjuk .20
Forgejo ke 192.168.88.23:3000 (git.home.arpa
lewat Caddy), Nextcloud ke 192.168.88.26:8080.
Nama .lan Edisi 2 boleh tetap berdampingan
dengan \*.home.arpa
Bab 11.2 (VM 201) Memory 4096 MiB Boleh diturunkan ke 2048 MB setelah Forgejo dan
Nextcloud tidak lagi di VM 201 [BELUM PASTI]
Bab 11.7 (templat 9000) Templat cloud-init untuk VM k3s Tetap untuk VM 203. Templat 200 (Bab 49)
terpisah, untuk VM layanan
Bab 13.4
(adguardhome-sync)
Jalan di VM 201 Tidak berubah
Lampiran B Rencana IP dan ID Edisi 2 Tidak ada ID atau IP yang diubah; ditambah VM
204 sampai 212, alamat .23 sampai .31, dan
templat 200 (tabel 48.3)
PERINGATAN
Homepage memakai port 3002, bukan 3001: Uptime Kuma (Suplemen 3 Bab 31) sudah memakai 3001 di VM 201,
sehingga dua layanan tidak bisa berbagi port itu sebelum Caddy dipasang.

**TERMINAL VM DOCKER-CORE** | VM 201, sebagai root (setelah su -)

```
cd /opt/stacks/homepage && nano compose.yaml
```
> Penjelasan: Ubah baris ports dan HOMEPAGE_ALLOWED_HOSTS seperti tabel di atas.
```
docker compose up -d
```
> Penjelasan: Membuat ulang container dengan port baru.
```
ss -tlnp | grep -E ":(80|3002)\b"
```
> Penjelasan: Port 3002 dipakai Homepage; port 80 harus bebas untuk Caddy.


<!-- SOURCE: docs/bab/suplemen/49-templat-vm.md -->

# Bab 49. Template VM Debian dan CT Debian serta Cara Mengklon Guest

PENEMPATAN - BARU - VM 200 (templat), lalu klon per layanan
Tempat: VM 200 Template-VM di host Proxmox. Templat tidak pernah dinyalakan setelah jadi; ia hanya
disalin.
Alasan: Satu sumber yang sama untuk semua VM Docker: cepat, seragam, dan pembaruan keamanan dasar sudah
ada. Setiap layanan lalu mendapat salinan penuh yang berdiri sendiri.
Tidak termasuk: Tailscale (setiap node harus punya identitas sendiri) dan layanan apa pun.

Bab ini menjelaskan dua sumber dasar yang bisa dipakai berulang: VM 200 untuk aplikasi berbasis VM/Docker, dan CT 100 untuk layanan Linux ringan tanpa Docker. Keduanya sudah dibuat dengan Debian 13 di Proxmox pada 1 November 2026. SSH baca-saja mengonfirmasi VM 200: 1 vCPU, RAM 2 GiB, disk 32 GiB, QEMU Agent aktif pada konfigurasi; CT 100: 1 vCPU, RAM/swap 512 MiB, disk 8 GiB, unprivileged, nesting, DHCP. Nama aktual tertulis `Tamplate-VM` dan `Tamplate-CT` (kemungkinan typo). Paket guest VM 200 belum diperiksa; periksa sebelum memakai template sebagai sumber guest Docker. Template adalah sumber yang tidak dijalankan; buat clone untuk setiap layanan, lalu atur nama, IP, resource, dan aplikasinya sendiri.

**Prasyarat sebelum mulai:** pembaruan Proxmox selesai dan host sudah reboot. Jalankan verifikasi pasca-update di Bab 9.6; `lscpu` harus menunjukkan VT-x dan `/dev/kvm` harus ada sebelum membuat template VM. Jika pemeriksaan gagal, perbaiki firmware mengikuti Bab 27.5. Template VM 200 dan CT 100 sudah tercatat dibuat; jangan buat ulang jika ID tersebut masih ada.

## 49.1 Rencana: dari mana templat dibuat

Template yang sudah tampak pada UI adalah VM 200 `Tamplate-VM` dan CT 100 `Tamplate-CT`; pengguna mengonfirmasi keduanya memakai Debian 13. Paket dasar VM 200 belum dicatat. Jangan jalankan ulang langkah pembuatan atau mengubah template berisi data; gunakan bagian 49.2–49.3 hanya bila perlu membangun ulang dari awal setelah memastikan template lama memang boleh diganti.

## 49.2 Membuat dan mengisi VM dasar

Pemasangan Debian secara rinci ada di Edisi 2 (Debian 13, ISO netinst, tanpa lingkungan desktop). Ringkasnya
di Proxmox:
1. Di web Proxmox klik Create VM. VM ID 200, Name Template-VM. Pada OS pilih ISO Debian 13 netinst.
2. System: biarkan bawaan dan centang QEMU Agent. Disks: Bus SCSI, ukuran 24 GiB (Debian + Docker dan
layanan kecil; data besar nanti pakai disk kedua). CPU 2 inti. Memory 2048.
3. Network: bridge vmbr0, model VirtIO. Selesaikan, jalankan, dan pasang Debian lewat konsol: hanya SSH
server dan standard system utilities yang dipilih.
4. Setelah masuk sebagai root (su -), lanjutkan di bawah.

**TERMINAL VM TEMPLAT** | VM 200, sebagai root (setelah su -)

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

**TERMINAL VM TEMPLAT** | VM 200, sebagai root

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

**TERMINAL VM TEMPLAT** | VM 200, sebagai root

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
1. Di Proxmox klik kanan VM 200 &gt; Convert to template (atau di shell host: qm template 200). Setelah ini
VM tidak bisa dinyalakan, hanya disalin.
2. Opsional: di Options templat, matikan Start at boot.

## 49.4 Penyiapan awal setiap VM hasil klon

Prosedur ini dipakai oleh semua bab yang membuat VM baru (kotak penempatan menyebut "Bab 49.4"). Contoh di bawah untuk VM 205 vault; ganti ID, nama, dan IP sesuai peta 48.3. Saat server masih di jaringan sementara, biarkan jaringan clone memakai DHCP dan jangan membuat reservasi MikroTik atau menetapkan IP `192.168.88.x`. Setelah host tersambung kembali ke MikroTik, ikuti langkah reservasi alamat di bawah.

**TERMINAL HOST PROXMOX** | Shell node Proxmox (host), sebagai root

```
qm clone 200 205 --name vault --full 1
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
Setelah host dan VM tersambung ke MikroTik, alamat tetap lewat reservasi DHCP MikroTik (DNS otomatis dari DHCP, sehingga menunjuk AdGuard). Dari Terminal di WinBox atau SSH ke MikroTik:

**TERMINAL MIKROTIK** | Terminal WinBox atau SSH ke 192.168.88.1

```
/ip dhcp-server print
```
> Penjelasan: Melihat nama server DHCP (misalnya defconf) untuk dipakai di bawah.
```
/ip dhcp-server lease add address=192.168.88.24 mac-address=AA:BB:CC:DD:EE:FF server=defconf comment=vault
```
> Penjelasan: Mereservasi 192.168.88.24 untuk MAC VM. Ganti MAC dan nama server. Alamat di luar rentang pool 100-254 untuk lease statis umumnya diterima [BELUM PASTI]; bila ditolak, atur IP statis di Debian.

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

## 49.6 Template CT Debian dasar dan cara mengklon

### Bedakan template unduhan dan template CT

Proxmox memakai arsip OS CT saat membuat container baru. Arsip unduhan itu belum menjadi CT yang siap diklon. Bagian ini membuat satu CT dasar bernama `Template-CT`, memasang pembaruan dan alat umum, lalu mengubah CT itu menjadi template Proxmox.

Gunakan CT untuk layanan Linux ringan tanpa Docker. Layanan yang memakai Docker tetap ditempatkan di VM Debian. Template CT memakai mode unprivileged sebagai pilihan awal. Jangan memasang layanan, Tailscale, kunci, token, atau data pribadi ke template.

### A. Unduh arsip Debian

Di web Proxmox pilih storage `local` > CT Templates > Templates. Cari Debian 13/Trixie standard amd64 terbaru yang tersedia, lalu unduh. Nama berkas dapat berubah mengikuti rilis.

### B. Buat CT dasar

1. Pilih Create CT. Gunakan CTID `100` dan hostname `Template-CT`.
2. Pilih template Debian yang baru diunduh.
3. Pilih storage `local-lvm` untuk disk root 8 GiB.
4. Pertahankan unprivileged container. Berikan 1 core dan RAM 512 MiB sebagai baseline.
5. Hubungkan ke bridge `vmbr0` dengan IPv4 DHCP. Jangan menanam IP layanan pada template.
6. Selesaikan wizard, nyalakan CT, lalu buka Console.

Jika server masih di jaringan sementara, DHCP membuat template bisa diperbarui tanpa memakai IP rumah yang belum terhubung. IP final diatur pada clone setelah MikroTik aktif.

### C. Perbarui sistem dasar

**TERMINAL CT DASAR** | Console CT 100, login root

```
apt update && apt full-upgrade -y
```
> Penjelasan: Memasang pembaruan dan perbaikan keamanan dasar.

```
apt install -y ca-certificates curl nano
```
> Penjelasan: Memasang alat umum minimum. Paket aplikasi dipasang nanti pada clone yang sesuai.

```
poweroff
```
> Penjelasan: Matikan CT sebelum mengubahnya menjadi template.

### D. Jadikan CT sebagai template

Pastikan CT 100 berhenti. Di UI pilih CT 100 > More > Convert to template. Alternatif pada shell host Proxmox:

**TERMINAL HOST PROXMOX** | Shell node sebagai root

```
pct template 100
```
> Penjelasan: Mengunci CT dasar sebagai sumber clone. Jangan menyalakan atau memasang aplikasi langsung pada template.

### E. Klon untuk layanan

Contoh membuat CT 101 untuk AdGuard kedua. Jalankan setelah host tersambung ke jaringan rumah dan pastikan IP `.11` belum digunakan:

```
pct clone 100 101 --full 1
```
> Penjelasan: Membuat salinan penuh yang berdiri sendiri dari template CT 100.

```
pct set 101 --hostname adguard2 --cores 1 --memory 512 --net0 name=eth0,bridge=vmbr0,ip=192.168.88.11/24,gw=192.168.88.1
```
> Penjelasan: Mengatur nama, resource, dan jaringan clone. Ganti CTID, hostname, CPU/RAM, dan IP sesuai peta guest.

```
pct start 101
pct exec 101 -- hostname
pct exec 101 -- ip -4 -br address
```
> Penjelasan: Menyalakan CT dan memeriksa hostname serta IP sebelum memasang aplikasi.

Untuk CT 102 Samba, ulangi proses clone dengan CTID `102`, nama `files`, dan IP `192.168.88.12`. Jangan memakai alamat `192.168.88.x` ketika host masih di jaringan sementara; gunakan DHCP atau tunggu sampai MikroTik tersambung.

### Catatan pembaruan template

Template tidak menerima pembaruan otomatis setelah dibuat. Untuk baseline baru, perbarui dan uji clone sementara, lalu buat template versi baru. Setiap clone perlu identitas SSH, hostname, alamat jaringan, dan resource yang unik.


<!-- SOURCE: docs/bab/suplemen/50-proxmox-backup-server.md -->

# Bab 50. Proxmox Backup Server

> **Revisi 3.** Datastore PBS direncanakan memakai salah satu dari dua HDD Seagate Surveillance 2 TB (Bab 27.4); contoh ukuran 200 GiB di bawah hanya patokan awal.

PENEMPATAN - BARU - VM sendiri
Tempat: VM 212 pbs (192.168.88.30), dipasang dari ISO resmi PBS, bukan dari templat Debian (VM 200).
Alasan: Server backup harus terpisah dari yang dicadangkan. Dokumentasi PBS menyebut server atau VM khusus;
memasang PBS di host Proxmox hanya sebuah opsi dan tidak dipakai di sini agar host tetap polos.
Tidak boleh: Digabung dengan layanan lain, dan tidak ikut dicadangkan oleh jobnya sendiri.
Batas yang jujur: PBS di mesin yang sama melindungi dari salah hapus, korupsi, dan kebobolan di dalam guest,
tetapi tidak dari kerusakan disk atau mesin. Karena itu datastore di disk fisik terpisah (50.2) dan ada salinan
kedua (50.13).
Proxmox Backup Server menyimpan backup VM secara terdeduplikasi dan bertahap: hanya bagian yang
berubah yang disimpan, sehingga backup harian murah. Backup bisa dienkripsi di sisi klien (PVE) sehingga
server tidak bisa membacanya.

## 50.1 Gambaran dan keputusan

Keputusan Pilihan buku ini Alasan
Tempat PBS VM 212 di host yang sama Satu mesin tersedia; ditutup oleh salinan kedua
50.13
Datastore Disk virtual dari disk fisik kedua Jangan sama dengan disk sistem; backup dan
VM tidak boleh hilang bersamaan
Jenis disk SSD bila ada; HDD diterima dengan harapan
lambat
Dokumentasi PBS menyarankan penyimpanan
lokal yang cepat; HDD memperlambat verifikasi,
GC, dan pemulihan [BELUM PASTI]
Enkripsi Aktif (AES-256-GCM, kunci dari PVE) Isi backup tidak terbaca dari sisi PBS; kunci
wajib disimpan terpisah
Penghapusan backup lama Dilakukan di sisi PBS Pengguna PVE hanya boleh menambah backup,
tidak menghapus (lebih aman bila host PVE
kebobolan)

## 50.2 Menyiapkan disk fisik untuk datastore (host)

Di web Proxmox buka node &gt; Disks. Disk kedua (bukan yang berisi Proxmox) harus kosong. Bila ada isi lama:
pilih disk &gt; Wipe Disk (menghapus semuanya, pastikan disk yang benar). Lalu buat penyimpanan di atasnya:
1. Node &gt; Disks &gt; Directory &gt; Create: Directory. Pilih disk kedua, filesystem ext4, nama backup-disk. Biarkan
Add Storage tercentang.
2. Hasilnya penyimpanan backup-disk tampil di Datacenter &gt; Storage. Di sinilah disk virtual datastore PBS akan
dibuat.
CATATAN
Disk kedua adalah HDD 2 TB (bay 2,5" atau USB; lihat Bab 27.4). Datastore PBS wajib di perangkat fisik berbeda dari NVMe sistem.

## 50.3 Mengunduh ISO dan membuat VM pbs

1. Unduh ISO Proxmox Backup Server terbaru dari proxmox.com/en/downloads (dokumentasi resmi yang saya
baca mencantumkan rilis 4.1; nomor terbaru [BELUM PASTI]).
2. Di Proxmox: node &gt; storage local &gt; ISO Images &gt; Upload, pilih ISO PBS.
3. Klik Create VM: VM ID 212, Name pbs, ISO PBS. System bawaan. Disks: SCSI 32 GiB di local-lvm untuk
sistem. CPU 2 inti. Memory 2048 (perkiraan [BELUM PASTI]). Network vmbr0, VirtIO.
4. Setelah VM terbentuk: Hardware &gt; Add &gt; Hard Disk: Storage backup-disk, ukuran sesuai kebutuhan (mulai
dari 200 GiB; ukuran bergantung total data dan retensi).
5. Nyalakan VM dan buka Console.
PERINGATAN
Pada pemasangan nanti, pilih disk 32 GiB sebagai target sistem. Disk besar jangan dipilih; ia dipakai untuk datastore
sesudah pemasangan.

## 50.4 Pemasangan PBS

1. Pilih Install Proxmox Backup Server (Graphical) dan setujui EULA.
2. Target: disk 32 GiB, filesystem ext4. Lanjut.
3. Negara Indonesia, zona waktu Asia/Jakarta, papan ketik sesuai.
4. Kata sandi root yang kuat (simpan di Vaultwarden) dan email Anda.
5. Jaringan: Hostname (FQDN) pbs.home.arpa, IP 192.168.88.30/24, Gateway 192.168.88.1, DNS
192.168.88.253.
6. Install. Setelah selesai, di web Proxmox buka VM 212 &gt; Hardware &gt; CD/DVD &gt; Do not use any media, lalu
reboot VM.
TIPS
Gunakan alamat IP, bukan nama pbs.home.arpa, saat menghubungkan PVE ke PBS. Rewrite wildcard \*.home.arpa di
AdGuard mengarahkan nama itu ke docker-core, bukan ke PBS.

## 50.5 Pasca-instalasi

1. Dari laptop buka https://192.168.88.30:8007 (setujui peringatan sertifikat). Masuk: User root, Realm Linux
PAM standard authentication.
2. Buka Administration &gt; Repositories. Nonaktifkan repositori enterprise (Disable), lalu Add &gt;
No-Subscription. Pesan peringatan tanpa langganan di login boleh diabaikan.
3. Buka Administration &gt; Updates &gt; Refresh lalu Upgrade.

## 50.6 Membuat datastore

**TERMINAL PBS** | Shell PBS: Administration &gt; Shell, atau konsol VM 212

```
lsblk -o NAME,SIZE,TYPE,MOUNTPOINT
```
> Penjelasan: Mengenali disk besar yang kosong (misalnya sdb) dan membedakannya dari disk sistem 32 GiB.
1. Di web PBS buka Administration &gt; Storage / Disks &gt; Directory &gt; Create: Directory. Disk: disk besar tadi,
filesystem ext4, nama store1, dan biarkan Add as Datastore tercentang.
2. Datastore store1 muncul di panel kiri. Alternatif baris perintah (sintaks belum saya verifikasi [BELUM PASTI]):
proxmox-backup-manager disk fs create store1 --disk sdb --filesystem ext4 --add-datastore true.

## 50.7 Pengguna khusus untuk Proxmox VE

1. Buka Configuration &gt; Access Control &gt; User Management &gt; Add: User name pve, Realm Proxmox
Backup authentication server, kata sandi kuat (simpan di Vaultwarden).
2. Tab Permissions &gt; Add &gt; User Permission: Path /datastore/store1, User pve@pbs, Role
DatastoreBackup, Propagate dicentang.
Peran DatastoreBackup memungkinkan membuat dan memulihkan backup miliknya tanpa menghapus backup
lain; nama peran dan batasnya [BELUM PASTI] - periksa di daftar Role pada PBS. Penghapusan backup lama
ditangani job prune di PBS (50.11), bukan oleh PVE.

## 50.8 Sidik jari sertifikat PBS

1. Di Dashboard PBS klik Show Fingerprint dan salin nilainya (deretan heksadesimal berpasangan).

**TERMINAL PBS** | Shell PBS (alternatif)

```
proxmox-backup-manager cert info | grep -i fingerprint
```
> Penjelasan: Menampilkan sidik jari yang sama dari baris perintah.

## 50.9 Menambahkan PBS ke Proxmox VE

1. Di web Proxmox: Datacenter &gt; Storage &gt; Add &gt; Proxmox Backup Server.
2. ID pbs-home, Server 192.168.88.30, Username pve@pbs, Password, Datastore store1, Fingerprint tempel
dari 50.8.
3. Tab Encryption: pilih Auto-generate a client encryption key lalu Add.
4. Simpan kunci enkripsi yang ditampilkan. Salin ke Vaultwarden (catatan aman atau lampiran) dan cetak
satu salinan di kertas yang disimpan terpisah.
PERINGATAN
Tanpa kunci ini backup terenkripsi tidak bisa dipulihkan, termasuk bila host Proxmox rusak. Kunci hanya ada
di host PVE (di /etc/pve/priv/storage/); jika host hilang dan Anda tidak menyalinnya, backup di PBS menjadi tak
berguna. Ini risiko terbesar bab ini.
CATATAN
Alternatif baris perintah ada di dokumentasi (pvesm add pbs), tetapi memasukkan kata sandi di baris perintah tercatat
di riwayat shell; antarmuka web lebih aman untuk langkah ini.

## 50.10 Job backup terjadwal

1. Pastikan setiap VM yang dicadangkan memiliki opsi QEMU Guest Agent aktif (Options) dan agen terpasang
(sudah ada di templat 49).
2. Datacenter &gt; Backup &gt; Add: Node pve, Storage pbs-home, Schedule 02:00 (setiap hari), Selection mode
Include selected VMs: 201, 202, 203, 204, 205, 206, 207, 208, 209, 210, 211, 213, 214 (disk pustaka musik
VM 211 ditandai backup=0 di Bab 53.1; disk foto VM 214 ikut backup, Bab 55.8). Jangan mencentang 212
(pbs) dan 200 (templat). Mode Snapshot.
3. Tab Retention: centang Keep all backups (penghapusan dilakukan di PBS).
4. Pilih job &gt; Run now. Lihat tab Tasks: setiap VM harus selesai dengan TASK OK.
Backup tingkat VM (snapshot) melindungi seluruh isi VM. Dump logis yang dibuat di bab lama (pg_dump, tar)
tetap berguna sebagai lapisan kedua: bisa dipulihkan per aplikasi tanpa memulihkan satu VM utuh.

## 50.11 Prune, garbage collection, dan verifikasi (di PBS)

1. Di PBS pilih store1 &gt; Prune & GC &gt; Add Prune Job: Schedule daily 03:00, Keep Last 3, Daily 7, Weekly 4,
Monthly 3 (contoh retensi; sesuaikan dengan disk).
2. Atur Garbage Collection Schedule pada Options datastore, misalnya sat 04:00.
3. Buka Verify Jobs &gt; Add: Schedule daily 05:00, centang Skip verified, verifikasi ulang setelah 30 hari.
CATATAN
Prune hanya menandai backup lama untuk dibuang; ruang baru kembali setelah garbage collection berjalan. GC
tidak langsung membuang data yang baru dihapus (ada masa tunggu sekitar satu hari [BELUM PASTI]), jadi ruang
tidak turun seketika.

## 50.12 Uji pemulihan (wajib)

Backup yang belum pernah dipulihkan belum terbukti. Pulihkan satu VM kecil ke ID sementara:
1. Datacenter &gt; Storage &gt; pbs-home &gt; VM Backups: pilih backup VM 209 &gt; Restore.
2. VM ID 999, centang Unique (alamat MAC baru), jangan centang Start after restore.
3. Sebelum menyalakan: VM 999 &gt; Hardware &gt; Network Device &gt; Edit &gt; centang Disconnect. Ini mencegah
salinan memakai IP, nama, atau identitas Tailscale yang sama dengan aslinya.
4. Nyalakan VM 999 dan buka konsol: pastikan sistem naik dan data ada (misalnya docker ps, folder
/opt/stacks). Lalu matikan dan hapus VM 999.
KEAMANAN
Jangan pernah menyalakan hasil pemulihan VM vault dengan jaringan tersambung sementara aslinya hidup: dua
mesin dengan identitas Tailscale yang sama saling mengganggu.

## 50.13 Salinan kedua di luar mesin (aturan 3-2-1)

Dokumentasi PBS membahas aturan 3-2-1: tiga salinan, dua media, satu di luar lokasi. Dengan satu mesin Anda
minimal butuh satu salinan di media lain:
Opsi Cara Catatan
A. Disk USB (disarankan
sekarang)
Node &gt; Disks &gt; pilih disk USB &gt; Directory &gt; Create (ext4, nama
usb-backup); Datacenter &gt; Backup &gt; Add job mingguan ke
storage usb-backup, Selection 205 dan 207 (vault, nextcloud)
atau semua, retensi Keep Last 2
Colokkan hanya saat job
berjalan, lalu lepas;
salinan offline tahan
ransomware
B. PBS kedua + Sync Job Server PBS di lokasi lain, lalu Sync Job dari store1 Terbaik, tetapi butuh
perangkat dan lokasi
kedua; untuk nanti
C. Konfigurasi host Proxmox Perintah di bawah, lalu salin ke laptop Wajib: berisi definisi VM
dan penyimpanan

**TERMINAL HOST PROXMOX** | Shell node Proxmox (host), sebagai root

```
tar czf /root/pve-config-$(date +%F).tgz /etc/pve /etc/network/interfaces /etc/hosts /etc/fstab
```
> Penjelasan: Mengarsipkan konfigurasi host (termasuk kunci enkripsi backup di /etc/pve/priv). Perlakukan sebagai rahasia.

**POWERSHELL WINDOWS** | PowerShell (laptop)

```
scp root@192.168.88.10:/root/pve-config-*.tgz .
```
> Penjelasan: Menyalin arsip ke laptop. Simpan di tempat aman, bukan di folder yang disinkronkan ke layanan
publik.

## 50.14 Notifikasi ke Gotify

1. Di Gotify (Suplemen 3 Bab 32) buat aplikasi baru proxmox dan salin tokennya.
2. Di Proxmox: Datacenter &gt; Notifications &gt; Targets &gt; Add &gt; Gotify. Server URL http://192.168.88.20:8070,
Token tadi, lalu Test.
3. Buka tab Notification Matchers &gt; Add: kecocokan tingkat warning dan error (atau semua kategori backup),
target gotify. Nama menu persis [BELUM PASTI] menurut versi Proxmox 9.2.
4. Di PBS: Configuration &gt; Notifications dengan cara serupa agar kegagalan prune, GC, atau verifikasi juga
sampai ke HP.

## 50.15 Sisi klien

Perangkat Yang dilakukan Catatan
Windows Kelola PBS di https://192.168.88.30:8007; ambil arsip konfigurasi
host dengan scp
Pekerjaan utama dari sini
Android Aplikasi Gotify menerima peringatan backup; buka dasbor PBS
lewat Tailscale bila perlu
Aktifkan notifikasi Gotify (Suplemen 3
Bab 32)
iPhone Sama; pastikan notifikasi Gotify diizinkan di Pengaturan iOS Peringatan sertifikat PBS disetujui di
Safari


<!-- SOURCE: docs/bab/suplemen/51-firewall-proxmox.md -->

# Bab 51. Firewall Proxmox antar-guest

PENEMPATAN - HOST - tidak ada guest baru
Tempat: Aturan dibuat di host Proxmox (web Proxmox atau berkas /etc/pve/firewall) dan berlaku untuk semua guest.
Alasan: Firewall Proxmox bekerja di jembatan jaringan, di luar guest. Port yang dibuka Docker di dalam VM tidak
bisa menembusnya, tidak seperti UFW di dalam VM.
PERINGATAN
Firewall Proxmox mati secara bawaan. Setelah dinyalakan di tingkat Datacenter, lalu lintas ke host diblokir kecuali
web (8006) dan SSH (22) dari jaringan lokal (menurut dokumentasi). Buka sesi SSH ke host sebelum
mengaktifkannya, dan ikuti urutan di 51.3. Konsol web VM (noVNC) tetap berfungsi bila aturan VM salah.

## 51.1 Tiga tingkat

Tingkat Tempat Fungsi
Datacenter Datacenter &gt; Firewall Saklar utama, daftar IPSet, kelompok aturan;
aturannya ikut berlaku untuk host
Node (host) Node &gt; Firewall Aturan khusus host; lebih diutamakan daripada
aturan Datacenter
VM / CT VM &gt; Firewall, dan kotak Firewall pada Network
Device
Aturan per guest. Tanpa kotak itu pada kartu
jaringan, aturan VM tidak berlaku

## 51.2 Matriks akses: siapa boleh ke mana

Tujuan Port Boleh dari Alasan
201 docker-core 80, 443 Seluruh LAN 192.168.88.0/24 Pintu semua layanan (Caddy)
201 docker-core 8070 (Gotify) host .10, n8n .27, pbs .30 Peringatan Proxmox, PBS, dan n8n
204 git 3000 (web) docker-core .20 Web Forgejo hanya lewat Caddy
(git.home.arpa)
204 git 2222 (SSH Git) IPSet admin dan VM 203 k3s .22 Clone dari laptop dan Flux (Edisi 2 Bab
21)
202 haos 8123 Seluruh LAN 192.168.88.0/24 Aplikasi HP dan peramban; dari luar
rumah lewat Tailscale (alamat CT103)
203 k3s 6443 IPSet admin kubectl dari laptop
206 affine 3010 docker-core .20 Hanya lewat Caddy
207 nextcloud 8080 docker-core .20 Hanya lewat Caddy
208 n8n 5678 docker-core .20 Hanya lewat Caddy
209 web 8081, 8082 docker-core .20 Hanya lewat Caddy
205 vault (tidak ada) - Hanya lewat Tailscale Serve (koneksi
keluar)
210 web-public (tidak ada) - Hanya koneksi keluar lewat tunnel;
keluar ke LAN diblokir
211 music (tidak ada) - Hanya lewat Tailscale Serve (koneksi
keluar); berkas aturan di Bab 53.6
213 sso (tidak ada) - Hanya lewat Tailscale Serve (koneksi
keluar); berkas aturan di Bab 54.7
214 immich (tidak ada) - Hanya lewat Tailscale Serve (koneksi
keluar); berkas aturan di Bab 55.8
212 pbs 8007 host .10 dan admin Antarmuka dan sinkron PVE
Semua VM 22 (SSH) IPSet admin Pengelolaan
Semua VM port agen Beszel docker-core .20 Hub menghubungi agen (port:
Suplemen 3 Bab 33)
Host .10 8006, 22 IPSet admin Pengelolaan Proxmox
IPSet admin berisi perangkat yang boleh mengelola: PC kabel (192.168.88.252), laptop Anda, dan alamat
CT103 (router-vm). Perangkat yang masuk lewat Tailscale tiba dari alamat CT103 (subnet router menyamarkan
sumbernya [BELUM PASTI]), jadi tanpa itu SSH dari luar rumah akan diblokir. Kendali siapa yang boleh lewat
Tailscale ada di kebijakan tailnet.

## 51.3 Urutan menyalakan (agar tidak terkunci)

1. Buka SSH ke host (ssh root@192.168.88.10) dan biarkan terbuka. Siapkan juga konsol web VM.
2. Reservasi alamat tetap untuk laptop Anda di MikroTik (seperti Bab 49.4) agar IPSet tidak basi.
3. Datacenter &gt; Firewall &gt; IPSet &gt; Create admin; tambahkan 192.168.88.252, alamat laptop, dan alamat CT103.
4. Datacenter &gt; Firewall &gt; Options: Firewall Yes, Input Policy DROP, Output Policy ACCEPT. Uji bahwa web
Proxmox (8006) dan SSH host tetap terbuka dari laptop.
5. Aktifkan firewall per VM satu demi satu, mulai dari yang paling sederhana (VM 205). Setiap kali: Options VM:
Firewall Yes, Input DROP, Output ACCEPT; kotak Firewall pada Hardware &gt; Network Device; tambah aturan;
uji (51.6).
6. Biarkan opsi IP filter dan MAC filter pada setelan bawaannya; laporan pengguna menyebut IP filter yang aktif
bisa membuat VM tak terjangkau.

## 51.4 Aturan per VM

Contoh berikut mengikuti matriks di 51.2 dan contoh berkas di `konfigurasi/firewall/`. Port agen Beszel adalah `45876` menurut `docs/07-port-dan-akses.md`. Sesuaikan hanya setelah memeriksa port aktual pada guest; aktifkan firewall per guest satu per satu dan uji dari klien.

Berkas docker-core:

**/etc/pve/firewall/201.fw** | Isi berkas

```
[OPTIONS]
enable: 1
policy_in: DROP
policy_out: ACCEPT
dhcp: 1
[RULES]
IN ACCEPT -source +dc/admin -p tcp -dport 22
IN ACCEPT -source 192.168.88.0/24 -p tcp -dport 80,443
IN ACCEPT -source 192.168.88.10 -p tcp -dport 8070
IN ACCEPT -source 192.168.88.27 -p tcp -dport 8070
IN ACCEPT -source 192.168.88.30 -p tcp -dport 8070
IN ACCEPT -p icmp
```

VM aplikasi di belakang Caddy (contoh VM 206 AFFiNE):

**/etc/pve/firewall/206.fw** | Isi berkas

```
[OPTIONS]
enable: 1
policy_in: DROP
policy_out: ACCEPT
dhcp: 1
[RULES]
IN ACCEPT -source +dc/admin -p tcp -dport 22
IN ACCEPT -source 192.168.88.20 -p tcp -dport 3010
IN ACCEPT -source 192.168.88.20 -p tcp -dport 45876
IN ACCEPT -p icmp
```

Untuk VM 207, 208, dan 209, ganti port layanan dengan nilai pada matriks 51.2: `8080`, `5678`, dan `8081,8082`. Jika memakai mode hemat dan layanan digabung ke VM 206, aturan harus mencakup seluruh port layanan yang benar-benar dipakai VM tersebut.

VM git: web hanya dari Caddy; SSH Git dari admin dan VM k3s:

**/etc/pve/firewall/204.fw** | Isi berkas

```
[OPTIONS]
enable: 1
policy_in: DROP
policy_out: ACCEPT
dhcp: 1
[RULES]
IN ACCEPT -source +dc/admin -p tcp -dport 22
IN ACCEPT -source +dc/admin -p tcp -dport 2222
IN ACCEPT -source 192.168.88.22 -p tcp -dport 2222
IN ACCEPT -source 192.168.88.20 -p tcp -dport 3000
IN ACCEPT -source 192.168.88.20 -p tcp -dport 45876
IN ACCEPT -p icmp
```

VM web-public: izinkan SSH admin, DNS keluar ke AdGuard, lalu blokir akses ke LAN:

**/etc/pve/firewall/210.fw** | Isi berkas

```
[OPTIONS]
enable: 1
policy_in: DROP
policy_out: ACCEPT
dhcp: 1
[RULES]
IN ACCEPT -source +dc/admin -p tcp -dport 22
OUT ACCEPT -dest 192.168.88.253 -p udp -dport 53
OUT ACCEPT -dest 192.168.88.253 -p tcp -dport 53
OUT DROP -dest 192.168.88.0/24
```

Untuk VM 205, 211, 213, dan 214, jangan buka port layanan pada LAN; layanan diakses melalui Tailscale Serve. Untuk VM 212 PBS, izinkan port 8007 hanya dari host Proxmox dan perangkat admin. Aturan VM 202 Home Assistant dan VM 203 k3s mengikuti matriks 51.2.

> [!WARNING]
> Contoh ini mengasumsikan IPSet Datacenter bernama `admin` dan sintaks `+dc/admin` diterima oleh versi Proxmox yang dipakai. Bagian ini masih perlu diuji pada host sebelum firewall diaktifkan. Jangan mengaktifkan aturan massal; uji satu guest dan pastikan akses konsol serta jalur pemulihan tersedia.

**TERMINAL HOST PROXMOX** | Shell node Proxmox (host), sebagai root

```
pve-firewall status
```
> Penjelasan: Memastikan layanan firewall berjalan dan aktif.
```
qm config 206 | grep net0
```
> Penjelasan: Menampilkan baris kartu jaringan. Aktifkan firewall pada kartu itu bila belum (langkah berikut).
```
qm set 206 --net0 "virtio=AA:BB:CC:DD:EE:FF,bridge=vmbr0,firewall=1"
```
> Penjelasan: Menulis ulang net0 dengan firewall=1. Salin nilai MAC dan bridge dari baris sebelumnya; atau pakai
kotak Firewall di antarmuka web.

## 51.5 Sisi klien

1. Windows: buka https://affine.home.arpa, https://nextcloud.home.arpa, https://n8n.home.arpa,
https://wp.home.arpa. Semua tetap terbuka karena lewat Caddy (443).
2. Android dan iPhone: buka alamat yang sama di browser (rumah atau Tailscale). Hasil harus sama dengan di
laptop.
3. Kini alamat langsung seperti http://192.168.88.25:3010 dari laptop atau HP tidak boleh terbuka lagi. Itu
tandanya firewall bekerja.

## 51.6 Uji

**POWERSHELL WINDOWS** | PowerShell (laptop)

```
Test-NetConnection 192.168.88.25 -Port 3010
```
> Penjelasan: Harus TcpTestSucceeded: False (diblokir). Laptop tidak termasuk 192.168.88.20.
```
Test-NetConnection 192.168.88.20 -Port 443
```
> Penjelasan: Harus True (gerbang Caddy terbuka).

**TERMINAL VM DOCKER-CORE** | VM docker-core, sebagai root

```
timeout 3 bash -c '</dev/tcp/192.168.88.25/3010' && echo terbuka || echo tertutup
```
> Penjelasan: Dari docker-core ke AFFiNE: harus terbuka.
```
timeout 3 bash -c '</dev/tcp/192.168.88.26/22' && echo terbuka || echo tertutup
```
> Penjelasan: Dari docker-core ke SSH nextcloud: harus tertutup (docker-core bukan IPSet admin).

**TERMINAL VM WEB-PUBLIC** | VM web-public (210), sebagai root

```
timeout 3 bash -c '</dev/tcp/192.168.88.20/443' && echo terbuka || echo tertutup
```
> Penjelasan: Harus tertutup: VM publik tidak boleh menjangkau LAN.
```
curl -sI https://example.com | head -1
```
> Penjelasan: Harus berhasil (internet tetap bisa, termasuk untuk tunnel dan pembaruan).
TIPS
Terkunci? Buka konsol web VM di Proxmox (tidak lewat jaringan VM), atau di VM: Firewall &gt; Options &gt; Firewall No,
perbaiki aturan, lalu nyalakan lagi.


<!-- SOURCE: docs/bab/suplemen/52-audit-keamanan.md -->

# Bab 52. Audit Keamanan

PENEMPATAN - SEMUA GUEST - baca-saja
Tempat: Skrip audit dijalankan di setiap VM (dan bagian host di shell node Proxmox). Tidak ada guest baru, tidak ada
layanan baru.
Alasan: Setiap guest dapat berbeda keadaannya. Hasil audit dicatat per guest supaya temuan jelas milik siapa.
Prinsip: Skrip hanya membaca dan mencetak; tidak mengubah apa pun.
Audit adalah pemeriksaan berkala bahwa keadaan sebenarnya sama dengan yang Anda kira. Bab ini memberi
daftar, satu skrip untuk VM, dan tabel laporan. Hasilnya bukan jaminan aman; ia hanya menunjukkan apa yang
terlihat dari alat yang dipakai.

## 52.1 Daftar pemeriksaan per lapisan

Lapisan Pemeriksaan Cara Hasil yang diharapkan
MikroTik Tidak ada port forward; layanan
terbatas
/ip firewall nat print; /ip service
print
Hanya masquerade; layanan
dibatasi 192.168.88.0/24 (Edisi
2)
Tailscale Funnel tidak aktif; perangkat
dikenal; key expiry
tailscale funnel status (di tiap
node); konsol admin Machines
Funnel kosong; tidak ada
perangkat asing
Tailscale Kebijakan tailnet Editor kebijakan Hanya entri yang Anda pahami
(Suplemen 1 Bab 26.6, 44.3)
Host Proxmox Tidak ada Docker; pembaruan; port which docker; apt list
--upgradable; ss -tlnp
docker tidak ada; port hanya
8006, 22, layanan Proxmox
Host Proxmox Firewall aktif; 2FA untuk root pve-firewall status; Datacenter &gt;
Permissions &gt; Two Factor
Aktif; TOTP terpasang
Setiap VM Port mendengarkan dan port
Docker
Skrip 52.2 Hanya yang ada di matriks 51.2
Setiap VM Kontainer privileged; docker.sock Skrip 52.2 Kosong, atau risiko dicatat
(Portainer)
Setiap VM Berkas .env Skrip 52.2 Tidak dapat dibaca orang lain
(mode 600)
Setiap VM SSH: kunci saja, tanpa root Skrip 52.2; 52.4 passwordauthentication no;
permitrootlogin no
Setiap VM Pembaruan keamanan otomatis systemctl is-enabled
unattended-upgrades
enabled
Lynis Skor dan saran 52.3 Dibaca, bukan diterapkan buta
Backup Job terakhir berhasil; uji pulih; kunci
tersimpan; salinan kedua
Datacenter &gt; Backup; Bab 50 Semua ya, bertanggal
Publik Hanya tunnel VM 210 yang
menghadap internet
Dasbor Cloudflare: daftar route Hanya hostname situs publik

## 52.2 Skrip audit untuk VM

**TERMINAL VM** | Setiap VM, sebagai root (setelah su -)

```
nano /root/audit-vm.sh
```
> Penjelasan: Isi seperti kotak di bawah.

**/root/audit-vm.sh** | Isi berkas

```
#!/bin/bash
# Audit baca-saja. Mencetak temuan, tidak mengubah apa pun.
echo "== Host: $(hostname) | $(date '+%F %T')"
echo "== Port mendengarkan selain loopback"
ss -tulnH | awk '$5 !~ /^127\.|^\[::1\]/ {print $1, $5}'
if command -v docker >/dev/null; then
 echo "== Port Docker yang dipublikasikan"
 docker ps --format '{{.Names}}: {{.Ports}}' | grep -- '->'
 echo "== Kontainer privileged (idealnya kosong)"
```

 docker ps -q | xargs -r docker inspect \
 --format '{{.Name}} {{.HostConfig.Privileged}}' | grep true
 echo "== Kontainer yang memasang docker.sock"
 docker ps -q | xargs -r docker inspect \
 --format '{{.Name}} {{range .Mounts}}{{.Source}} {{end}}' | grep docker.sock
fi
echo "== Berkas .env terbaca orang lain (idealnya kosong)"
find /opt/stacks -maxdepth 2 -name .env -perm /077 2&gt;/dev/null
echo "== Pengaturan SSH"
sshd -T 2&gt;/dev/null | grep -E '^(permitrootlogin|passwordauthentication) '
echo "== Pembaruan otomatis"
systemctl is-enabled unattended-upgrades 2&gt;/dev/null || echo "tidak aktif"
echo "== Jumlah paket menunggu pembaruan"
apt list --upgradable 2&gt;/dev/null | grep -vc '^Listing'

**TERMINAL VM** | Setiap VM, sebagai root

```
chmod 700 /root/audit-vm.sh && /root/audit-vm.sh | tee /root/audit-$(date +%F).txt
```
> Penjelasan: Menjalankan skrip dan menyimpan hasilnya bertanggal untuk laporan 52.7.
Bagian keluaran Cara membacanya
Port mendengarkan Cocokkan dengan matriks 51.2. Port yang tidak Anda kenal: cari prosesnya dengan ss -tulnp
Port Docker Setiap tanda 0.0.0.0:PORT-&gt; adalah port terbuka di LAN VM; pastikan firewall Proxmox
membatasinya
Privileged / docker.sock Kontainer dengan docker.sock setara akses root ke VM. Portainer dan agen Beszel biasanya
memerlukannya; catat sebagai risiko diterima (52.7)
SSH Targetnya permitrootlogin no dan passwordauthentication no setelah 52.4
Pembaruan Angka besar berarti VM jarang diperbarui; jalankan apt update && apt upgrade dan periksa

## 52.3 Lynis (opsional tetapi berguna)

**TERMINAL VM** | Satu VM dulu (misalnya docker-core), sebagai root

```
apt install -y lynis
```
> Penjelasan: Memasang pemindai audit dari repositori Debian (versinya bisa lebih lama dari rilis terbaru proyeknya
[BELUM PASTI]).
```
lynis audit system
```
> Penjelasan: Memindai sistem (beberapa menit). Di akhir tercetak Hardening index dan daftar saran.
```
grep -E "^(warning|suggestion)" /var/log/lynis-report.dat | head -40
```
> Penjelasan: Mencetak peringatan dan saran dari laporan.
PERINGATAN
Jangan menerapkan semua saran Lynis secara buta; sebagian mengubah perilaku sistem (misalnya mematikan
layanan atau mengunci kernel) dan bisa merusak Docker atau agen tamu. Baca satu per satu, terapkan yang Anda
pahami, catat yang ditolak.

## 52.4 SSH dengan kunci (tanpa kata sandi)

**POWERSHELL WINDOWS** | PowerShell (laptop)

```
ssh-keygen -t ed25519
```
> Penjelasan: Membuat pasangan kunci di folder .ssh Anda. Beri frasa sandi pada kunci.
```
scp $env:USERPROFILE\.ssh\id_ed25519.pub <USER>@192.168.88.24:/tmp/
```
> Penjelasan: Menyalin kunci publik ke VM (ganti &lt;USER&gt; dan IP; ulangi untuk tiap VM).

**TERMINAL VM** | VM tujuan, sebagai pengguna biasa (bukan root)

```
mkdir -p ~/.ssh && cat /tmp/id_ed25519.pub >> ~/.ssh/authorized_keys
```
> Penjelasan: Mendaftarkan kunci.
```
chmod 700 ~/.ssh && chmod 600 ~/.ssh/authorized_keys
```
> Penjelasan: Izin yang disyaratkan SSH.
Uji dulu dari jendela PowerShell kedua (ssh &lt;USER&gt;@IP) sampai masuk tanpa kata sandi akun. Baru kunci
sandi, dengan sesi lama tetap terbuka:

**TERMINAL VM** | VM tujuan, sebagai root (setelah su -)

```
nano /etc/ssh/sshd_config.d/10-hardening.conf
```
> Penjelasan: Isi dua baris seperti kotak di bawah.

**/etc/ssh/sshd_config.d/10-hardening.conf** | Isi berkas

```
PasswordAuthentication no
PermitRootLogin no
```

**TERMINAL VM** | VM tujuan, sebagai root

```
sshd -t && systemctl reload ssh
```
> Penjelasan: Memeriksa sintaks, lalu memuat ulang SSH. Jangan menutup sesi lama sebelum uji sesi baru
berhasil.
CATATAN
Konsol web Proxmox tetap menjadi jalur darurat bila SSH terkunci. Untuk Android dan iPhone, SSH ke VM tidak
diperlukan; pekerjaan itu dilakukan dari laptop.

## 52.5 Pembaruan otomatis dan pembaruan host

**TERMINAL VM** | Setiap VM, sebagai root

```
dpkg-reconfigure -plow unattended-upgrades
```
> Penjelasan: Mengaktifkan pembaruan keamanan otomatis Debian (jawab Yes). Ini tidak memperbarui image
Docker; image diperbarui manual dengan docker compose pull (dengan backup lebih dulu).
```
unattended-upgrade --dry-run -d 2>&1 | tail -5
```
> Penjelasan: Uji kering: menunjukkan apa yang akan dilakukan tanpa menjalankannya.
Host Proxmox: node &gt; Updates &gt; Refresh lalu Upgrade, dan jadwalkan pemeriksaan bulanan. Buat backup (Bab
50) sebelum pembaruan besar.

## 52.6 Tailscale, Cloudflare, MikroTik, PBS

1. Di setiap node tailnet (router-vm, lab-vault): tailscale funnel status harus kosong, dan tailscale serve status
hanya memuat layanan yang Anda niatkan.
2. Konsol admin Tailscale &gt; Machines: cabut perangkat yang tidak dikenali; periksa tanggal kedaluwarsa kunci
(server dinonaktifkan expiry-nya).
3. Cloudflare (bila Bab 43 dikerjakan): daftar route tunnel hanya berisi hostname situs publik; token pernah
dirotasi bila ada kecurigaan.
4. MikroTik: /ip firewall nat print tidak memuat dst-nat; layanan IP sesuai Edisi 2.
5. PBS: akun root memakai 2FA (Access Control &gt; Two Factor); pengguna pve@pbs hanya berperan
DatastoreBackup.

## 52.7 Laporan audit

Isi satu baris per guest setiap audit. Simpan keluaran skrip bertanggal di VM masing-masing.
Guest Tanggal Port sesuai
matriks
Privileged /
docker.sock
SSH kunci Update
otomatis
Skor Lynis
201 docker-core
204 git
205 vault
206 affine
207 nextcloud
208 n8n
209 web
210 web-public
211 music
212 pbs
213 sso
214 immich
Host Proxmox -
Risiko yang diterima (isi dengan sadar)
Temuan Alasan diterima Tinjau kembali
Portainer memasang docker.sock
(docker-core)
Fungsinya memang mengelola Docker; terbatas pada VM
docker-core dan hanya dapat dijangkau dari LAN via
Caddy
Tiap audit
Agen Beszel memasang docker.sock
(bila dipakai)
Untuk membaca statistik kontainer Tiap audit
(tambahkan sendiri)

## 52.8 Sisi klien dan jadwal

Perangkat Pemeriksaan berkala
Windows Jalankan skrip audit lewat SSH; perbarui Windows dan Tailscale; pastikan kunci SSH berfrasa sandi
Android Buka aplikasi Tailscale dan pastikan hanya perangkat Anda yang tersambung; periksa notifikasi Gotify
masih tiba; perbarui Android, Bitwarden, DAVx5
iPhone Sama: periksa Tailscale dan Gotify; perbarui iOS dan aplikasi; kunci layar aktif
Jadwal: audit penuh setiap bulan, ditambah satu audit singkat (skrip 52.2 pada VM terkait) setiap kali menambah
atau mengubah layanan. Catat tanggalnya di laporan 52.7.


<!-- SOURCE: docs/bab/suplemen/bagian-7-99-penutup.md -->

# Bagian 7. Penempatan VM/LXC, Backup, dan Audit: Uji, Masalah Umum, Lembar Pembaruan, Syarat Lulus Fase 7

Uji, Masalah Umum, dan Lembar Pembaruan
Uji menyeluruh
No Uji Hasil yang diharapkan
1 qm list di host Terlihat VM 201-212 (sesuai yang sudah dibuat) dan
templat 200
2 Satu VM baru dari templat (Bab 49.4) Nama host, kunci SSH, dan IP unik; ping DNS dan
internet berhasil
3 Backup pertama ke pbs-home TASK OK untuk setiap VM; ukuran datastore
bertambah
4 Uji pulih VM 999 tanpa jaringan Sistem naik, data ada; VM sementara dihapus
5 Prune, GC, dan verify berjalan sekali Tidak ada galat di tab Tasks PBS
6 Kegagalan backup disimulasikan (matikan PBS lalu jalankan
job)
Notifikasi Gotify tiba di HP
7 Firewall: Test-NetConnection ke port layanan langsung Diblokir; lewat Caddy (443) terbuka
8 VM 210 mencoba menjangkau LAN Diblokir; internet tetap bisa
9 Skrip audit di setiap VM Tidak ada temuan di luar matriks atau risiko tercatat
10 Salinan kedua (USB) dan arsip konfigurasi host Tersimpan di luar mesin
Masalah dan solusi
Gejala Penyebab Solusi
VM klon tidak bisa di-SSH Kunci host dihapus di templat dan
belum dibuat ulang
Konsol Proxmox: dpkg-reconfigure
openssh-server
Dua VM sama-sama muncul
sebagai satu perangkat
machine-id atau kunci SSH sama Ulangi 49.3 pada templat; pada klon: truncate
machine-id lalu reboot
VM baru tidak mendapat IP yang
diharapkan
MAC pada reservasi MikroTik salah qm config ID | grep net0; perbaiki lease
Job backup gagal: "guest agent not
running"
Agen tamu belum terpasang atau
opsi agen mati
apt install qemu-guest-agent; Options &gt; QEMU
Guest Agent: Yes; mulai ulang VM
PVE gagal menambah PBS: sidik
jari tidak cocok
Fingerprint salah salin atau PBS
dipasang ulang
Ambil ulang di Dashboard PBS (50.8); Edit
storage
Ruang PBS tidak turun setelah
prune
GC belum berjalan atau masa tunggu Jalankan GC di Options datastore; tunggu sekitar
sehari
Tidak bisa memulihkan backup
terenkripsi
Kunci enkripsi hilang Pulihkan dari salinan di Vaultwarden atau kertas;
tanpa kunci tidak bisa
Terkunci dari host setelah firewall Aturan Datacenter atau node
memblokir 8006 atau 22
Konsol fisik host: pve-firewall stop; perbaiki
aturan; pve-firewall start
Layanan tiba-tiba tidak terjangkau
dari Caddy
Aturan IN di VM tujuan belum
mengizinkan 192.168.88.20 pada
port itu
Cek /etc/pve/firewall/ID.fw dan kotak firewall di
kartu jaringan
Semua VM mati setelah host mati Start at boot belum diaktifkan qm set ID --onboot 1
Lembar pembaruan
Dokumen Perubahan Rujukan
Suplemen 1 sampai 4 (Revisi 2) Tiap bab pemasangan diawali Kotak Penempatan. Suplemen 1
Bab 26: Tailscale pindah dari pilihan B (VM Docker) ke C (LXC
CT103)
Bab 48.5
Suplemen 5 (Revisi 2) Situs statis dan WordPress di VM 209, n8n di VM 208, tunnel di
VM 210; Caddy meneruskan ke IP:port
Bab 48.4
Suplemen 6 (Revisi 2) Vaultwarden di VM 205 (lab-vault, port 443), AFFiNE di VM 206,
Nextcloud di VM 207
Bab 48.4
Edisi 2 VM Debian pertama menjadi docker-core atau sumber templat
200
Bab 49.1
Backup (Edisi 2 Bab 23) Backup tingkat VM oleh PBS menjadi lapisan utama; dump logis
tetap sebagai lapisan kedua
Bab 50
Daftar hal yang belum dipastikan
No Hal Cara memastikan
1 RAM awal tiap VM dan jumlah total Ukur dengan Beszel; sesuaikan qm set
--memory
2 Instruksi pemasangan Docker untuk Debian 13 tidak berubah dari 49.2 Bandingkan dengan halaman instalasi
Docker resmi
3 Lease DHCP statis di luar rentang pool MikroTik diterima Uji; bila ditolak pakai IP statis di Debian
4 Nomor rilis ISO PBS terbaru; HDD sebagai datastore lambat Cek halaman unduhan; ukur waktu
verifikasi
5 Nama peran DatastoreBackup dan batas haknya; sintaks pembuatan disk
lewat proxmox-backup-manager
Cek daftar Role dan bantuan perintah di
PBS
6 Masa tunggu GC dan nama menu notifikasi di Proxmox 9.2 dan PBS Baca dokumentasi pada versi terpasang
7 Sintaks +dc/admin, perilaku opsi dhcp: 1, dan port keluar tunnel 7844 Uji aturan; lihat dokumentasi firewall
Proxmox dan Cloudflare
8 Sumber IP perangkat Tailscale yang tiba di VM (CT103 sebagai subnet
router)
Uji SSH dari luar rumah; lihat IP sumber di
log sshd
9 Versi lynis di Debian lynis show version
Syarat lulus Fase 7
No Poin Ya / Tidak
1 Templat VM 200 ada; setiap VM layanan dibuat dari templat dengan kunci SSH dan IP sendiri
2 Setiap layanan berada di guest sesuai peta 48.3 (atau sesuai mode hemat yang dicatat)
3 PBS berjalan; backup harian ke store1 sukses; datastore di disk fisik terpisah
4 Satu uji pulih berhasil; kunci enkripsi tersimpan di dua tempat terpisah
5 Salinan kedua (USB) dan arsip konfigurasi host sudah ada di luar mesin
6 Firewall Proxmox aktif; uji blokir port langsung lulus; VM 210 tidak bisa menjangkau LAN
7 Skrip audit dijalankan di setiap VM; laporan terisi; risiko diterima tercatat
8 Notifikasi kegagalan backup tiba di Gotify
Berikutnya (Suplemen 8): SSO dan Immich. Rencana penempatan (belum keputusan, akan dibuka dengan
Kotak Penempatan): Immich di VM sendiri karena disk dan CPU besar; layanan SSO di VM sendiri karena
memegang identitas semua layanan lain. Backup dan firewall keduanya akan mengikuti pola Bab 50 dan 51.


<!-- SOURCE: docs/bab/suplemen/bagian-8-00-pengantar.md -->

# Bagian 8. Navidrome: Streaming Musik Pribadi (pengantar)

Bagian 8. Navidrome: Streaming Musik Pribadi
Asal: Suplemen 8. Bab 53.
Suplemen 8 menambah satu layanan: Navidrome, server musik pribadi yang berfungsi seperti Spotify untuk
koleksi musik milik Anda sendiri. Aplikasi di Windows, Android, dan iPhone memutarnya lewat Tailscale dari
mana saja.
Bab Isi Hasil akhir
53. Navidrome VM music, disk pustaka, server, Tailscale Serve, mengisi
musik, klien Windows/Android/iPhone, backup dan firewall
Pustaka musik dapat
diputar dari semua
perangkat
Prasyarat
• Templat VM 200 (Suplemen 7 Bab 49) dan tailnet dengan HTTPS Certificates aktif serta entri grants tcp:443
(Suplemen 6 Bab 44.3).
• Perintah server dijalankan sebagai root setelah su - (tanpa sudo), di guest yang ditunjuk Kotak Penempatan.
CATATAN
Navidrome bukan katalog. Ia memutar berkas musik yang Anda simpan sendiri (CD yang Anda rip, unduhan yang
Anda beli, rekaman sendiri, musik berlisensi bebas). Ia tidak menyediakan jutaan lagu, dan algoritma rekomendasi
seperti Spotify tidak ada. Hal yang belum bisa saya pastikan ditandai [BELUM PASTI].


<!-- SOURCE: docs/bab/suplemen/53-navidrome.md -->

# Bab 53. Navidrome: Streaming Musik Pribadi

> **Revisi 3.** Disk contoh (musik 200 GiB) harus disesuaikan dengan NVMe 500 GB. Lihat Bab 27.4: kecilkan ukuran awal, dan taruh backup di HDD 2 TB.

PENEMPATAN - BARU - VM sendiri (dan disk data terpisah)
Tempat: VM 211 music (192.168.88.31): qm clone 200 211 --name music --full 1, ditambah disk data kedua untuk
pustaka musik.
Alasan: Pustaka musik tumbuh besar dan berganti-ganti; Navidrome ringan tetapi datanya berbeda sifat dari layanan
lain, dan backup disk musiknya diperlakukan terpisah (backup=0).
Tidak boleh: Digabung dengan vault atau n8n.
Mode hemat: Boleh digabung ke VM 206 (apps); disk musik tetap dipasang sebagai disk kedua VM itu.
Navidrome adalah server streaming musik sumber terbuka. Menurut dokumentasinya ia memakai image Docker
resmi, menyimpan database dan cache di /data, dan membaca musik dari /music. Ia kompatibel dengan klien
Subsonic, sehingga banyak aplikasi di Windows, Android, dan iPhone bisa dipakai.
Keputusan Pilihan buku ini Alasan
Sertifikat HTTPS Jalur 1: Tailscale Serve (nama
lab-music.NAMA-TAILNET.ts.net)
Banyak aplikasi musik pihak ketiga memakai
penyimpanan sertifikat sendiri; sertifikat
tepercaya menghindari masalah CA lokal
seperti di Bab 44 [BELUM PASTI]
Lewat Caddy? Tidak Satu alamat saja yang berlaku; sama seperti
Vaultwarden
Akses di rumah Tailscale tetap aktif di HP Nama .ts.net hanya terjawab lewat Tailscale;
jalur langsung dalam LAN tetap dipakai
Tailscale bila bisa
Pustaka musik Disk data kedua, dipasang baca-saja untuk
Navidrome
Navidrome tidak bisa merusak berkas musik
Anda
Backup disk musik Dikecualikan dari PBS (backup=0); simpan
salinan asli di tempat lain
Pustaka besar dan biasanya bisa dibuat ulang
dari sumber aslinya
PERINGATAN
Bila koleksi Anda tidak punya salinan lain (misalnya rekaman sendiri yang unik), jangan mengecualikan disk musik
dari backup. Hapus opsi backup=0 di 53.1 atau salin pustaka ke disk USB secara berkala.

## 53.1 Membuat VM music dan disk pustaka

**TERMINAL HOST PROXMOX** | Shell node Proxmox (host), sebagai root

```
qm clone 200 211 --name music --full 1
```
> Penjelasan: Membuat VM 211 bernama music sebagai salinan penuh dari templat VM 200 (Suplemen 7 Bab 49).
```
qm set 211 --memory 1024 --cores 2 --onboot 1
```
> Penjelasan: RAM (MB), inti, dan nyalakan otomatis. Angka awal adalah perkiraan [BELUM PASTI]; transkoding
membutuhkan CPU lebih.
```
qm set 211 --scsi1 local-lvm:200,backup=0
```
> Penjelasan: Menambah disk kedua 200 GiB untuk pustaka musik dan menandainya tidak ikut backup. Ganti
local-lvm dengan nama penyimpanan Anda dan ukuran sesuai koleksi; sintaks disk [BELUM PASTI] pada versi
Proxmox Anda.
```
qm start 211
```
> Penjelasan: Menyalakan. Lakukan penyiapan awal di Suplemen 7 Bab 49.4 (nama host music, kunci SSH, alamat
192.168.88.31), lalu lanjut di bawah.
Langkah berikut dijalankan di VM music. Disk kedua perlu diformat sekali:

**TERMINAL VM MUSIC** | VM music (192.168.88.31), sebagai root (setelah su -)

```
lsblk -o NAME,SIZE,TYPE,MOUNTPOINT
```
> Penjelasan: Mengenali disk kedua (biasanya sdb, tanpa partisi dan tanpa mountpoint). Pastikan benar sebelum
memformat.
```
mkfs.ext4 -L music /dev/sdb
```
> Penjelasan: Memformat disk (menghapus isinya). Ganti sdb bila berbeda.
```
mkdir -p /srv/music
echo "LABEL=music /srv/music ext4 defaults,nofail 0 2" >> /etc/fstab
```
> Penjelasan: Membuat titik pasang dan mendaftarkannya ke fstab agar terpasang saat boot. nofail mencegah VM macet bila disk hilang.
```
mount -a && df -h /srv/music
```
> Penjelasan: Memasang dan memastikan ukurannya benar.
```
chown <USER>: /srv/music && id <USER>
```
> Penjelasan: Menjadikan pustaka milik pengguna biasa (ganti &lt;USER&gt;) agar bisa diunggah lewat scp. Catat
UID:GID dari perintah id untuk 53.2.

## 53.2 Server Navidrome

**TERMINAL VM MUSIC** | VM music, sebagai root

```
mkdir -p /opt/stacks/music/data && cd /opt/stacks/music
```
> Penjelasan: Folder aplikasi dan folder data (database, cache).
```
chown 1000:1000 data
```
> Penjelasan: Data dimiliki UID:GID yang akan menjalankan Navidrome. Dokumentasi menyarankan memakai
UID:GID pemilik pustaka; ganti 1000:1000 bila perintah id di 53.1 menunjukkan angka lain.
```
echo "ND_VERSION=latest" > .env
```
> Penjelasan: Nomor versi image. Dokumentasi resmi memakai latest; setelah berjalan, ganti dengan nomor rilis
tertentu agar pembaruan terkendali.
```
nano compose.yaml
```
> Penjelasan: Isi seperti kotak di bawah.

**/opt/stacks/music/compose.yaml** | Isi berkas

```
services:
  navidrome:
    image: deluan/navidrome:${ND_VERSION}
    container_name: navidrome
    user: "1000:1000"
    restart: unless-stopped
    ports:
      - "127.0.0.1:4533:4533"
    environment:
      ND_SCANSCHEDULE: 1h
      ND_LOGLEVEL: info
      ND_BASEURL: ""
    volumes:
      - ./data:/data
      - /srv/music:/music:ro
```

Pengaturan Fungsi
user "1000:1000" Menjalankan Navidrome sebagai pengguna biasa, bukan root
127.0.0.1:4533:4533 Port hanya di dalam VM; Tailscale Serve meneruskan ke sini. Tidak terbuka di LAN
ND_SCANSCHEDULE: 1h Memindai pustaka untuk lagu baru tiap jam
/music:ro Pustaka dipasang baca-saja

**TERMINAL VM MUSIC** | VM music, sebagai root di /opt/stacks/music

```
docker compose up -d && docker compose logs --tail=20
```
> Penjelasan: Menyalakan. Cari baris yang menyebut Navidrome mendengarkan di port 4533 dan tidak ada galat
izin.

## 53.3 Tailscale Serve di VM music

**TERMINAL VM MUSIC** | VM music, sebagai root

```
curl -fsSL https://tailscale.com/install.sh | sh
```
> Penjelasan: Memasang Tailscale (sama seperti Suplemen 6 Bab 44.3).
```
tailscale up --hostname=lab-music --accept-dns=false
```
> Penjelasan: Mendaftarkan node bernama lab-music. Buka tautan login di browser laptop.
```
tailscale serve --bg --https=443 4533
```
> Penjelasan: HTTPS port 443 di nama lab-music diteruskan ke 127.0.0.1:4533. Sertifikat tepercaya diminta pada
kali pertama (beberapa detik).
```
tailscale serve status
```
> Penjelasan: Memeriksa rute. Jangan menjalankan tailscale funnel.
1. Di konsol admin Tailscale (Machines) nonaktifkan key expiry untuk lab-music dan catat nama panjangnya.
Entri grants tcp:443 dari Bab 44.3 sudah mencukupi.

## 53.4 Akun pertama dan mengisi musik

1. Dari laptop (Tailscale aktif) buka https://lab-music.NAMA-TAILNET.ts.net. Halaman pertama meminta
pembuatan akun admin (nama pengguna dan kata sandi kuat; simpan di Vaultwarden).
2. Buat akun harian terpisah di menu pengguna Navidrome dan pakai akun itu di aplikasi; admin hanya untuk
pengelolaan. Letak menu persis [BELUM PASTI].
Menata berkas. Susun dengan pola Artis/Album/01 - Judul.flac dan pastikan tag (artis, album, nomor trek,
sampul) benar. Di Windows, MusicBrainz Picard membantu merapikan tag. Navidrome membaca tag, bukan
nama berkas, jadi tag yang rapi menentukan tampilan pustaka.

**POWERSHELL WINDOWS** | PowerShell (laptop), di folder musik Anda

```
scp -r .\* <USER>@192.168.88.31:/srv/music/
```
> Penjelasan: Menyalin semua isi folder ke pustaka di VM music. Ganti &lt;USER&gt;. Untuk koleksi besar, proses ini
lama; jalankan sekali dan biarkan selesai.
TIPS
Navidrome memindai tiap jam (ND_SCANSCHEDULE). Untuk memaksa pindai, mulai ulang container: docker
compose restart navidrome di VM music (Navidrome memindai saat mulai [BELUM PASTI]); atau cari tombol pindai
di antarmuka web.

## 53.5 Sisi klien

Windows
1. Tanpa instalasi: buka https://lab-music.NAMA-TAILNET.ts.net di browser; pemutar web sudah ada.
Opsional: Chrome/Edge Menu &gt; Instal sebagai aplikasi.
2. Aplikasi desktop: Feishin (klien lintas-platform yang tercantum di halaman Apps & Players milik
navidrome.org). Tambahkan server: tipe Navidrome, URL yang sama, nama pengguna dan kata sandi akun
harian.
Android
1. Pastikan Tailscale aktif. Pilih satu klien: Symfonium (berbayar), Tempo, Ultrasonic, atau Substreamer,
semuanya terdaftar sebagai klien Subsonic di navidrome.org. Pasang dari Play Store atau F-Droid.
2. Tambahkan server: tipe Subsonic/Navidrome, alamat https://lab-music.NAMA-TAILNET.ts.net, nama
pengguna, dan kata sandi akun harian.
3. Agar pemutaran tidak berhenti saat layar terkunci, matikan penghematan baterai untuk aplikasinya:
Pengaturan &gt; Aplikasi &gt; nama aplikasi &gt; Baterai &gt; Tanpa batasan. Laporan pengguna menyebut
beberapa klien berhenti setelah satu lagu bila ini tidak diatur; perilaku tiap klien [BELUM PASTI].
iPhone
1. Pastikan Tailscale aktif. Pilih klien: Amperfy, Substreamer, Narjo, atau Navic (ada di navidrome.org).
Pasang dari App Store.
2. Tambahkan server dengan URL, nama pengguna, dan kata sandi yang sama.
3. Izinkan pemutaran latar belakang dan unduhan offline bila ditawarkan; ketersediaan fitur berbeda antar
aplikasi [BELUM PASTI].
CATATAN
Klien yang menolak sertifikat bukan masalah di sini, karena alamat .ts.net memakai sertifikat tepercaya. Bila aplikasi
gagal tersambung, periksa Tailscale aktif dan alamat tanpa salah ketik.

## 53.6 Backup, firewall, pemantauan

1. Proxmox Backup Server: tambahkan 211 ke job backup (Bab 50.10). Disk pustaka tidak ikut karena
backup=0; sistem dan database Navidrome (playlist, akun) ikut.
2. Firewall: buat /etc/pve/firewall/211.fw seperti kotak di bawah dan aktifkan kotak Firewall pada kartu jaringan
(Bab 51).
3. Pasang agen Beszel di VM music dan tambah monitor Uptime Kuma sesuai Suplemen 3.

**/etc/pve/firewall/211.fw** | Isi berkas

```
[OPTIONS]
enable: 1
policy_in: DROP
policy_out: ACCEPT
dhcp: 1
[RULES]
IN ACCEPT -source +dc/admin -p tcp -dport 22
```

IN ACCEPT -source 192.168.88.20 -p tcp -dport PORT-AGEN-BESZEL
IN ACCEPT -p icmp
Tidak ada port layanan yang dibuka di LAN: Navidrome hanya terjangkau lewat Tailscale Serve. Salinan pustaka
asli tetap Anda simpan sendiri di disk lain.

## 53.7 Pembaruan

**TERMINAL VM MUSIC** | VM music, sebagai root di /opt/stacks/music

```
docker compose pull && docker compose up -d
```
> Penjelasan: Mengunduh image baru dan membuat ulang container. Baca catatan rilis Navidrome lebih dulu bila
memakai nomor versi tertentu; backup VM sudah dilakukan PBS tiap malam.


<!-- SOURCE: docs/bab/suplemen/bagian-8-99-penutup.md -->

# Bagian 8. Navidrome: Streaming Musik Pribadi: Uji, Masalah Umum, Lembar Pembaruan, Syarat Lulus Fase 8

Uji, Masalah Umum, dan Lembar Pembaruan
Uji menyeluruh
No Uji Hasil yang diharapkan
1 df -h /srv/music di VM music Ukuran disk kedua terlihat; terpasang setelah reboot
2 tailscale serve status Rute 443 menuju 4533
3 Laptop: https://lab-music.NAMA-TAILNET.ts.net Halaman Navidrome dengan gembok tanpa peringatan
4 Unggah satu album, tunggu pemindaian Album muncul di pustaka dan bisa diputar
5 Android dan iPhone: tambah server, putar lagu Suara keluar; layar terkunci tidak menghentikan
pemutaran
6 Tailscale mati di HP Aplikasi gagal tersambung (normal); pulih saat
Tailscale aktif
7 Dari laptop: Test-NetConnection 192.168.88.31 -Port 4533 False (tidak terbuka di LAN)
8 Job backup PBS untuk VM 211 TASK OK; ukuran backup kecil (tanpa disk musik)
Masalah dan solusi
Gejala Penyebab Solusi
Container berhenti dengan galat
izin
Folder data bukan milik UID:GID
yang dipakai
chown -R 1000:1000 data; sesuaikan dengan
user di compose
Pustaka kosong Berkas milik root atau belum dipindai Periksa izin baca di /srv/music; mulai ulang
container
Lagu tampil dengan judul berkas
atau tanpa sampul
Tag berkas tidak lengkap Rapikan tag dengan Picard lalu pindai ulang
Aplikasi tidak bisa tersambung Tailscale mati atau alamat salah Aktifkan Tailscale; salin alamat persis dari konsol
admin
Pemutaran berhenti saat layar
terkunci
Penghematan baterai membatasi
aplikasi
Atur baterai aplikasi ke tanpa batasan (Android);
izinkan latar belakang (iPhone)
Sertifikat belum tersedia saat serve HTTPS Certificates belum aktif Aktifkan di halaman DNS konsol admin
(Suplemen 6 Bab 44.3)
Lembar pembaruan
Dokumen Perubahan Rujukan
Suplemen 7, Bab 48 Peta guest bertambah VM 211 music; tabel RAM diperbarui
(jumlah sebelumnya salah hitung, lihat tabel baru)
Bab 48.3, 48.6
Suplemen 7, Bab 50.10 Job backup mencakup VM 211 (disk pustaka tidak ikut) Bab 53.6
Suplemen 7, Bab 51 Aturan firewall untuk VM 211 Bab 53.6
Suplemen 7, Bab 52 Laporan audit bertambah baris VM 211 Bab 52.7
Daftar hal yang belum dipastikan
No Hal Cara memastikan
1 Aplikasi musik pihak ketiga dan CA lokal (mengapa dipilih Jalur 1) Tidak perlu diuji; Jalur 1 sudah
menghindarinya
2 Sintaks qm set --scsi1 STORAGE:UKURAN,backup=0 dan nama
penyimpanan
qm config 211; lihat Datacenter &gt; Storage
3 Letak menu pengguna dan tombol pindai di antarmuka Navidrome;
pemindaian saat container dimulai
Lihat antarmuka dan dokumentasi
Navidrome
4 Perilaku tiap klien (pemutaran latar belakang, unduhan offline, harga
Symfonium)
Uji di perangkat Anda
5 Nomor versi Navidrome untuk dipasang tetap Halaman rilis Navidrome di GitHub
6 Kebutuhan RAM dan CPU saat transkoding Ukur dengan Beszel
Syarat lulus
No Poin Ya / Tidak
1 VM 211 berjalan dengan disk pustaka terpasang otomatis
2 Navidrome hanya terbuka lewat Tailscale Serve (tidak di LAN)
3 Album uji diputar di Windows, Android, dan iPhone
4 Backup VM 211 berhasil; keputusan backup disk musik sudah sadar (ikut atau tidak)
5 Firewall VM 211 aktif; entri audit terisi
Berikutnya: Suplemen 9 (Bab 54-56): SSO dan Immich (pengganti Google Photos), masing-masing dengan
Kotak Penempatan, backup, dan firewall mengikuti pola Suplemen 7.


<!-- SOURCE: docs/bab/suplemen/bagian-9-00-pengantar.md -->

# Bagian 9. SSO dengan Pocket ID dan Immich (pengantar)

Bagian 9. SSO dengan Pocket ID dan Immich
Asal: Suplemen 9. Bab 54-56.
Suplemen 9 menambah dua layanan dan satu panduan pengaturan. Pocket ID adalah satu pintu masuk (SSO)
berbasis passkey, tanpa kata sandi. Immich adalah pengganti Google Photos yang menyimpan foto dan video di
server Anda sendiri. RAM yang dilaporkan saat ini 24 GB (16+8), tetapi belum diverifikasi di BIOS/MemTest86; bab terakhir menyusun profil pemakaian agar
tidak semua VM menyala bersamaan.
Bab Isi Hasil akhir
54. SSO dengan Pocket ID VM sso, Tailscale Serve, server, passkey di
Windows/Android/iPhone, klien OIDC, backup dan firewall
Satu akun passkey untuk
layanan yang
mendukung OIDC
55. Immich VM immich dan disk foto, server, SSO, klien
Windows/Android/iPhone, backup dan firewall
Foto HP tercadangkan
otomatis ke server sendiri
56. Mesin 16 GB Anggaran RAM, lima profil, skrip pergantian profil, jadwal
PBS, rencana saat RAM naik
Semua layanan bisa
dipakai bergantian tanpa
kehabisan RAM
Prasyarat
• Templat VM 200 (Suplemen 7 Bab 49) dan tailnet dengan HTTPS Certificates aktif serta entri grants tcp:443
(Suplemen 6 Bab 44.3).
• Vaultwarden (Suplemen 6) untuk menyimpan kunci dan kata sandi yang dibuat di sini.
• Perintah server dijalankan sebagai root setelah su - (tanpa sudo), di guest yang ditunjuk Kotak Penempatan.
PERINGATAN
Urutan penting. Kerjakan Bab 54 sebelum Bab 55, dan tetapkan nama tailnet Anda dulu. Passkey terikat ke nama
alamat Pocket ID; bila nama berubah setelah passkey terdaftar, semua passkey harus didaftar ulang. Hal yang belum
bisa saya pastikan ditandai [BELUM PASTI].


<!-- SOURCE: docs/bab/suplemen/54-sso-pocket-id.md -->

# Bab 54. SSO dengan Pocket ID

PENEMPATAN - BARU - VM sendiri
Tempat: VM 213 sso (192.168.88.32): qm clone 200 213 --name sso --full 1. Node tailnet lab-sso ada di
dalamnya.
Alasan: Penyedia SSO memegang kunci masuk ke layanan lain. Bila digabung dengan aplikasi, kebobolan aplikasi itu
membuka semua pintu; sebaliknya, VM ini kecil, jarang berubah, dan hanya menjalankan Pocket ID.
Tidak boleh: Digabung dengan layanan lain, termasuk pada mode hemat.
SSO (single sign-on) berarti Anda masuk sekali ke satu penyedia identitas, lalu aplikasi lain meminta penyedia itu
memastikan siapa Anda memakai standar OpenID Connect (OIDC). Aplikasi tidak menyimpan kata sandi Anda.
Pocket ID adalah penyedia OIDC yang hanya menerima passkey (sidik jari, wajah, PIN perangkat, atau kunci
keamanan), sehingga tidak ada kata sandi yang bisa bocor dari servernya.
Keputusan Pilihan buku ini Alasan
Penyedia SSO Pocket ID (bukan Authentik atau Authelia) Ringan (satu container, database SQLite) dan cocok
dengan gaya lab; dokumentasinya menjelaskan
bahwa ia hanya memakai passkey
HTTPS Tailscale Serve
(lab-sso.NAMA-TAILNET.ts.net)
Passkey (WebAuthn) mewajibkan HTTPS. Sertifikat
.ts.net tepercaya di semua perangkat, jadi tidak ada
masalah CA lokal seperti di Suplemen 4 Bab 37 dan
Immich (server) bisa memverifikasinya
Lewat Caddy? Tidak Satu alamat saja yang berlaku, sama seperti
Vaultwarden dan Navidrome; passkey terikat ke satu
nama
Akun darurat Setiap aplikasi tetap punya akun lokal (kata
sandi) milik admin
Bila Pocket ID mati, Anda tidak terkunci dari Immich
dan lainnya
Akses di rumah Tailscale aktif di HP dan laptop Nama .ts.net hanya terjawab lewat Tailscale
PERINGATAN
Jangan matikan login kata sandi lokal di aplikasi (misalnya Immich) pada tahap awal. SSO baru boleh menjadi
satu-satunya jalan setelah Anda menguji bahwa passkey di sedikitnya dua perangkat berfungsi dan Anda memegang
cara pemulihan (54.5).

## 54.1 Membuat VM sso

**TERMINAL HOST PROXMOX** | Shell node Proxmox (host), sebagai root

```
qm clone 200 213 --name sso --full 1
```
> Penjelasan: Membuat VM 213 bernama sso sebagai salinan penuh dari templat VM 200 (Suplemen 7 Bab 49).
```
qm set 213 --memory 1024 --cores 1 --onboot 1
```
> Penjelasan: RAM (MB), inti, dan nyalakan otomatis. Angka awal adalah perkiraan [BELUM PASTI]; ukur dengan
Beszel.
```
qm start 213
```
> Penjelasan: Menyalakan. Lakukan penyiapan awal di Suplemen 7 Bab 49.4 (nama host sso, kunci SSH, alamat
192.168.88.32), lalu lanjut di bawah.

## 54.2 Tailscale Serve di VM sso

Tailscale dipasang lebih dulu karena nama panjang alamat Pocket ID (lab-sso.NAMA-TAILNET.ts.net)
dibutuhkan untuk berkas konfigurasi di 54.3.

**TERMINAL VM SSO** | VM sso (192.168.88.32), sebagai root (setelah su -)

```
curl -fsSL https://tailscale.com/install.sh | sh
```
> Penjelasan: Memasang Tailscale (sama seperti Suplemen 6 Bab 44.3).
```
tailscale up --hostname=lab-sso --accept-dns=false
```
> Penjelasan: Mendaftarkan node bernama lab-sso. Buka tautan login di browser laptop.
```
tailscale ip -4
```
> Penjelasan: Menampilkan alamat Tailscale VM ini (100.x.y.z). Catat; dipakai Immich di Bab 55.3.
1. Di konsol admin Tailscale (Machines) nonaktifkan key expiry untuk lab-sso dan catat nama panjangnya
(lab-sso.NAMA-TAILNET.ts.net). Entri grants tcp:443 dari Suplemen 6 Bab 44.3 sudah mencukupi.
Perintah tailscale serve dijalankan di 54.4, setelah Pocket ID berjalan.

## 54.3 Server Pocket ID

**TERMINAL VM SSO** | VM sso, sebagai root

```
mkdir -p /opt/stacks/sso/data && cd /opt/stacks/sso
```
> Penjelasan: Folder aplikasi dan folder data (database dan kunci).
```
chown 1000:1000 data
```
> Penjelasan: Data dimiliki UID:GID yang menjalankan Pocket ID (PUID dan PGID di .env). Dokumentasi menyebut
nilai bawaan 1000.
```
printf 'APP_URL=https://lab-sso.NAMA-TAILNET.ts.net\nTRUST_PROXY=true\nPUID=1000\nPGID=1000\n' > .env
```
> Penjelasan: Menulis .env. Ganti NAMA-TAILNET dengan nama tailnet Anda. APP_URL harus persis alamat yang dipakai browser.
```
echo "ENCRYPTION_KEY=$(openssl rand -base64 32)" >> .env
```
> Penjelasan: Menambahkan kunci enkripsi acak. Sejak versi 2 kunci ini wajib; tanpanya Pocket ID tidak mau mulai.
Bila openssl tidak ada: apt install -y openssl.
```
chmod 600 .env && cat .env
```
> Penjelasan: Membatasi izin. Salin seluruh isi .env ke Vaultwarden: kehilangan ENCRYPTION_KEY membuat
data terenkripsi (termasuk kunci privat) tidak terbaca.
```
nano compose.yaml
```
> Penjelasan: Isi seperti kotak di bawah.

**/opt/stacks/sso/compose.yaml** | Isi berkas

```
services:
  pocket-id:
    image: ghcr.io/pocket-id/pocket-id:v2
    container_name: pocket-id
    restart: unless-stopped
    env_file: .env
    ports:
      - "127.0.0.1:1411:1411"
    volumes:
      - ./data:/app/data
    healthcheck:
      test: ["CMD", "/app/pocket-id", "healthcheck"]
      interval: 1m30s
      timeout: 5s
      retries: 2
      start_period: 10s
```

Pengaturan Fungsi
image ...:v2 Mengikuti rilis mayor 2. Setelah stabil, ganti dengan nomor rilis tertentu agar
pembaruan terkendali
TRUST_PROXY=true Pocket ID berada di belakang proxy (Tailscale Serve), jadi header penerusan
dipercaya
127.0.0.1:1411:1411 Port 1411 hanya di dalam VM; Tailscale Serve meneruskan ke sini. Tidak terbuka di
LAN
./data:/app/data Database SQLite dan kunci ada di folder data (ikut backup VM)

## 54.4 Menyalakan dan mengaktifkan HTTPS

**TERMINAL VM SSO** | VM sso, sebagai root di /opt/stacks/sso

```
docker compose up -d && docker compose logs --tail=20
```
> Penjelasan: Menyalakan. Cari tanda Pocket ID mendengarkan di port 1411 dan tidak ada galat tentang
ENCRYPTION_KEY atau izin.
```
tailscale serve --bg --https=443 1411
```
> Penjelasan: HTTPS port 443 di nama lab-sso diteruskan ke 127.0.0.1:1411. Sertifikat tepercaya diminta pada kali
pertama (beberapa detik).
```
tailscale serve status
```
> Penjelasan: Memeriksa rute. Jangan menjalankan tailscale funnel.

## 54.5 Akun admin pertama dan passkey

1. Dari laptop (Tailscale aktif) buka https://lab-sso.NAMA-TAILNET.ts.net/setup. Halaman penyiapan awal
meminta nama pengguna, email, dan nama tampilan admin. Letak halaman persis pada versi Anda [BELUM
PASTI]; bila /setup tidak ada, ikuti petunjuk di layar atau dokumentasi Pocket ID.
2. Daftarkan passkey pertama di laptop (lihat sisi klien di bawah). Setelah itu Anda bisa masuk tanpa kata
sandi.
3. Masuk ke Pocket ID dari HP dan daftarkan passkey kedua di sana. Dua perangkat mencegah terkunci bila
satu hilang.
PERINGATAN
Pemulihan bila semua passkey hilang. Pocket ID memakai token akses satu kali yang dibuat dari server. Masuk
SSH ke VM sso (su -), lalu di /opt/stacks/sso jalankan docker compose exec pocket-id /app/pocket-id
one-time-access-token NAMA-PENGGUNA dan buka tautan yang dikeluarkan di browser untuk mendaftarkan
passkey baru. Perintah ini ada di dokumentasi pihak ketiga yang saya baca [BELUM PASTI]; periksa dokumentasi
Pocket ID untuk versi Anda.
Sisi klien: mendaftarkan passkey
Windows
1. Buka alamat Pocket ID di Chrome atau Edge dengan Tailscale aktif. Saat diminta menambah passkey, pilih
Windows Hello (PIN, sidik jari, atau wajah) atau kunci keamanan USB.
2. Bila Windows Hello belum aktif: Pengaturan &gt; Akun &gt; Opsi masuk, atur PIN lebih dulu. Letak menu bisa
berbeda antar versi Windows [BELUM PASTI].
Android
1. Pastikan Tailscale aktif dan layar terkunci dengan sidik jari atau PIN. Buka alamat Pocket ID di Chrome.
2. Saat diminta menambah passkey, pilih Google Password Manager dan konfirmasi dengan sidik jari atau
PIN. Passkey tersimpan di akun Google Anda dan ikut ke HP baru.
3. Alternatif lebih aman dari akun Google: simpan passkey di kunci keamanan fisik. Pilihan tersedia di dialog
yang sama [BELUM PASTI].
iPhone
1. Pastikan Tailscale aktif dan iCloud Keychain (Kata Sandi) menyala: Pengaturan &gt; nama Anda &gt; iCloud &gt;
Kata Sandi. Letak menu bisa berbeda antar versi iOS [BELUM PASTI].
2. Buka alamat Pocket ID di Safari, daftarkan passkey, dan konfirmasi dengan Face ID atau Touch ID.
TIPS
Simpan alamat https://lab-sso.NAMA-TAILNET.ts.net dan salinan .env di Vaultwarden. Catat juga bahwa pemulihan
butuh akses SSH ke VM 213.

## 54.6 Pengguna dan klien OIDC

1. Di Pocket ID buat akun harian terpisah dari admin (menu pengguna; letak persis [BELUM PASTI]), isi nama
pengguna dan email. Banyak aplikasi, termasuk Immich, membutuhkan klaim email.
2. Untuk setiap aplikasi, buat klien OIDC: menu OIDC Clients di bagian admin, tambahkan nama dan callback
URL milik aplikasi itu. Setelah disimpan Anda mendapat Client ID dan Client Secret.
3. Alamat penemuan (discovery) penyedia adalah
https://lab-sso.NAMA-TAILNET.ts.net/.well-known/openid-configuration (alamat standar OIDC). Aplikasi
memerlukan alamat penyedia (issuer) persis seperti APP_URL.
Aplikasi Status di buku ini Catatan
Immich (VM 214) Dibahas di Bab 55.7 Callback web dan HP; server Immich harus bisa
menjangkau lab-sso
Beszel, Nextcloud, AFFiNE,
Vaultwarden, Portainer
Tidak dibahas Dukungan OIDC dan callback masing-masing harus
dibaca di dokumentasi aplikasinya [BELUM PASTI].
Pola sama: klien baru di Pocket ID, lalu alamat issuer
di aplikasi
CATATAN
Server ke server. Saat Anda masuk lewat SSO, server aplikasi (bukan hanya browser) menghubungi Pocket ID.
Karena VM memakai --accept-dns=false, nama .ts.net tidak terjawab di dalam VM aplikasi. Bab 55.3
menyelesaikannya dengan satu baris extra_hosts yang menunjuk ke alamat Tailscale VM sso.

## 54.7 Backup, firewall, pemantauan

1. Proxmox Backup Server: tambahkan 213 ke job backup (Suplemen 7 Bab 50.10). Folder data ikut dalam
backup VM.
2. Firewall: buat /etc/pve/firewall/213.fw seperti kotak di bawah dan aktifkan kotak Firewall pada kartu jaringan
(Suplemen 7 Bab 51).
3. Pasang agen Beszel di VM sso dan tambah monitor Uptime Kuma (alamat Tailscale, bukan LAN) sesuai
Suplemen 3.

**/etc/pve/firewall/213.fw** | Isi berkas

```
[OPTIONS]
enable: 1
policy_in: DROP
policy_out: ACCEPT
dhcp: 1
[RULES]
IN ACCEPT -source +dc/admin -p tcp -dport 22
```

IN ACCEPT -source 192.168.88.20 -p tcp -dport PORT-AGEN-BESZEL
IN ACCEPT -p icmp
Tidak ada port layanan yang dibuka di LAN: Pocket ID hanya terjangkau lewat Tailscale Serve. Lalu lintas
Tailscale antar-VM memakai UDP keluar yang diizinkan oleh policy_out; bila jalur langsung antar-VM terblokir,
Tailscale memakai relai DERP yang lebih lambat tetapi tetap bekerja [BELUM PASTI].

## 54.8 Pembaruan

**TERMINAL VM SSO** | VM sso, sebagai root di /opt/stacks/sso

```
docker compose pull && docker compose up -d
```
> Penjelasan: Mengunduh image baru dan membuat ulang container. Baca catatan rilis Pocket ID lebih dulu; backup
VM dilakukan PBS tiap malam. Jangan mengubah APP_URL atau ENCRYPTION_KEY saat memperbarui.


<!-- SOURCE: docs/bab/suplemen/55-immich.md -->

# Bab 55. Immich: Foto dan Video Pribadi

> **Revisi 3.** Disk contoh (foto 300 GiB) harus disesuaikan dengan NVMe 500 GB. Lihat Bab 27.4: kecilkan ukuran awal, dan taruh backup di HDD 2 TB.

PENEMPATAN - BARU - VM sendiri (dan disk foto terpisah)
Tempat: VM 214 immich (192.168.88.33): qm clone 200 214 --name immich --full 1, ditambah disk data kedua
untuk foto. Node tailnet lab-immich.
Alasan: Dokumentasi Immich menyarankan VM penuh (Docker di LXC tidak direkomendasikan) dan RAM sekitar 6
GB; database vektor, machine learning, dan foto pribadi yang besar membuatnya layak sendirian.
Tidak boleh: Digabung dengan layanan lain; juga tidak ke VM 206 (apps) pada mode hemat.
RAM 16 GB: Tidak menyala bersamaan dengan semua VM lain; lihat profil di Bab 56.
Immich adalah aplikasi sumber terbuka yang menggantikan Google Photos: foto dan video dari HP dicadangkan
otomatis ke server Anda, dapat dicari, dan dikelompokkan berdasarkan wajah dan tempat. Menurut
dokumentasinya ia berjalan dengan Docker Compose, memerlukan VM penuh (Docker di dalam LXC tidak
direkomendasikan), dan melayani web serta aplikasi HP di port 2283.
Keputusan Pilihan buku ini Alasan
Tempat VM 214 immich, bukan LXC dan bukan
digabung
Rekomendasi dokumentasi; database vektor dan
machine learning
RAM 6144 MB (4096 MB bila machine learning
dimatikan)
Dokumentasi: minimal 4 GB, disarankan 6 GB;
dengan 4 GB fitur machine learning sebaiknya
dimatikan
Disk Disk sistem (database di /opt/stacks) dan disk
foto kedua
Database butuh disk lokal yang stabil; foto tumbuh
besar dan perlu ukuran sendiri
HTTPS Tailscale Serve
(lab-immich.NAMA-TAILNET.ts.net)
Aplikasi HP memakai sertifikat tepercaya; tidak ada
masalah CA lokal seperti Suplemen 4 Bab 37 dan
Navidrome (Bab 53)
Backup disk foto Ikut backup PBS (tidak memakai backup=0) Foto tidak tergantikan. Backup bawaan Immich
mencakup database, bukan berkas foto [BELUM
PASTI]
Login Akun lokal admin tetap ada; SSO Pocket ID
untuk harian
Pemulihan bila Pocket ID mati
PERINGATAN
Koreksi atas rencana awal. Rencana yang saya ajukan sebelumnya menandai disk foto backup=0 dan menyebut
backup Immich sebagai pengamannya. Itu keliru: dokumentasi menyebut backup bawaan sebagai backup database.
Karena foto adalah data yang tidak bisa dibuat ulang, buku ini memasukkan disk foto ke backup PBS. Pastikan
datastore PBS cukup besar (55.1) dan simpan satu salinan lagi di disk lain di luar mesin.

## 55.1 Membuat VM immich dan disk foto

**TERMINAL HOST PROXMOX** | Shell node Proxmox (host), sebagai root

```
qm clone 200 214 --name immich --full 1
```
> Penjelasan: Membuat VM 214 bernama immich sebagai salinan penuh dari templat VM 200 (Suplemen 7 Bab
49).
```
qm set 214 --memory 6144 --cores 2 --onboot 0
```
> Penjelasan: RAM (MB), inti, dan tidak menyala otomatis (diatur lewat profil di Bab 56). Jumlah inti [BELUM
PASTI]; machine learning memanfaatkan inti tambahan.
```
qm set 214 --scsi1 local-lvm:300
```
> Penjelasan: Menambah disk kedua 300 GiB untuk foto. Ganti local-lvm dengan nama penyimpanan Anda dan
ukuran sesuai koleksi. Disk ikut backup (tanpa backup=0). Sintaks disk [BELUM PASTI]; periksa dengan qm
config 214.
```
qm start 214
```
> Penjelasan: Menyalakan. Lakukan penyiapan awal di Suplemen 7 Bab 49.4 (nama host immich, kunci SSH,
alamat 192.168.88.33), lalu lanjut di bawah.
Langkah berikut dijalankan di VM immich. Disk kedua diformat sekali:

**TERMINAL VM IMMICH** | VM immich (192.168.88.33), sebagai root (setelah su -)

```
lsblk -o NAME,SIZE,TYPE,MOUNTPOINT
```
> Penjelasan: Mengenali disk kedua (biasanya sdb, tanpa partisi dan tanpa mountpoint). Pastikan benar sebelum
memformat.
```
mkfs.ext4 -L foto /dev/sdb
```
> Penjelasan: Memformat disk (menghapus isinya). Ganti sdb bila berbeda.
```
mkdir -p /srv/foto && echo "LABEL=foto /srv/foto ext4 defaults,nofail 0 2" >> /etc/fstab
```
> Penjelasan: Membuat titik pasang dan mendaftarkannya ke fstab agar terpasang saat boot. nofail mencegah VM
macet bila disk hilang.
```
mount -a && mkdir -p /srv/foto/library && df -h /srv/foto
```
> Penjelasan: Memasang, membuat folder library, dan memastikan ukurannya benar.

## 55.2 Tailscale di VM immich

**TERMINAL VM IMMICH** | VM immich, sebagai root

```
curl -fsSL https://tailscale.com/install.sh | sh
```
> Penjelasan: Memasang Tailscale.
```
tailscale up --hostname=lab-immich --accept-dns=false
```
> Penjelasan: Mendaftarkan node bernama lab-immich. Buka tautan login di browser laptop.
1. Di konsol admin Tailscale (Machines) nonaktifkan key expiry untuk lab-immich dan catat nama panjangnya
(lab-immich.NAMA-TAILNET.ts.net). Entri grants tcp:443 sudah mencukupi.

## 55.3 Berkas Compose resmi dan pengaturannya

Dokumentasi Immich meminta Anda memakai docker-compose.yml dari rilis terbaru, karena isinya (versi
database, image Valkey) berubah antar rilis. Karena itu buku ini mengunduh berkas resmi, bukan menyalinnya,
dan hanya menambah dua pengaturan.

**TERMINAL VM IMMICH** | VM immich, sebagai root

```
mkdir -p /opt/stacks/immich && cd /opt/stacks/immich
```
> Penjelasan: Folder aplikasi (database ada di sini, di disk sistem).
```
wget -O docker-compose.yml https://github.com/immich-app/immich/releases/latest/download/docker-compose.yml
```
> Penjelasan: Mengunduh berkas compose rilis terbaru dari halaman resmi.
```
wget -O .env https://github.com/immich-app/immich/releases/latest/download/example.env
```
> Penjelasan: Mengunduh contoh .env dari rilis yang sama.
```
nano .env
```
> Penjelasan: Ubah nilainya seperti kotak di bawah.

**/opt/stacks/immich/.env** | Isi berkas

```
UPLOAD_LOCATION=/srv/foto/library
DB_DATA_LOCATION=./postgres
IMMICH_VERSION=v2
DB_PASSWORD=GANTI_DENGAN_ACAK
DB_USERNAME=postgres
DB_DATABASE_NAME=immich
```

Pengaturan Fungsi
UPLOAD_LOCATION Folder foto di disk kedua (/srv/foto/library)
DB_DATA_LOCATION Database di disk sistem VM (folder postgres di samping compose); dokumentasi
menekankan koneksi database harus cepat dan stabil
IMMICH_VERSION=v2 Mengikuti rilis mayor 2. Berkas contoh menyebut bisa dipin ke nomor tertentu (misalnya
v2.1.0) agar pembaruan terkendali
DB_PASSWORD Kata sandi acak. Pakai huruf dan angka saja untuk menghindari masalah karakter
khusus [BELUM PASTI]; buat dengan openssl rand -hex 16 dan simpan di Vaultwarden

**TERMINAL VM IMMICH** | VM immich, sebagai root di /opt/stacks/immich

```
grep -n 2283 docker-compose.yml
```
> Penjelasan: Mencari baris yang menerbitkan port 2283. Bentuknya biasanya 2283:2283 (dalam tanda kutip) pada
layanan immich-server.
```
sed -i 's/"2283:2283"/"127.0.0.1:2283:2283"/' docker-compose.yml
grep -n 2283 docker-compose.yml
```
> Penjelasan: Mengikat port ke 127.0.0.1 agar tidak terbuka di LAN (Tailscale Serve meneruskan ke sini). Bila hasil grep tidak berubah, bentuk barisnya berbeda; ubah dengan nano. Ulangi setelah mengunduh compose baru saat pembaruan.
```
nano docker-compose.override.yml
```
> Penjelasan: Berkas tambahan (tidak menimpa berkas resmi): isi seperti kotak di bawah.

**/opt/stacks/immich/docker-compose.override.yml** | Isi berkas

```
services:
  immich-server:
    extra_hosts:
      - "lab-sso.NAMA-TAILNET.ts.net:100.X.Y.Z"
```

Mengapa extra_hosts. Saat Anda masuk lewat SSO, server Immich menghubungi Pocket ID. VM memakai
--accept-dns=false, jadi nama .ts.net tidak terjawab di dalam VM. Baris ini memetakan nama lab-sso ke alamat
Tailscale VM sso (100.X.Y.Z dari perintah tailscale ip -4 di Bab 54.2). Sertifikat tetap cocok karena nama yang
dipakai tidak berubah. Cara ini [BELUM PASTI]: uji di 55.6, dan bila gagal, aktifkan MagicDNS di VM (tanpa
--accept-dns=false) sebagai alternatif.

## 55.4 Menyalakan dan mengaktifkan HTTPS

**TERMINAL VM IMMICH** | VM immich, sebagai root di /opt/stacks/immich

```
docker compose up -d
```
> Penjelasan: Mengunduh image dan menyalakan semua layanan. Pada kali pertama unduhan besar; tunggu
sampai selesai.
```
docker compose ps
```
> Penjelasan: Semua layanan (immich-server, immich-machine-learning, redis, database) harus berstatus running
atau healthy.
```
tailscale serve --bg --https=443 2283
```
> Penjelasan: HTTPS port 443 di nama lab-immich diteruskan ke 127.0.0.1:2283. Sertifikat tepercaya diminta pada
kali pertama.
```
tailscale serve status
```
> Penjelasan: Memeriksa rute. Jangan menjalankan tailscale funnel.
1. Dari laptop (Tailscale aktif) buka https://lab-immich.NAMA-TAILNET.ts.net. Halaman pertama
mengarahkan pembuatan akun admin (email dan kata sandi kuat); akun pertama menjadi admin. Simpan di
Vaultwarden.
2. Ikuti wizard awal (bahasa, tema, privasi). Letak dan urutan layar bisa berbeda antar versi [BELUM PASTI].

## 55.5 Pengaturan awal di admin

1. Buka Administration (ikon admin) lalu Settings. Cari bagian Machine Learning Settings. Bila RAM VM
4096 MB, matikan machine learning; dengan 6144 MB biarkan menyala. Nama dan letak pengaturan
[BELUM PASTI].
2. Cari Job Settings dan turunkan konkurensi pekerjaan bila VM terasa berat saat impor pertama; angka yang
cocok tergantung CPU Anda [BELUM PASTI].
3. Pastikan pengaturan database backup (pencadangan database terjadwal) aktif. Dokumentasi menyebut
Immich memiliki backup database bawaan; letak berkasnya [BELUM PASTI].

## 55.6 SSO dengan Pocket ID

1. Di Pocket ID (Bab 54.6): buat klien OIDC bernama Immich dengan callback URL berikut, sesuai
dokumentasi Immich: https://lab-immich.NAMA-TAILNET.ts.net/auth/login,
https://lab-immich.NAMA-TAILNET.ts.net/user-settings, dan untuk aplikasi HP
app.immich:///oauth-callback (wajib agar aplikasi iOS dan Android berfungsi).
2. Bila Pocket ID menolak alamat app.immich:///oauth-callback (skema khusus) [BELUM PASTI], pakai
alternatif dari dokumentasi Immich: daftarkan
https://lab-immich.NAMA-TAILNET.ts.net/api/oauth/mobile-redirect sebagai callback, lalu aktifkan Mobile
Redirect URI Override di Immich (langkah 4).
3. Salin Client ID dan Client Secret dari Pocket ID ke Vaultwarden.
4. Di Immich: Administration &gt; Settings &gt; Authentication Settings &gt; OAuth. Aktifkan OAuth. Isi Issuer URL
dengan https://lab-sso.NAMA-TAILNET.ts.net (bila Immich menolak, coba alamat penemuan penuh yang
berakhir /.well-known/openid-configuration [BELUM PASTI]), Client ID, dan Client Secret. Biarkan scope
bawaan (openid email profile). Isi Button Text misalnya Masuk dengan Pocket ID. Nyalakan Auto Register
agar akun dibuat saat login pertama. Bila memakai alternatif langkah 2, aktifkan Mobile Redirect URI Override
dengan alamat mobile-redirect tadi.
5. Jangan mematikan login kata sandi dan jangan menyalakan Auto Launch dulu. Simpan pengaturan.
6. Uji: buka alamat Immich di jendela privat, klik tombol SSO, masuk dengan passkey Pocket ID, dan pastikan
Anda masuk ke Immich.
CATATAN
Immich mencocokkan atau membuat akun dari email. Pastikan akun harian di Pocket ID punya email yang sama
dengan yang Anda inginkan di Immich. Bila Immich gagal menghubungi penyedia (galat tentang issuer atau koneksi),
periksa baris extra_hosts di 55.3 dan alamat Tailscale VM sso.

## 55.7 Sisi klien

Windows
1. Tanpa instalasi: buka https://lab-immich.NAMA-TAILNET.ts.net di browser dengan Tailscale aktif dan
masuk. Unggah foto dengan menyeret berkas ke jendela. Opsional: Menu &gt; Instal sebagai aplikasi di
Chrome atau Edge.
2. Impor besar dari komputer: dokumentasi Immich menyebut alat immich-go untuk memindahkan pustaka
(misalnya dari Google Takeout). Baca petunjuknya di dokumentasi resmi sebelum memakainya [BELUM
PASTI].
Android
1. Pastikan Tailscale aktif. Pasang aplikasi Immich dari toko aplikasi atau halaman rilis resminya (sumber
pemasangan [BELUM PASTI]).
2. Pada layar awal isi server endpoint URL dengan https://lab-immich.NAMA-TAILNET.ts.net. Pilih masuk
dengan OAuth (tombol SSO) atau dengan email dan kata sandi admin.
3. Buka tab cadangan (ikon awan) dan pilih album yang dicadangkan (misalnya Kamera). Nyalakan cadangan.
Atur agar hanya memakai WiFi bila kuota terbatas; nama opsi persis [BELUM PASTI].
4. Agar cadangan latar belakang tidak dimatikan sistem: Pengaturan &gt; Aplikasi &gt; Immich &gt; Baterai &gt; Tanpa
batasan dan biarkan Tailscale aktif terus (VPN selalu menyala). Perilaku tiap merek HP [BELUM PASTI].
iPhone
1. Pastikan Tailscale aktif. Pasang Immich dari App Store.
2. Isi server endpoint URL yang sama, lalu masuk dengan OAuth atau email dan kata sandi.
3. Pilih album yang dicadangkan dan nyalakan cadangan. Izinkan Pengaturan &gt; Immich &gt; Penyegaran App di
Latar Belakang dan akses penuh ke Foto. iOS membatasi tugas latar belakang, sehingga cadangan paling
andal berjalan saat aplikasi dibuka sebentar sambil mengisi daya [BELUM PASTI].
CATATAN
Cadangan foto hanya berjalan saat Tailscale aktif, di rumah maupun di luar. Cadangan pertama berukuran besar;
jalankan di rumah dengan WiFi, daya tersambung, dan Tailscale aktif.

## 55.8 Backup, firewall, pemantauan

1. Proxmox Backup Server: tambahkan 214 ke job backup (Suplemen 7 Bab 50.10). Disk foto ikut. Backup
pertama besar; backup berikutnya hanya mengirim bagian yang berubah. Periksa ruang datastore PBS
sebelum menambah VM ini.
2. Salinan di luar mesin: sebulan sekali salin folder /srv/foto/library ke disk USB atau komputer lain (rsync atau
penyalinan biasa). Satu backup di mesin yang sama bukan perlindungan penuh.
3. Firewall: buat /etc/pve/firewall/214.fw seperti kotak di bawah dan aktifkan kotak Firewall pada kartu jaringan
(Suplemen 7 Bab 51).
4. Pasang agen Beszel dan monitor Uptime Kuma sesuai Suplemen 3. Pantau terutama RAM dan ruang
/srv/foto.

**/etc/pve/firewall/214.fw** | Isi berkas

```
[OPTIONS]
enable: 1
policy_in: DROP
policy_out: ACCEPT
dhcp: 1
[RULES]
IN ACCEPT -source +dc/admin -p tcp -dport 22
```

IN ACCEPT -source 192.168.88.20 -p tcp -dport PORT-AGEN-BESZEL
IN ACCEPT -p icmp
Tidak ada port layanan yang dibuka di LAN: Immich hanya terjangkau lewat Tailscale Serve.

## 55.9 Pembaruan

**TERMINAL VM IMMICH** | VM immich, sebagai root di /opt/stacks/immich

```
docker compose pull && docker compose up -d
```
> Penjelasan: Mengunduh image baru dan membuat ulang container. Backup VM dilakukan PBS tiap malam.
PERINGATAN
Immich sering merilis versi baru dan kadang berisi perubahan yang memutus kompatibilitas. Baca catatan rilis
sebelum memperbarui, unduh ulang berkas compose dari rilis yang sama bila catatan memintanya (lalu ulangi
pengaturan port di 55.3), dan jalankan backup PBS lebih dulu.


<!-- SOURCE: docs/bab/suplemen/bagian-9-99-penutup.md -->

# Bagian 9. SSO dengan Pocket ID dan Immich: Uji, Masalah Umum, Lembar Pembaruan, Syarat Lulus Fase 9

Uji, Masalah Umum, dan Lembar Pembaruan
Uji menyeluruh
No Uji Hasil yang diharapkan
1 tailscale serve status di VM sso Rute 443 menuju 1411
2 Laptop: https://lab-sso.NAMA-TAILNET.ts.net Halaman Pocket ID dengan gembok tanpa peringatan
3 Masuk dengan passkey di laptop dan HP Berhasil tanpa kata sandi
4 docker compose ps di VM immich Semua layanan running atau healthy
5 Laptop: https://lab-immich.NAMA-TAILNET.ts.net Halaman Immich dengan gembok tanpa peringatan
6 Immich: masuk lewat tombol SSO Masuk setelah passkey Pocket ID
7 Unggah beberapa foto dari HP Muncul di Immich dan terhitung di /srv/foto/library
8 Dari laptop: Test-NetConnection 192.168.88.33 -Port 2283 False (tidak terbuka di LAN)
9 Dari laptop: Test-NetConnection 192.168.88.32 -Port 1411 False (tidak terbuka di LAN)
10 Job backup PBS untuk VM 213 dan 214 TASK OK; backup 214 memuat disk foto
11 /root/profil.sh harian, lalu foto VM berganti sesuai tabel 56.2 dan free -m tetap lega
Masalah dan solusi
Gejala Penyebab Solusi
Pocket ID tidak mau mulai ENCRYPTION_KEY kosong atau
terlalu pendek
Pastikan baris ENCRYPTION_KEY ada di .env
dan dibuat dengan openssl rand -base64 32
Passkey tidak bisa didaftarkan Alamat bukan HTTPS atau nama
tidak sama dengan APP_URL
Buka lewat alamat .ts.net persis seperti
APP_URL; periksa tailscale serve status
Semua passkey hilang HP rusak atau hilang Buat token akses satu kali dari server (Bab 54.5)
dan daftarkan passkey baru
Immich tidak bisa menghubungi
penyedia SSO
Nama lab-sso tidak terjawab di VM,
atau alamat issuer berbeda
Periksa extra_hosts di 55.3 dan alamat Tailscale
VM sso; issuer harus sama dengan APP_URL
Aplikasi HP menolak tombol SSO Callback aplikasi tidak terdaftar Tambahkan app.immich:///oauth-callback atau
pakai Mobile Redirect URI Override (55.6)
Immich lambat atau terhenti di VM
4 GB
RAM kurang untuk machine learning Matikan machine learning (55.5) atau naikkan
RAM VM
Cadangan foto HP berhenti Tailscale mati, baterai membatasi
aplikasi, atau iOS membatasi tugas
latar belakang
Aktifkan Tailscale terus-menerus; atur baterai;
buka aplikasi sebentar sambil mengisi daya
Setelah pembaruan Immich port
terbuka di LAN
Berkas compose baru menimpa
pengaturan port
Ulangi sed di 55.3 dan periksa grep 2283
VM tidak menyala setelah ganti
profil
RAM host tidak cukup free -m; matikan VM lain; periksa daftar di 56.2
PBS mati saat backup berjalan Pergantian profil pukul 06:30 terlalu
dini
Atur ulang jam cron setelah memantau durasi
backup (56.5)
Lembar pembaruan
Dokumen Perubahan Rujukan
Suplemen 7, Bab 48 Peta guest bertambah VM 213 sso dan 214 immich; tabel RAM
menjadi 22.272 MB (terpisah penuh) dan 19.200 MB (mode
hemat)
Bab 48.3, 48.6
Suplemen 7, Bab 50.10 Job backup mencakup VM 213 dan 214 (disk foto ikut) Bab 54.7, 55.8
Suplemen 7, Bab 51 Aturan firewall untuk VM 213 dan 214 Bab 54.7, 55.8
Suplemen 7, Bab 52 Laporan audit bertambah baris VM 204, 213, dan 214 Bab 52.7
Daftar hal yang belum dipastikan
No Hal Cara memastikan
1 Halaman penyiapan awal Pocket ID (/setup) dan letak menu pengguna
dan klien OIDC
Lihat antarmuka dan dokumentasi Pocket
ID
2 Perintah token akses satu kali untuk versi Pocket ID Anda Dokumentasi Pocket ID; docker compose
exec pocket-id /app/pocket-id --help
3 Pocket ID menerima callback app.immich:///oauth-callback; bentuk Issuer
URL yang diminta Immich
Uji di 55.6; pakai alternatif mobile-redirect
bila ditolak
4 extra_hosts ke alamat Tailscale VM sso dari dalam container Uji masuk lewat SSO (55.6); alternatif
MagicDNS
5 Jalur Tailscale antar-VM saat firewall Proxmox aktif (langsung atau lewat
relai DERP)
tailscale status di VM immich
6 Backup bawaan Immich hanya database atau lebih Dokumentasi Immich bagian backup and
restore
7 Nomor versi tetap Immich dan Pocket ID untuk dipasang Halaman rilis masing-masing di GitHub
8 Kebutuhan RAM dan CPU sebenarnya (Immich saat impor, Pocket ID,
host)
Ukur dengan Beszel; sesuaikan tabel 56.2
9 Perilaku cadangan latar belakang di Android dan iOS Uji di perangkat Anda
10 Sumber aplikasi Immich di Android (toko aplikasi atau halaman rilis) Dokumentasi Immich bagian aplikasi HP
11 Batas ZFS ARC pada instalasi Anda cat /etc/modprobe.d/zfs.conf dan
zfs_arc_max (56.1)
Syarat lulus
No Poin Ya / Tidak
1 VM 213 berjalan; Pocket ID hanya terbuka lewat Tailscale Serve
2 Passkey terdaftar di sedikitnya dua perangkat dan cara pemulihan dicatat
3 ENCRYPTION_KEY dan Client Secret tersimpan di Vaultwarden
4 VM 214 berjalan dengan disk foto terpasang otomatis dan hanya terbuka lewat Tailscale Serve
5 Foto uji dari Android dan iPhone muncul di Immich
6 Akun lokal admin Immich masih bisa masuk (login darurat)
7 Backup VM 213 dan 214 berhasil; salinan foto di luar mesin sudah dijadwalkan
8 Skrip profil berjalan dan hanya VM harian yang onboot 1
9 Firewall VM 213 dan 214 aktif; entri audit terisi
Berikutnya: Suplemen 10 (opsional): server game dengan AMP dan playit.gg, Ollama untuk model bahasa lokal,
dan katalog layanan kecil. Ollama dan model besar membutuhkan RAM jauh lebih banyak, sehingga sebaiknya
menunggu penambahan RAM.


<!-- SOURCE: docs/bab/suplemen/56-profil-ram.md -->

# Bab 56. Profil Pemakaian RAM (16 GB, 24 GB, dan 32 GB)

> **Pembaruan 31 Oktober 2026.** M710q dilaporkan memakai **1×16 GB + 1×8 GB (total 24 GB)** setelah modul 8 GB pada slot pertama diganti dengan 16 GB. BIOS/OS dan MemTest86 belum dikonfirmasi. Bagian 56.1–56.6 adalah baseline konservatif 16 GB; 56.7 membahas opsi 32 GB; 56.8 memberi batas awal sementara untuk konfigurasi 24 GB. Jangan menganggap semua VM aman menyala bersamaan sebelum diukur.

PENEMPATAN - HOST - mesin fisik
Tempat: Pengaturan di host Proxmox (skrip profil dan jadwal PBS). Tidak ada VM baru.
Aturan: Host tetap hanya menjalankan Proxmox; skrip kecil di /root bukan aplikasi.
Baseline konservatif 16 GB dipakai agar host tetap punya ruang untuk bekerja. Konfigurasi fisik terbaru dilaporkan 24 GB, tetapi harus diverifikasi di BIOS/Proxmox. Semua VM di buku ini bila menyala bersamaan
membutuhkan jauh lebih banyak (Suplemen 7 Bab 48.6 dan 56.6). Solusinya bukan memaksa semuanya
menyala, tetapi membagi VM menjadi profil: sekelompok VM yang menyala untuk satu keperluan, sementara
yang lain dimatikan.

## 56.1 Anggaran RAM

Bagian Perkiraan Catatan
RAM fisik 16384 MB (16 GB)
Host Proxmox sekitar 1 sampai 2 GB Perkiraan [BELUM PASTI]; ukur di Summary node
Cache ZFS (bila memakai ZFS) bawaan 10% RAM, maksimum
16 GiB
Sekitar 1,6 GiB di mesin 16 GB. Dokumentasi
Proxmox: pemasangan baru sejak 8.1 menetapkan
batas ini; kolam ZFS yang dibuat belakangan atau
instalasi lama mungkin memakai batas lain (periksa
di bawah)
Batas jumlah RAM VM yang menyala 12288 MB (12 GB) Sisakan sekitar 4 GB untuk host, cache, dan
lonjakan. Angka kebijakan buku ini [BELUM PASTI]

**TERMINAL HOST PROXMOX** | Shell node Proxmox (host), sebagai root

```
free -m
```
> Penjelasan: Melihat RAM terpakai dan tersedia. Kolom available adalah yang bisa dipakai VM baru.
```
cat /sys/module/zfs/parameters/zfs_arc_max
```
> Penjelasan: Hanya bila memakai ZFS: batas cache dalam byte (0 berarti nilai bawaan OpenZFS [BELUM PASTI]).
Berkas /etc/modprobe.d/zfs.conf menyimpan batas yang ditetapkan saat instalasi.
PERINGATAN
Proxmox tidak menolak menyalakan VM yang melebihi RAM. Bila jumlahnya melampaui RAM fisik, sistem
mematikan proses (OOM) dan VM bisa terhenti mendadak. Jaga jumlah RAM VM aktif di bawah batas 56.1 dan
pantau lewat Beszel.

## 56.2 Daftar VM dan profilnya

Tabel memakai mode hemat (Suplemen 7 Bab 48.6): n8n, web, AFFiNE, dan musik digabung dalam VM 206
apps, sehingga VM 208, 209, dan 211 tidak dibuat.
VM Nama RAM (MB) Menyala pada profil
201 docker-core 2048 harian, kerja, foto, backup, belajar
202 haos 2048 harian, kerja, foto, backup
205 vault 1024 semua profil
213 sso 1024 semua profil
207 nextcloud 2048 harian, kerja, backup
204 git 1024 kerja, belajar
206 apps (n8n, web, AFFiNE, musik) 3072 kerja
VM Nama RAM (MB) Menyala pada profil
203 k3s 3072 belajar
214 immich 6144 (4096 tanpa ML) foto
212 pbs 2048 backup
210 web-public 768 opsional; tambahkan ke profil mana
pun bila situs publik perlu hidup
Profil VM yang menyala Jumlah RAM Keperluan
harian 201, 202, 205, 207, 213 8192 MB (8,0 GB) Pemakaian sehari-hari: dashboard,
rumah pintar, kata sandi, SSO,
berkas
kerja harian + 204, 206 12288 MB (12,0 GB) Git, AFFiNE, n8n, situs web, musik
foto 201, 202, 205, 213, 214 12288 MB (12,0 GB) Cadangan dan pencarian foto
(Immich); Nextcloud dimatikan
backup harian + 212 10240 MB (10,0 GB) Malam hari saat PBS
mencadangkan
belajar 201, 203, 204, 205, 213 8192 MB (8,0 GB) Latihan Kubernetes dan GitOps
Dengan Immich 4096 MB (machine learning mati), profil foto menjadi 10240 MB. Menambahkan VM 210
web-public (768 MB) ke profil harian menghasilkan 8960 MB. Semua angka RAM VM adalah perkiraan [BELUM
PASTI]; sesuaikan setelah mengukur dengan Beszel.

## 56.3 Skrip pergantian profil

Skrip kecil di host Proxmox mematikan VM yang tidak termasuk profil dan menyalakan yang termasuk. Ia hanya
memakai perintah qm bawaan dan tidak memasang aplikasi.

**TERMINAL HOST PROXMOX** | Shell node Proxmox (host), sebagai root

```
nano /root/profil.sh
```
> Penjelasan: Isi seperti kotak di bawah.
```
chmod 700 /root/profil.sh
```
> Penjelasan: Hanya root yang boleh menjalankan.

**/root/profil.sh** | Isi berkas

```
#!/bin/bash
# Ganti profil pemakaian. Pakai: profil.sh harian|kerja|foto|backup|belajar
ALL="201 202 203 204 205 206 207 210 212 213 214"
case "${1:-}" in
 harian) ON="201 202 205 207 213" ;;
 kerja) ON="201 202 205 207 213 204 206" ;;
 foto) ON="201 202 205 213 214" ;;
 backup) ON="201 202 205 207 213 212" ;;
 belajar) ON="201 203 204 205 213" ;;
 *) echo "pakai: $0 harian|kerja|foto|backup|belajar"; exit 1 ;;
esac
if pgrep -f vzdump >/dev/null; then
 echo "vzdump masih berjalan; ditunda"; exit 1
fi
for id in $ALL; do
 case " $ON " in *" $id "*) continue ;; esac
 if qm status "$id" 2>/dev/null | grep -q running; then
 qm shutdown "$id" --timeout 120
 fi
done
for id in $ON; do
 if ! qm status "$id" 2>/dev/null | grep -q running; then
 qm start "$id"
 fi
done
qm list
```

Bagian Fungsi
ALL Semua VM yang diatur skrip (ganti bila nomor VM Anda berbeda atau ada VM
tambahan)
ON Daftar VM yang harus menyala pada profil itu
pgrep -f vzdump Menolak berganti profil selagi backup berjalan agar PBS tidak dimatikan di tengah
jalan [BELUM PASTI]
qm shutdown ... --timeout 120 Mematikan dengan bersih; menunggu sampai 120 detik
2&gt;/dev/null Menyembunyikan galat untuk VM yang belum dibuat (misalnya 206 bila Anda
belum memakai mode hemat)

**TERMINAL HOST PROXMOX** | Shell node Proxmox (host), sebagai root

```
/root/profil.sh foto
```
> Penjelasan: Contoh: beralih ke profil foto. Pantau Tasks di web Proxmox; Immich butuh beberapa menit untuk
siap.
```
free -m
```
> Penjelasan: Memastikan RAM tersedia masih cukup setelah berganti profil.

## 56.4 Hanya VM harian yang menyala otomatis

Saat host dinyalakan ulang, VM yang diberi --onboot 1 ikut menyala. Pada mesin 16 GB hanya VM profil harian
yang boleh begitu.

**TERMINAL HOST PROXMOX** | Shell node Proxmox (host), sebagai root

```
for id in 201 202 205 207 213; do qm set $id --onboot 1; done
```
> Penjelasan: Menyalakan otomatis lima VM profil harian.
```
for id in 203 204 206 210 212 214; do qm set $id --onboot 0; done
```
> Penjelasan: Mematikan penyalaan otomatis VM lain. Abaikan galat untuk nomor yang belum dibuat.
```
qm config 214 | grep onboot
```
> Penjelasan: Memeriksa satu VM (onboot: 0 berarti tidak otomatis).
CATATAN
AdGuard kedua (CT101) dan Samba (CT102) berupa LXC kecil (Edisi 2) dan tetap menyala otomatis. Atur urutan
nyala di Start/Shutdown order sesuai Edisi 2 Bab 23.

## 56.5 PBS dan backup malam hari

Backup terjadwal berjalan pukul 02:00 (Suplemen 7 Bab 50.10) dan membutuhkan VM pbs menyala. Di mesin 16
GB pbs tidak menyala sepanjang hari, jadi ganti profil sebelum dan sesudah backup memakai cron di host.

**TERMINAL HOST PROXMOX** | Shell node Proxmox (host), sebagai root

```
crontab -e
```
> Penjelasan: Membuka jadwal root; tambahkan dua baris di bawah.

**crontab (host Proxmox)** | Isi berkas

```
45 1 * * * /root/profil.sh backup
30 6 * * * /root/profil.sh harian
```

Baris Arti
45 1 \* \* \* Pukul 01:45 beralih ke profil backup (PBS menyala; VM kerja atau foto dimatikan)
30 6 \* \* \* Pukul 06:30 kembali ke profil harian (PBS dimatikan)
PERINGATAN
Pantau durasi backup di Tasks selama beberapa malam sebelum mengandalkan jam ini. Backup pertama (terutama
disk foto Immich) bisa jauh lebih lama dari jeda 02:00 sampai 06:30. Skrip menolak berganti profil selagi vzdump
berjalan, tetapi bila backup belum selesai pukul 06:30 profil harian tidak akan terpasang sampai Anda menjalankannya
lagi. Prune, garbage collection, dan verifikasi PBS (Bab 50.10) harus dijadwalkan sebelum PBS dimatikan; sesuaikan
jamnya atau jalankan manual [BELUM PASTI].

## 56.6 Saat RAM naik

Jumlah RAM VM bila semuanya menyala (mode terpisah penuh, tanpa mode hemat), menurut tabel Suplemen 7
Bab 48.6 ditambah VM 213 dan 214:
Konfigurasi RAM VM (MB) RAM VM (GB) Dengan 16 GB
VM 201 dan 204 sampai 214, terpisah penuh 22272 21,8 Tidak muat
Ditambah HAOS (2048) dan k3s (3072 sampai 4096) 27392 sampai 28416 26,8 sampai 27,8 Tidak muat
Mode hemat (apps 3072 menggantikan 206, 208, 209, 211) 19200 18,8 Tidak muat
Mode hemat ditambah HAOS dan k3s 24320 sampai 25344 23,8 sampai 24,8 Tidak muat
Dari tabel ini: 32 GB cukup untuk menyalakan hampir semuanya sekaligus dalam mode hemat, dan terpisah
penuh hanya pas dengan sisa sangat tipis [BELUM PASTI]. Saat RAM ditambah, langkahnya: (1) pasang RAM
dan periksa free -m; (2) naikkan RAM VM yang terasa sempit (qm set ID --memory ...); (3) ubah profil menjadi
lebih besar atau berhenti memakai skrip; (4) atur --onboot 1 untuk VM yang kini boleh menyala otomatis; (5)
perbarui batas ZFS bila perlu (56.1).

## 56.7 Jika RAM ditingkatkan menjadi 32 GB (16 + 16)

Jika tersedia modul 16 GB yang kompatibel, ganti modul 8 GB dengan modul 16 GB (Bab 27.1), uji MemTest86, lalu periksa dengan `free -m` di host (total sekitar 32.000 MB). Ini rencana masa depan, bukan kondisi saat ini.

| Konfigurasi | RAM VM (MB) | Sisa dari 32.768 MB |
|---|---|---|
| Mode hemat (apps menggantikan 206, 208, 209, 211) + HAOS + k3s | 24.320 sampai 25.344 | sekitar 7,4 sampai 8,4 GB (untuk host dan lonjakan) |
| Terpisah penuh + HAOS + k3s | 27.392 sampai 28.416 | sekitar 4,3 sampai 5,4 GB (pas-pasan) |

Mode hemat dapat dipertimbangkan setelah hasil pemantauan memastikan sisa RAM host cukup. Jangan menyalakan semua VM hanya karena kapasitas teoritis tampak cukup. Langkah penyalaan otomatis di bawah ini baru diterapkan setelah VM masing-masing diuji:

1. Atur penyalaan otomatis untuk semua VM yang dipakai: `for id in 201 202 204 205 206 207 212 213 214; do qm set $id --onboot 1; done` (sesuaikan daftar dengan VM yang sudah dibuat; abaikan galat untuk nomor yang belum ada). Biarkan `203` (k3s) dan `210` (web-public) sesuai kebutuhan.
2. PBS (VM 212) boleh menyala terus; cron `profil.sh backup` dan `profil.sh harian` di 56.5 tidak diperlukan lagi.
3. Skrip `profil.sh` tetap berguna untuk sesi latihan: `belajar` mematikan layanan yang tidak dipakai sehingga CPU dan RAM lebih lega.
4. **Batas berikutnya adalah CPU**: i5-6500T hanya 4 thread. Jangan memberi banyak core ke setiap VM; mulai 1-2 core. Impor foto pertama di Immich dan machine learning akan memakan CPU lama; jalankan saat tidak sibuk.
5. Pantau di Beszel (Bab 33): RAM terpakai, beban CPU, suhu, dan ruang NVMe/HDD. Naikkan RAM VM hanya bila terbukti perlu.

## 56.8 Batas sementara untuk konfigurasi 24 GB (16 + 8)

Kapasitas 24 GB dilaporkan dari susunan 16 GB + 8 GB, tetapi belum dicatat dari BIOS atau hasil MemTest86. Setelah instalasi Proxmox, konfirmasi kapasitas dengan `free -h` dan catat konsumsi host saat tidak ada VM aktif.

Sampai ada hasil pengukuran, gunakan profil konservatif 16 GB di Bagian 56.1–56.5. Setelah itu, naikkan alokasi VM sedikit demi sedikit; jangan melebihi total alokasi 18 GB untuk VM yang aktif sebelum pemantauan membuktikan host tetap memiliki setidaknya 4–6 GB tersedia saat beban normal. Profil mode hemat yang menyalakan VM dengan total sekitar 19,2 GB atau lebih belum cocok untuk dijalankan serentak pada 24 GB tanpa pengukuran.

Jika RAM tersedia terus rendah, ballooning/oom muncul, atau VM tersendat, matikan guest yang tidak diperlukan dan kembali ke profil 16 GB. Catat profil yang dipakai serta nilai RAM available di `catatan/hasil-uji.md`.


# Roadmap terbaru: manfaat dan keamanan

Sumber roadmap lengkap: `docs/12-roadmap-manfaat-keamanan.md`.

[[ROADMAP:INCLUDE]]

## Penutup: server dianggap siap setelah diuji

Proxmox sudah dipasang dan diperbarui. Backup, firewall, layanan, Tailscale, dan instruksi pemulihan dalam buku belum dibuktikan di mesin ini. Template VM/CT menjadi langkah pertama setelah update host dan pemeriksaan KVM. Catat uji aktual, versi, kendala, dan hasil restore sebelum menandai pekerjaan selesai. Repo menjadi catatan utama untuk perubahan konfigurasi.
