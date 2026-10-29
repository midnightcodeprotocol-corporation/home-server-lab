# Bab 55. Immich: Foto dan Video Pribadi

> **Revisi 3.** Disk contoh (foto 300 GiB) harus disesuaikan dengan NVMe 500 GB. Lihat Bab 27.4: kecilkan ukuran awal, dan taruh backup di HDD 2 TB.

PENEMPATAN - BARU - VM sendiri (dan disk foto terpisah)  
Tempat: VM 214 immich (192.168.88.33): qm clone 9100 214 --name immich --full 1, ditambah disk data kedua  
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
qm clone 9100 214 --name immich --full 1
```
> Penjelasan: Membuat VM 214 bernama immich sebagai salinan penuh dari templat VM 9100 (Suplemen 7 Bab
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
