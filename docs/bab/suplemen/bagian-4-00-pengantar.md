# Bagian 4. Reverse Proxy dan Sertifikat SSL Lokal (pengantar)

Bagian 4. Reverse Proxy dan Sertifikat SSL  
Lokal  
Asal: Suplemen 4. Bab 35-38.  
Sampai Suplemen 3, setiap layanan dibuka lewat alamat IP dan port (misalnya 192.168.88.20:3001) dan tanpa  
HTTPS. Suplemen ini memasang reverse proxy: satu pintu yang menerima semua permintaan, memberi  
sertifikat HTTPS, dan meneruskannya ke layanan yang tepat. Hasilnya, Anda cukup membuka  
https://kuma.home.arpa.  
Bab Isi Hasil akhir  
35. Konsep dan keputusan Cara kerja, tiga jalur sertifikat, memilih nama domain  
lokal  
Tahu jalur yang dipakai dan alasannya  
36. Memasang Caddy DNS, jaringan Docker, Caddy, memindahkan  
layanan ke belakang proxy  
Layanan terbuka lewat nama dengan  
HTTPS  
37. Sertifikat di perangkat Mengambil sertifikat akar dan memasangnya di  
Windows, Android, iPhone  
Gembok hijau tanpa peringatan di semua  
perangkat  
38. Jalur opsional: domain  
asli  
Sertifikat tepercaya tanpa memasang apa pun di  
perangkat  
Alternatif bila aplikasi HP menolak  
sertifikat lokal  
Mengapa HTTPS di jaringan sendiri?  
• Banyak aplikasi web (Vaultwarden, AFFiNE, kamera, notifikasi, dan kunci sandi/passkey) mensyaratkan  
HTTPS agar fitur penting bekerja.  
• Satu pintu lebih mudah dijaga: port aplikasi bisa ditutup dan yang terbuka hanya 80 dan 443.  
• Alamat berupa nama lebih mudah diingat daripada IP dan port.  
• Lalu lintas lewat Tailscale sudah terenkripsi; HTTPS menambah kompatibilitas aplikasi, bukan menggantikan  
Tailscale.  
Prasyarat  
• VM Debian dengan Docker Compose dan struktur /opt/stacks (Suplemen 3, Bab 31).  
• AdGuard Home di STB (Edisi 2 Bab 12) dengan alamat 192.168.88.253.  
• Tailscale dengan Split DNS (Suplemen 1 Bab 26.7) bila ingin memakai nama dari luar rumah.  
PERINGATAN  
Suplemen ini mengubah file Compose layanan yang sudah berjalan (Uptime Kuma, Beszel, Gotify). Buat backup  
/opt/stacks lebih dulu (Suplemen 3 Bab 34.3).
