# Bagian 7. Penempatan VM/LXC, Backup, dan Audit (pengantar)

Bagian 7. Penempatan VM/LXC, Backup, dan  
Audit  
Asal: Suplemen 7. Bab 48-52.  
Suplemen 7 membuat satu keputusan besar: setiap layanan berjalan di VM atau container Proxmox yang  
terpisah, kecuali beberapa layanan ringan yang sengaja digabung. Sesudah itu ia memasang Proxmox Backup  
Server, firewall antar-guest, dan audit keamanan. Suplemen 1 sampai 6 diterbitkan ulang sebagai Revisi 2 agar  
setiap bab pemasangan diawali Kotak Penempatan yang menyebut guest tujuan.  
Bab Isi Hasil akhir  
48. Peta penempatan Prinsip, daftar guest dan IP, aturan menerjemahkan bab  
lama, mode hemat, penyesuaian Edisi 2  
Tahu setiap layanan tinggal di  
mana  
49. Templat VM Debian +  
Docker  
Membuat templat, menyalin VM baru, penyiapan awal  
tiap VM  
VM baru jadi dalam beberapa  
menit  
50. Proxmox Backup Server VM pbs, datastore, pengguna, job backup, prune, uji  
pulih, salinan kedua  
Backup otomatis dan terbukti bisa  
dipulihkan  
51. Firewall Proxmox  
antar-guest  
Matriks akses, IPSet, aturan per VM, isolasi VM publik Hanya jalur yang diizinkan yang  
terbuka  
52. Audit keamanan Skrip audit baca-saja, Lynis, SSH kunci, laporan Daftar temuan dan keputusan  
risiko  
Urutan kerja yang disarankan  
1. Baca Bab 48 lalu kerjakan Bab 49 (membuat templat VM 200).  
2. Pasang layanan menurut Kotak Penempatan di Suplemen 3, 4, 5, 6 (Revisi 2), masing-masing di guest yang  
ditunjuk.  
3. Kerjakan Bab 50 setelah ada guest yang berisi data, lalu Bab 51, terakhir Bab 52.  
PERINGATAN  
Tidak ada suplemen yang sudah Anda uji. Karena belum ada yang terpasang, Anda tidak perlu memindahkan apa  
pun: pasang langsung di guest tujuan. Bila sebagian sudah terpasang di satu VM Docker (192.168.88.20), jangan  
memigrasi sekaligus; pindahkan satu layanan, uji, baru lanjut.  
CATATAN  
Angka RAM, nomor VMID, dan alamat IP di sini adalah rancangan yang bisa Anda ubah selama konsisten. Hal yang  
belum bisa saya pastikan ditandai [BELUM PASTI] dan dikumpulkan di tabel pada halaman penutup.
