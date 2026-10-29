# Bab 27. Mesin Anda: Lenovo ThinkCentre M710q

PENEMPATAN - TIDAK ADA GUEST. Tempat: bab ini tentang mesin fisik. Belum ada VM/LXC.

Mesin server Anda adalah **Lenovo ThinkCentre M710q (Tiny)**. Bab ini mencatat spesifikasi, rencana RAM dan disk, dan pengaturan BIOS-nya. Menu BIOS bisa berbeda antar versi; nama di bawah adalah patokan, cocokkan dengan layar Anda.

## 27.1 Spesifikasi dan kebutuhan

| Komponen | Kebutuhan | M710q Anda | Status |
|---|---|---|---|
| CPU | 64-bit dengan VT-x/AMD-V, 4 core disarankan | Core i5-6500T, 4 core / 4 thread, VT-x dan VT-d | Lulus |
| RAM | 16 GB atau lebih | 16 GB terpasang; cadangan 16 GB dan 8 GB | Lulus (target 32 GB) |
| Disk sistem | SSD 120 GB atau lebih | NVMe M.2 500 GB | Lulus |
| Disk data / backup | HDD/SSD terpisah | 2 × HDD Seagate Surveillance 2 TB, 3,5 inci | Rencana awal memakai satu unit melalui enclosure single-bay yang tersedia; HDD kedua ditunda |
| Jaringan | 1 port LAN kabel | 1 Gigabit Ethernet (Intel) | Lulus |

Spesifikasi di atas adalah patokan umum model M710q; **cek label RAM, tipe slot, dan ketebalan disk pada unit Anda sendiri** sebelum membeli atau memasang.

### Rencana RAM

| Pilihan | Total | Catatan |
|---|---|---|
| 16 GB terpasang saja | 16 GB | Memakai profil pemakaian (Bab 56) |
| **16 GB terpasang + 16 GB cadangan** | **32 GB** | Disarankan. Dua slot penuh; semua VM bisa menyala bersamaan (Bab 56.7) |
| 16 GB + 8 GB | 24 GB | Jalan, tetapi tidak simetris dan lebih sempit |
| 8 GB cadangan | - | Simpan sebagai suku cadang; slot hanya dua |

Langkah memasang RAM: matikan mesin, cabut kabel daya, buka penutup, ganti/tambah modul SO-DIMM sampai klik, pasang penutup. Gunakan modul dengan jenis dan kecepatan yang sama bila bisa. Setelah terpasang, jalankan **MemTest86 dari USB sampai 1-2 putaran penuh tanpa error** sebelum instalasi; RAM bermasalah merusak VM secara diam-diam.

## 27.2 Memeriksa spesifikasi dari Windows

Selagi M710q masih menjalankan Windows, buka PowerShell di komputer itu dan jalankan perintah  
berikut. Catat hasilnya; ini akan dipakai untuk memilih disk dan ukuran VM.  

**POWERSHELL WINDOWS** | PowerShell di M710q

```powershell
Get-CimInstance Win32_Processor | Select-Object Name, NumberOfCores, NumberOfLogicalProcessors, VirtualizationFirmwareEnabled
```
> Penjelasan: Menampilkan CPU, jumlah core, dan apakah virtualisasi sudah aktif di BIOS (True atau False).
```
Get-CimInstance Win32_PhysicalMemory | Select Capacity,Speed,Manufacturer
```
> Penjelasan: Menampilkan setiap keping RAM. Jumlahkan kapasitasnya (satuan byte; 8589934592 = 8 GB).
```
Get-PhysicalDisk | Select FriendlyName,MediaType,Size,HealthStatus
```
> Penjelasan: Menampilkan disk, jenis (SSD atau HDD), ukuran, dan status kesehatan dasar.
```
Get-NetAdapter | Select Name,InterfaceDescription,LinkSpeed
```
> Penjelasan: Menampilkan kartu jaringan. Catat merek chipset (Intel, Realtek) dan kecepatan (1 Gbps).
TIPS  
Jika VirtualizationFirmwareEnabled bernilai False, bukan berarti CPU tidak mampu; biasanya hanya belum dinyalakan  
di BIOS (Bab 27.5). Cek juga merek dan model CPU di internet untuk memastikan ada VT-x atau AMD-V.  

## 27.3 Memeriksa kesehatan komputer

M710q bisa menyimpan masalah tersembunyi. Dua jam pemeriksaan sekarang menghemat berhari-hari  
kemudian.  
Yang diperiksa Alat Lulus jika Bila gagal  
Kesehatan disk CrystalDiskInfo (gratis,  
Windows)  
Status "Baik"; tidak ada Reallocated  
atau Pending sector; SSD sisa umur  
masih tinggi  
Ganti disk. Disk rusak adalah  
penyebab kehilangan data  
nomor satu  
RAM MemTest86 dari USB, 1  
sampai 2 putaran penuh  
Nol error Cabut keping bergantian, ganti  
yang rusak  
Suhu dan kipas HWiNFO atau cek manual Suhu diam di bawah 60 derajat,  
kipas berputar dan tidak berisik  
berlebihan  
Bersihkan debu, ganti pasta  
termal  
Port LAN Colok kabel ke MikroTik Lampu LAN menyala dan IP didapat Pakai adaptor USB-LAN  
sebagai cadangan (kurang  
ideal)  
Baterai laptop Lihat fisik Tidak menggembung Lepas baterai, pakai tanpa  
baterai  
Tombol power dan  
layar  
Coba nyalakan Berfungsi Layar rusak tidak masalah bila  
HDMI jalan


## 27.4 Memutuskan disk dan sistem berkas

| Disk | Peran | Sistem berkas | Catatan |
|---|---|---|---|
| NVMe M.2 500 GB | Sistem Proxmox + disk VM (local-lvm) | **ext4** (bawaan installer) | RAM 16-32 GB; ZFS tidak dipakai (satu disk, tanpa mirror) |
| HDD Seagate Surveillance 2 TB (unit 1) | Calon disk data / datastore PBS | ext4 (Directory) | Rencana awal memakai satu unit lewat enclosure single-bay; pilih setelah model dan kondisi diverifikasi |
| HDD Seagate Surveillance 2 TB (unit 2) | Ditunda | — | Enclosure yang tersedia hanya single-bay; peran unit ini belum ditentukan |

**Anggaran ruang NVMe 500 GB.** Disk VM dibuat tipis (thin), jadi ruang terpakai mengikuti isi, bukan ukuran yang diminta. Tetap hitung: sekitar 10-15 VM dengan sistem 4-8 GB aktual, ditambah image Docker dan data aplikasi. Contoh di bab layanan memakai disk data besar (musik 200 GiB di Bab 53, foto 300 GiB di Bab 55, datastore PBS 200 GiB di Bab 50). **Jangan menaruh semuanya di NVMe.** Saran:

| Data | Tempat | Ukuran awal |
|---|---|---|
| Sistem VM / container | NVMe (local-lvm) | sesuai bab |
| Foto Immich (disk kedua VM 214) | NVMe, ukuran dikecilkan (contoh 150 GiB) lalu diperbesar bila perlu | 150 GiB |
| Pustaka musik (VM 211) | NVMe atau HDD, 80-100 GiB | 80 GiB |
| Datastore PBS (VM 212) | **HDD 2 TB** | 1-1,5 TB |

**Menghubungkan HDD pertama.** Anda memiliki dua HDD Seagate Surveillance 2 TB berukuran 3,5 inci; model tiap unit belum dicatat dan setidaknya satu belum diformat. M710q Tiny hanya menyediakan satu bay SATA 2,5", jadi keduanya perlu terhubung dari luar. Enclosure yang tersedia single-bay; rencana sementara memakai satu HDD dahulu dan menunda yang kedua. Pastikan enclosure memiliki catu daya sendiri. Pilih peruntukan disk setelah model dan kondisi diverifikasi. Jangan mencabut disk saat backup berjalan. Catat model (dan serial secara lokal, jangan di repo) agar tidak salah pilih saat menyiapkan storage.

> Disk tunggal bukan backup. Backup VM ke HDD 2 TB (Bab 50), ditambah satu salinan lagi di media lain (Bab 50.13).

## 27.5 Pengaturan BIOS/UEFI lengkap (ThinkCentre)

Masuk BIOS: tekan **F1** berulang saat logo Lenovo muncul. Menu boot sekali pakai: **F12**. (Tombol Novo/Enter menu opsional pada beberapa varian.)

| Pengaturan | Nilai | Mengapa |
|---|---|---|
| Intel Virtualization Technology (VT-x) | Enabled | Wajib agar VM berjalan dengan akselerasi KVM |
| Intel VT-d | Enabled | Untuk passthrough PCI di masa depan (opsional) |
| SATA Controller Mode | AHCI | Agar disk 2,5" terbaca; NVMe tidak terpengaruh |
| Boot Mode | UEFI (CSM/Legacy dimatikan) | Instalasi bersih dan boot stabil |
| Secure Boot | Disabled | Mengurangi masalah saat instalasi |
| After Power Loss (Power) | Power On | Menyala sendiri setelah listrik padam dan kembali |
| Wake on LAN | Automatic / Enabled | Agar bisa dinyalakan dari STB (Bab 30.5) |
| Enhanced Power Saving Mode / ErP | Disabled | Mode hemat daya ini memutus daya kartu LAN dan membuat Wake-on-LAN gagal |
| Fast Boot | Disabled | Menghindari USB terlewat saat instalasi |
| Startup Sequence | USB di atas NVMe saat instalasi, lalu NVMe | Setelah instalasi, NVMe di urutan pertama |
| Supervisor password | Isi (opsional) | Mencegah perubahan BIOS oleh orang lain; simpan di Vaultwarden |

Nama menu persis berbeda antar versi BIOS (mis. "Power > Automatic Power On" untuk Wake on LAN dan After Power Loss). Bila ragu, cari kata kunci "Virtualization", "Wake", dan "Power Loss". Memperbarui BIOS lewat situs dukungan Lenovo disarankan sebelum instalasi.
