# Bab 8. Instalasi Proxmox VE, Layar demi Layar

Bab ini berlaku untuk instalasi di mesin asli (ThinkCentre M710q). Mesin di-boot dari USB, lalu langkah di installer sama untuk semua mesin.  
CATATAN  
Gambar di bab ini adalah ilustrasi skematis tata letak layar installer. Tampilan asli bisa sedikit berbeda, tetapi  
nama kolom dan urutannya sama.  

## 8.1 Siapkan data ini sebelum mulai

Data Nilai yang dipakai di buku Catatan  
Hostname (FQDN) pve.lab.local Nama lengkap server. Bagian depan (pve) menjadi nama  
node.  
Alamat IP/CIDR 192.168.88.10/24 Di luar rentang DHCP MikroTik (.100 - .254).  
Gateway 192.168.88.1 Alamat MikroTik.  
DNS 192.168.88.253 AdGuard di STB. Jika belum ada, pakai 1.1.1.1.  
Password root (buat sendiri, kuat) Simpan di password manager. Jangan sampai lupa.  
Email bebas, contoh  
admin@lab.local  
Untuk notifikasi sistem.  

## 8.2 Boot installer

1. Boot dari USB (Bab 6.4).  
> Penjelasan: Tekan F12 saat logo Lenovo muncul, lalu pilih flashdisk (entri berawalan UEFI).
2. Pada menu hitam-biru, pilih Install Proxmox VE (Graphical) lalu tekan Enter.  
> Penjelasan: Mode grafis memudahkan pemilihan dengan mouse.
Pilihan di menu boot Fungsi  
Install Proxmox VE (Graphical) Pilihan normal.  
Install Proxmox VE (Terminal UI) Installer berbasis teks. Pakai jika layar grafis bermasalah atau terlalu  
kecil.  
Install Proxmox VE (Terminal UI, Serial Console) Untuk server tanpa monitor lewat konsol serial.  
Advanced Options Debug mode, Rescue Boot (memperbaiki instalasi yang ada), dan  
Test memory (Memtest).  
PERINGATAN  
Jika muncul peringatan No support for KVM virtualization detected, VT-x belum aktif di BIOS (Bab 27.5). Installer tetap bisa  
dilanjutkan, tetapi VM di dalam Proxmox nanti tidak bisa berjalan normal.  

## 8.3 Layar 1: persetujuan lisensi

Klik I agree. Ini adalah lisensi AGPL v3 Proxmox. Tidak ada yang perlu diisi.  

## 8.4 Layar 2: Target Harddisk

Proxmox VE Installer - Target Harddisk  
1 Target harddisk /dev/nvme0n1 (465.76GiB, NVMe SSD 500GB)  
2 Filesystem (klik Options) ext4  
hdsize 465.8  
swapsize (otomatis)  
maxroot / minfree / maxvz (kosongkan)  
Options Next  
Gambar 8.1 - Ilustrasi layar Target Harddisk. (1) Pilih disk tujuan. (2) Pilih filesystem lewat tombol Options.  
1. Pada Harddisk, pilih disk tujuan.  
> Penjelasan: Pilih NVMe 500 GB (nvme0n1). Jangan memilih HDD 2 TB (lepas dari mesin selama instalasi). Seluruh isi disk akan dihapus.
2. Klik Options untuk memilih filesystem.  
> Penjelasan: Menentukan cara disk diformat. Lihat tabel di bawah.
3. Klik Next.  
Filesystem Cocok untuk Catatan  
ext4 (bawaan) Lab, satu disk, RAM kecil Ringan dan sederhana. Membuat storage local  
dan local-lvm. Pilihan untuk M710q (satu NVMe).  
xfs Alternatif ext4 Mirip ext4.  
ZFS (RAID0) Satu disk dengan fitur ZFS Butuh RAM lebih besar; berguna untuk snapshot  
dan kompresi.  
ZFS (RAID1/mirror) Mesin asli dengan 2 SSD Pelindung dari satu disk rusak. Disarankan di  
server asli bila ada 2 disk identik.  
ZFS (RAIDZ-1/2/3, RAID10) Mesin asli dengan 3+ disk Butuh RAM besar (16 GB atau lebih).  
Btrfs Eksperimen Masih dianggap teknologi preview pada Proxmox.  
Opsi lanjutan Arti Nilai  
hdsize Total ruang disk yang dipakai instalasi (GB) Biarkan penuh  
Opsi lanjutan Arti Nilai  
swapsize Ukuran swap (memori cadangan di disk) Biarkan otomatis  
maxroot Ukuran maksimum partisi sistem (root) Biarkan  
minfree Ruang kosong yang disisakan dalam LVM Biarkan  
maxvz Ukuran maksimum storage data local-lvm Biarkan  
TIPS  
Jika mesin asli memiliki satu SSD kecil (untuk sistem) dan satu HDD besar (untuk data), instal Proxmox hanya  
di SSD, lalu tambahkan HDD sebagai storage setelah instalasi (Bab 9.9).  

## 8.5 Layar 3: lokasi, zona waktu, dan keyboard

Proxmox VE Installer - Location and Time Zone selection  
1 Country Indonesia  
2 Time zone Asia/Jakarta  
3 Keyboard Layout U.S. English  
Previous Next  
Gambar 8.2 - Ilustrasi layar lokasi. (1) Negara. (2) Zona waktu. (3) Tata letak keyboard.  
1. Country: ketik atau pilih Indonesia.  
> Penjelasan: Menentukan mirror unduhan dan zona waktu otomatis.
2. Time zone: Asia/Jakarta (WIB). Gunakan Asia/Makassar atau Asia/Jayapura untuk WITA/WIT.  
> Penjelasan: Waktu yang benar penting untuk log, jadwal backup, dan sertifikat.
3. Keyboard Layout: U.S. English.  
> Penjelasan: Hampir semua keyboard di Indonesia berlayout US. Salah layout membuat tanda tertentu (|, \, /)
salah saat mengetik password.  

## 8.6 Layar 4: password dan email

Proxmox VE Installer - Administration Password and Email Address  
1 Password \*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*  
1 Confirm \*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*  
2 Email admin@lab.local  
Previous Next  
Gambar 8.3 - Ilustrasi layar password. (1) Password root diisi dua kali. (2) Email administrator.  
1. Isi Password dan Confirm dengan password root yang kuat.  
> Penjelasan: Password ini dipakai untuk login web dan login konsol/SSH sebagai root. Panjang minimal 8
karakter; gunakan 12 atau lebih.  
2. Isi Email.  
> Penjelasan: Dipakai Proxmox mengirim peringatan (misalnya backup gagal). Boleh diisi email apa saja jika
belum mengatur pengiriman email.  
PERINGATAN  
Jangan lupa password root. Memulihkannya butuh boot ke mode rescue.  

## 8.7 Layar 5: konfigurasi jaringan manajemen

Proxmox VE Installer - Management Network Configuration  
1 Management Interface enp0s31f6 - XX:XX:XX:XX:XX:XX (e1000e)  
2 Hostname (FQDN) pve.lab.local  
3 IP Address (CIDR) 192.168.88.10 / 24  
4 Gateway 192.168.88.1  
5 DNS Server 192.168.88.253  
Previous Next  
Gambar 8.4 - Ilustrasi layar jaringan. Nilai di sini adalah yang dipakai di buku (jaringan MikroTik).  
1. Management Interface: pilih kartu jaringan yang tersambung ke LAN.  
> Penjelasan: Di VM biasanya hanya satu. Di mesin asli pilih port yang tercolok kabel ke MikroTik. Nama kartu
(contoh enp0s31f6, enp3s0) akan dipakai bridge vmbr0.  
2. Hostname (FQDN): pve.lab.local.  
> Penjelasan: Nama lengkap server. Bagian pertama menjadi nama node.
3. IP Address (CIDR): 192.168.88.10 / 24.  
> Penjelasan: Alamat tetap Proxmox. /24 berarti jaringan 192.168.88.x.
4. Gateway: 192.168.88.1.  
> Penjelasan: Alamat MikroTik. Tanpa gateway yang benar Proxmox tidak bisa ke internet.
5. DNS Server: 192.168.88.253 (AdGuard) atau 1.1.1.1 jika AdGuard belum siap.  
> Penjelasan: Tanpa DNS yang benar apt update gagal dengan "Temporary failure resolving".
PERINGATAN  
Alamat IP, gateway, dan DNS harus berada di jaringan yang sama dengan laptop/komputer Anda (tiga  
angka depan sama). Jika Anda sedang berada di jaringan lain (misalnya 192.168.2.x), isi dengan alamat  
jaringan itu dan ubah nanti (Bab 9.3).  
TIPS  
Installer biasanya sudah mengisi kolom ini dari DHCP. Periksa nilainya, lalu ganti IP menjadi alamat tetap yang  
Anda rencanakan.  

## 8.8 Layar 6: ringkasan dan instalasi

Proxmox VE Installer - Summary  
Filesystem ext4  
Disk /dev/sda  
Country / Time zone Indonesia / Asia/Jakarta  
Keyboard / Email us / admin@lab.local  
Management interface enp0s31f6  
1 Hostname / IP / Gateway pve.lab.local / 192.168.88.10/24 / 192.168.88.1  
2 Automatically reboot [x] centang  
Previous Install  
Gambar 8.5 - Ilustrasi layar ringkasan. (1) Periksa alamat sekali lagi. (2) Biarkan reboot otomatis tercentang.  
1. Periksa semua isi ringkasan, terutama IP, gateway, dan disk.  
> Penjelasan: Setelah klik Install, disk dihapus dan tidak bisa dibatalkan.
2. Klik Install.  
> Penjelasan: Instalasi memakan sekitar 5 sampai 15 menit (lebih lama pada HDD).
3. Tunggu hingga selesai. Jika Automatically reboot tercentang, mesin restart sendiri.  
4. Cabut USB saat mesin restart.  
> Penjelasan: Agar mesin boot dari disk, bukan dari installer lagi.

## 8.9 Setelah instalasi

Layar konsol menampilkan teks seperti berikut. Catat alamatnya.  
Contoh hasil yang benar  
Welcome to the Proxmox Virtual Environment. Please use your web browser to  
configure this server - connect to:  
 https://192.168.88.10:8006/  
pve login:  

**TERMINAL (login sebagai root)** | Konsol VM/mesin (login root dengan password dari langkah 8.6)

```
pveversion
```
> Penjelasan: Menampilkan versi Proxmox (contoh 9.2.x).
```
egrep -c '(vmx|svm)' /proc/cpuinfo
```
> Penjelasan: Menghitung baris yang berisi vmx/svm. Hasil harus lebih dari 0 (VT-x tersedia). 0 = VT-x belum
aktif di BIOS (Bab 27.5).  
```
ls -l /dev/kvm
```
> Penjelasan: Memastikan perangkat KVM ada. Tanpa ini VM di dalam Proxmox sangat lambat.
```
ip a
```
> Penjelasan: Menampilkan alamat IP. Pada vmbr0 harus ada 192.168.88.10/24.

## 8.10 Login web pertama

https://192.168.88.10:8006 - Proxmox VE Login  
1 User name root  
2 Password \*\*\*\*\*\*\*\*  
3 Realm Linux PAM standard authentication  
Language English - English  
Login  
Gambar 8.6 - Ilustrasi layar login web.  
1. Dari browser di laptop buka https://192.168.88.10:8006 (gunakan https dan port 8006).  
> Penjelasan: Proxmox hanya melayani web lewat HTTPS di port 8006.
2. Klik Advanced &gt; Proceed to ... (unsafe).  
> Penjelasan: Peringatan sertifikat muncul karena sertifikat dibuat sendiri oleh Proxmox. Wajar dan aman di
jaringan rumah.  
3. Login: User name root, Password dari langkah 8.6, Realm Linux PAM standard authentication.  
4. Jendela No valid subscription: klik OK.  
> Penjelasan: Hanya pengingat langganan berbayar. Bisa diabaikan.

## 8.11 Pertanyaan yang sering muncul saat instalasi

Masalah / pertanyaan Jawaban  
Layar installer terlalu kecil / buram Gunakan Install Proxmox VE (Terminal UI).  
Bagaimana memilih disk? Pilih NVMe 500 GB berdasarkan ukuran dan merek di daftar.  
Kolom IP kosong / berisi alamat aneh Installer tidak mendapat DHCP. Isi manual sesuai 8.1. Pastikan kabel/adapter  
bridged benar.  
Instalasi gagal di tengah ISO rusak (cek hash, Bab 2.4), RAM VM terlalu kecil (minimal 4 GB), atau disk  
bermasalah.  
Masalah / pertanyaan Jawaban  
Setelah reboot masuk installer lagi ISO/USB masih terpasang. Lepas ISO atau cabut USB.  
Layar hitam setelah reboot Tunggu 1 sampai 2 menit (boot pertama). Jika tetap, periksa mode boot (Model  
B/C: UEFI/Legacy).  
Apakah mengisi IP statis di installer  
wajib?  
Ya, Proxmox memakai IP tetap. Jangan memakai DHCP untuk host Proxmox.
