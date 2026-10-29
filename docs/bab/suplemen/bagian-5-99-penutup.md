# Bagian 5. Hosting Web dan n8n: Uji, Masalah Umum, Lembar Pembaruan, Syarat Lulus Fase 5

Uji, Masalah Umum, dan Lembar Pembaruan  
Uji menyeluruh  
No Uji Hasil yang diharapkan  
1 Caddy validate setelah semua blok ditambah Valid configuration  
2 Laptop: https://web.home.arpa Halaman Halo, gembok tanpa peringatan  
3 Laptop: https://wp.home.arpa, selesaikan pemasangan Dasbor WordPress; alamat Site dan WordPress  
berawalan https  
4 Laptop: https://n8n.home.arpa, buat akun pemilik Editor n8n terbuka  
5 Webhook uji ke /webhook-test/uji Notifikasi tiba di Gotify di HP  
6 Aktifkan workflow, panggil /webhook/uji dengan autentikasi Notifikasi tiba; tanpa kredensial ditolak  
7 HP Android dan iPhone: tiga alamat privat (WiFi rumah) Terbuka dengan gembok  
8 HP, data seluler, Tailscale aktif Tiga alamat privat tetap terbuka  
9 Opsional: HP data seluler, Tailscale mati, alamat publik Situs statis publik tampil; alamat home.arpa tidak  
terbuka  
10 Uptime Kuma: tambah monitor untuk web, wp, dan n8n Semua hijau  
Masalah dan solusi  
Gejala Penyebab Solusi  
502 Bad Gateway pada web,  
wp, atau n8n  
Container belum siap, port tidak  
dibuka, atau firewall Proxmox  
menolak docker-core  
Di VM tujuan: docker compose ps; ss -tlnp. Dari  
docker-core: timeout 3 bash -c '&lt;/dev/tcp/IP-VM/PORT' &&  
echo terbuka  
WordPress: "Error  
establishing a database  
connection"  
MariaDB belum selesai inisialisasi  
atau kata sandi .env berubah  
setelah database dibuat  
docker compose logs wp-db; bila kata sandi diubah  
sesudah inisialisasi, hapus folder db hanya jika belum ada  
data penting  
WordPress: loop pengalihan  
atau halaman tanpa gaya  
WordPress tidak mengenali  
HTTPS di belakang proxy  
Ulangi pemeriksaan grep di 41.2; periksa Site Address  
berawalan https; bila grep kosong, tambahkan  
penanganan X-Forwarded-Proto lewat  
WORDPRESS_CONFIG_EXTRA mengikuti dokumentasi  
image  
n8n: error izin pada  
/home/node/.n8n  
Folder data bukan milik uid 1000 chown -R 1000:1000 /opt/stacks/n8n/data  
n8n: cookie aman / tidak bisa  
login lewat IP  
n8n menuntut HTTPS untuk  
cookie  
Selalu buka lewat https://n8n.home.arpa, bukan IP dan  
port  
n8n: alamat webhook tampil  
localhost  
WEBHOOK_URL salah atau  
tanpa garis miring akhir  
Perbaiki di compose, docker compose up -d  
n8n: webhook produksi 404 Workflow belum Active, atau  
memakai alamat webhook-test  
Aktifkan workflow dan pakai /webhook/...  
Postgres: database kosong  
setelah ganti versi  
PGDATA terhapus atau lompat  
versi mayor  
Pertahankan PGDATA; backup dengan pg_dump sebelum  
naik versi mayor  
Tunnel: halaman 502 atau  
1033 di alamat publik  
cloudflared tidak terhubung atau  
Service URL salah  
docker compose logs cloudflared; pastikan Service URL  
http://web-public:80 dan kedua container di jaringan  
publicweb  
Lembar pembaruan  
Bab sebelumnya Perubahan Rujukan  
Suplemen 4, Bab 36.3 Tidak ada perubahan compose Caddy. Caddy tidak lagi  
menyajikan berkas; hanya meneruskan  
Bab 40.3  
Suplemen 4, Bab 36.6 Caddyfile bertambah: web, wp, n8n sebagai reverse_proxy ke  
IP:port VM masing-masing  
Bab 40, 41, 42  
Suplemen 7, Bab 48-51 Peta penempatan VM, templat VM 9100, dan firewall Proxmox  
yang membatasi port 8081, 8082, 5678  
Suplemen 7  
Suplemen 3, Bab 32 Tambah monitor Uptime Kuma untuk tiga alamat baru (Ignore  
TLS error)  
Uji no. 10  
Suplemen 1, Bab 25 Jalur publik tidak membuka port masuk; firewall tidak berubah.  
Jaringan Docker publicweb dipisah  
Bab 43  
Edisi 2, Bab 19 dan Suplemen 3  
Bab 34.2  
Tambah kartu dashboard Homepage untuk situs, WordPress, n8n Bab 40-42  
Edisi 2, Bab 23 dan Suplemen 3  
Bab 34.3  
Backup tambahan: /opt/stacks/web, wordpress (html dan dump  
SQL), n8n (dump SQL; kunci enkripsi disimpan terpisah),  
tunnel-web (tanpa .env di tempat bersama)  
Bab 41.6, 42.8  
Daftar hal yang belum dipastikan  
No Hal Cara memastikan  
1 Tag wordpress:6-apache dan mariadb:11 ada di Docker Hub Cek halaman tag; bila tidak ada pilih tag apache  
terdekat  
2 Nomor versi n8n stabil terkini (contoh 2.29.10 dari sumber pihak  
ketiga)  
Ambil dari halaman rilis n8n-io/n8n  
3 Perkiraan RAM WordPress dan n8n Ukur dengan Beszel  
4 Aplikasi WordPress, HTTP Shortcuts, dan Pintasan menerima CA  
lokal  
Uji di perangkat; bila ditolak pakai browser  
5 Letak menu dasbor Cloudflare (Tunnels) dan batasan quick tunnel Ikuti halaman Setup di  
developers.cloudflare.com/tunnel  
6 Biaya domain dan apakah Tunnel gratis untuk kebutuhan Anda Cek halaman harga Cloudflare dan pendaftar  
domain  
7 Pembatasan akses (Cloudflare Access) dan webhook sebagian jalur Tidak dikaji; baca dokumentasi sebelum  
mencoba  
8 Alamat IP publik IndiHome dinamis atau berbagi Tidak berpengaruh pada tunnel; hanya relevan  
bila port forwarding  
Syarat lulus Fase 5  
No Poin Ya / Tidak  
1 web.home.arpa, wp.home.arpa, n8n.home.arpa terbuka dengan HTTPS di laptop dan HP  
2 WordPress terpasang, pembaruan diterapkan, akun bukan bernama admin  
3 n8n berjalan di Postgres; webhook uji mengirim notifikasi ke Gotify  
4 Webhook produksi memakai autentikasi  
5 Dump SQL WordPress dan n8n serta kunci enkripsi n8n tersimpan di luar server  
6 Bila bab 43 dikerjakan: situs publik tampil dari data seluler, layanan privat tidak terbuka  
Berikutnya (Suplemen 6): AFFiNE, kalender Nextcloud, dan Vaultwarden, masing-masing dengan sisi klien  
Windows, Android, dan iPhone. Vaultwarden dan AFFiNE sangat bergantung pada HTTPS yang benar; hasil uji  
Suplemen 4 akan menentukan apakah jalur CA lokal cukup.
