# Bab 47. Nextcloud dan Kalender Pribadi

PENEMPATAN - BARU - VM sendiri  
Tempat: VM 207 nextcloud (192.168.88.26): qm clone 9100 207 --name nextcloud --full 1.  
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
qm clone 9100 207 --name nextcloud --full 1
```
> Penjelasan: Membuat VM 207 bernama nextcloud sebagai salinan penuh dari templat VM 9100 (Suplemen 7 Bab
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
