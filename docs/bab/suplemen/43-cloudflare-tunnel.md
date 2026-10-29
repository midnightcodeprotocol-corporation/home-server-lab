# Bab 43. Opsional: Situs Statis Publik dengan Cloudflare Tunnel

PENEMPATAN - BARU - VM sendiri, paling terisolasi  
Tempat: VM 210 web-public (192.168.88.29): qm clone 9100 210 --name web-public --full 1.  
Alasan: Satu-satunya yang menghadap internet. Bila dibobol, penyerang tidak boleh punya jalan ke LAN: firewall  
Proxmox memblokir keluar ke LAN (Bab 51.4).  
Tidak boleh: Digabung dengan layanan lain, termasuk situs statis privat di VM 209.  
PERINGATAN  
Bab ini opsional. Kerjakan hanya bila Anda memang ingin situs bisa dibuka siapa pun. Yang dipublikasikan hanya  
situs statis dalam container terpisah. Jangan memublikasikan WordPress, n8n, Portainer, Proxmox, atau Gotify.  

## 43.1 Prasyarat dan cara kerja

• Akun Cloudflare dan domain milik sendiri yang DNS-nya dikelola Cloudflare (dokumentasi menyebut langkah  
membuat catatan DNS untuk aplikasi). Biaya domain tahunan ada di luar buku ini.  
• Langkah resmi: membuat tunnel di dasbor Cloudflare, menjalankan cloudflared dengan token, lalu menambah  
published application route berisi hostname dan Service URL.  
• Nama menu dasbor Cloudflare berubah dari waktu ke waktu [BELUM PASTI]; ikuti halaman Setup pada  
developers.cloudflare.com/tunnel bila tampilan berbeda dari tulisan di bawah.  
Pengunjung  
www.domain-anda  
Cloudflare  
HTTPS publik  
cloudflared  
di VM, koneksi keluar  
web-public  
situs statis  
Jaringan Docker terpisah (publicweb): tidak terhubung ke proxy, WordPress, n8n, atau Gotify  
Gambar 43.1 - cloudflared membuat koneksi keluar; tidak ada port yang dibuka di router.  

## 43.2 Mencoba dulu tanpa domain (quick tunnel)

Dokumentasi Cloudflare menyediakan perintah satu baris yang membuat alamat acak trycloudflare.com untuk  
mencoba. Alamatnya berubah setiap kali dijalankan dan cocok untuk uji, bukan untuk penggunaan tetap [BELUM  
PASTI] (sifat batasannya belum saya baca di dokumentasi). Siapkan dulu situs publik (43.3, langkah 1 sampai 3),  
lalu:  

**TERMINAL VM WEB-PUBLIC** | VM web-public, sebagai root

```
docker run --rm --network publicweb cloudflare/cloudflared:latest tunnel --url http://web-public:80
```
> Penjelasan: Menjalankan quick tunnel sementara untuk uji. Tag `latest` di sini hanya untuk uji sekali jalan; jangan gunakan untuk konektor tunnel permanen. Perintah menampilkan alamat
https://....trycloudflare.com; buka dari HP dengan data seluler. Hentikan dengan Ctrl+C.  

## 43.3 Server: VM web-public dan situs publik

**TERMINAL HOST PROXMOX** | Shell node Proxmox (host), sebagai root

```
qm clone 9100 210 --name web-public --full 1
```
> Penjelasan: Membuat VM 210 sebagai salinan penuh dari templat VM 9100 (Suplemen 7 Bab 49).
```
qm set 210 --memory 768 --cores 1
```
> Penjelasan: RAM (MB) dan inti. Angka awal adalah perkiraan [BELUM PASTI].
```
qm start 210
```
> Penjelasan: Menyalakan. Lakukan penyiapan awal di Suplemen 7 Bab 49.4 (alamat 192.168.88.29), lalu pasang
firewall Proxmox untuk VM ini (Bab 51.4) sebelum membuka tunnel ke internet.  
Langkah berikut dijalankan di VM web-public. VM ini sengaja tidak berbagi apa pun dengan VM web privat (209):  

**TERMINAL VM WEB-PUBLIC** | VM web-public (192.168.88.29), sebagai root (setelah su -)

```
mkdir -p /opt/stacks/tunnel-web/public && cd /opt/stacks/tunnel-web
```
> Penjelasan: Folder khusus situs publik. Isinya terpisah dari situs privat di VM web.
```
nano public/index.html
```
> Penjelasan: Isi halaman publik. Boleh meniru contoh HTML di Bab 40.2, tetapi jangan menyalin folder situs privat.
```
docker network create publicweb
```
> Penjelasan: Jaringan Docker khusus yang tidak dihubungkan ke jaringan proxy.
```
nano Caddyfile
```
> Penjelasan: Isi seperti kotak di bawah.

**/opt/stacks/tunnel-web/Caddyfile** | Isi berkas

```
:80 {
 root * /srv
 encode gzip
 file_server
}
```

**TERMINAL VM WEB-PUBLIC** | VM web-public, sebagai root di /opt/stacks/tunnel-web

```
nano compose.yaml
```
> Penjelasan: Isi seperti kotak di bawah. Token ditaruh di .env pada langkah 43.4, bukan di berkas ini.

**/opt/stacks/tunnel-web/compose.yaml** | Isi berkas

```
services:
  web-public:
    image: caddy:2
    container_name: web-public
    restart: unless-stopped
    volumes:
      - ./Caddyfile:/etc/caddy/Caddyfile:ro
      - ./public:/srv:ro
    networks:
      - publicweb
  cloudflared:
    image: cloudflare/cloudflared:${CLOUDFLARED_VERSION}
    container_name: cloudflared
    restart: unless-stopped
    command: tunnel --no-autoupdate run --token ${TUNNEL_TOKEN}
    depends_on:
      - web-public
    networks:
      - publicweb
networks:
  publicweb:
    external: true
```

Container web-public memakai Caddy tersendiri pada port 80 di dalam jaringan publicweb saja; ia tidak memublikasikan port ke host. Perintah tunnel --no-autoupdate run --token mengikuti contoh Docker Cloudflare. Sebelum menjalankan Compose, isi `CLOUDFLARED_VERSION` di `.env` dengan tag versi yang telah diperiksa pada dokumentasi/rilis resmi Cloudflare. Jangan biarkan variabel kosong dan jangan memakai `latest` untuk konektor permanen.  

## 43.4 Membuat tunnel di dasbor Cloudflare

1. Masuk ke dasbor Cloudflare dan buka bagian pengelolaan Tunnels (di area Zero Trust / Cloudflare One; letak  
menu [BELUM PASTI]).  
2. Buat tunnel baru, pilih konektor cloudflared, beri nama (misalnya home-web), lalu pilih lingkungan Docker.  
3. Dasbor menampilkan perintah docker run dengan token panjang. Salin hanya token (teks setelah --token).  
4. Di server, edit `/opt/stacks/tunnel-web/.env` secara lokal. Isi `TUNNEL_TOKEN=...` dengan token dari dasbor dan `CLOUDFLARED_VERSION=...` dengan tag versi yang sudah diverifikasi. Jangan kirim token ke chat atau GitHub. Setelah disimpan, jalankan `chmod 600 .env`.  
5. Di dasbor, tambah Route bertipe Published application: hostname (misalnya www.domain-anda), Service  
URL http://web-public:80. Dasbor membuat catatan DNS yang diperlukan.  

**TERMINAL VM WEB-PUBLIC** | VM web-public, sebagai root di /opt/stacks/tunnel-web

```
docker compose up -d && docker compose logs --tail=20 cloudflared
```
> Penjelasan: Menyalakan dan memeriksa log. Cari tanda koneksi tunnel terdaftar; di dasbor status tunnel berubah
menjadi sehat.  
KEAMANAN  
Token tunnel setara kunci: pemegangnya dapat menjalankan tunnel Anda. Jangan dibagikan atau dimasukkan ke  
repositori. Bila bocor, ganti (rotasi) token di dasbor dan perbarui .env. Cloudflare menyediakan pembatasan akses  
(Access) untuk menaruh login di depan alamat tertentu [BELUM PASTI] (tidak dikaji di sini).  

## 43.5 Sisi klien

Perangkat Cara uji Hasil yang diharapkan  
Windows Buka https://www.domain-anda di browser Halaman tampil dengan gembok; tidak perlu  
sertifikat tambahan  
Android Matikan Wi-Fi dan Tailscale, buka alamat di Chrome  
lewat data seluler  
Halaman tampil; membuktikan situs  
benar-benar publik  
iPhone Sama, di Safari lewat data seluler Halaman tampil tanpa langkah kepercayaan  
sertifikat  
Mengubah isi Dari laptop: scp ke  
&lt;USER&gt;@192.168.88.29:/opt/stacks/tunnel-web/public  
(ubah kepemilikan folder ke pengguna biasa seperti Bab  
40.2)  
Berkas baru langsung tampil, tanpa restart  
CATATAN  
Sertifikat HTTPS untuk jalur publik berasal dari Cloudflare, sehingga semua perangkat memercayainya tanpa  
memasang apa pun. Ini berbeda dari jalur privat yang memakai CA lokal Caddy.
