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
