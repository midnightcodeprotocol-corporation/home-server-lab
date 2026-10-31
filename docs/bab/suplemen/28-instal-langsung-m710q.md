# Bab 28. Instal Langsung di Lenovo ThinkCentre M710q

> **Pembaruan 31 Oktober 2026.** Bab ini adalah panduan instalasi langsung di **Lenovo ThinkCentre M710q**. SSD NVMe M.2 500 GB sudah terpasang di slot 1. RAM dilaporkan 16+8 GB (24 GB total), tetapi harus dikonfirmasi di BIOS dan lulus MemTest86 **sebelum** menginstal. Periksa isi/partisi NVMe dan cadangkan data penting sebelum memilih disk target. Kartu jaringan Intel biasanya bernama `enp0s31f6` (periksa dengan `ip -br link`); BIOS F1, menu boot F12.

PENEMPATAN - HOST - mesin fisik  
Tempat: Langsung di ThinkCentre M710q (host Proxmox), bukan di dalam VM.  
Aturan: Host hanya menjalankan Proxmox. Jangan memasang Docker atau aplikasi di host; semua aplikasi masuk  
ke guest menurut Peta Penempatan (Suplemen 7 Bab 48).  
Ini cara standar dan paling disarankan untuk ThinkCentre M710q Anda: Proxmox dipasang langsung ke disk  
komputer itu. Bab ini memperluas Edisi 2 Bab 6 dengan langkah rinci, pilihan di installer, dan penanganan  
masalah.  

## 28.1 Gambaran alur dan waktu

Langkah Perkiraan waktu  
Cadangkan data dan periksa komputer (Bab 27) 30 sampai 120 menit  
Unduh dan verifikasi ISO 10 sampai 30 menit  
Membuat USB bootable 10 menit  
Mengatur BIOS dan boot dari USB 10 menit  
Instalasi di layar 10 sampai 15 menit  
Boot pertama, pemeriksaan, update 20 menit  

## 28.2 Siapkan data ini sebelum mulai

Data Nilai Catatan  
Alamat IP (CIDR) 192.168.88.10/24 Di luar rentang DHCP MikroTik (.100 sampai .254)  
Gateway 192.168.88.1 MikroTik  
DNS 192.168.88.253 AdGuard di STB; bila belum siap, 1.1.1.1  
Hostname (FQDN) pve.lab.local Harus berformat nama.domain  
Password root Kuat dan panjang Simpan di tempat aman; lupa berarti harus mode  
rescue  
Email administrator Email aktif Dipakai untuk notifikasi sistem  
Kabel LAN Dari komputer ke MikroTik Wajib terhubung saat instalasi agar IP bisa diuji  

## 28.3 Mengunduh dan memverifikasi ISO

1. Di laptop, buka proxmox.com/en/downloads dan unduh Proxmox VE ISO Installer versi 9 terbaru. Edisi 2  
memakai proxmox-ve_9.2-1.iso; versi yang lebih baru juga boleh.  
2. Di halaman yang sama catat nilai SHA256 milik berkas itu.  

**POWERSHELL WINDOWS** | PowerShell (laptop)

```
Get-FileHash -Algorithm SHA256 $env:USERPROFILE\Downloads\proxmox-ve_9.2-1.iso
```
> Penjelasan: Menghitung sidik jari berkas. Ganti nama berkas sesuai unduhan Anda. Nilai Hash harus sama persis
dengan SHA256 di situs. Jika beda, unduh ulang; berkas rusak atau tidak asli.  

## 28.4 Membuat USB bootable

Siapkan flashdisk minimal 8 GB. Semua isinya akan terhapus. ISO Proxmox adalah image hibrida, jadi cara  
menulisnya harus mode image mentah.  
Cara 1: Rufus (disarankan di Windows)  
1. Unduh Rufus dari rufus.ie dan jalankan.  
2. Pada Device, pilih flashdisk yang benar (periksa nama dan ukurannya; jangan memilih HDD).  
3. Klik SELECT dan pilih berkas ISO Proxmox.  
4. Partition scheme: GPT untuk komputer UEFI (MBR hanya untuk BIOS lama). Target system akan  
menyesuaikan.  
5. Klik START. Saat muncul pertanyaan mode penulisan, pilih Write in DD Image mode lalu OK. Dokumentasi  
Proxmox menyebut mode DD wajib agar Rufus berfungsi.  
6. Tunggu status READY, lalu cabut flashdisk dengan aman.  
Cara 2: balenaEtcher  
1. Pilih Flash from file dan pilih ISO.  
2. Pilih Select target dan pilih flashdisk.  
3. Klik Flash! dan tunggu selesai.  
CATATAN  
Ventoy praktis untuk banyak ISO tetapi pada sebagian komputer installer Proxmox bermasalah lewat Ventoy. Bila  
instalasi aneh, ulangi dengan Rufus (mode DD) atau Etcher.  

## 28.5 Boot dari USB

1. Colokkan flashdisk dan kabel LAN ke ThinkCentre M710q, lalu nyalakan sambil menekan tombol menu boot  
berulang kali (tabel Bab 27.5).  
2. Pilih flashdisk. Pilih entri yang berawalan UEFI: bila ada.  
3. Menu Proxmox muncul. Pilih Install Proxmox VE (Graphical) dan tekan Enter.  
4. Bila layar hitam, berkedip, atau rusak, restart dan pilih Install Proxmox VE (Terminal UI); urutan layarnya  
sama.  
TIPS  
Menu juga memuat Advanced Options (mode debug dan Rescue Boot). Rescue Boot dipakai bila sistem terpasang  
tetapi gagal boot (Bab 29.5).  

## 28.6 Layar demi layar di mesin asli

Tampilan lengkap tiap layar ada di Edisi 2 Bab 8. Di bawah ini hal yang khusus untuk instalasi di mesin asli.  
Layar Isi yang dipilih Perhatian di mesin asli  
1. Lisensi Klik I agree -  
2. Target Harddisk Pilih SSD NVMe 500 GB (nvme0n1). Klik Options untuk sistem berkas Periksa merek dan ukuran dengan teliti; disk ini  
akan dihapus seluruhnya. Disk lain jangan  
dipilih  
3. Lokasi dan zona  
waktu  
Indonesia, Asia/Jakarta, keyboard US Zona waktu salah membuat jam dan 2FA  
meleset  
4. Password dan email Password root kuat, email aktif Simpan password di password manager  
Layar Isi yang dipilih Perhatian di mesin asli  
5. Jaringan manajemen Interface yang terhubung kabel, hostname  
pve.lab.local, IP 192.168.88.10/24, gateway  
192.168.88.1, DNS 192.168.88.253  
Pilih interface yang statusnya terhubung; salah  
pilih berarti web tidak bisa dibuka  
6. Ringkasan Periksa semua isian, centang reboot otomatis Cabut USB saat mesin restart pertama  
Opsi disk di layar 2 (tombol Options)  
Opsi Arti Disarankan  
Filesystem ext4, XFS, BTRFS (pratinjau), ZFS ext4 untuk satu SSD (Bab 27.4)  
hdsize Ukuran disk yang dipakai installer Biarkan penuh, kecuali ingin menyisakan  
ruang di disk  
swapsize Ukuran swap Biarkan bawaan  
maxroot Ukuran maksimum partisi sistem Biarkan bawaan  
minfree Ruang kosong yang disisakan di grup volume Biarkan bawaan  
maxvz Ukuran partisi data VM (local-lvm) Biarkan bawaan  
PERINGATAN  
Pada layar 2, jika ada beberapa disk (misalnya SSD dan HDD 2 TB), pilih hanya SSD. Sebaiknya lepaskan HDD  
berisi data penting dari komputer selama instalasi untuk menghilangkan risiko salah pilih.  

## 28.7 Boot pertama dan pemeriksaan

1. Saat mesin restart, cabut USB. Mesin boot ke Proxmox dan layar menampilkan alamat  
https://192.168.88.10:8006.  
2. Dari laptop yang terhubung ke jaringan MikroTik, buka alamat itu. Peringatan sertifikat itu normal; lanjutkan,  
login root, Realm Linux PAM standard authentication.  

**TERMINAL PROXMOX** | Konsol ThinkCentre M710q atau Shell web (root)

```
pveversion
```
> Penjelasan: Menampilkan versi Proxmox yang terpasang.
```
ip -br a
```
> Penjelasan: Memeriksa alamat. Pada vmbr0 harus ada 192.168.88.10/24.
```
lscpu | grep -E "Model name|Virtualization"
```
> Penjelasan: Memastikan VT-x atau AMD-V aktif (baris Virtualization tidak kosong).
```
lsblk -o NAME,SIZE,TYPE,MODEL
```
> Penjelasan: Daftar disk. Pastikan disk yang diharapkan terlihat, termasuk HDD data.
```
free -h
```
> Penjelasan: Memeriksa jumlah RAM yang terbaca.
```
ping -c 3 192.168.88.1
```
> Penjelasan: Menguji koneksi ke MikroTik.
Lanjutkan ke Edisi 2 Bab 9.2 sampai 9.6 (mencatat di MikroTik, DNS, repository no-subscription, update), lalu Bab  
30 di suplemen ini.  

## 28.8 Masalah umum dan solusi

Gejala Penyebab Solusi  
Installer menyatakan tidak ada  
disk (no hard disk found)  
Mode SATA berupa RAID atau Intel  
RST/VMD  
Ubah SATA Mode ke AHCI di BIOS (Bab 27.5)  
Flashdisk tidak muncul di menu  
boot  
Penulisan salah, Secure Boot, atau  
mode boot tidak cocok  
Tulis ulang dengan Rufus (DD), nonaktifkan  
Secure Boot, pilih entri UEFI:  
Layar hitam atau rusak saat  
installer  
Masalah driver grafis installer Pilih Install Proxmox VE (Terminal UI)  
Tidak ada interface jaringan di  
layar 5  
Kartu LAN tidak dikenali kernel atau  
kabel tidak terpasang  
Pastikan kabel terpasang; ganti ke adaptor  
USB-LAN sementara; cari dukungan chipset  
(sebagian Realtek 2.5G butuh driver tambahan)  
Web tidak terbuka setelah  
instalasi  
IP, gateway, atau interface salah Ikuti Edisi 2 Bab 9.3: periksa  
/etc/network/interfaces dan /etc/hosts  
Mesin kembali ke installer terus USB belum dicabut Cabut USB dan restart  
Tidak mau boot tanpa keyboard BIOS menahan karena error keyboard Matikan Halt on keyboard error di BIOS
