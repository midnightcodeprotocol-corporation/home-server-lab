# Bab 40. Situs Web Statis dengan Caddy

PENEMPATAN - GABUNG - ke VM web  
Tempat: VM 209 web (192.168.88.28). Dibuat dari templat VM 200: qm clone 200 209 --name web --full 1  
(Suplemen 7 Bab 49).  
Alasan: Situs statis dan WordPress sama-sama konten web privat dengan data kecil, jadi boleh serumah. Caddy di  
docker-core hanya meneruskan ke VM ini.  
Dipisahkan dari: n8n (VM 208), situs publik (VM 210), dan semua layanan lain.  
Mode hemat: Boleh digabung ke VM 206 (apps).  
Situs statis adalah kumpulan berkas (HTML, CSS, gambar). Berkasnya disajikan oleh sebuah Caddy kecil di VM  
web; Caddy besar di docker-core hanya menjadi gerbang HTTPS yang meneruskan ke sana. VM web juga akan  
menampung WordPress (Bab 41).  

## 40.1 Membuat VM web

**TERMINAL HOST PROXMOX** | Shell node Proxmox (host), sebagai root

```
qm clone 200 209 --name web --full 1
```
> Penjelasan: Membuat VM 209 bernama web sebagai salinan penuh dari templat VM 200 (Suplemen 7 Bab 49).
```
qm set 209 --memory 1536 --cores 2
```
> Penjelasan: Mengatur RAM (MB) dan jumlah inti. Angka awal adalah perkiraan [BELUM PASTI]; pantau di Beszel
lalu sesuaikan.  
```
qm start 209
```
> Penjelasan: Menyalakan VM. Lakukan penyiapan awal di Suplemen 7 Bab 49.4 (nama host, kunci SSH, alamat
192.168.88.28), lalu kembali ke sini.  

## 40.2 Sisi server: situs di VM web

**TERMINAL VM WEB** | VM web (192.168.88.28), sebagai root (setelah su -)

```
mkdir -p /opt/stacks/web/sites/halo && cd /opt/stacks/web
```
> Penjelasan: Folder induk semua situs; satu subfolder per situs.
```
chown -R <USER>: /opt/stacks/web/sites
```
> Penjelasan: Menjadikan folder ini milik pengguna biasa Anda (ganti &lt;USER&gt;) agar bisa diunggah dari laptop lewat
scp tanpa login root.  
```
nano sites/halo/index.html
```
> Penjelasan: Isi seperti kotak di bawah sebagai halaman uji.

**/opt/stacks/web/sites/halo/index.html** | Isi berkas

```
<!doctype html>
<html lang="id">
<head><meta charset="utf-8"><title>Halo</title>
<meta name="viewport" content="width=device-width, initial-scale=1"></head>
<body><h1>Halo dari home server</h1><p>Situs statis ini disajikan oleh Caddy.</p></body>
</html>
```

**TERMINAL VM WEB** | VM web, sebagai root di /opt/stacks/web

```
nano Caddyfile
```
> Penjelasan: Caddy kecil: HTTP saja, memilih folder situs menurut nama host. Isi seperti kotak di bawah.

**/opt/stacks/web/Caddyfile** | Isi berkas

```
{
 auto_https off
}
http://web.home.arpa {
 root * /srv/sites/halo
 encode gzip
 file_server
}
```

**TERMINAL VM WEB** | VM web, sebagai root di /opt/stacks/web

```
nano compose.yaml
```
> Penjelasan: Isi seperti kotak di bawah.

**/opt/stacks/web/compose.yaml** | Isi berkas

```
services:
  sites:
    image: caddy:2
    container_name: sites
    restart: unless-stopped
    volumes:
      - ./Caddyfile:/etc/caddy/Caddyfile:ro
      - ./sites:/srv/sites:ro
    ports:
      - "8082:80"
```

**TERMINAL VM WEB** | VM web, sebagai root di /opt/stacks/web

```
docker compose up -d
```
> Penjelasan: Menyalakan Caddy kecil. Port 8082 dibuka untuk LAN; firewall Proxmox (Suplemen 7 Bab 51) hanya
mengizinkan docker-core menjangkaunya.  
```
docker exec sites caddy validate --config /etc/caddy/Caddyfile
```
> Penjelasan: Memeriksa sintaks. Hasil benar: Valid configuration.

## 40.3 Gerbang HTTPS di docker-core

**TERMINAL VM DOCKER-CORE** | VM docker-core (192.168.88.20), sebagai root

```
nano /opt/stacks/caddy/Caddyfile
```
> Penjelasan: Tambahkan blok di bawah ini di akhir berkas. Volume Caddy tidak perlu diubah.

**/opt/stacks/caddy/Caddyfile (tambahan)** | Tambahan

```
web.home.arpa {
 reverse_proxy 192.168.88.28:8082
}
```

**TERMINAL VM DOCKER-CORE** | VM docker-core, sebagai root

```
docker exec caddy caddy validate --config /etc/caddy/Caddyfile
```
> Penjelasan: Memeriksa sintaks seluruh Caddyfile.
```
docker exec caddy caddy reload --config /etc/caddy/Caddyfile
```
> Penjelasan: Memuat blok baru tanpa memutus layanan lain.
CATATAN  
Nama web.home.arpa sudah terjawab oleh rewrite \*.home.arpa di AdGuard (Suplemen 4 Bab 36.1) dan mengarah ke  
docker-core. Caddy meneruskan nama host asli ke VM web, sehingga Caddy kecil memilih folder yang benar. Bila  
halaman tidak muncul, lihat tabel masalah di halaman penutup.  

## 40.4 Sisi klien: Windows

1. Buka browser ke https://web.home.arpa. Halaman "Halo dari home server" harus tampil dengan gembok  
(setelah Suplemen 4 Bab 37).  
Mengunggah situs dari laptop (OpenSSH sudah ada di Windows 10 dan 11) langsung ke VM web:  

**POWERSHELL WINDOWS** | PowerShell (laptop), di folder situs Anda

```
scp -r .\* <USER>@192.168.88.28:/opt/stacks/web/sites/halo/
```
> Penjelasan: Menyalin semua isi folder saat ini ke folder situs di VM web. Ganti &lt;USER&gt;. Berkas lama dengan
nama sama akan tertimpa.  
TIPS  
Bila lebih suka antarmuka grafis, WinSCP memakai akun dan jalur yang sama. Berkas baru langsung disajikan; tidak  
perlu restart.  

## 40.5 Sisi klien: Android dan iPhone

1. Di rumah: buka https://web.home.arpa di Chrome (Android) atau Safari (iPhone). Di luar rumah nyalakan  
Tailscale lebih dulu.  
2. Gembok tanpa peringatan bergantung pada sertifikat akar (Suplemen 4 Bab 37.3 dan 37.4). Di iPhone jangan  
lupa mengaktifkan kepercayaan sertifikat.  
3. Opsional: Android Chrome &gt; Menu &gt; Tambahkan ke layar utama; iPhone Safari &gt; Bagikan &gt; Tambah ke  
Layar Utama agar situs punya ikon sendiri.  
CATATAN  
Mengedit berkas situs langsung dari HP tidak dibahas di sini; lakukan dari laptop. Editor berbasis web (code studio)  
ada di daftar rencana Anda untuk suplemen berikutnya.  

## 40.6 Menambah situs kedua

1. Di VM web: buat folder mkdir /opt/stacks/web/sites/blog dan isi dengan berkas.  
2. Di VM web: tambah blok http://blog.home.arpa { root \* /srv/sites/blog file_server } ke  
/opt/stacks/web/Caddyfile, lalu docker exec sites caddy reload --config /etc/caddy/Caddyfile.  
3. Di docker-core: tambah blok blog.home.arpa { reverse_proxy 192.168.88.28:8082 } ke Caddyfile gerbang  
dan muat ulang seperti 40.3.
