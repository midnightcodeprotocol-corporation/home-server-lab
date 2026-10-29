# Bab 24. Katalog Masalah dan Solusi

Kumpulan masalah yang sudah terjadi pada proyek ini (ditandai [Nyata]) dan yang sering muncul. Cari  
gejalanya di tabel.  

## 24.1 Alur cepat: Proxmox tidak bisa dibuka dari browser

1. Pastikan VM/mesin Proxmox menyala dan layar konsol menampilkan Please use your web  
browser ... https://...:8006.  
2. Di laptop ipconfig: catat IPv4 dan gateway adapter yang aktif. Tiga angka depan IP Proxmox harus  
sama dengan laptop.  
3. Di konsol Proxmox: ip a dan ping -c 3 192.168.88.1. Jika gagal, periksa kabel LAN dan bridge-ports.  
4. Pastikan alamat https://IP:8006 (https, bukan http).  
5. Periksa /etc/hosts dan systemctl status pveproxy.  
6. Ping dari laptop: ping IP-Proxmox. Ping berhasil tetapi web tidak = masalah layanan; ping gagal =  
masalah jaringan.  

## 24.2 Tabel masalah

| Gejala | Penyebab | Solusi | Rujukan |
|---|---|---|---|
| [Nyata] Tidak bisa membuka `https://192.168.100.2:8006` | IP Proxmox beda jaringan dengan laptop | Sesuaikan alamat/gateway di `interfaces` dan `hosts`; verifikasi dari konsol sebelum reboot | Bab 9.3 |
| [Nyata] Layar nano kosong saat mengedit jaringan | Nama berkas salah | Keluar tanpa menyimpan, lalu buka `/etc/network/interfaces` | Bab 9.3 |
| [Nyata] `apt update`: Temporary failure resolving | DNS kosong atau salah | Periksa System > DNS dan uji resolusi nama | Bab 9.4 |
| [Nyata] Tidak menemukan menu Repositories | Menu berada di bawah Updates | Buka Node > Updates > Repositories | Bab 9.5 |
| [Nyata] Refresh sangat lambat (9 KB/s) | Internet lambat atau uplink WiFi | Gunakan kabel LAN, mirror terdekat, atau waktu sepi | Bab 9.6 |
| [Nyata] Perintah `sudo` tidak terbaca | Sudah root; sudo tidak dipasang | Jangan gunakan sudo; di Debian masuk root dengan `su -` | Bab 1.7 |
| [Nyata] `ipconfig /release` memutus WiFi | IP dilepas tanpa diminta kembali | Jalankan `ipconfig /renew` | Bab 3.9 |
| [Nyata] STB punya dua instalasi Armbian | Instalasi lama di eMMC dan baru di SD | Periksa `lsblk` dan `findmnt /`; tentukan satu media | Bab 12.2 |
| [Nyata] Double NAT / router di belakang router lain | Urutan perangkat salah | Ikuti topologi jaringan terbaru | Bab 3.9 dan docs/02 |
| USB tidak muncul di boot menu | Mode boot, Secure Boot, atau penulisan USB | Periksa mode penulisan USB dan pengaturan boot sesuai panduan M710q | Bab 6.4, 27.5 |
| Layanan web Proxmox mati setelah ganti IP | `/etc/hosts` masih memuat IP lama | Perbarui `hosts`, lalu periksa hostname dan `pveproxy` | Bab 9.3 |
| Error 401 pada repository | Repository enterprise aktif | Nonaktifkan enterprise dan aktifkan no-subscription sesuai panduan | Bab 9.5 |
| Container tidak mendapat IP | Reservasi, bridge, atau DHCP bermasalah | Periksa lease MikroTik, bridge, dan alamat yang ditetapkan | Bab 10.5 |
| VM gagal start: KVM tidak tersedia | VT-x belum aktif | Aktifkan VT-x di BIOS dan periksa `/dev/kvm` | Bab 11, 27.5 |
| Peringatan cdrom saat `apt update` | Sumber instalasi masih tersisa | Nonaktifkan baris cdrom di sumber APT | Bab 11.5 |
| Port 53 dipakai systemd-resolved | DNS stub memakai port yang dibutuhkan AdGuard | Atur `DNSStubListener=no`, lalu mulai ulang layanan terkait | Bab 12.3 |
| Subnet Tailscale tidak terjangkau | Rute belum disetujui atau IP forwarding mati | Setujui rute dan periksa `ip_forward=1` | Bab 26 |
| Satu perangkat masih menampilkan iklan | DNS sendiri atau lease lama | Periksa Secure DNS, perbarui lease, lalu evaluasi aturan firewall | Bab 13.10 |
| Portainer timeout saat setup | Admin awal terlambat dibuat | Mulai ulang Portainer dan segera selesaikan setup | Bab 14.4 |
| Docker permission denied | Pengguna bukan root atau tidak punya izin socket | Jalankan sebagai root; jika memakai grup docker, pahami dampak hak aksesnya | Bab 14.4 |
| Forgejo: clone SSH gagal | Port SSH Git salah | Pastikan `SSH_PORT = 2222` di konfigurasi Forgejo | Bab 15 |
| Nextcloud: untrusted domain | Domain belum terdaftar | Tambahkan domain tepercaya melalui `occ` | Bab 16.3 |
| Home Assistant OS tidak boot | Secure Boot atau urutan boot salah | Periksa konfigurasi EFI dan urutan disk VM | Bab 18 |
| Dashboard: Host validation failed | Host belum diizinkan | Tambahkan nama host pada `ALLOWED_HOSTS` | Bab 19 |
| k3s NotReady | RAM kurang atau sumber daya terbatas | Periksa RAM dan matikan VM yang tidak dipakai | Bab 20 |
| Flux: permission denied (publickey) | Deploy key tidak punya izin tulis | Tambahkan deploy key dengan izin yang diperlukan | Bab 21 |
| Renovate tidak membuat PR | Izin bot atau image tidak dipatok | Periksa izin akun bot dan tag versi image | Bab 22 |
| Restore sukses tetapi jaringan gagal | Nama kartu jaringan fisik berubah | Cocokkan `bridge-ports` dengan nama kartu aktual sebelum menerapkan konfigurasi | Bab 23 |

## 24.3 Cara meminta bantuan dengan efektif

• Apa yang dilakukan dan pesan error persis (salin teks).  
• Keluaran ip a, ip route, dan cat /etc/resolv.conf dari server bermasalah.  
• ipconfig dari laptop untuk masalah jaringan.  
• Log: klik dua kali tugas di panel Tasks Proxmox, atau journalctl -u NAMA -n 50.  
• Foto layar konsol server atau tangkapan layar Proxmox (Hardware dan Network).
