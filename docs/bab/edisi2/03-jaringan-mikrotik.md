# Bab 3. Fondasi Jaringan Rumah (MikroTik)

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
192.168.88.253 STB HG680 (AdGuard utama + Tailscale) Static lease MikroTik  
192.168.88.100 - .254 Laptop, HP, dan perangkat lain DHCP otomatis  
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
