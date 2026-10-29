# Bagian 3. Monitoring dan Notifikasi (pengantar)

Bagian 3. Monitoring dan Notifikasi  
Asal: Suplemen 3. Bab 31-34.  
Suplemen ini memasang tiga hal yang menjawab permintaan awal Anda: memantau uptime seluruh layanan,  
memantau CPU, RAM, disk, dan suhu, dan mengirim peringatan ke HP. Dua alat utamanya ringan dan cocok  
untuk pemula: Uptime Kuma (apakah layanan hidup) dan Beszel (seberapa sehat mesinnya), dengan Gotify  
sebagai pengirim notifikasi.  
Bab Isi Hasil akhir  
31. Fondasi Docker  
Compose  
Struktur folder, aturan versi dan port, perintah rutin Cara seragam memasang semua aplikasi  
berikutnya  
32. Uptime Kuma dan  
Gotify  
Pasang, tambah monitor, notifikasi ke HP (Android,  
iPhone)  
Notifikasi di HP saat layanan mati atau  
hidup kembali  
33. Beszel Hub dan agen di VM, Proxmox, dan STB; suhu,  
Docker, peringatan  
Grafik CPU, RAM, disk, suhu, dengan  
peringatan  
34. Menyatukan dan  
menguji  
Alur peringatan, kartu dashboard, backup, uji  
menyeluruh, batas monitoring  
Sistem pemantau teruji dan tercadangkan  
Prasyarat  
• VM Debian 13 di 192.168.88.20 dengan Docker dan Docker Compose (Edisi 2 Bab 14).  
• Disarankan: Suplemen 1 (keamanan dan Tailscale) dan Suplemen 2 (Proxmox di mesin asli) sudah dikerjakan.  
Suhu CPU terbaca di mesin asli (ThinkCentre M710q).  
• Bila UFW aktif di VM (Suplemen 1 Bab 25.6), ikuti catatan port di Bab 31.3.  
• Satu akun Telegram bila ingin kanal notifikasi kedua (opsional, disarankan untuk iPhone).  
CATATAN  
Prometheus dan Grafana tidak dipasang di sini. Untuk kebutuhan Anda (CPU, RAM, disk, suhu, uptime) Beszel dan  
Uptime Kuma sudah cukup, memakai RAM jauh lebih sedikit, dan lebih mudah dirawat pemula. Prometheus dan  
Grafana tetap bisa ditambahkan belakangan bila butuh grafik yang sangat khusus.  
PERINGATAN  
Pemantau yang berjalan di mesin yang sama dengan yang dipantau ikut mati saat mesin itu mati. Pada tahap ini  
semua dipasang di VM Debian; saat STB 2 atau mesin kedua tersedia, Uptime Kuma sebaiknya dipindah ke sana  
(Bab 34.6).
