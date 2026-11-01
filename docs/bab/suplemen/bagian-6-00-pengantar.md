# Bagian 6. Vaultwarden, AFFiNE, dan Kalender Nextcloud (pengantar)

Bagian 6. Vaultwarden, AFFiNE, dan Kalender  
Nextcloud  
Asal: Suplemen 6. Bab 44-47.  
Suplemen 6 memasang tiga layanan pribadi yang menyimpan data paling sensitif di server Anda: kata sandi  
(Vaultwarden), catatan dan dokumen bergaya Notion (AFFiNE), dan kalender (Nextcloud). Ketiganya punya  
aplikasi di HP, dan di situlah persoalan sertifikat HTTPS dari Suplemen 4 menjadi penting.  
Bab Isi Hasil akhir  
44. Jalur sertifikat per  
aplikasi  
Mengapa aplikasi HP bisa menolak CA lokal; Tailscale  
Serve sebagai jalur tepercaya tanpa domain  
Tahu aplikasi mana memakai jalur  
mana  
45. Vaultwarden Server kata sandi, akun, aplikasi Windows, Android,  
iPhone, backup  
Kata sandi tersinkron di semua  
perangkat  
46. AFFiNE Server catatan, aplikasi desktop dan HP, backup Catatan tersinkron di semua  
perangkat  
47. Nextcloud dan Kalender Server Nextcloud, aplikasi Calendar, sinkron ke  
Thunderbird, Android (DAVx5), iPhone  
Kalender pribadi pengganti Google  
Calendar  
Prasyarat  
• Caddy, jaringan Docker proxy, dan sertifikat akar terpasang di perangkat (Suplemen 4); struktur /opt/stacks  
(Suplemen 3).  
• Tailscale dengan router-vm (Suplemen 1 Bab 26) dan kebijakan jaringan yang sudah Anda ubah di Bab 26.6.  
• VM 205 vault, 206 affine, dan 207 nextcloud dibuat dari templat VM 200 (Suplemen 7 Bab 48-49). Caddy  
tetap di VM 201 docker-core.  
• Semua perintah server dijalankan sebagai root setelah su - (tanpa sudo), di guest yang ditunjuk Kotak  
Penempatan di awal tiap bab.  
PERINGATAN  
Suplemen 1 sampai 5 belum Anda uji. Suplemen ini bergantung pada Tailscale (Suplemen 1), Caddy dan sertifikat  
(Suplemen 4). Kerjakan Bab 44 setelah Tailscale dan Bab 37 terbukti jalan, dan laporkan hasilnya.  
KEAMANAN  
Data di sini tidak tergantikan (kata sandi, kalender, catatan). Backup yang tersimpan hanya di server yang sama  
bukan backup. Proxmox Backup Server dibahas di Suplemen 7; sampai saat itu salin backup secara manual ke laptop  
atau disk luar.  
CATATAN  
Hal yang belum bisa saya pastikan dari dokumentasi ditandai [BELUM PASTI] dan dikumpulkan di tabel pada  
halaman penutup.
