# Bab 6. Instal Proxmox di Lenovo ThinkCentre M710q

> **Revisi 3.** Bab ini sekarang khusus untuk **Lenovo ThinkCentre M710q**. Model A (VMware) dan Model C (instal ke disk dulu) dihapus.

## 6.1 Perangkat yang dibutuhkan

| Kebutuhan | Mesin Anda (M710q) | Catatan |
|---|---|---|
| CPU | Intel Core i5-6500T (4 core, 4 thread, 35 W), mendukung VT-x dan VT-d | Cukup untuk Proxmox; thread terbatas, jangan memberi banyak core ke tiap VM |
| RAM | 16 GB terpasang; cadangan 16 GB dan 8 GB belum dipasang | Dua slot SO-DIMM DDR4. Rencana: 16 + 16 = 32 GB (Bab 27.1) |
| Disk sistem | SSD NVMe M.2 500 GB | Proxmox dan disk VM |
| Disk data / backup | HDD 2 TB | Dipasang sebagai disk kedua (bay 2,5" atau USB, Bab 27.4) |
| Jaringan | 1 port Gigabit Ethernet | Kabel ke MikroTik; jangan memakai WiFi |
| Saat instalasi | Monitor, keyboard, flashdisk 8 GB | Setelah itu dikelola lewat web |

## 6.2 Pengaturan BIOS/UEFI

Lengkapnya ada di **Bab 27.5**. Ringkasnya: aktifkan Intel Virtualization Technology (VT-x) dan VT-d, UEFI, matikan Secure Boot, SATA AHCI, Wake on LAN aktif, After Power Loss = Power On. Masuk BIOS dengan **F1** saat logo Lenovo muncul; menu boot sekali pakai dengan **F12**.

## 6.3 Membuat USB bootable

Siapkan flashdisk minimal 8 GB. Semua isinya akan dihapus. Pilih salah satu alat berikut (tautan di Bab  
2.2).  
Cara 1: Rufus (Windows)  
1. Buka Rufus, pilih flashdisk pada Device.  
> Penjelasan: Pastikan itu flashdisk yang benar, bukan HDD.
2. Klik SELECT, pilih berkas proxmox-ve_9.2-1.iso.  
3. Partition scheme: GPT untuk mesin UEFI (MBR untuk BIOS lama).  
> Penjelasan: Harus sesuai mode boot mesin tujuan.
4. Klik START. Jika muncul pertanyaan mode, pilih Write in DD Image mode.  
> Penjelasan: ISO Proxmox adalah image hybrid; mode DD memastikan struktur boot tertulis benar.
5. Tunggu sampai READY.  
Cara 2: balenaEtcher  
1. Pilih Flash from file &gt; pilih ISO.  
2. Select target &gt; pilih flashdisk.  
3. Flash! lalu tunggu selesai.  
> Penjelasan: Etcher selalu menulis sebagai image mentah.
Cara 3: Ventoy  
Pasang Ventoy ke flashdisk sekali, lalu cukup salin berkas ISO ke flashdisk. Praktis untuk banyak ISO,  
tetapi pada beberapa mesin installer Proxmox bermasalah lewat Ventoy. Jika instalasi aneh, gunakan  
Rufus DD atau Etcher.  

## 6.4 Boot dari USB

1. Colokkan USB ke mesin, nyalakan, dan tekan tombol boot menu berkali-kali.  
> Penjelasan: Tombol umum: F12, F11, F8, Esc. Tertulis di layar logo.
2. Pilih flashdisk (cari nama USB, kadang berawalan "UEFI:").  
> Penjelasan: Pilihan berawalan UEFI cocok bila mesin memakai mode UEFI.
3. Menu instalasi Proxmox muncul. Lanjut ke Bab 8.  

## 6.5 Setelah instalasi

• Cabut USB saat mesin restart pertama kali.  
• Mesin menampilkan alamat web: https://192.168.88.10:8006. Monitor dan keyboard sudah boleh  
dicabut (mesin dikelola lewat web).  
• Beberapa BIOS menolak boot tanpa keyboard; jika terjadi, matikan opsi "Halt on keyboard error" di  
BIOS.  
• Tambahkan disk data (HDD/SSD kedua) lewat Node &gt; Disks (Bab 9.9).  
PERINGATAN  
Pada layar Target Harddisk pastikan memilih disk yang benar. Disk yang dipilih akan dihapus seluruhnya.  
KASUS NYATA - Flashdisk tidak muncul di menu boot  
Gejala: Mesin langsung masuk Windows/OS lama atau menampilkan "no bootable device".  
Penyebab: Mode boot tidak cocok (GPT/MBR vs UEFI/Legacy), Secure Boot aktif, atau flashdisk belum ditulis  
dengan benar.  
Solusi: Tulis ulang dengan Rufus (DD mode), ganti skema partisi sesuai mode BIOS, matikan Secure Boot,  
dan pilih entri USB yang berawalan UEFI.
