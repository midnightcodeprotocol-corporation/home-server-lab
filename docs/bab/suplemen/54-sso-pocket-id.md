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
