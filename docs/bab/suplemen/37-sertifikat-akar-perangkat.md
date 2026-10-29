# Bab 37. Memasang Sertifikat Akar di Perangkat

PENEMPATAN - TIDAK ADA GUEST  
Tempat: Langkah di perangkat klien. Tidak ada VM/LXC baru.  
Caddy menandatangani sertifikat layanan dengan otoritas lokal-nya. Agar perangkat percaya, sertifikat akar  
otoritas itu dipasang sekali di tiap perangkat. Yang dipasang hanya sertifikat akar (berkas root.crt, publik), bukan  
kunci privat.  

## 37.1 Mengambil sertifikat akar dari server

**TERMINAL VM DEBIAN** | Sebagai root

```
cp /opt/stacks/caddy/data/caddy/pki/authorities/local/root.crt /root/caddy-root.crt
```
> Penjelasan: Menyalin hanya berkas root.crt ke lokasi mudah. Jangan menyalin berkas root.key di folder yang
sama; itu kunci privat.  
```
ls -l /root/caddy-root.crt
```
> Penjelasan: Memastikan berkas ada dan ukurannya tidak nol.

**POWERSHELL WINDOWS** | PowerShell (laptop)

```
scp <USER>@192.168.88.20:/root/caddy-root.crt .
```
> Penjelasan: Karena login root SSH dimatikan (Suplemen 1), ambil berkas lewat pengguna biasa; salin dulu
berkasnya ke home pengguna itu bila izin menolak. Alternatif: ambil lewat Portainer atau WinSCP dengan akun  
pengguna biasa.  
TIPS  
Jika izin menolak, jalankan di VM: cp /root/caddy-root.crt /home/&lt;USER&gt;/ && chown &lt;USER&gt;  
/home/&lt;USER&gt;/caddy-root.crt, lalu scp berkas itu dari folder home.  
Setelah berkas ada di laptop, kirim ke HP: lewat kabel USB (Android), email ke diri sendiri, Google Drive atau  
iCloud Drive, atau Telegram. Berkas ini aman dikirim karena hanya berisi sertifikat publik.  

## 37.2 Laptop Windows

Cara A: dengan antarmuka  
1. Klik dua kali caddy-root.crt &gt; Install Certificate.  
2. Pilih Local Machine (butuh izin administrator) atau Current User, klik Next.  
3. Pilih Place all certificates in the following store &gt; Browse &gt; Trusted Root Certification Authorities &gt; OK  
&gt; Next &gt; Finish.  
4. Konfirmasi peringatan keamanan dengan Yes. Tutup lalu buka ulang browser.  
Cara B: dengan PowerShell  

**POWERSHELL WINDOWS** | PowerShell sebagai Administrator

1  
PS&gt; Import-Certificate -FilePath "$env:USERPROFILE\caddy-root.crt" -CertStoreLocation  
Cert:\LocalMachine\Root  
> Penjelasan: Memasang sertifikat akar ke penyimpanan tepercaya Windows. Sesuaikan lokasi berkas. Chrome
dan Edge memakai penyimpanan ini.  
CATATAN  
Firefox memiliki penyimpanan sendiri. Impor di Settings &gt; Privacy & Security &gt; Certificates &gt; View Certificates &gt;  
Authorities &gt; Import lalu centang "Trust this CA to identify websites".  

## 37.3 HP Android

1. Salin caddy-root.crt ke HP (folder Download).  
2. Pastikan HP memakai kunci layar (PIN, pola, atau sidik jari); Android mewajibkannya untuk memasang  
sertifikat.  
3. Buka Pengaturan &gt; Keamanan dan privasi &gt; Keamanan lainnya &gt; Enkripsi dan kredensial &gt; Instal  
sertifikat &gt; Sertifikat CA. (Nama menu berbeda antar merek HP; cari kata "Install a certificate" atau "Instal  
sertifikat".)  
4. Muncul peringatan bahwa jaringan bisa dipantau. Ketuk Instal saja dan pilih berkas caddy-root.crt.  
5. Buka Chrome dan kunjungi https://kuma.home.arpa (Tailscale aktif bila di luar rumah). Gembok harus tampil  
tanpa peringatan.  
PERINGATAN  
Android akan menampilkan pemberitahuan tetap "Jaringan mungkin dipantau" selama sertifikat pengguna terpasang.  
Itu normal untuk CA yang Anda pasang sendiri.  
Sertifikat ini dipercaya oleh browser. Aplikasi lain (Gotify, DAVx5, Bitwarden) bisa menolaknya; uji satu per satu.  
Untuk Gotify, tetap pakai http://192.168.88.20:8070. Jika sebuah aplikasi bersikeras, pertimbangkan Jalur 2 (Bab 38).  
37.4 iPhone  
1. Kirim caddy-root.crt ke iPhone (iCloud Drive, email ke diri sendiri, atau AirDrop dari Mac). Buka dari aplikasi  
Files atau email dan ketuk berkasnya.  
2. Muncul "Profile Downloaded". Buka Pengaturan &gt; Umum &gt; VPN & Manajemen Perangkat, ketuk profil yang  
diunduh, lalu Pasang dan masukkan kode.  
3. Langkah yang sering terlewat: buka Pengaturan &gt; Umum &gt; Tentang &gt; Pengaturan Kepercayaan  
Sertifikat dan aktifkan sakelar untuk "Caddy Local Authority - ... Root". Tanpa ini sertifikat terpasang tetapi  
belum dipercaya.  
4. Buka Safari ke https://kuma.home.arpa (Tailscale aktif bila di luar rumah). Gembok harus tampil tanpa  
peringatan.  

## 37.5 Memeriksa dan merawat

Hal Penjelasan  
Masa berlaku Sertifikat akar Caddy berlaku sangat lama (sekitar 10 tahun); sertifikat layanan diperbarui otomatis  
oleh Caddy. Anda tidak perlu mengurusnya.  
Backup Folder /opt/stacks/caddy/data wajib dicadangkan. Jika hilang, Caddy membuat otoritas baru dan  
semua perangkat harus memasang akar baru.  
Perangkat hilang Hapus sertifikat akar dari perangkat lain bukan keharusan, tetapi jangan biarkan kunci privat bocor  
dari server.  
Memeriksa penerbit Di browser buka detail sertifikat: penerbit tertulis Caddy Local Authority.
