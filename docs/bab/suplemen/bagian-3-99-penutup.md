# Bagian 3. Monitoring dan Notifikasi: Lembar Pembaruan dan Syarat Lulus Fase 3

Lembar Pembaruan dan Syarat Lulus  
Bab sebelumnya Perubahan Rujukan  
Edisi 2, Bab 19 (Dashboard) Tambahkan kartu Uptime Kuma, Beszel, Gotify Bab 34.2  
Edisi 2, Bab 23 (Backup) Tambahkan /opt/stacks ke daftar backup, termasuk .env Bab 32.6 dan 34.3  
Edisi 2, Bab 24 (Masalah) Tambahkan tabel masalah Gotify, Uptime Kuma, dan Beszel Bab 32.7 dan 33.6  
Suplemen 1, Bab 25.5 (firewall  
Proxmox)  
Tambahkan aturan masuk tcp 45876 dari 192.168.88.20 untuk  
agen Beszel  
Bab 33.3  
Suplemen 1, Bab 25.6 (UFW) Tambahkan aturan 172.16.0.0/12 ke port 45876 bila agen  
Beszel di VM  
Bab 33.2  
Suplemen 2, Bab 30.4 (sensor) Data sensors kini dibaca Beszel untuk panel suhu Bab 33.3  
Syarat lulus Fase 3  
No Poin Ya / Tidak  
1 Gotify, Uptime Kuma, dan Beszel berjalan (docker compose ps)  
2 Notifikasi uji tiba di HP (Gotify di Android, Telegram di iPhone atau cadangan)  
3 Monitor Proxmox, MikroTik, AdGuard, VM, dan internet aktif  
4 Beszel menampilkan vm-debian dan Proxmox; panel suhu muncul di mesin asli  
5 Peringatan CPU, RAM, disk, suhu, dan status dikonfigurasi  
6 Uji skenario 1 dan 3 berhasil; notifikasi tiba juga dari luar rumah (Tailscale)  
7 Backup /opt/stacks sudah dibuat dan disalin ke luar server  
Berikutnya (Suplemen 4): reverse proxy lokal dengan sertifikat SSL, sehingga layanan diakses lewat nama  
(misalnya kuma.lab.local) dan bukan IP:port, dengan sisi klien (memasang sertifikat di laptop, Android, dan  
iPhone).
