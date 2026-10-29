# Bab 39. Hosting Web di Rumah: Konsep dan Keputusan

PENEMPATAN - TIDAK ADA GUEST  
Tempat: Bab konsep. Penempatan: situs statis dan WordPress di VM 209 web, n8n di VM 208, situs publik di VM 210.  

## 39.1 Dua jalur: privat dan publik

Sampai Suplemen 4 semua layanan hanya bisa dibuka dari jaringan rumah atau lewat Tailscale. Itu jalur privat  
dan tetap menjadi jalur utama buku ini. Jalur publik berarti siapa pun di internet bisa membuka alamat Anda.  
Jalur A - privat (bab 40, 41, 42)  
Jalur B - publik, opsional (bab 43, hanya situs statis)  
HP / Laptop  
Tailscale / Wi-Fi  
AdGuard  
nama \*.home.arpa  
Caddy :443  
HTTPS CA lokal  
Layanan  
WordPress, n8n, situs  
Pengunjung  
internet  
Cloudflare  
HTTPS publik  
cloudflared  
koneksi KELUAR dari VM  
web-public  
situs statis saja  
Gambar 39.1 - Jalur privat (Tailscale + Caddy) dan jalur publik opsional (Cloudflare Tunnel).  
Jalur A: privat Jalur B: publik (opsional)  
Siapa bisa membuka Perangkat Anda (rumah atau Tailscale) Siapa saja di internet  
Sertifikat CA lokal Caddy (pasang akar di perangkat) Sertifikat publik dari Cloudflare, tanpa pemasangan  
Risiko Rendah Ada: serangan otomatis, beban, kesalahan  
konfigurasi  
Biaya Gratis Perlu domain milik sendiri (biaya tahunan); Tunnel  
sendiri gratis [BELUM PASTI] cek halaman harga  
Cloudflare  
Cocok untuk WordPress, n8n, alat pribadi Situs statis kecil (portofolio, halaman info)  

## 39.2 Mengapa tunnel, bukan port forwarding

Internet Anda melewati beberapa lapis jaringan: router IndiHome, TL-WR840N dalam mode WISP, lalu MikroTik.  
Membuka port ke dalam berarti menembus setiap lapis (dan router IndiHome mungkin tidak bisa Anda atur).  
Alamat IP publik IndiHome juga bisa berubah atau berbagi [BELUM PASTI]. Cloudflare Tunnel membalik arah:  
program cloudflared di VM membuat koneksi keluar ke Cloudflare, sehingga tidak ada port yang dibuka ke  
dalam.  
KEAMANAN  
Tunnel menghindari port forwarding, tetapi tidak membuat aplikasi yang Anda publikasikan menjadi aman.  
Karena itu hanya situs statis (tanpa login, tanpa database) yang dipublikasikan di buku ini.  

## 39.3 Keputusan: apa dipasang di mana

Layanan Alamat Guest Proxmox Jalur Alasan  
Situs statis (privat) web.home.arpa VM 209 web (.28) A Hanya berkas HTML;  
permukaan serangan kecil  
WordPress wp.home.arpa VM 209 web (.28) A saja Halaman login, plugin, dan  
pembaruan rutin sering jadi  
sasaran serangan  
n8n n8n.home.arpa VM 208 n8n (.27) A saja Menyimpan kredensial ke  
layanan lain; kebocoran  
berdampak besar  
Situs statis (publik) domain Anda (Bab 43) VM 210 web-public (.29) B opsional Satu-satunya yang menghadap  
internet; VM paling terisolasi  
Setiap layanan berjalan di VM sendiri atau VM web bersama sesuai Peta Penempatan (Suplemen 7 Bab 48).  
Caddy di docker-core hanya meneruskan permintaan ke alamat IP:port VM tujuan.  
PERINGATAN  
Alamat WordPress tersimpan di databasenya. Bila Anda memasang dengan wp.home.arpa lalu pindah ke domain  
publik, alamat harus diganti (Pengaturan atau alat WP-CLI). Putuskan alamat akhir sebelum Bab 41.  

## 39.4 Sumber daya dan persiapan

WordPress dengan MariaDB dan n8n dengan Postgres masing-masing menjalankan dua container. Sebagai  
gambaran kasar, tiap pasangan memakai beberapa ratus MB RAM [BELUM PASTI] (perkiraan, bukan angka  
resmi), ditambah RAM sistem operasi VM-nya sendiri. Periksa juga RAM total host Proxmox (free -h di shell  
host) karena kini ada tiga VM tambahan. Pantau di Beszel (Suplemen 3) setelah dipasang dan sesuaikan RAM  
VM di Proxmox bila perlu.  

**TERMINAL VM DOCKER-CORE** | VM docker-core (192.168.88.20), sebagai root (setelah su -)

```
free -h && df -h /
```
> Penjelasan: Melihat RAM dan ruang disk VM ini (lakukan juga di host Proxmox).
```
tar czf /root/stacks-sebelum-s5.tgz /opt/stacks
```
> Penjelasan: Backup seluruh /opt/stacks sebelum mengubah Caddy (berkas ini berisi kunci CA, simpan aman,
jangan dibagikan).  
```
docker ps --format "table {{.Names}}\t{{.Status}}"
```
> Penjelasan: Memastikan caddy, gotify, uptime-kuma berjalan sebelum mulai.
