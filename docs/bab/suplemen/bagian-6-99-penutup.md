# Bagian 6. Vaultwarden, AFFiNE, dan Kalender Nextcloud: Uji, Masalah Umum, Lembar Pembaruan, Syarat Lulus Fase 6

Uji, Masalah Umum, dan Lembar Pembaruan  
Uji menyeluruh  
No Uji Hasil yang diharapkan  
1 tailscale status di VM vault; konsol admin Machines lab-vault hidup, kunci tidak kedaluwarsa  
2 Laptop (Tailscale): https://lab-vault.NAMA-TAILNET.ts.net Vault Bitwarden, gembok tanpa peringatan  
3 Buat akun, aktifkan TOTP, tutup pendaftaran Akun lain tidak bisa dibuat  
4 Android dan iPhone: login Bitwarden ke server sendiri Login berhasil, item tersinkron antar perangkat  
5 Android: Tailscale mati Mengisi kata sandi dari salinan lokal tetap bisa; sinkron  
tertunda  
6 Laptop: https://affine.home.arpa, akun admin, buat satu  
halaman  
Halaman tersimpan  
7 Aplikasi AFFiNE Windows, Android, iPhone tersambung Halaman uji muncul di semua perangkat (atau catat  
mana yang gagal)  
8 Nextcloud: login, ganti kata sandi admin, Overview tanpa  
peringatan penting  
Cron aktif; hanya peringatan ringan  
9 Acara dibuat di web; muncul di DAVx5/Android dan iPhone Sinkron dua arah: acara dari HP muncul di web  
10 Backup dibuat untuk tiga layanan dan disalin ke luar server Arsip ada di laptop atau disk luar  
Masalah dan solusi  
Gejala Penyebab Solusi  
Alamat .ts.net tidak terbuka dari  
HP  
Tailscale mati, atau kebijakan  
jaringan belum mengizinkan port 443  
Aktifkan Tailscale; periksa entri grants Bab 44.3;  
tailscale serve status di VM vault  
Serve: sertifikat belum tersedia HTTPS Certificates belum diaktifkan  
di konsol admin  
Aktifkan di halaman DNS konsol admin, ulangi  
tailscale serve  
Bitwarden: galat sertifikat di  
aplikasi  
Alamat diketik salah atau memakai  
nama lain (misalnya lab-docker lama)  
Samakan persis dengan DOMAIN di compose  
Vaultwarden menolak  
pendaftaran  
SIGNUPS_ALLOWED false (normal) Buat akun hanya saat true; atau undang lewat  
pengaturan yang Anda aktifkan sendiri  
AFFiNE: server tidak menyala Migrasi database gagal atau nama  
image salah  
docker compose logs affine_migration; bandingkan  
image dengan berkas resmi (46.1)  
AFFiNE: tautan atau login  
mengarah ke alamat salah  
AFFINE_SERVER_EXTERNAL_URL  
atau HTTPS tidak diatur  
Periksa .env lalu docker compose up -d  
Nextcloud: "Access through  
untrusted domain"  
Nama tidak ada di  
NEXTCLOUD_TRUSTED_DOMAINS  
Perbaiki compose; atau occ config:system:set  
trusted_domains 1 --value=nextcloud.home.arpa  
Nextcloud: loop pengalihan  
atau http di tautan  
OVERWRITEPROTOCOL atau proxy  
tepercaya salah  
Periksa compose (47.1) dan Caddyfile  
DAVx5 tidak menemukan  
kalender  
Kata sandi aplikasi salah atau  
.well-known belum dialihkan  
Buat ulang kata sandi aplikasi; pastikan dua baris  
redir ada di Caddyfile  
iPhone: "Tidak dapat  
memverifikasi identitas server"  
Sertifikat akar belum dipercaya Aktifkan di Pengaturan Kepercayaan Sertifikat  
(Suplemen 4 Bab 37.4)  
Lembar pembaruan  
Bab sebelumnya Perubahan Rujukan  
Suplemen 1, Bab 26.6 Kebijakan tailnet bertambah satu entri grants untuk autogroup:self  
pada tcp:443  
Bab 44.3  
Suplemen 1, Bab 26.3 VM vault (bukan VM Docker) menjadi perangkat tailnet kedua  
(lab-vault), bukan penerus rute  
Bab 44.3  
Suplemen 4, Bab 36.6 Caddyfile bertambah: affine dan nextcloud sebagai reverse_proxy  
ke IP:port VM masing-masing (Vaultwarden tidak lewat Caddy)  
Bab 46, 47  
Suplemen 7, Bab 48-51 Peta penempatan VM, templat VM 200, dan firewall Proxmox  
yang membatasi port 3010, 8080  
Suplemen 7  
Suplemen 3, Bab 32 Monitor Uptime Kuma baru untuk affine dan nextcloud (Ignore  
TLS error). Alamat pantau memakai IP:port VM  
(192.168.88.25:3010, 192.168.88.26:8080). Vaultwarden hanya  
terbuka lewat Tailscale; pantau dengan agen Beszel di VM vault;  
titik pemeriksaan sehat [BELUM PASTI]  
Uji menyeluruh  
Edisi 2, Bab 23 dan Suplemen 3  
Bab 34.3  
Backup baru: vaultwarden (tar data), affine (sql dan files),  
nextcloud (sql dan files). Wajib disalin ke luar server  
Bab 45.5, 46.4, 47.8  
Daftar hal yang belum dipastikan  
No Hal Cara memastikan  
1 Android Bitwarden dengan CA lokal (laporan gagal dari pengguna); Jalur  
1 dipilih untuk menghindarinya  
Tidak perlu diuji; Jalur 1 sudah  
menghindarinya  
2 Sintaks grants ip "tcp:443" dan autogroup:self; serve berjalan dengan  
--accept-dns=false  
Coba; gunakan bentuk acls lama bila  
ditolak  
3 Nama image AFFiNE (affine vs affine-graphql) dan tata letak compose  
resmi  
Bandingkan dengan berkas resmi (46.1)  
4 Alamat halaman admin AFFiNE, nama opsi pendaftaran, login email  
tanpa SMTP  
Lihat dokumentasi AFFiNE After Installation  
dan Email Notifications  
5 AFFiNE di Android dan iPhone menerima CA lokal; langkah menu  
aplikasi  
Uji; bila gagal pakai 46.5  
6 Nomor mayor Nextcloud terkini untuk NEXTCLOUD_TAG Cek Docker Hub nextcloud  
7 DAVx5 menerima CA lokal dan harga di Play Store; Thunderbird  
memakai penyimpanan sertifikat sendiri; kode kalender bawaan  
"personal"  
Uji di perangkat  
8 Perintah backup daring Vaultwarden dan titik pemeriksaan sehat Baca wiki Vaultwarden; pakai cara stop dan  
tar bila ragu  
9 Kebutuhan RAM gabungan Ukur dengan Beszel  
Syarat lulus Fase 6  
No Poin Ya / Tidak  
1 Vaultwarden hanya lewat Tailscale Serve; pendaftaran ditutup; TOTP aktif  
2 Bitwarden tersinkron di Windows, Android, iPhone  
3 AFFiNE berjalan; aplikasi desktop dan HP tersambung (atau Jalur 1 diterapkan)  
4 Nextcloud berjalan dengan Cron; kalender tersinkron ke Android dan iPhone  
5 Kata sandi aplikasi dipakai di perangkat, bukan kata sandi akun  
6 Backup tiga layanan sudah disalin ke luar server  
7 Funnel tidak pernah dijalankan (tailscale funnel status kosong)  
Berikutnya (Suplemen 7): Proxmox Backup Server dan audit keamanan keseluruhan. Backup kata sandi dan  
kalender di suplemen ini akan dipindahkan ke jadwal backup otomatis di sana.
