# Bab 36. Memasang Caddy dan Memindahkan Layanan

PENEMPATAN - GABUNG - ke docker-core  
Tempat: Caddy di VM 201 docker-core (192.168.88.20) sebagai satu-satunya gerbang HTTPS.  
Aturan baru: Layanan di VM lain ditulis reverse_proxy IP:port, bukan nama container. Hanya layanan di docker-core  
yang memakai jaringan proxy.  

## 36.1 DNS: nama menuju VM Debian

1. Buka AdGuard Home (http://192.168.88.253) &gt; Filters &gt; DNS rewrites &gt; Add DNS rewrite.  
2. Isi Domain: \*.home.arpa, Answer: 192.168.88.20, simpan. Tanda bintang membuat semua nama di bawah  
home.arpa mengarah ke VM.  
3. Ulangi aturan yang sama di AdGuard kedua (LXC 192.168.88.11, Edisi 2 Bab 13) agar nama tetap dikenali  
bila STB mati.  
4. Agar nama berfungsi dari luar rumah: di konsol Tailscale DNS &gt; Nameservers tambahkan nameserver  
Custom 192.168.88.253 dengan Restrict to domain bernilai home.arpa (cara seperti Suplemen 1 Bab  
26.7B).  

**POWERSHELL WINDOWS** | PowerShell (laptop)

```
nslookup kuma.home.arpa 192.168.88.253
```
> Penjelasan: Menanyakan langsung ke AdGuard. Jawaban harus 192.168.88.20.

## 36.2 Jaringan Docker bersama

Caddy dan container yang berada di VM 201 harus bergabung ke jaringan Docker `proxy` agar Caddy dapat memanggilnya memakai nama container. Jaringan Docker ini hanya berlaku di VM 201; layanan pada VM lain dijangkau memakai alamat IP dan port yang diizinkan firewall Proxmox.  

**TERMINAL VM DEBIAN** | Sebagai root (setelah su -)

```
docker network create proxy
```
> Penjelasan: Membuat jaringan bernama proxy. Cukup sekali.
```
ss -tlnp | grep -E ":(80|443)\b" || echo port-bebas
```
> Penjelasan: Memastikan port 80 dan 443 di VM belum dipakai. Jika dipakai (biasanya Homepage Edisi 2),
pindahkan dulu portnya; lihat peringatan di bawah.  
PERINGATAN  
Homepage dari Edisi 2 Bab 19 memakai ports "80:3000" dan merebut port 80 yang dibutuhkan Caddy. Ubah ke  
"3002:3000" dan perbarui HOMEPAGE_ALLOWED_HOSTS sebelum Caddy dinyalakan (Suplemen 7 Bab 48.8). Port  
3001 tidak bisa dipakai karena sudah milik Uptime Kuma.  

## 36.3 Memasang Caddy

**TERMINAL VM DEBIAN** | Sebagai root

```
mkdir -p /opt/stacks/caddy/data /opt/stacks/caddy/config && cd /opt/stacks/caddy
```
> Penjelasan: Membuat folder aplikasi. Folder data akan menyimpan sertifikat dan otoritas lokal.
```
nano compose.yaml
```
> Penjelasan: Isi seperti kotak di bawah.

**/opt/stacks/caddy/compose.yaml** | Isi berkas

```
services:
  caddy:
    image: caddy:2
    container_name: caddy
    restart: unless-stopped
    ports:
      - "80:80"
      - "443:443"
      - "443:443/udp"
    volumes:
      - ./Caddyfile:/etc/caddy/Caddyfile:ro
      - ./data:/data
      - ./config:/config
    networks:
      - proxy
networks:
  proxy:
    external: true
```

**TERMINAL VM DEBIAN** | Sebagai root di /opt/stacks/caddy

```
nano Caddyfile
```
> Penjelasan: Berkas pengaturan Caddy. Isi seperti kotak di bawah.

**/opt/stacks/caddy/Caddyfile** | Isi berkas

```
{
 local_certs
}
kuma.home.arpa {
 reverse_proxy uptime-kuma:3001
}
beszel.home.arpa {
 reverse_proxy beszel:8090
}
gotify.home.arpa {
 reverse_proxy gotify:80
}
proxmox.home.arpa {
 reverse_proxy https://192.168.88.10:8006 {
 transport http {
 tls_insecure_skip_verify
 }
 }
}
portainer.home.arpa {
 reverse_proxy https://192.168.88.20:9443 {
 transport http {
 tls_insecure_skip_verify
 }
 }
}
adguard.home.arpa {
 reverse_proxy 192.168.88.253:80
}
dash.home.arpa {
 reverse_proxy 192.168.88.20:3002
}
```

Opsi global `local_certs` memerintahkan Caddy memakai otoritas sertifikat lokal untuk nama-nama ini. `tls_insecure_skip_verify` hanya dipakai untuk Proxmox dan Portainer karena sertifikat bawaan mereka ditandatangani sendiri; koneksi tetap berada di LAN.  

## 36.4 Menyiapkan layanan agar berada di belakang Caddy

Untuk container di VM 201 yang hanya diakses melalui Caddy, hapus publikasi port dan hubungkan container ke jaringan `proxy`; Caddy dapat mengaksesnya lewat nama container. Gotify tetap memublikasikan port 8070 untuk klien dan pengirim notifikasi. Homepage tetap diakses lewat port 3002. Container di VM lain tidak dapat bergabung ke jaringan Docker ini: pertahankan port layanan di LAN VM dan batasi sumbernya dengan firewall Proxmox.  

**TERMINAL VM DEBIAN** | Sebagai root

```
cd /opt/stacks/uptime-kuma && nano compose.yaml
```
> Penjelasan: Ubah menjadi seperti kotak di bawah: baris ports dihapus, ditambah jaringan proxy.

**/opt/stacks/uptime-kuma/compose.yaml** | Contoh setelah diubah

```
services:
  uptime-kuma:
    image: louislam/uptime-kuma:2
    container_name: uptime-kuma
    restart: unless-stopped
    volumes:
      - ./data:/app/data
    networks:
      - proxy
networks:
  proxy:
    external: true
```

Layanan Perubahan pada compose.yaml Alasan  
Uptime Kuma Hapus ports, tambah networks proxy (seperti contoh) Hanya lewat Caddy  
Beszel hub Hapus ports, tambah networks proxy; extra_hosts  
tetap  
Agen terhubung lewat host.docker.internal  
sehingga tidak butuh port hub  
Gotify Tetap ports "8070:80", tambah networks proxy Aplikasi Android memakai  
http://192.168.88.20:8070 lewat Tailscale;  
monitor Uptime Kuma juga  
Homepage Tetap ports "3002:3000" (bukan 80); tidak perlu  
networks proxy  
Caddy menjangkaunya lewat  
192.168.88.20:3002 seperti Portainer  
TIPS  
Bila agen Beszel Anda memakai token universal (Suplemen 3 Bab 33.3), agen menyambung ke port hub.  
Pertahankan baris ports 8090 pada hub dalam kasus itu.  

**TERMINAL VM DEBIAN** | Sebagai root

```
cd /opt/stacks/uptime-kuma && docker compose up -d
```
> Penjelasan: Menerapkan perubahan; container dibuat ulang dengan jaringan baru. Data aman di folder data.
```
cd /opt/stacks/beszel && docker compose up -d
```
> Penjelasan: Hal yang sama untuk Beszel (setelah mengubah compose.yaml-nya).
```
cd /opt/stacks/gotify && docker compose up -d
```
> Penjelasan: Hal yang sama untuk Gotify.

## 36.5 Menyalakan Caddy dan memeriksa

**TERMINAL VM DEBIAN** | Sebagai root

```
cd /opt/stacks/caddy && docker compose up -d
```
> Penjelasan: Menyalakan Caddy.
```
docker compose logs --tail=40
```
> Penjelasan: Melihat log. Cari baris yang menyebut pembuatan sertifikat lokal untuk nama-nama tadi dan tidak ada
error.  
```
docker exec caddy caddy validate --config /etc/caddy/Caddyfile
```
> Penjelasan: Memeriksa sintaks Caddyfile. Hasil yang benar: Valid configuration.
Dari laptop buka https://kuma.home.arpa. Sebelum sertifikat akar dipasang (Bab 37), browser akan  
menampilkan peringatan. Itu normal. Jika halaman Uptime Kuma tampil setelah memilih lanjut, jalur proxy sudah  
benar.  
KEAMANAN  
Folder /opt/stacks/caddy/data berisi kunci privat otoritas sertifikat lokal Anda. Siapa pun yang memilikinya bisa  
membuat sertifikat yang dipercaya perangkat Anda. Jangan dibagikan, jangan disajikan lewat web, dan sertakan  
dalam backup yang tersimpan aman.  

## 36.6 Menambah layanan baru ke depannya

1. Pastikan layanan bergabung ke jaringan proxy dan catat nama container serta port di dalamnya.  
2. Tambahkan satu blok di Caddyfile: nama.home.arpa { reverse_proxy nama-container:port }.  
3. Muat ulang tanpa memutus layanan: docker exec caddy caddy reload --config /etc/caddy/Caddyfile.  
Tidak perlu menambah DNS karena \*.home.arpa sudah mencakupnya.  

## 36.7 Memperbarui monitor dan dashboard

Di Uptime Kuma ubah target monitor ke nama baru (centang Ignore TLS/SSL error karena container Kuma  
belum mempercayai CA lokal). Di Homepage (Edisi 2 Bab 19 dan Suplemen 3 Bab 34.2) ganti tautan kartu ke  
alamat https yang baru. Homepage sendiri kini dibuka di https://dash.home.arpa.
