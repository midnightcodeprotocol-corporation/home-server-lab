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
