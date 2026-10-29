# Bagian 4. Reverse Proxy dan Sertifikat SSL Lokal: Uji, Masalah Umum, Lembar Pembaruan, Syarat Lulus Fase 4

Uji, Masalah Umum, dan Lembar Pembaruan  
Uji menyeluruh  
No Uji Hasil yang diharapkan  
1 nslookup kuma.home.arpa 192.168.88.253 Jawaban 192.168.88.20  
2 Laptop: buka https://kuma.home.arpa setelah Bab 37 Halaman Uptime Kuma, gembok tanpa peringatan  
3 Buka https://proxmox.home.arpa Halaman login Proxmox; konsol VM berfungsi (bila tidak,  
buka lewat IP:8006)  
4 HP Android (Chrome), WiFi rumah Gembok tanpa peringatan  
5 HP Android, data seluler, Tailscale aktif Nama terbuka dari luar rumah  
6 iPhone (Safari), setelah mengaktifkan kepercayaan  
sertifikat  
Gembok tanpa peringatan  
7 Notifikasi Gotify dari Uptime Kuma tetap tiba Ya (Gotify tetap lewat 192.168.88.20:8070)  
8 Port lama 3001 dan 8090 dari laptop Tidak lagi terbuka (hanya Caddy 80 dan 443)  
Masalah dan solusi  
Gejala Penyebab Solusi  
Nama tidak ditemukan DNS rewrite belum ada, atau  
perangkat memakai DNS lain  
Periksa AdGuard (Bab 36.1); di Android matikan  
Private DNS yang menimpa DNS jaringan; Tailscale  
split DNS bila di luar rumah  
Peringatan sertifikat tetap  
muncul  
Sertifikat akar belum dipasang atau  
belum dipercaya  
Ulangi Bab 37; iPhone: aktifkan di Pengaturan  
Kepercayaan Sertifikat; Firefox: impor terpisah  
Error 502 Bad Gateway Layanan tidak berada di jaringan  
proxy atau nama container salah  
docker network inspect proxy; samakan nama  
container di Caddyfile  
Caddy gagal start Kesalahan sintaks atau port 80/443  
terpakai  
docker exec caddy caddy validate ... ; ss -tlnp | grep  
-E ":(80|443)"  
Konsol VM Proxmox putus Proxy dan WebSocket Buka Proxmox langsung lewat  
https://192.168.88.10:8006 untuk konsol  
Aplikasi Android menolak  
sertifikat  
Aplikasi tidak mempercayai CA  
pengguna  
Pakai IP:port untuk aplikasi itu atau beralih ke Jalur 2  
(Bab 38)  
Setelah reinstal semua  
perangkat menolak  
Folder data Caddy hilang sehingga  
CA baru dibuat  
Pulihkan backup /opt/stacks/caddy/data, atau pasang  
akar baru di semua perangkat  
Lembar pembaruan  
Bab sebelumnya Perubahan Rujukan  
Suplemen 1, Bab 25.6 Setelah layanan dipindah ke belakang Caddy, port aplikasi tidak  
lagi dipublikasikan; hanya 80 dan 443  
Bab 36.4  
Suplemen 1, Bab 26.7 Tambahkan Split DNS untuk home.arpa selain lab.local Bab 36.1  
Suplemen 3, Bab 32.3 dan 34.2 Ganti target monitor dan tautan Homepage ke nama https baru  
(Gotify tetap IP:port)  
Bab 36.7  
Edisi 2, Bab 19 Tautan kartu dashboard memakai nama baru Bab 36.7  
Edisi 2, Bab 23 dan Suplemen 3  
Bab 34.3  
Tambahkan /opt/stacks/caddy (termasuk data berisi kunci CA)  
ke backup  
Bab 36.5  
Syarat lulus Fase 4  
No Poin Ya / Tidak  
1 AdGuard (dan AdGuard kedua) memiliki rewrite \*.home.arpa ke 192.168.88.20  
2 Caddy berjalan; kuma, beszel, gotify, proxmox, portainer, adguard terbuka lewat https  
3 Sertifikat akar terpasang di laptop, Android, dan iPhone; gembok tanpa peringatan  
4 Dari luar rumah (Tailscale) nama tetap terbuka  
5 Port aplikasi lama tertutup kecuali Gotify 8070  
6 Backup folder Caddy (data) tersimpan di luar server  
Berikutnya (Suplemen 5): hosting web (situs statis dan WordPress) dan n8n di belakang Caddy yang sama,  
lengkap dengan sisi klien. Setelah itu Proxmox Backup Server, SSO, Immich, dan opsional AMP, Ollama, sesuai  
daftar Anda.
