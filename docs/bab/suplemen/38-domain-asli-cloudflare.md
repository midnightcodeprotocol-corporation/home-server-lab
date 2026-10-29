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
