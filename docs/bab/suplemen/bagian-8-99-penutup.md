# Bagian 8. Navidrome: Streaming Musik Pribadi: Uji, Masalah Umum, Lembar Pembaruan, Syarat Lulus Fase 8

Uji, Masalah Umum, dan Lembar Pembaruan  
Uji menyeluruh  
No Uji Hasil yang diharapkan  
1 df -h /srv/music di VM music Ukuran disk kedua terlihat; terpasang setelah reboot  
2 tailscale serve status Rute 443 menuju 4533  
3 Laptop: https://lab-music.NAMA-TAILNET.ts.net Halaman Navidrome dengan gembok tanpa peringatan  
4 Unggah satu album, tunggu pemindaian Album muncul di pustaka dan bisa diputar  
5 Android dan iPhone: tambah server, putar lagu Suara keluar; layar terkunci tidak menghentikan  
pemutaran  
6 Tailscale mati di HP Aplikasi gagal tersambung (normal); pulih saat  
Tailscale aktif  
7 Dari laptop: Test-NetConnection 192.168.88.31 -Port 4533 False (tidak terbuka di LAN)  
8 Job backup PBS untuk VM 211 TASK OK; ukuran backup kecil (tanpa disk musik)  
Masalah dan solusi  
Gejala Penyebab Solusi  
Container berhenti dengan galat  
izin  
Folder data bukan milik UID:GID  
yang dipakai  
chown -R 1000:1000 data; sesuaikan dengan  
user di compose  
Pustaka kosong Berkas milik root atau belum dipindai Periksa izin baca di /srv/music; mulai ulang  
container  
Lagu tampil dengan judul berkas  
atau tanpa sampul  
Tag berkas tidak lengkap Rapikan tag dengan Picard lalu pindai ulang  
Aplikasi tidak bisa tersambung Tailscale mati atau alamat salah Aktifkan Tailscale; salin alamat persis dari konsol  
admin  
Pemutaran berhenti saat layar  
terkunci  
Penghematan baterai membatasi  
aplikasi  
Atur baterai aplikasi ke tanpa batasan (Android);  
izinkan latar belakang (iPhone)  
Sertifikat belum tersedia saat serve HTTPS Certificates belum aktif Aktifkan di halaman DNS konsol admin  
(Suplemen 6 Bab 44.3)  
Lembar pembaruan  
Dokumen Perubahan Rujukan  
Suplemen 7, Bab 48 Peta guest bertambah VM 211 music; tabel RAM diperbarui  
(jumlah sebelumnya salah hitung, lihat tabel baru)  
Bab 48.3, 48.6  
Suplemen 7, Bab 50.10 Job backup mencakup VM 211 (disk pustaka tidak ikut) Bab 53.6  
Suplemen 7, Bab 51 Aturan firewall untuk VM 211 Bab 53.6  
Suplemen 7, Bab 52 Laporan audit bertambah baris VM 211 Bab 52.7  
Daftar hal yang belum dipastikan  
No Hal Cara memastikan  
1 Aplikasi musik pihak ketiga dan CA lokal (mengapa dipilih Jalur 1) Tidak perlu diuji; Jalur 1 sudah  
menghindarinya  
2 Sintaks qm set --scsi1 STORAGE:UKURAN,backup=0 dan nama  
penyimpanan  
qm config 211; lihat Datacenter &gt; Storage  
3 Letak menu pengguna dan tombol pindai di antarmuka Navidrome;  
pemindaian saat container dimulai  
Lihat antarmuka dan dokumentasi  
Navidrome  
4 Perilaku tiap klien (pemutaran latar belakang, unduhan offline, harga  
Symfonium)  
Uji di perangkat Anda  
5 Nomor versi Navidrome untuk dipasang tetap Halaman rilis Navidrome di GitHub  
6 Kebutuhan RAM dan CPU saat transkoding Ukur dengan Beszel  
Syarat lulus  
No Poin Ya / Tidak  
1 VM 211 berjalan dengan disk pustaka terpasang otomatis  
2 Navidrome hanya terbuka lewat Tailscale Serve (tidak di LAN)  
3 Album uji diputar di Windows, Android, dan iPhone  
4 Backup VM 211 berhasil; keputusan backup disk musik sudah sadar (ikut atau tidak)  
5 Firewall VM 211 aktif; entri audit terisi  
Berikutnya: Suplemen 9 (Bab 54-56): SSO dan Immich (pengganti Google Photos), masing-masing dengan  
Kotak Penempatan, backup, dan firewall mengikuti pola Suplemen 7.
