# Bagian 5. Hosting Web dan n8n (pengantar)

Bagian 5. Hosting Web dan n8n  
Asal: Suplemen 5. Bab 39-43.  
Suplemen 4 membuat satu pintu HTTPS (Caddy). Suplemen ini memasang tiga hal di belakang pintu itu: situs  
web statis, WordPress, dan n8n (otomasi alur kerja). Satu bab opsional menunjukkan cara membuka situs  
statis ke internet dengan Cloudflare Tunnel tanpa membuka port di router.  
Bab Isi Hasil akhir  
39. Konsep dan keputusan Jalur privat vs publik, mengapa tunnel, apa dipasang  
di mana  
Tahu mana yang privat dan mana yang  
boleh publik  
40. Situs statis Folder situs, blok Caddy, unggah dari laptop https://web.home.arpa tampil di semua  
perangkat  
41. WordPress WordPress + MariaDB, pemasangan, pengamanan  
dasar  
https://wp.home.arpa dengan HTTPS  
benar  
42. n8n n8n + Postgres, uji webhook ke Gotify, webhook luar https://n8n.home.arpa dan notifikasi uji  
tiba  
43. Cloudflare Tunnel  
(opsional)  
Situs statis publik lewat koneksi keluar Situs terbuka dari internet tanpa port  
forwarding  
Prasyarat  
• Caddy dan jaringan Docker proxy dari Suplemen 4 (Bab 36) sudah berjalan; Gotify dan Uptime Kuma dari  
Suplemen 3.  
• Sertifikat akar Caddy terpasang di perangkat (Suplemen 4 Bab 37) bila ingin gembok tanpa peringatan.  
• VM 208 n8n, 209 web, dan 210 web-public dibuat dari templat VM 200 (Suplemen 7 Bab 48-49). Caddy tetap  
di VM 201 docker-core.  
• Semua perintah dijalankan sebagai root setelah su - (tanpa sudo), di guest yang ditunjuk Kotak  
Penempatan di awal tiap bab.  
PERINGATAN  
Suplemen 1 sampai 4 belum Anda uji. Suplemen ini bergantung langsung pada Caddy (Suplemen 4). Saran urutan:  
uji dulu Bab 36 dan 37, baru kerjakan Bab 40 dan seterusnya. Bila Caddy bermasalah, kesalahan di sini sulit  
dibedakan dari kesalahan di sana.  
CATATAN  
Hal yang tidak bisa saya pastikan dari dokumentasi ditandai [BELUM PASTI] di teks dan dikumpulkan di tabel pada  
halaman penutup. Laporkan hasil uji per bab agar bisa dikoreksi.
