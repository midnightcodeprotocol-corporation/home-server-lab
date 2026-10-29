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
