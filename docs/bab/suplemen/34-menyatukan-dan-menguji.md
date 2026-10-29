# Bab 34. Menyatukan, Menguji, dan Memahami Batasnya

PENEMPATAN - TIDAK ADA GUEST  
Tempat: Bab ini menyatukan dan menguji layanan Suplemen 3 yang berada di docker-core.  

## 34.1 Alur peringatan

Layanan dan mesin  
Proxmox, VM, STB, MikroTik  
Uptime Kuma  
hidup atau mati?  
Beszel  
CPU, RAM, disk, suhu  
Gotify  
dan Telegram  
HP Anda  
notifikasi  
Gambar 34.1 - Uptime Kuma dan Beszel mengirim peringatan lewat Gotify atau Telegram ke HP.  
Pertanyaan Dijawab oleh  
Apakah layanan hidup dan menjawab? Uptime Kuma  
Apakah internet rumah putus? Uptime Kuma (ping 1.1.1.1)  
Apakah CPU, RAM, disk, atau suhu mendekati batas? Beszel  
Container mana yang memakai sumber daya terbanyak? Beszel (halaman sistem vm-debian)  
Apakah disk mulai rusak? Pemeriksaan bulanan: smartctl -H (Suplemen 2 Bab  
30.4)  

## 34.2 Kartu di dashboard Homepage

Konfigurasi contoh di repo sudah memuat kartu monitoring ini. Jika Anda membuat Homepage dari awal, tambahkan entri berikut ke services.yaml, lalu muat ulang halaman. Gunakan nama HTTPS lokal setelah Caddy aktif.  

**services.yaml (tambahan)** | Hati-hati dengan spasi; YAML sensitif terhadap indentasi

```
- Monitoring:
    - Uptime Kuma:
        href: https://kuma.home.arpa
        description: Uptime semua layanan
    - Beszel:
        href: https://beszel.home.arpa
        description: CPU, RAM, disk, suhu
    - Gotify:
        href: https://gotify.home.arpa
        description: Notifikasi ke HP
```

## 34.3 Backup dan rutinitas bulanan

Kapan Tindakan  
Sebulan sekali Update image: di tiap folder /opt/stacks/\*, docker compose pull lalu up -d (backup dulu)  
Sebulan sekali apt update dan apt full-upgrade di VM dan Proxmox; cek /var/run/reboot-required  
Sebulan sekali smartctl -H pada semua disk; tinjau riwayat peringatan di Uptime Kuma dan Beszel  
Sebulan sekali Tinjau daftar Machines Tailscale (hapus perangkat tak dikenal)  
Tiga bulan sekali Uji pemulihan: ekstrak arsip backup ke folder uji dan pastikan aplikasi dapat menyala  
Folder yang dicadangkan: seluruh /opt/stacks (compose, .env, data). Hentikan container sebentar saat  
mengarsipkan agar basis data konsisten, seperti di Bab 32.6.  

## 34.4 Uji menyeluruh

No Skenario Cara Hasil yang diharapkan  
1 Layanan mati docker stop portainer (lalu docker start portainer  
setelah alarm)  
Notifikasi DOWN lalu UP di HP  
dalam beberapa menit  
2 Beban CPU apt install -y stress-ng, lalu stress-ng --cpu 0 --timeout  
900s (turunkan sementara ambang CPU ke 2 menit)  
Peringatan CPU dari Beszel  
3 Mesin mati Matikan VM Debian dari web Proxmox (pakai jendela  
pemeliharaan bila perlu)  
Beszel: sistem down; Uptime  
Kuma: monitor VM merah  
4 Notifikasi di luar rumah Matikan WiFi HP, Tailscale aktif, ulangi uji 1 Notifikasi tetap tiba  
5 Pemulihan backup Ekstrak arsip Uptime Kuma ke folder lain dan jalankan Monitor dan riwayat muncul  
PERINGATAN  
Setelah uji nomor 2, kembalikan ambang CPU ke nilai normal (10 menit).  

## 34.5 Batas yang perlu Anda pahami

KASUS NYATA  
Pemantau di dalam rumah tidak bisa memberi tahu saat rumah kehilangan internet atau listrik. Pesan Gotify  
dan Telegram butuh jaringan. Bila IndiHome mati, Anda tidak menerima apa pun, dan baru tahu saat tidak bisa  
mengakses.  
Solusi opsional: layanan pihak luar seperti Healthchecks.io (periksa ketentuan paket gratisnya). Server rumah  
mengirim sinyal berkala ke layanan itu, dan layanan itulah yang memperingatkan Anda bila sinyal berhenti. Pada VM  
tambahkan satu baris cron berisi perintah curl ke alamat ping yang diberikan layanan itu.  
KEAMANAN  
Kanal Telegram adalah satu-satunya yang melewati internet publik. Isinya hanya status layanan; jangan mengirim  
password atau data pribadi lewat notifikasi.  

## 34.6 Langkah berikutnya untuk ketahanan

• Pindahkan Uptime Kuma ke mesin lain (STB 2 atau mini PC) begitu tersedia, agar tetap bisa melaporkan saat  
Proxmox mati.  
• Tambahkan monitor untuk setiap layanan baru pada hari yang sama layanan itu dipasang.  
• Pertimbangkan UPS kecil agar mati listrik tidak mematikan server tanpa shutdown (rencana monitor listrik  
Anda).
