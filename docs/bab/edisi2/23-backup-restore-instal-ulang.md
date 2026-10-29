# Bab 23. Backup, Restore, dan Instal Ulang

Tujuan: bila Proxmox perlu diinstal ulang (disk rusak, upgrade besar, atau mesin diganti), semua VM dan container dapat dipulihkan dari backup.  

## 23.1 Backup VM dan container

1. Pilih VM atau CT di panel kiri &gt; tab Backup &gt; Backup now.  
2. Storage: local (hasil di /var/lib/vz/dump). Mode: Stop untuk yang boleh dimatikan sesaat,  
Snapshot untuk yang harus tetap hidup. Compression: ZSTD.  
> Penjelasan: Mode Stop paling konsisten; Snapshot tidak mematikan layanan.
3. Klik Backup dan tunggu TASK OK.  
4. Jadwal otomatis: Datacenter &gt; Backup &gt; Add, pilih hari, jam, VM/CT, dan jumlah salinan  
(Retention).  
> Penjelasan: Backup yang dijadwalkan lebih andal daripada yang diingat.

**TERMINAL (login sebagai root)** | Shell Proxmox

```
vzdump 101 102 201 --storage local --mode snapshot --compress zstd
```
> Penjelasan: Backup beberapa VM/CT sekaligus dari terminal.
```
ls -lh /var/lib/vz/dump/
```
> Penjelasan: Melihat berkas backup yang dihasilkan.

## 23.2 Menyalin backup keluar dari server

Backup yang hanya ada di disk server ikut hilang saat Proxmox diinstal ulang. Salin keluar.  
1. Pasang WinSCP di laptop (Bab 2.2).  
2. Koneksi baru: File protocol SFTP, Host name 192.168.88.10, Port 22, user root, password root  
Proxmox. Klik Login.  
> Penjelasan: WinSCP menampilkan berkas laptop di kiri dan Proxmox di kanan.
3. Buka /var/lib/vz/dump di kanan, seret berkas vzdump-\* ke folder di HDD laptop (misalnya  
G:\Backup-Proxmox).  
> Penjelasan: Salinan di HDD aman dari kerusakan VM.
4. Simpan satu salinan lagi di tempat lain (flashdisk atau cloud) untuk data penting.  

## 23.3 Menyimpan konfigurasi host Proxmox

Backup VM tidak menyimpan pengaturan tingkat host. Simpan berkas berikut:  

**TERMINAL (login sebagai root)** | Shell Proxmox

```
tar czf /root/pve-host-config.tgz /etc/network/interfaces /etc/hosts \
  /etc/resolv.conf /etc/pve/storage.cfg /etc/pve/user.cfg \
  /etc/pve/jobs.cfg /etc/pve/firewall /etc/apt/sources.list.d
```
> Penjelasan: Mengarsipkan konfigurasi jaringan, storage, user, jadwal backup, firewall, dan repository.
```
ls -lh /root/pve-host-config.tgz
```
> Penjelasan: Memastikan arsip terbentuk.
Salin berkas .tgz ini keluar dengan WinSCP seperti 23.2.  

## 23.4 Restore

**TERMINAL (login sebagai root)** | Shell Proxmox

```
qmrestore /var/lib/vz/dump/vzdump-qemu-201-TANGGAL.vma.zst 201 --storage local-lvm
```
> Penjelasan: Memulihkan VM 201 dari backup ke storage local-lvm.
```
pct restore 101 /var/lib/vz/dump/vzdump-lxc-101-TANGGAL.tar.zst \
  --storage local-lvm
```
> Penjelasan: Memulihkan container 101.
Lewat web: pilih storage tempat berkas, buka Backups, pilih berkas, klik Restore, tentukan ID dan  
storage.  

## 23.5 Prosedur instal ulang dan restore

Langkah Rincian  
1. Backup lengkap Semua VM/CT di-backup dan disalin keluar; simpan pve-host-config.tgz dan Lampiran B.  
2. Instal bersih Instal Proxmox di mesin dengan IP 192.168.88.10 (Bab 6 dan 8).  
3. Jaringan Cek nama kartu (ip -br link) dan sesuaikan bridge-ports bila berubah.  
4. Repository dan update Bab 9.5 dan 9.6.  
5. Storage Buat storage dengan nama yang sama (lihat storage.cfg lama) agar restore menemukan targetnya.  
6. Restore Unggah berkas backup ke /var/lib/vz/dump (WinSCP), restore tiap VM/CT dengan ID yang sama.  
7. Periksa hardware Re-add perangkat USB (dongle Zigbee) pada HAOS; sesuaikan RAM/CPU; aktifkan Start at boot.  
8. MikroTik dan DNS MAC address VM/LXC hasil restore sama, jadi static lease tetap berlaku.  
Mengaktifkan Start at boot  
Pilih VM/CT &gt; Options &gt; Start at boot &gt; Yes. Atur urutan di Start/Shutdown order: container AdGuard  
order=1, VM lain setelahnya.  
CATATAN  
Untuk lingkungan lebih serius, pertimbangkan Proxmox Backup Server (PBS): backup incremental,  
deduplikasi, dan verifikasi, dijalankan di mesin/disk terpisah.  
KASUS NYATA - Restore berhasil tetapi tidak ada jaringan  
Gejala: VM/CT hasil restore tidak mendapat IP di mesin baru.  
Penyebab: Nama kartu fisik berbeda sehingga vmbr0 tidak terhubung ke LAN.  
Solusi: Periksa /etc/network/interfaces, ubah bridge-ports ke kartu yang benar, lalu ifreload -a.
