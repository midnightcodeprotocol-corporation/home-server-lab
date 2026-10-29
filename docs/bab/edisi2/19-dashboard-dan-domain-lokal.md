# Bab 19. Dashboard Pintasan dan Nama Domain Lokal

Dua hal membuat pengalaman memakai server jauh lebih nyaman: dashboard (satu halaman berisi  
tombol ke semua layanan, termasuk MikroTik dan TP-Link) dan nama domain lokal (mikrotik.lan,  
proxmox.lan) sehingga tidak perlu menghafal IP dan port.  
Home Server Lab 17 Okt 2026 | CPU 12% RAM 41%  
Jaringan  
MikroTik  
klik untuk membuka  
TP-Link AP  
klik untuk membuka  
TP-Link penerima  
klik untuk membuka  
AdGuard  
klik untuk membuka  
Server  
Proxmox  
klik untuk membuka  
Portainer  
klik untuk membuka  
Forgejo  
klik untuk membuka  
Nextcloud  
klik untuk membuka  
Rumah  
Home Assistant  
klik untuk membuka  
Dashboard  
klik untuk membuka  
k3s  
klik untuk membuka  
Tailscale  
klik untuk membuka  
Gambar 19.1 - Contoh tampilan dashboard Homepage (ilustrasi). Setiap kartu adalah pintasan yang membuka halaman  
layanan.  

## 19.1 Memasang dashboard Homepage

Homepage (gethomepage.dev) ringan, memakai berkas YAML, dan menampilkan status layanan.  
Dijalankan di Docker pada VM Debian 13 dan dibuka di http://home.lan.  

**TERMINAL (login sebagai root)** | VM Debian 13 (root)

```
mkdir -p /opt/stacks/homepage/config && cd /opt/stacks/homepage
```
> Penjelasan: Membuat folder aplikasi dan folder konfigurasi.
```
nano compose.yaml
```
> Penjelasan: Berkas compose (isi di bawah).

**BERKAS: /opt/stacks/homepage/compose.yaml** | Pin versi image pada pemakaian jangka panjang

```
services:
  homepage:
    image: ghcr.io/gethomepage/homepage:latest
    container_name: homepage
    restart: unless-stopped
    ports:
      - "80:3000"
    environment:
      - HOMEPAGE_ALLOWED_HOSTS=192.168.88.20,home.lan
volumes:
  - ./config:/app/config
```

Baris Arti  
80:3000 Dashboard dibuka di port 80 (http://home.lan tanpa mengetik port).  
HOMEPAGE_ALLOWED_HOSTS Nama/alamat yang boleh dipakai membuka dashboard. Wajib agar tidak ditolak.  
./config:/app/config Folder berkas konfigurasi YAML di host.  

## 19.2 Berkas konfigurasi

Buat empat berkas di /opt/stacks/homepage/config. Berkas services.yaml berisi semua pintasan:  
jaringan (MikroTik, TP-Link), server, dan aplikasi.  
BERKAS: /opt/stacks/homepage/config/settings.yaml  
 1 title: Home Server Lab  
 2 theme: dark  
 3 color: slate  
 4 headerStyle: boxed  
 5 layout:  
 6 Jaringan:  
 7 style: row  
 8 columns: 4  
 9 Server:  
10 style: row  
11 columns: 4  
12 Aplikasi:  
13 style: row  
14 columns: 4  

**BERKAS: /opt/stacks/homepage/config/widgets.yaml** | Widget di bagian atas: penggunaan sumber daya VM dan jam

```
- resources:
cpu: true
memory: true
disk: /
- datetime:
text_size: xl
format:
timeStyle: short
dateStyle: medium
```

**BERKAS: /opt/stacks/homepage/config/services.yaml** | Bagian 1 dari services.yaml (grup Jaringan)

```
- Jaringan:
- MikroTik:
href: http://192.168.88.1
description: Router utama (WebFig)
ping: 192.168.88.1
- TP-Link penerima:
href: http://192.168.0.1
description: TL-WR840N mode WISP
- TP-Link AP:
href: http://192.168.88.2
description: TL-WR820N Access Point
ping: 192.168.88.2
- AdGuard utama:
href: http://192.168.88.253
description: DNS pemblokir iklan (STB)
ping: 192.168.88.253
widget:
type: adguard
url: http://192.168.88.253
username: admin
password: GANTI
```

**BERKAS: /opt/stacks/homepage/config/services.yaml (lanjutan)** | Bagian 2: lanjutkan di berkas yang sama (grup Server dan Aplikasi)

```
- Server:
- Proxmox:
href: https://192.168.88.10:8006
description: Hypervisor
ping: 192.168.88.10
- Portainer:
href: https://192.168.88.20:9443
description: Manajemen Docker
- Forgejo:
href: http://192.168.88.20:3000
description: Git pribadi
- AdGuard kedua:
href: http://192.168.88.11
description: DNS cadangan (LXC 101)
ping: 192.168.88.11
- Aplikasi:
- Nextcloud:
href: http://192.168.88.20:8080
description: Cloud pribadi
- Home Assistant:
href: http://192.168.88.21:8123
description: Otomasi rumah
ping: 192.168.88.21
- Folder jaringan:
href: file://192.168.88.12/share
description: Samba (buka dari Explorer)
- Tailscale:
href: https://login.tailscale.com/admin/machines
description: Konsol admin
```

Kunci Arti  
href Alamat yang dibuka saat kartu diklik. Ganti dengan nama .lan setelah 19.4.  
description Keterangan di bawah nama.  
ping Menandai status hidup/mati (titik hijau/merah). Dipakai untuk perangkat yang tidak punya web,  
dan untuk situs HTTPS bersertifikat buatan sendiri.  
widget Menampilkan statistik langsung dari aplikasi (contoh AdGuard: jumlah kueri dan iklan terblokir).  

**TERMINAL (login sebagai root)** | Folder /opt/stacks/homepage (root)

```
nano config/settings.yaml
```
> Penjelasan: Membuat berkas pengaturan. Tempel isinya. Ulangi untuk widgets.yaml dan services.yaml
(gabungkan dua bagiannya).  
```
docker compose up -d
```
> Penjelasan: Menjalankan dashboard.
```
docker compose logs -f
```
> Penjelasan: Memeriksa pesan error konfigurasi YAML (spasi harus tepat).
Buka http://192.168.88.20. Konfigurasi dibaca ulang otomatis saat berkas diubah; cukup muat ulang  
halaman.  
PERINGATAN  
YAML sensitif terhadap spasi (indentasi). Gunakan spasi, bukan Tab, dan pertahankan lekukan seperti contoh.  
TIPS  
Alternatif dashboard: Homarr (antarmuka drag-and-drop), Dashy, atau Heimdall. Pintasan MikroTik/TP-Link  
cukup berupa kartu berisi alamat webnya.  

## 19.3 MikroTik dan WinBox

WinBox adalah aplikasi desktop, bukan halaman web, jadi tidak bisa dibuka dari dashboard. Untuk web,  
MikroTik menyediakan WebFig (http://192.168.88.1) yang dibuat dari layanan www.  

**TERMINAL MIKROTIK** | WinBox &gt; New Terminal

```
/ip service print
```
> Penjelasan: Memeriksa layanan www (port 80) aktif dan tidak dimatikan.

## 19.4 Nama domain lokal dengan AdGuard (DNS rewrites)

Fitur DNS rewrites AdGuard menjawab nama lokal dengan alamat IP yang Anda tentukan.  
AdGuard Home - Filters &gt; DNS rewrites &gt; Add DNS rewrite  
1 Domain mikrotik.lan  
2 Enter the IP address or domain name 192.168.88.1  
Cancel Save  
Gambar 19.2 - Ilustrasi penambahan DNS rewrite. (1) Nama. (2) Alamat IP tujuan.  
1. Buka AdGuard &gt; Filters &gt; DNS rewrites &gt; Add DNS rewrite.  
2. Isi Domain dan IP address sesuai tabel, lalu Save.  
3. Ulangi untuk setiap nama. Di AdGuard kedua, buat rewrites yang sama (atau biarkan  
adguardhome-sync menyalinnya).  
> Penjelasan: Agar nama tetap bekerja saat salah satu server mati.
4. Tes: nslookup mikrotik.lan 192.168.88.253, lalu buka http://mikrotik.lan.  
> Penjelasan: Harus menjawab 192.168.88.1.
Domain IP Fungsi  
mikrotik.lan 192.168.88.1 MikroTik (WebFig)  
ap.lan 192.168.88.2 TP-Link AP  
proxmox.lan 192.168.88.10 Proxmox (buka https://proxmox.lan:8006)  
adguard.lan 192.168.88.253 AdGuard utama  
adguard2.lan 192.168.88.11 AdGuard kedua  
home.lan 192.168.88.20 Dashboard  
git.lan 192.168.88.20 Forgejo (http://git.lan:3000)  
nextcloud.lan 192.168.88.20 Nextcloud (http://nextcloud.lan:8080)  
portainer.lan 192.168.88.20 Portainer (https://portainer.lan:9443)  
ha.lan 192.168.88.21 Home Assistant (http://ha.lan:8123)  
files.lan 192.168.88.12 Samba  
TIPS  
Gunakan akhiran .lan atau .home.arpa. Hindari .local karena bentrok dengan mDNS di sebagian  
perangkat. Setelah nama dibuat, ganti href di services.yaml dengan nama .lan.  
CATATAN  
Router MikroTik juga bisa menjawab nama statis (/ip dns static add name=mikrotik.lan  
address=192.168.88.1) untuk keperluan router sendiri, tetapi klien memakai AdGuard sehingga rewrites  
AdGuard yang menentukan.  
KASUS NYATA - Dashboard menolak dibuka: Host validation failed  
Gejala: Halaman Homepage menampilkan error tentang host.  
Penyebab: Nama/alamat yang dipakai tidak ada di HOMEPAGE_ALLOWED_HOSTS.  
Solusi: Tambahkan alamat dan namanya (misalnya 192.168.88.20,home.lan) pada compose.yaml, lalu  
docker compose up -d.
