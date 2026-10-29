# Bagian 9. SSO dengan Pocket ID dan Immich: Uji, Masalah Umum, Lembar Pembaruan, Syarat Lulus Fase 9

Uji, Masalah Umum, dan Lembar Pembaruan  
Uji menyeluruh  
No Uji Hasil yang diharapkan  
1 tailscale serve status di VM sso Rute 443 menuju 1411  
2 Laptop: https://lab-sso.NAMA-TAILNET.ts.net Halaman Pocket ID dengan gembok tanpa peringatan  
3 Masuk dengan passkey di laptop dan HP Berhasil tanpa kata sandi  
4 docker compose ps di VM immich Semua layanan running atau healthy  
5 Laptop: https://lab-immich.NAMA-TAILNET.ts.net Halaman Immich dengan gembok tanpa peringatan  
6 Immich: masuk lewat tombol SSO Masuk setelah passkey Pocket ID  
7 Unggah beberapa foto dari HP Muncul di Immich dan terhitung di /srv/foto/library  
8 Dari laptop: Test-NetConnection 192.168.88.33 -Port 2283 False (tidak terbuka di LAN)  
9 Dari laptop: Test-NetConnection 192.168.88.32 -Port 1411 False (tidak terbuka di LAN)  
10 Job backup PBS untuk VM 213 dan 214 TASK OK; backup 214 memuat disk foto  
11 /root/profil.sh harian, lalu foto VM berganti sesuai tabel 56.2 dan free -m tetap lega  
Masalah dan solusi  
Gejala Penyebab Solusi  
Pocket ID tidak mau mulai ENCRYPTION_KEY kosong atau  
terlalu pendek  
Pastikan baris ENCRYPTION_KEY ada di .env  
dan dibuat dengan openssl rand -base64 32  
Passkey tidak bisa didaftarkan Alamat bukan HTTPS atau nama  
tidak sama dengan APP_URL  
Buka lewat alamat .ts.net persis seperti  
APP_URL; periksa tailscale serve status  
Semua passkey hilang HP rusak atau hilang Buat token akses satu kali dari server (Bab 54.5)  
dan daftarkan passkey baru  
Immich tidak bisa menghubungi  
penyedia SSO  
Nama lab-sso tidak terjawab di VM,  
atau alamat issuer berbeda  
Periksa extra_hosts di 55.3 dan alamat Tailscale  
VM sso; issuer harus sama dengan APP_URL  
Aplikasi HP menolak tombol SSO Callback aplikasi tidak terdaftar Tambahkan app.immich:///oauth-callback atau  
pakai Mobile Redirect URI Override (55.6)  
Immich lambat atau terhenti di VM  
4 GB  
RAM kurang untuk machine learning Matikan machine learning (55.5) atau naikkan  
RAM VM  
Cadangan foto HP berhenti Tailscale mati, baterai membatasi  
aplikasi, atau iOS membatasi tugas  
latar belakang  
Aktifkan Tailscale terus-menerus; atur baterai;  
buka aplikasi sebentar sambil mengisi daya  
Setelah pembaruan Immich port  
terbuka di LAN  
Berkas compose baru menimpa  
pengaturan port  
Ulangi sed di 55.3 dan periksa grep 2283  
VM tidak menyala setelah ganti  
profil  
RAM host tidak cukup free -m; matikan VM lain; periksa daftar di 56.2  
PBS mati saat backup berjalan Pergantian profil pukul 06:30 terlalu  
dini  
Atur ulang jam cron setelah memantau durasi  
backup (56.5)  
Lembar pembaruan  
Dokumen Perubahan Rujukan  
Suplemen 7, Bab 48 Peta guest bertambah VM 213 sso dan 214 immich; tabel RAM  
menjadi 22.272 MB (terpisah penuh) dan 19.200 MB (mode  
hemat)  
Bab 48.3, 48.6  
Suplemen 7, Bab 50.10 Job backup mencakup VM 213 dan 214 (disk foto ikut) Bab 54.7, 55.8  
Suplemen 7, Bab 51 Aturan firewall untuk VM 213 dan 214 Bab 54.7, 55.8  
Suplemen 7, Bab 52 Laporan audit bertambah baris VM 204, 213, dan 214 Bab 52.7  
Daftar hal yang belum dipastikan  
No Hal Cara memastikan  
1 Halaman penyiapan awal Pocket ID (/setup) dan letak menu pengguna  
dan klien OIDC  
Lihat antarmuka dan dokumentasi Pocket  
ID  
2 Perintah token akses satu kali untuk versi Pocket ID Anda Dokumentasi Pocket ID; docker compose  
exec pocket-id /app/pocket-id --help  
3 Pocket ID menerima callback app.immich:///oauth-callback; bentuk Issuer  
URL yang diminta Immich  
Uji di 55.6; pakai alternatif mobile-redirect  
bila ditolak  
4 extra_hosts ke alamat Tailscale VM sso dari dalam container Uji masuk lewat SSO (55.6); alternatif  
MagicDNS  
5 Jalur Tailscale antar-VM saat firewall Proxmox aktif (langsung atau lewat  
relai DERP)  
tailscale status di VM immich  
6 Backup bawaan Immich hanya database atau lebih Dokumentasi Immich bagian backup and  
restore  
7 Nomor versi tetap Immich dan Pocket ID untuk dipasang Halaman rilis masing-masing di GitHub  
8 Kebutuhan RAM dan CPU sebenarnya (Immich saat impor, Pocket ID,  
host)  
Ukur dengan Beszel; sesuaikan tabel 56.2  
9 Perilaku cadangan latar belakang di Android dan iOS Uji di perangkat Anda  
10 Sumber aplikasi Immich di Android (toko aplikasi atau halaman rilis) Dokumentasi Immich bagian aplikasi HP  
11 Batas ZFS ARC pada instalasi Anda cat /etc/modprobe.d/zfs.conf dan  
zfs_arc_max (56.1)  
Syarat lulus  
No Poin Ya / Tidak  
1 VM 213 berjalan; Pocket ID hanya terbuka lewat Tailscale Serve  
2 Passkey terdaftar di sedikitnya dua perangkat dan cara pemulihan dicatat  
3 ENCRYPTION_KEY dan Client Secret tersimpan di Vaultwarden  
4 VM 214 berjalan dengan disk foto terpasang otomatis dan hanya terbuka lewat Tailscale Serve  
5 Foto uji dari Android dan iPhone muncul di Immich  
6 Akun lokal admin Immich masih bisa masuk (login darurat)  
7 Backup VM 213 dan 214 berhasil; salinan foto di luar mesin sudah dijadwalkan  
8 Skrip profil berjalan dan hanya VM harian yang onboot 1  
9 Firewall VM 213 dan 214 aktif; entri audit terisi  
Berikutnya: Suplemen 10 (opsional): server game dengan AMP dan playit.gg, Ollama untuk model bahasa lokal,  
dan katalog layanan kecil. Ollama dan model besar membutuhkan RAM jauh lebih banyak, sehingga sebaiknya  
menunggu penambahan RAM.
