# Bab 35. Reverse Proxy Lokal dan Sertifikat SSL: Konsep

PENEMPATAN - TIDAK ADA GUEST  
Tempat: Bab konsep. Caddy dipasang di Bab 36.  

## 35.1 Cara kerja

Perangkat Anda bertanya ke AdGuard: "di mana kuma.home.arpa?". AdGuard menjawab 192.168.88.20, alamat  
VM Debian. Di sana Caddy menerima koneksi HTTPS di port 443, menunjukkan sertifikat untuk nama itu, lalu  
meneruskan ke layanan yang sesuai di dalam Docker.  
HP / Laptop  
ketik kuma.home.arpa  
AdGuard (DNS)  
\*.home.arpa = 192.168.88.20  
Caddy  
port 443, sertifikat CA lokal  
Uptime Kuma  
Beszel  
Gotify  
Proxmox  
AdGuard  
HTTPS  
Gambar 35.1 - Nama diterjemahkan AdGuard, Caddy memberi HTTPS dan meneruskan ke layanan.  

## 35.2 Tiga jalur untuk sertifikat

Sertifikat HTTPS harus dipercaya oleh perangkat Anda. Untuk alamat yang hanya ada di jaringan rumah, ada tiga  
cara:  
Jalur Cara Kelebihan Kekurangan  
1. CA lokal Caddy  
(dipakai di Bab 36 dan 37)  
Caddy membuat otoritas  
sertifikat sendiri; sertifikat  
akarnya dipasang di tiap  
perangkat  
Gratis, tanpa domain, tanpa  
akun luar, sertifikat otomatis  
diperbarui  
Sertifikat akar harus dipasang di  
setiap perangkat; sebagian  
aplikasi HP menolaknya  
2. Domain asli + DNS-01  
(Bab 38, opsional)  
Membeli domain; Caddy  
membuktikan kepemilikan lewat  
catatan DNS di Cloudflare  
Dipercaya semua perangkat  
dan aplikasi tanpa  
memasang apa pun  
Biaya domain tahunan, perlu  
akun Cloudflare dan token API  
3. HTTPS bawaan  
Tailscale  
Sertifikat untuk nama \*.ts.net  
dari Tailscale  
Tanpa domain, tepercaya Satu nama per perangkat  
sehingga kurang cocok untuk  
banyak layanan; nama tampil di  
catatan sertifikat publik  
CATATAN  
Pilihan buku ini: Jalur 1 dikerjakan penuh karena tidak butuh biaya. Jalur 2 disediakan di Bab 38 bila nanti Anda  
membeli domain. Keduanya dapat hidup berdampingan di Caddy yang sama.  
PERINGATAN  
Batasan Android yang perlu Anda tahu: Chrome di Android mempercayai sertifikat yang Anda pasang, tetapi sejak  
Android 7 banyak aplikasi hanya mempercayai sertifikat bawaan sistem. Aplikasi seperti Gotify, DAVx5, atau  
Bitwarden bisa menolak CA buatan sendiri, atau punya pengaturan sertifikat sendiri. Karena itu Gotify tetap dibiarkan  
terbuka lewat IP dan port (Bab 36.5), dan Jalur 2 menjadi jalan keluar untuk aplikasi lain.  

## 35.3 Memilih nama domain lokal

Edisi 2 memakai lab.local (misalnya pve.lab.local). Akhiran .local dicadangkan untuk mDNS (penemuan nama  
otomatis), sehingga sebagian perangkat, terutama iPhone dan macOS, bisa lambat atau gagal menanyakannya  
ke DNS biasa. Standar yang disiapkan khusus untuk jaringan rumah adalah home.arpa. Layanan baru memakai  
home.arpa; pve.lab.local lama tetap berfungsi seperti sebelumnya.  
Layanan Nama baru Tujuan di belakang Caddy  
Uptime Kuma kuma.home.arpa container uptime-kuma, port 3001  
Beszel beszel.home.arpa container beszel, port 8090  
Gotify (web) gotify.home.arpa container gotify, port 80  
Proxmox proxmox.home.arpa https://192.168.88.10:8006 (sertifikat Proxmox diabaikan)  
Portainer portainer.home.arpa https://192.168.88.20:9443 (sertifikat diabaikan)  
AdGuard adguard.home.arpa http://192.168.88.253:80
