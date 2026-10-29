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

1  
# docker exec -u www-data nextcloud \  
 php occ config:system:set trusted_domains 2 --value=nextcloud.lan  
> Penjelasan: Menambah nama nextcloud.lan ke daftar domain tepercaya. Ulangi dengan angka 3, 4 untuk
nama lain.  

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
