# Bab 46. AFFiNE: Catatan dan Dokumen Bergaya Notion

PENEMPATAN - BARU - VM sendiri  
Tempat: VM 206 affine (192.168.88.25): qm clone 9100 206 --name affine --full 1.  
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
qm clone 9100 206 --name affine --full 1
```
> Penjelasan: Membuat VM 206 bernama affine sebagai salinan penuh dari templat VM 9100 (Suplemen 7 Bab 49).
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
