# Bab 31. Fondasi Docker Compose yang Rapi dan Aman

PENEMPATAN - GABUNG - berlaku di setiap VM Docker  
Tempat: Struktur /opt/stacks dan pola compose berlaku di setiap VM Docker. Jaringan Docker proxy hanya dibuat di  
VM 201 docker-core (192.168.88.20).  
Alasan: Jaringan Docker tidak melintasi VM. Layanan di VM lain dijangkau Caddy lewat alamat IP:port, bukan nama  
container (Suplemen 7 Bab 48.3).  
Semua aplikasi di suplemen berikutnya dipasang dengan cara yang sama. Bab singkat ini menetapkan cara itu  
sekali, sehingga tiap bab aplikasi cukup menyebut isi berkasnya.  

## 31.1 Struktur folder

Setiap aplikasi punya satu folder berisi berkas compose.yaml, berkas .env bila ada rahasia, dan folder data.  
Seluruh folder inilah yang dicadangkan.  

**Struktur** | Susunan folder di VM Debian

```
/opt/stacks/
 uptime-kuma/
 compose.yaml
 data/
 gotify/
 compose.yaml
 .env
 data/
 beszel/
 compose.yaml
 beszel_data/
```

## 31.2 Aturan yang dipakai di buku ini

Aturan Alasan  
Satu folder per aplikasi di /opt/stacks Mudah dicari, dicadangkan, dan dihapus  
restart: unless-stopped Aplikasi menyala kembali setelah reboot, tetapi tidak bila sengaja  
dimatikan  
Versi image: tag mayor bila ada (misalnya :2); latest  
hanya untuk layanan monitoring ringan  
Menghindari lompatan versi besar yang merusak; backup dulu  
sebelum update  
Rahasia (password) di berkas .env dengan izin 600 Tidak tercecer di compose.yaml yang mungkin dibagikan  
Data di folder lokal (bind mount) bukan volume  
tersembunyi  
Folder bisa dilihat dan dicadangkan langsung  
Port dicatat di tabel alokasi (31.3) Mencegah bentrok antar aplikasi  

## 31.3 Alokasi port dan catatan firewall

Layanan Port host Alamat akses  
Uptime Kuma 3001 http://192.168.88.20:3001  
Gotify 8070 (di container 80) http://192.168.88.20:8070  
Beszel hub 8090 http://192.168.88.20:8090  
Beszel agent (mesin yang dipantau) 45876 (hanya bila hub yang  
menghubungi agen)  
Tidak dibuka bila memakai token universal  
(Bab 33)  
PERINGATAN - Docker dan UFW  
Port yang dipublikasikan Docker (kolom port host di atas) melewati UFW (Suplemen 1 Bab 25.6) dan terbuka dari  
seluruh LAN. Ini dapat diterima selama semua perangkat di LAN tepercaya dan tidak ada port forwarding. Nanti  
reverse proxy (suplemen berikutnya) menjadi pintu tunggal.  

## 31.4 Memeriksa Docker dan menyiapkan folder

**TERMINAL VM DEBIAN** | Sebagai root (setelah su -)

```
docker --version
```
> Penjelasan: Memastikan Docker terpasang.
```
docker compose version
```
> Penjelasan: Memastikan plugin Compose terpasang (perintahnya "docker compose", dengan spasi).
```
mkdir -p /opt/stacks
```
> Penjelasan: Membuat folder induk untuk semua aplikasi.
```
ss -tlnp | grep -E ":(3001|8070|8090)\b" || echo port-bebas
```
> Penjelasan: Memastikan port 3001, 8070, dan 8090 belum dipakai. Hasil port-bebas berarti aman.

## 31.5 Perintah rutin (tempel di catatan Anda)

Tujuan Perintah (dijalankan di folder aplikasi)  
Menyalakan atau menerapkan perubahan docker compose up -d  
Melihat status docker compose ps  
Melihat log docker compose logs -f --tail=50  
Memperbarui image docker compose pull && docker compose up -d  
Mematikan tanpa menghapus data docker compose stop  
Menghapus kontainer (data di folder tetap ada) docker compose down
