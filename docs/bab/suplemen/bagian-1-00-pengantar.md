# Bagian 1. Keamanan dan Akses Jarak Jauh (pengantar)

Bagian 1. Keamanan dan Akses Jarak Jauh  
Asal: Suplemen 1. Bab 25-26.  
Suplemen ini adalah tambahan untuk Buku Panduan Home Server Lab Edisi 2. Isi Edisi 2 tidak ditulis ulang.  
Setiap suplemen berisi bab baru bernomor lanjutan (mulai Bab 25) dan satu lembar pembaruan di bagian akhir  
yang menunjukkan bab lama mana yang berubah.  
Isi Suplemen 1  
Bab Isi Hasil akhir  
25. Keamanan dasar  
server  
Backup sebelum mengubah, akun admin Proxmox  
terpisah + 2FA, SSH hanya kunci, firewall Proxmox,  
pengerasan VM Debian (UFW, update otomatis),  
pengerasan MikroTik, checklist uji.  
Server tidak bisa dimasuki dengan  
password saja, hanya LAN yang boleh  
mengakses panel admin, dan ada jalan  
keluar bila terkunci.  
26. Tailscale Cara kerja, memilih perangkat subnet router,  
pemasangan di sisi server, sisi laptop Windows, sisi HP  
(Android dan iPhone), kebijakan akses, DNS, uji dari  
luar jaringan.  
Panel Proxmox, SSH, dan layanan lain  
dapat dibuka dari mana saja lewat  
Tailscale, tanpa membuka satu port pun ke  
internet.  
Prasyarat  
• Proxmox VE sudah terpasang dan web UI terbuka di https://192.168.88.10:8006 (Edisi 2 Bab 8 dan 9).  
• VM Debian 13 sudah berjalan di 192.168.88.20 dengan pengguna biasa dan password root (Bab 11).  
• MikroTik RB750GL sudah dikonfigurasi dasar dan dapat dibuka lewat WinBox (Bab 3).  
• Laptop Windows berada di jaringan MikroTik (192.168.88.0/24) saat mengerjakan bab ini.  
• Satu akun email (Google, Microsoft, Apple, atau GitHub) yang sudah memakai verifikasi dua langkah, untuk  
Tailscale di Bab 26.  
Alamat jaringan yang dipakai (sama dengan Edisi 2 Bab 3.2)  
Alamat Perangkat Catatan  
192.168.88.1 MikroTik RB750GL Gateway, firewall  
192.168.88.2 TL-WR820N (Access Point)  
192.168.88.10 Proxmox VE Mesin asli (ThinkCentre M710q)  
192.168.88.11 / .12 LXC AdGuard kedua / LXC Samba Edisi 2 Bab 13 dan 17  
192.168.88.20 VM Debian 13 Docker, Portainer, Git, Nextcloud  
192.168.88.253 STB HG680 (AdGuard) DNS utama  
192.168.88.250 (usulan) STB 2 (subnet router Tailscale) Belum tiba; buat reservasi di MikroTik saat  
tiba  
CATATAN  
Seperti Edisi 2 Bab 1.7, perintah di buku ini tidak memakai sudo. Untuk VM Debian, masuk SSH sebagai pengguna  
biasa lalu jalankan su - sehingga prompt menjadi # dan perintah berikutnya tanpa sudo. Teks seperti &lt;USER&gt;  
adalah placeholder yang harus diganti dengan nilai Anda.  
PERINGATAN - Risiko terkunci  
Bab 25 mengubah cara login ke server. Selalu ikuti urutan langkah, biarkan satu sesi SSH lama tetap terbuka saat  
menguji sesi baru, dan siapkan jalur darurat (Bab 25.2) sebelum mulai.
