# Bab 50. Proxmox Backup Server

> **Status 2 November 2026.** Pengguna memutuskan kedua HDD 2 TB digunakan untuk data aplikasi; backup sementara memakai NVMe. PBS 212 di `.30` telah diuji ping 3/3 dan HTTPS 8007 HTTP 200 setelah hard reset. Volume disk qcow2 1.5 TiB pada HDD dilepas dari VM tanpa dihapus. Disk virtual baru 100 GiB dari `local-lvm`/NVMe terpasang sebagai scsi1, pengguna melaporkan datastore `store1` dibuat; belum diverifikasi dari dashboard dan belum ada backup.

PENEMPATAN - BARU - VM sendiri  
Tempat: VM 212 pbs (192.168.88.30), dipasang dari ISO resmi PBS, bukan dari templat Debian (VM 200).  
Alasan: Server backup harus terpisah dari yang dicadangkan. Dokumentasi PBS menyebut server atau VM khusus;  
memasang PBS di host Proxmox hanya sebuah opsi dan tidak dipakai di sini agar host tetap polos.  
Tidak boleh: Digabung dengan layanan lain, dan tidak ikut dicadangkan oleh jobnya sendiri.  
Batas yang jujur: PBS di mesin yang sama melindungi dari salah hapus, korupsi, dan kebobolan di dalam guest,  
tetapi tidak dari kerusakan disk atau mesin. Karena itu datastore di disk fisik terpisah (50.2) dan ada salinan  
kedua (50.13).  
Proxmox Backup Server menyimpan backup VM secara terdeduplikasi dan bertahap: hanya bagian yang  
berubah yang disimpan, sehingga backup harian murah. Backup bisa dienkripsi di sisi klien (PVE) sehingga  
server tidak bisa membacanya.  

## 50.1 Gambaran dan keputusan

Keputusan Pilihan buku ini Alasan  
Tempat PBS VM 212 di host yang sama Satu mesin tersedia; ditutup oleh salinan kedua  
50.13  
Datastore Sementara pada NVMe; HDD untuk aplikasi Pengguna mengubah prioritas; disk virtual 100 GiB terpasang; `store1` dilaporkan dibuat pengguna, menunggu verifikasi
Jenis disk SSD bila ada; HDD diterima dengan harapan  
lambat  
Dokumentasi PBS menyarankan penyimpanan  
lokal yang cepat; HDD memperlambat verifikasi,  
GC, dan pemulihan [BELUM PASTI]  
Enkripsi Aktif (AES-256-GCM, kunci dari PVE) Isi backup tidak terbaca dari sisi PBS; kunci  
wajib disimpan terpisah  
Penghapusan backup lama Dilakukan di sisi PBS Pengguna PVE hanya boleh menambah backup,  
tidak menghapus (lebih aman bila host PVE  
kebobolan)  

## 50.2 Menyiapkan disk fisik untuk datastore (host)

**Keputusan terbaru pengguna:** kedua HDD dialokasikan untuk data aplikasi; backup sementara di NVMe. HDD unit 1 sudah GPT/ext4 pada Proxmox Directory storage `backup-disk` di `/mnt/pve/backup-disk`. Volume qcow2 sparse 1.5 TiB telah dilepas dari PBS 212 tanpa dihapus; disk virtual 100 GiB NVMe kini terpasang sebagai scsi1. Pengguna melaporkan datastore `store1` dibuat di disk 100 GiB; periksa dashboard PBS untuk memastikan. HDD dapat disiapkan untuk aplikasi tanpa memformat ulang.
## 50.3 Mengunduh ISO dan membuat VM pbs

1. Gunakan ISO PBS 4.2-1 resmi. ISO lokal pengguna telah diverifikasi SHA256 terhadap checksum resmi, lalu disalin ke storage local pada host.
2. VM 212 `pbs` sudah dibuat dari ISO ini; instalasi selesai menurut pengguna dan VM masih running.
3. Konfigurasi saat ini: 2 vCPU, 2 GiB RAM, VirtIO NIC, QEMU agent enabled. Disk OS SCSI 32 GiB dan disk datastore sementara 100 GiB (scsi1) berada di `local-lvm`; keduanya thin-provisioned. Disk qcow2 1.5 TiB pada HDD sudah dilepas dari VM tanpa menghapus file volumenya.
4. Instalasi selesai menurut pengguna; VM berjalan dan ISO sudah dilepas. Ringkasan installer menampilkan `.30/24`, gateway `.1`, DNS `.3`; setelah hard reset, ping 3/3 dan HTTPS 8007 HTTP 200 dari host.
PERINGATAN  
Pada pemasangan nanti, pilih disk 32 GiB sebagai target sistem. Disk besar jangan dipilih; ia dipakai untuk datastore  
sesudah pemasangan.  

## 50.4 Pemasangan PBS

Installer PBS selesai menurut laporan pengguna. Pengaturan yang ditampilkan: target OS 32 GiB, zona Asia/Jakarta, hostname `pbs`, IP `192.168.88.30/24`, gateway `.1`, DNS `.3`. Setelah hard reset, ping 3/3 dan HTTPS 8007 HTTP 200 dari host. Disk virtual 100 GiB pada NVMe telah ditambahkan ke VM; pengguna melaporkan `store1` dibuat. Verifikasi dashboard masih pending dan belum ada backup.
## 50.5 Pasca-instalasi

1. Dari laptop buka https://192.168.88.30:8007 (setujui peringatan sertifikat). Masuk: User root, Realm Linux  
PAM standard authentication.  
2. Buka Administration &gt; Repositories. Nonaktifkan repositori enterprise (Disable), lalu Add &gt;  
No-Subscription. Pesan peringatan tanpa langganan di login boleh diabaikan.  
3. Buka Administration &gt; Updates &gt; Refresh lalu Upgrade.  

## 50.6 Membuat datastore

**TERMINAL PBS** | Shell PBS: Administration &gt; Shell, atau konsol VM 212

```
lsblk -o NAME,SIZE,TYPE,MOUNTPOINT
```
> Penjelasan: Kenali disk data sekitar 100 GiB dan bedakan dari disk sistem 32 GiB. Jangan pilih disk 1.5 TiB; disk HDD sudah dilepas dari guest. Pastikan `lsblk` menunjukkan disk 100 GiB yang baru ditambahkan.
1. Di web PBS buka Administration &gt; Storage / Disks &gt; Directory &gt; Create: Directory. Pilih disk sekitar 100 GiB yang telah dipastikan lewat `lsblk`, filesystem ext4, nama `store1`, lalu centang Add as Datastore. Jangan pilih disk 32 GiB OS.
2. Datastore store1 muncul di panel kiri. Alternatif baris perintah (sintaks belum saya verifikasi [BELUM PASTI]):  
proxmox-backup-manager disk fs create store1 --disk sdb --filesystem ext4 --add-datastore true.  

## 50.7 Pengguna khusus untuk Proxmox VE

1. Buka Configuration &gt; Access Control &gt; User Management &gt; Add: User name pve, Realm Proxmox  
Backup authentication server, kata sandi kuat (simpan di Vaultwarden).  
2. Tab Permissions &gt; Add &gt; User Permission: Path /datastore/store1, User pve@pbs, Role  
DatastoreBackup, Propagate dicentang.  
Peran DatastoreBackup memungkinkan membuat dan memulihkan backup miliknya tanpa menghapus backup  
lain; nama peran dan batasnya [BELUM PASTI] - periksa di daftar Role pada PBS. Penghapusan backup lama  
ditangani job prune di PBS (50.11), bukan oleh PVE.  

## 50.8 Sidik jari sertifikat PBS

1. Di Dashboard PBS klik Show Fingerprint dan salin nilainya (deretan heksadesimal berpasangan).  

**TERMINAL PBS** | Shell PBS (alternatif)

```
proxmox-backup-manager cert info | grep -i fingerprint
```
> Penjelasan: Menampilkan sidik jari yang sama dari baris perintah.

## 50.9 Menambahkan PBS ke Proxmox VE

1. Di web Proxmox: Datacenter &gt; Storage &gt; Add &gt; Proxmox Backup Server.  
2. ID pbs-home, Server 192.168.88.30, Username pve@pbs, Password, Datastore store1, Fingerprint tempel  
dari 50.8.  
3. Tab Encryption: pilih Auto-generate a client encryption key lalu Add.  
4. Simpan kunci enkripsi yang ditampilkan. Salin ke Vaultwarden (catatan aman atau lampiran) dan cetak  
satu salinan di kertas yang disimpan terpisah.  
PERINGATAN  
Tanpa kunci ini backup terenkripsi tidak bisa dipulihkan, termasuk bila host Proxmox rusak. Kunci hanya ada  
di host PVE (di /etc/pve/priv/storage/); jika host hilang dan Anda tidak menyalinnya, backup di PBS menjadi tak  
berguna. Ini risiko terbesar bab ini.  
CATATAN  
Alternatif baris perintah ada di dokumentasi (pvesm add pbs), tetapi memasukkan kata sandi di baris perintah tercatat  
di riwayat shell; antarmuka web lebih aman untuk langkah ini.  

## 50.10 Job backup terjadwal

1. Pastikan setiap VM yang dicadangkan memiliki opsi QEMU Guest Agent aktif (Options) dan agen terpasang  
(sudah ada di templat 49).  
2. Datacenter &gt; Backup &gt; Add: Node pve, Storage pbs-home, Schedule 02:00 (setiap hari), Selection mode  
Include selected VMs: 201, 202, 203, 204, 205, 206, 207, 208, 209, 210, 211, 213, 214 (disk pustaka musik  
VM 211 ditandai backup=0 di Bab 53.1; disk foto VM 214 ikut backup, Bab 55.8). Jangan mencentang 212  
(pbs) dan 200 (templat). Mode Snapshot.  
3. Tab Retention: centang Keep all backups (penghapusan dilakukan di PBS).  
4. Pilih job &gt; Run now. Lihat tab Tasks: setiap VM harus selesai dengan TASK OK.  
Backup tingkat VM (snapshot) melindungi seluruh isi VM. Dump logis yang dibuat di bab lama (pg_dump, tar)  
tetap berguna sebagai lapisan kedua: bisa dipulihkan per aplikasi tanpa memulihkan satu VM utuh.  

## 50.11 Prune, garbage collection, dan verifikasi (di PBS)

1. Di PBS pilih store1 &gt; Prune & GC &gt; Add Prune Job: Schedule daily 03:00, Keep Last 3, Daily 7, Weekly 4,  
Monthly 3 (contoh retensi; sesuaikan dengan disk).  
2. Atur Garbage Collection Schedule pada Options datastore, misalnya sat 04:00.  
3. Buka Verify Jobs &gt; Add: Schedule daily 05:00, centang Skip verified, verifikasi ulang setelah 30 hari.  
CATATAN  
Prune hanya menandai backup lama untuk dibuang; ruang baru kembali setelah garbage collection berjalan. GC  
tidak langsung membuang data yang baru dihapus (ada masa tunggu sekitar satu hari [BELUM PASTI]), jadi ruang  
tidak turun seketika.  

## 50.12 Uji pemulihan (wajib)

Backup yang belum pernah dipulihkan belum terbukti. Pulihkan satu VM kecil ke ID sementara:  
1. Datacenter &gt; Storage &gt; pbs-home &gt; VM Backups: pilih backup VM 209 &gt; Restore.  
2. VM ID 999, centang Unique (alamat MAC baru), jangan centang Start after restore.  
3. Sebelum menyalakan: VM 999 &gt; Hardware &gt; Network Device &gt; Edit &gt; centang Disconnect. Ini mencegah  
salinan memakai IP, nama, atau identitas Tailscale yang sama dengan aslinya.  
4. Nyalakan VM 999 dan buka konsol: pastikan sistem naik dan data ada (misalnya docker ps, folder  
/opt/stacks). Lalu matikan dan hapus VM 999.  
KEAMANAN  
Jangan pernah menyalakan hasil pemulihan VM vault dengan jaringan tersambung sementara aslinya hidup: dua  
mesin dengan identitas Tailscale yang sama saling mengganggu.  

## 50.13 Salinan kedua di luar mesin (aturan 3-2-1)

Dokumentasi PBS membahas aturan 3-2-1: tiga salinan, dua media, satu di luar lokasi. Dengan satu mesin Anda  
minimal butuh satu salinan di media lain:  
Opsi Cara Catatan  
A. Disk USB (disarankan  
sekarang)  
Node &gt; Disks &gt; pilih disk USB &gt; Directory &gt; Create (ext4, nama  
usb-backup); Datacenter &gt; Backup &gt; Add job mingguan ke  
storage usb-backup, Selection 205 dan 207 (vault, nextcloud)  
atau semua, retensi Keep Last 2  
Colokkan hanya saat job  
berjalan, lalu lepas;  
salinan offline tahan  
ransomware  
B. PBS kedua + Sync Job Server PBS di lokasi lain, lalu Sync Job dari store1 Terbaik, tetapi butuh  
perangkat dan lokasi  
kedua; untuk nanti  
C. Konfigurasi host Proxmox Perintah di bawah, lalu salin ke laptop Wajib: berisi definisi VM  
dan penyimpanan  

**TERMINAL HOST PROXMOX** | Shell node Proxmox (host), sebagai root

```
tar czf /root/pve-config-$(date +%F).tgz /etc/pve /etc/network/interfaces /etc/hosts /etc/fstab
```
> Penjelasan: Mengarsipkan konfigurasi host (termasuk kunci enkripsi backup di /etc/pve/priv). Perlakukan sebagai rahasia.  

**POWERSHELL WINDOWS** | PowerShell (laptop)

```
scp root@192.168.88.10:/root/pve-config-*.tgz .
```
> Penjelasan: Menyalin arsip ke laptop. Simpan di tempat aman, bukan di folder yang disinkronkan ke layanan
publik.  

## 50.14 Notifikasi ke Gotify

1. Di Gotify (Suplemen 3 Bab 32) buat aplikasi baru proxmox dan salin tokennya.  
2. Di Proxmox: Datacenter &gt; Notifications &gt; Targets &gt; Add &gt; Gotify. Server URL http://192.168.88.20:8070,  
Token tadi, lalu Test.  
3. Buka tab Notification Matchers &gt; Add: kecocokan tingkat warning dan error (atau semua kategori backup),  
target gotify. Nama menu persis [BELUM PASTI] menurut versi Proxmox 9.2.  
4. Di PBS: Configuration &gt; Notifications dengan cara serupa agar kegagalan prune, GC, atau verifikasi juga  
sampai ke HP.  

## 50.15 Sisi klien

Perangkat Yang dilakukan Catatan  
Windows Kelola PBS di https://192.168.88.30:8007; ambil arsip konfigurasi  
host dengan scp  
Pekerjaan utama dari sini  
Android Aplikasi Gotify menerima peringatan backup; buka dasbor PBS  
lewat Tailscale bila perlu  
Aktifkan notifikasi Gotify (Suplemen 3  
Bab 32)  
iPhone Sama; pastikan notifikasi Gotify diizinkan di Pengaturan iOS Peringatan sertifikat PBS disetujui di  
Safari
