# Bagian 7. Penempatan VM/LXC, Backup, dan Audit: Uji, Masalah Umum, Lembar Pembaruan, Syarat Lulus Fase 7

Uji, Masalah Umum, dan Lembar Pembaruan  
Uji menyeluruh  
No Uji Hasil yang diharapkan  
1 qm list di host Terlihat VM 201-212 (sesuai yang sudah dibuat) dan  
templat 9100  
2 Satu VM baru dari templat (Bab 49.4) Nama host, kunci SSH, dan IP unik; ping DNS dan  
internet berhasil  
3 Backup pertama ke pbs-home TASK OK untuk setiap VM; ukuran datastore  
bertambah  
4 Uji pulih VM 999 tanpa jaringan Sistem naik, data ada; VM sementara dihapus  
5 Prune, GC, dan verify berjalan sekali Tidak ada galat di tab Tasks PBS  
6 Kegagalan backup disimulasikan (matikan PBS lalu jalankan  
job)  
Notifikasi Gotify tiba di HP  
7 Firewall: Test-NetConnection ke port layanan langsung Diblokir; lewat Caddy (443) terbuka  
8 VM 210 mencoba menjangkau LAN Diblokir; internet tetap bisa  
9 Skrip audit di setiap VM Tidak ada temuan di luar matriks atau risiko tercatat  
10 Salinan kedua (USB) dan arsip konfigurasi host Tersimpan di luar mesin  
Masalah dan solusi  
Gejala Penyebab Solusi  
VM klon tidak bisa di-SSH Kunci host dihapus di templat dan  
belum dibuat ulang  
Konsol Proxmox: dpkg-reconfigure  
openssh-server  
Dua VM sama-sama muncul  
sebagai satu perangkat  
machine-id atau kunci SSH sama Ulangi 49.3 pada templat; pada klon: truncate  
machine-id lalu reboot  
VM baru tidak mendapat IP yang  
diharapkan  
MAC pada reservasi MikroTik salah qm config ID | grep net0; perbaiki lease  
Job backup gagal: "guest agent not  
running"  
Agen tamu belum terpasang atau  
opsi agen mati  
apt install qemu-guest-agent; Options &gt; QEMU  
Guest Agent: Yes; mulai ulang VM  
PVE gagal menambah PBS: sidik  
jari tidak cocok  
Fingerprint salah salin atau PBS  
dipasang ulang  
Ambil ulang di Dashboard PBS (50.8); Edit  
storage  
Ruang PBS tidak turun setelah  
prune  
GC belum berjalan atau masa tunggu Jalankan GC di Options datastore; tunggu sekitar  
sehari  
Tidak bisa memulihkan backup  
terenkripsi  
Kunci enkripsi hilang Pulihkan dari salinan di Vaultwarden atau kertas;  
tanpa kunci tidak bisa  
Terkunci dari host setelah firewall Aturan Datacenter atau node  
memblokir 8006 atau 22  
Konsol fisik host: pve-firewall stop; perbaiki  
aturan; pve-firewall start  
Layanan tiba-tiba tidak terjangkau  
dari Caddy  
Aturan IN di VM tujuan belum  
mengizinkan 192.168.88.20 pada  
port itu  
Cek /etc/pve/firewall/ID.fw dan kotak firewall di  
kartu jaringan  
Semua VM mati setelah host mati Start at boot belum diaktifkan qm set ID --onboot 1  
Lembar pembaruan  
Dokumen Perubahan Rujukan  
Suplemen 1 sampai 4 (Revisi 2) Tiap bab pemasangan diawali Kotak Penempatan. Suplemen 1  
Bab 26: Tailscale pindah dari pilihan B (VM Docker) ke C (LXC  
CT103)  
Bab 48.5  
Suplemen 5 (Revisi 2) Situs statis dan WordPress di VM 209, n8n di VM 208, tunnel di  
VM 210; Caddy meneruskan ke IP:port  
Bab 48.4  
Suplemen 6 (Revisi 2) Vaultwarden di VM 205 (lab-vault, port 443), AFFiNE di VM 206,  
Nextcloud di VM 207  
Bab 48.4  
Edisi 2 VM Debian pertama menjadi docker-core atau sumber templat  
9100  
Bab 49.1  
Backup (Edisi 2 Bab 23) Backup tingkat VM oleh PBS menjadi lapisan utama; dump logis  
tetap sebagai lapisan kedua  
Bab 50  
Daftar hal yang belum dipastikan  
No Hal Cara memastikan  
1 RAM awal tiap VM dan jumlah total Ukur dengan Beszel; sesuaikan qm set  
--memory  
2 Instruksi pemasangan Docker untuk Debian 13 tidak berubah dari 49.2 Bandingkan dengan halaman instalasi  
Docker resmi  
3 Lease DHCP statis di luar rentang pool MikroTik diterima Uji; bila ditolak pakai IP statis di Debian  
4 Nomor rilis ISO PBS terbaru; HDD sebagai datastore lambat Cek halaman unduhan; ukur waktu  
verifikasi  
5 Nama peran DatastoreBackup dan batas haknya; sintaks pembuatan disk  
lewat proxmox-backup-manager  
Cek daftar Role dan bantuan perintah di  
PBS  
6 Masa tunggu GC dan nama menu notifikasi di Proxmox 9.2 dan PBS Baca dokumentasi pada versi terpasang  
7 Sintaks +dc/admin, perilaku opsi dhcp: 1, dan port keluar tunnel 7844 Uji aturan; lihat dokumentasi firewall  
Proxmox dan Cloudflare  
8 Sumber IP perangkat Tailscale yang tiba di VM (CT103 sebagai subnet  
router)  
Uji SSH dari luar rumah; lihat IP sumber di  
log sshd  
9 Versi lynis di Debian lynis show version  
Syarat lulus Fase 7  
No Poin Ya / Tidak  
1 Templat VM 9100 ada; setiap VM layanan dibuat dari templat dengan kunci SSH dan IP sendiri  
2 Setiap layanan berada di guest sesuai peta 48.3 (atau sesuai mode hemat yang dicatat)  
3 PBS berjalan; backup harian ke store1 sukses; datastore di disk fisik terpisah  
4 Satu uji pulih berhasil; kunci enkripsi tersimpan di dua tempat terpisah  
5 Salinan kedua (USB) dan arsip konfigurasi host sudah ada di luar mesin  
6 Firewall Proxmox aktif; uji blokir port langsung lulus; VM 210 tidak bisa menjangkau LAN  
7 Skrip audit dijalankan di setiap VM; laporan terisi; risiko diterima tercatat  
8 Notifikasi kegagalan backup tiba di Gotify  
Berikutnya (Suplemen 8): SSO dan Immich. Rencana penempatan (belum keputusan, akan dibuka dengan  
Kotak Penempatan): Immich di VM sendiri karena disk dan CPU besar; layanan SSO di VM sendiri karena  
memegang identitas semua layanan lain. Backup dan firewall keduanya akan mengikuti pola Bab 50 dan 51.
