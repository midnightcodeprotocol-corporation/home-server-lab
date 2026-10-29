# Bab 12. STB HG680: AdGuard Home dan Tailscale

> [!IMPORTANT]
> **Catatan Revisi 3:** Bab ini adalah materi historis Edisi 2. Dalam rancangan saat ini, STB HG680 .253 menjalankan AdGuard Home saja; Tailscale subnet router ditunda sampai STB 2 tersedia, dengan CT103 Proxmox sebagai pilihan sementara. Jangan ikuti langkah pemasangan Tailscale di STB 1 dari bab ini. Gunakan [Bab 26 versi terbaru](../suplemen/26-tailscale.md) dan [status proyek](../../../../STATUS.md).


## 12.1 Ringkasan

Item Isi  
Perangkat STB HG680 (Amlogic S905x) dengan Armbian (build ophub, contoh v25.05.0, Linux 6.1)  
Peran DNS pemblokir iklan utama (AdGuard Home) dan akses jarak jauh (Tailscale subnet router)  
Alamat 192.168.88.253 (static lease MikroTik)  
Kenapa di STB Selalu hidup dan terpisah dari Proxmox, sehingga internet rumah dan akses jauh tidak mati saat  
Proxmox diutak-atik  

## 12.2 Persiapan STB

Menyambungkan dan memberi IP tetap  
1. Colokkan STB ke port MikroTik (contoh ether4) dan nyalakan.  
> Penjelasan: STB mendapat IP DHCP sementara dari MikroTik.
2. Di MikroTik: IP &gt; DHCP Server &gt; Leases, cari STB (hostname armbian), Make Static, ubah  
Address menjadi 192.168.88.253.  
> Penjelasan: Resep di Bab 3.5.
3. Reboot STB agar mengambil alamat baru.  

**TERMINAL MIKROTIK** | WinBox &gt; New Terminal

```
/ip dhcp-server lease print
```
> Penjelasan: Mencari baris STB dan nomornya.
```
/ip dhcp-server lease make-static numbers=0
```
> Penjelasan: Menjadikan lease nomor 0 sebagai statis (ganti 0 dengan nomor STB).
```
/ip dhcp-server lease set numbers=0 address=192.168.88.253 comment="stb-adguard"
```
> Penjelasan: Menetapkan alamat dan komentar.
Masuk lewat SSH (PuTTY)  
1. Buka PuTTY. Host Name 192.168.88.253, Port 22, Connection type SSH, klik Open.  
> Penjelasan: Tautan unduh PuTTY ada di Bab 2.2.
2. Klik Accept pada peringatan kunci host (hanya pertama kali).  
> Penjelasan: PuTTY menyimpan sidik jari server.
3. Login root. Password bawaan Armbian: 1234, lalu sistem meminta password baru dan  
pembuatan user.  
> Penjelasan: Pada instalasi Armbian pertama kali ada wizard yang meminta password root baru.
Atau dari PowerShell: ssh root@192.168.88.253.  
Memeriksa apakah sistem berjalan dari eMMC atau SD  

**TERMINAL (login sebagai root)** | SSH ke STB

```
lsblk
```
> Penjelasan: Daftar disk. mmcblk1 biasanya kartu SD (misal 29 GB), mmcblk2 adalah eMMC internal (misal 7,3
GB).  
```
findmnt /
```
> Penjelasan: Menunjukkan partisi root yang sedang dipakai (misal /dev/mmcblk1p2 = SD).
```
df -h /
```
> Penjelasan: Ukuran dan sisa ruang partisi root.
Contoh hasil: sistem aktif ada di SD (mmcblk1)  
NAME SIZE TYPE MOUNTPOINTS  
mmcblk1 29.7G disk  
+-mmcblk1p1 256M part /boot  
+-mmcblk1p2 29.4G part /  
mmcblk2 7.3G disk  
+-mmcblk2p1 256M part  
+-mmcblk2p2 7G part  
KASUS NYATA - Dua instalasi Armbian di satu STB  
Gejala: Tidak jelas sistem aktif ada di eMMC atau SD. lsblk memperlihatkan mmcblk1 (SD 29 GB) dan  
mmcblk2 (eMMC 7,3 GB).  
Penyebab: eMMC masih menyimpan instalasi lama (label BOOT_EMMC dan ROOTFS_EMMC) sedangkan  
SD menjalankan instalasi baru.  
Solusi: Pastikan dengan findmnt /. Pilih satu. Untuk menjalankan dari eMMC gunakan armbian-install  
lalu cabut SD setelah selesai. Pada pengalaman proyek lain Armbian di eMMC kadang layar kosong setelah  
STB dimatikan; simpan SD cadangan dan periksa /boot/uEnv.txt (contoh  
FDT=/dtb/amlogic/meson-gxl-s905x-p212.dtb).  
Memperbarui sistem dan pengaturan dasar  

**TERMINAL (login sebagai root)** | SSH ke STB (root)

```
apt update && apt full-upgrade -y
```
> Penjelasan: Memperbarui paket Armbian (tanpa sudo karena login root).
```
apt install -y curl nano
```
> Penjelasan: Memasang curl dan nano.
```
hostnamectl set-hostname stb-adguard
```
> Penjelasan: Memberi nama STB.
```
timedatectl set-timezone Asia/Jakarta
```
> Penjelasan: Mengatur zona waktu WIB agar log AdGuard benar.

## 12.3 Instal dan konfigurasi AdGuard Home

Membebaskan port 53  
Ubuntu/Debian memakai systemd-resolved yang menahan port 53 pada alamat 127.0.0.53, sehingga  
AdGuard tidak bisa memakai port itu. Matikan "stub listener"-nya.  

**TERMINAL (login sebagai root)** | SSH ke STB

```
nano /etc/systemd/resolved.conf
```
> Penjelasan: Buka berkas. Di bagian [Resolve] ubah/tambahkan DNSStubListener=no (hapus tanda # jika
ada).  
```
mv /etc/resolv.conf /etc/resolv.conf.backup
```
> Penjelasan: Mencadangkan berkas resolver lama.
```
ln -s /run/systemd/resolve/resolv.conf /etc/resolv.conf
```
> Penjelasan: Mengarahkan resolver ke berkas yang tidak memakai stub 127.0.0.53.
```
systemctl restart systemd-resolved
```
> Penjelasan: Menerapkan perubahan.
```
ss -tulpn | grep :53
```
> Penjelasan: Memeriksa: tidak boleh ada program yang menahan port 53.

**BERKAS: /etc/systemd/resolved.conf** | Bagian yang perlu ada

```
 1 [Resolve]
 2 DNSStubListener=no
Memasang AdGuard Home
```

**TERMINAL (login sebagai root)** | SSH ke STB

1  
# U=https://raw.githubusercontent.com/AdguardTeam/AdGuardHome/master/scripts  
 curl -s -S -L $U/install.sh | sh -s -- -v  
> Penjelasan: Mengunduh dan menjalankan skrip instalasi resmi. AdGuard dipasang di /opt/AdGuardHome dan
dijalankan sebagai layanan.  
```
/opt/AdGuardHome/AdGuardHome -s status
```
> Penjelasan: Memeriksa layanan berjalan.
Wizard awal (http://192.168.88.253:3000)  
AdGuard Home - Setup (langkah 2 dari 5)  
1 Admin Web Interface: listen All interfaces  
1 Admin Web Interface: port 80  
2 DNS server: listen All interfaces  
2 DNS server: port 53  
Back Next  
Gambar 12.1 - Ilustrasi wizard AdGuard. (1) Antarmuka admin di port 80. (2) Server DNS di port 53 pada semua interface.  
1. Buka http://192.168.88.253:3000 dari laptop, klik Get Started.  
> Penjelasan: Port 3000 hanya dipakai wizard awal.
2. Langkah 2: Admin Web Interface All interfaces, port 80. DNS server All interfaces, port 53. Klik  
Next.  
> Penjelasan: Port 80 untuk web admin, port 53 untuk layanan DNS.
3. Langkah 3: buat username dan password admin.  
> Penjelasan: Dipakai untuk login ke antarmuka admin.
4. Langkah 4: baca petunjuk, klik Next; langkah 5: Open Dashboard.  
> Penjelasan: Setelah ini admin ada di http://192.168.88.253 (port 80).
Konfigurasi di AdGuard Home  
1. Settings &gt; DNS settings &gt; Upstream DNS servers: isi https://dns10.quad9.net/dns-query dan  
1.1.1.1, atau pilih satu penyedia. Pilih Parallel requests.  
> Penjelasan: Upstream adalah DNS tempat AdGuard bertanya untuk situs yang tidak diblokir. Parallel requests
mengambil jawaban tercepat.  
2. Bootstrap DNS servers: 1.1.1.1, 9.9.9.9.  
> Penjelasan: Dipakai hanya untuk mengetahui alamat upstream bertipe nama (DoH).
3. Filters &gt; DNS blocklists &gt; Add blocklist &gt; Choose from the list: aktifkan daftar yang disarankan.  
> Penjelasan: Daftar blokir memuat ribuan domain iklan dan pelacak.
4. Settings &gt; General settings: aktifkan statistik dan log kueri (retensi 24 jam sampai 7 hari).  
> Penjelasan: Agar terlihat siapa meminta apa. Retensi pendek menghemat disk STB.
5. Filters &gt; DNS rewrites: akan dipakai di Bab 19 untuk nama lokal.  
Tes AdGuard  

**COMMAND PROMPT WINDOWS** | Windows (laptop)

```
nslookup google.com 192.168.88.253
```
> Penjelasan: Tes jawaban normal: harus menampilkan alamat IP.
```
nslookup doubleclick.net 192.168.88.253
```
> Penjelasan: Tes blokir: harus menjawab 0.0.0.0 (domain iklan diblokir).
Konfigurasi di MikroTik  

**TERMINAL MIKROTIK** | WinBox &gt; New Terminal

```
/ip dhcp-server network set 0 dns-server=192.168.88.253
```
> Penjelasan: Membagikan AdGuard sebagai DNS ke seluruh klien DHCP.
```
/ip dns set servers=192.168.88.253 allow-remote-requests=no
```
> Penjelasan: DNS untuk router sendiri.

**COMMAND PROMPT WINDOWS** | Windows (laptop)

```
ipconfig /renew
```
> Penjelasan: Meminta DHCP ulang agar laptop memakai DNS baru.
```
ipconfig /all
```
> Penjelasan: Memeriksa baris DNS Servers: harus 192.168.88.253.
Backup AdGuard  

**POWERSHELL WINDOWS** | PowerShell (laptop)

```
scp root@192.168.88.253:/opt/AdGuardHome/AdGuardHome.yaml .
```
> Penjelasan: Menyalin berkas konfigurasi lengkap ke folder aktif di laptop. Atau pakai WinSCP.

## 12.4 Instal dan konfigurasi Tailscale

Tailscale membuat jaringan privat antar perangkat Anda tanpa membuka port di router. Dengan subnet  
router, STB membuat seluruh jaringan 192.168.88.0/24 dapat dijangkau dari HP/laptop di mana saja:  
halaman MikroTik, Proxmox, Nextcloud, dan lainnya.  
Instalasi pada STB  

**TERMINAL (login sebagai root)** | SSH ke STB (root)

```
curl -fsSL https://tailscale.com/install.sh | sh
```
> Penjelasan: Mengunduh dan memasang Tailscale resmi untuk Debian/Armbian.
```
echo 'net.ipv4.ip_forward = 1' > /etc/sysctl.d/99-tailscale.conf
```
> Penjelasan: Mengaktifkan penerusan paket IPv4 agar STB dapat berfungsi sebagai router.
```
echo 'net.ipv6.conf.all.forwarding = 1' >> /etc/sysctl.d/99-tailscale.conf
```
> Penjelasan: Mengaktifkan penerusan IPv6.
```
sysctl -p /etc/sysctl.d/99-tailscale.conf
```
> Penjelasan: Menerapkan pengaturan tanpa reboot.
```
tailscale up --advertise-routes=192.168.88.0/24 --accept-dns=false
```
> Penjelasan: Menghubungkan STB ke akun Tailscale dan mengumumkan jaringan rumah.
--accept-dns=false mencegah Tailscale mengubah DNS di STB yang menjalankan AdGuard.  
Login dan persetujuan rute  
1. Perintah terakhir menampilkan tautan login. Buka di browser laptop dan masuk (akun Google,  
Microsoft, atau GitHub).  
> Penjelasan: Mendaftarkan STB ke akun Anda.
2. Buka login.tailscale.com/admin/machines. Pada baris STB klik ... &gt; Edit route settings, centang  
192.168.88.0/24, Save.  
> Penjelasan: Rute yang diumumkan tidak aktif sebelum Anda menyetujuinya.
3. Pada menu ... yang sama pilih Disable key expiry.  
> Penjelasan: Agar STB tidak terputus saat kunci kedaluwarsa (default sekitar 180 hari).
4. Opsional: di DNS &gt; Add nameserver &gt; Custom isi 192.168.88.253 dan aktifkan Override local  
DNS.  
> Penjelasan: Perangkat Anda di luar rumah memakai AdGuard rumah, sehingga iklan terblokir di mana saja.
Menyambungkan HP dan laptop  
1. Pasang aplikasi Tailscale (HP, Windows, macOS) dan login dengan akun yang sama.  
> Penjelasan: Windows, Android, dan iOS menerima rute subnet secara otomatis. Linux perlu tailscale up
--accept-routes.  
2. Matikan WiFi di HP (pakai data seluler) dan buka http://192.168.88.1 atau  
https://192.168.88.10:8006.  
> Penjelasan: Jika halaman terbuka, akses jarak jauh sudah bekerja.

**TERMINAL (login sebagai root)** | SSH ke STB

```
tailscale status
```
> Penjelasan: Menampilkan perangkat dalam jaringan Tailscale dan statusnya.
```
tailscale ip -4
```
> Penjelasan: Menampilkan alamat Tailscale STB (100.x.y.z).
Konfigurasi di MikroTik  
CATATAN  
Tidak ada rute atau port forward yang perlu ditambahkan di MikroTik. Tailscale mengubah alamat sumber paket  
(SNAT) sehingga perangkat rumah membalas langsung ke STB. Cukup pastikan STB mendapat IP tetap (12.2).  
PERINGATAN  
Jangan membuka port 8006, 22, atau 80 MikroTik ke internet. Seluruh akses jarak jauh cukup lewat Tailscale.  
Cadangan dan masalah umum  
• Subnet router cadangan bisa dipasang di LXC Proxmox (Bab 13.8) untuk berjaga jika STB mati.  
• Bila subnet tidak terjangkau dari luar: pastikan rute disetujui, sysctl net.ipv4.ip_forward bernilai  
1, dan jaringan tempat Anda berada tidak memakai subnet yang sama (192.168.88.0/24).  
• Jika STB mati, akses jarak jauh dan DNS utama berhenti: itu sebabnya DNS kedua (Bab 13) penting.  
KASUS NYATA - Subnet tidak bisa dijangkau dari luar rumah  
Gejala: Setelah tailscale up, alamat 192.168.88.x tidak terbuka dari HP.  
Penyebab: Rute belum disetujui, IP forwarding belum aktif, atau jaringan tempat Anda berada memakai subnet  
yang sama.  
Solusi: Setujui rute di konsol admin, cek sysctl net.ipv4.ip_forward, dan bila bentrok subnet  
pertimbangkan mengganti rentang jaringan rumah.  
KASUS NYATA - AdGuard gagal start karena port 53 dipakai  
Gejala: Wizard atau layanan menolak karena address already in use pada port 53.  
Penyebab: systemd-resolved memakai 127.0.0.53:53.  
Solusi: Atur DNSStubListener=no (12.3), restart systemd-resolved, lalu restart AdGuard.
