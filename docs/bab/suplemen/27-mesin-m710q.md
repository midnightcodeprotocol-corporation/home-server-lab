# Bab 27. Mesin Anda: Lenovo ThinkCentre M710q

PENEMPATAN - TIDAK ADA GUEST. Tempat: bab ini tentang mesin fisik. Belum ada VM/LXC.

Mesin server Anda adalah **Lenovo ThinkCentre M710q (Tiny)**. Bab ini mencatat spesifikasi, rencana RAM dan disk, dan pengaturan BIOS-nya. Menu BIOS bisa berbeda antar versi; nama di bawah adalah patokan, cocokkan dengan layar Anda.

## 27.1 Spesifikasi dan kebutuhan

| Komponen | Kebutuhan | M710q Anda | Status |
|---|---|---|---|
| CPU | 64-bit dengan VT-x/AMD-V, 4 core disarankan | Core i5-6500T, 4 core / 4 thread | VT-x/KVM aktif setelah perbaikan; VT-d Disabled |
| RAM | 16 GB atau lebih | 16 GB + 8 GB (24 GB fisik) | Linux melaporkan 23 GiB; BIOS/MemTest86 belum diperiksa |
| Disk sistem | SSD 120 GB atau lebih | NVMe Samsung MZALQ512HALU-000L2 | Proxmox berjalan; terdeteksi sebesar 476,9 GB |
| Disk data / backup | HDD/SSD terpisah | 2 × HDD Seagate Surveillance 2 TB, 3,5 inci | Belum tersambung; enclosure single-bay lama ditemukan tetapi belum diuji; HDD kedua ditunda |
| Jaringan | 1 port LAN kabel | 1 Gigabit Ethernet (Intel) | Lulus |

Spesifikasi di atas adalah patokan umum model M710q; **cek label RAM, tipe slot, dan ketebalan disk pada unit Anda sendiri** sebelum membeli atau memasang.

### Rencana RAM

| Pilihan | Total | Catatan |
|---|---|---|
| 16 GB | 16 GB | Profil konservatif Bab 56 |
| **16 GB + 8 GB (konfigurasi saat ini)** | **24 GB** | Diharapkan terpasang; periksa BIOS dan uji MemTest86. Gunakan profil konservatif sambil memantau beban. |
| 16 GB + 16 GB | 32 GB | Opsi peningkatan di masa depan; tetap ukur beban nyata, jangan anggap semua VM aman menyala bersamaan. |

RAM sudah dilaporkan diganti: modul pertama 8 GB diganti dengan 16 GB, sementara modul 8 GB lainnya tetap terpasang. Jadi total fisiknya 24 GB; Proxmox melaporkan 23 GiB yang dapat digunakan. BIOS dan MemTest86 belum diperiksa. Jalankan **MemTest86 dari USB sampai 1-2 putaran penuh tanpa error** sebelum menaruh beban kerja penting; RAM bermasalah dapat merusak VM secara diam-diam.

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
| NVMe Samsung MZALQ512HALU-000L2 (476,9 GB) | Sistem Proxmox + disk VM (local-lvm) | ext4 | Proxmox sudah berjalan; `local` dan `local-lvm` aktif |
| HDD Seagate Surveillance 2 TB (unit 1) | Calon disk data / datastore PBS | Belum dipilih | Belum tersambung; enclosure lama ditemukan tetapi belum diuji. Identifikasi model/kondisi sebelum dipakai |
| HDD Seagate Surveillance 2 TB (unit 2) | Ditunda | — | Enclosure yang tersedia hanya single-bay; peran unit ini belum ditentukan |

**Anggaran ruang NVMe 500 GB.** Disk VM dibuat tipis (thin), jadi ruang terpakai mengikuti isi, bukan ukuran yang diminta. Tetap hitung: sekitar 10-15 VM dengan sistem 4-8 GB aktual, ditambah image Docker dan data aplikasi. Contoh di bab layanan memakai disk data besar (musik 200 GiB di Bab 53, foto 300 GiB di Bab 55, datastore PBS 200 GiB di Bab 50). **Jangan menaruh semuanya di NVMe.** Saran:

| Data | Tempat | Ukuran awal |
|---|---|---|
| Sistem VM / container | NVMe (local-lvm) | sesuai bab |
| Foto Immich (disk kedua VM 214) | NVMe, ukuran dikecilkan (contoh 150 GiB) lalu diperbesar bila perlu | 150 GiB |
| Pustaka musik (VM 211) | NVMe atau HDD, 80-100 GiB | 80 GiB |
| Datastore PBS (VM 212) | **HDD 2 TB** | 1-1,5 TB |

**Menghubungkan HDD pertama.** Anda memiliki dua HDD Seagate Surveillance 2 TB berukuran 3,5 inci; keduanya dinyatakan aman. Satu HDD belum diformat sehingga sebelumnya tidak muncul di Windows. M710q Tiny hanya menyediakan satu bay SATA 2,5", jadi HDD 3,5 inci akan dipakai melalui koneksi luar. Enclosure yang tersedia single-bay dan belum diuji; rencana sementara memakai satu HDD dahulu dan menunda yang kedua. Pastikan enclosure memiliki catu daya sendiri. Pilih peruntukan disk setelah model dan kondisi diverifikasi. Jangan mencabut disk saat backup berjalan. Catat model (dan serial secara lokal, jangan di repo) agar tidak salah pilih saat menyiapkan storage.

> Disk tunggal bukan backup. Backup VM ke HDD 2 TB (Bab 50), ditambah satu salinan lagi di media lain (Bab 50.13).

## 27.5 Pengaturan BIOS/UEFI lengkap (ThinkCentre)

Masuk BIOS: tekan **F1** berulang saat logo Lenovo muncul. Menu boot sekali pakai: **F12**. (Tombol Novo/Enter menu opsional pada beberapa varian.)

| Pengaturan | Nilai | Mengapa |
|---|---|---|
| Intel Virtualization Technology (VT-x) | Enabled | Wajib agar VM berjalan dengan akselerasi KVM |
| Intel VT-d | Opsional; saat ini Disabled | Hanya diperlukan untuk kebutuhan passthrough perangkat PCI tertentu |
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

### BIOS Lenovo tanpa layar: gunakan thinklmi hanya bila tersedia

Kasus nyata pada M710q (31 Oktober 2026): VM gagal dinyalakan karena VT-x mati, dan pengguna tidak memiliki monitor untuk masuk BIOS. Host memiliki `/sys/class/firmware-attributes/thinklmi`, sehingga nilai Intel Virtualization Technology bisa diaktifkan lewat antarmuka firmware Linux. Dukungan ini bergantung pada model, BIOS, kernel, dan driver; jangan menganggap folder `thinklmi` tersedia pada setiap mesin.

> **Peringatan:** perubahan firmware berisiko membuat mesin tidak dapat boot. Gunakan hanya jika benar-benar perlu dan siapkan akses lokal/pemulihan. Jangan ubah atribut selain VT-x. Jangan mengirim password BIOS ke chat. Jika folder/atribut tidak ada, jangan membuatnya; gunakan monitor dan F1 atau dokumentasi Lenovo.

**TERMINAL HOST PROXMOX** | Shell host, sebagai root

```
ls /sys/class/firmware-attributes/
```
> Penjelasan: Pastikan keluaran memuat `thinklmi`. Jika tidak ada, berhenti dan gunakan cara BIOS biasa.

```
ls "/sys/class/firmware-attributes/thinklmi/attributes"
```
> Penjelasan: Cari nama atribut virtualization yang memang ada pada mesin. Jangan menyalin nama dari model lain bila tidak cocok.

```
cat "/sys/class/firmware-attributes/thinklmi/attributes/Intel(R) Virtualization Technology/current_value"
cat "/sys/class/firmware-attributes/thinklmi/attributes/Intel(R) Virtualization Technology/possible_values"
```
> Penjelasan: Pastikan atribut yang dipilih adalah Intel Virtualization Technology dan `Enabled` tercantum sebagai nilai yang diizinkan. Pada unit yang diuji, nilai awal `Disabled` dan pilihan `Disabled;Enabled`.

```
echo "Enabled" > "/sys/class/firmware-attributes/thinklmi/attributes/Intel(R) Virtualization Technology/current_value"
```
> Penjelasan: Mengubah hanya VT-x ke Enabled. Pada unit pengguna, perubahan bertahan setelah reboot; kebutuhan menulis `save_settings` belum dipastikan dan bukan bagian langkah ini.

```
reboot
```
> Penjelasan: Nyalakan ulang agar firmware menerapkan perubahan. Pastikan akses web/SSH tersedia kembali.

```
lscpu | grep -i virtualization
ls -l /dev/kvm
```
> Penjelasan: Hasil pada unit yang diuji adalah `Virtualization: VT-x` dan perangkat `/dev/kvm` tersedia. Jika tidak, jangan mulai membuat VM; cek BIOS/firmware secara lokal.

Intel VT-d boleh tetap `Disabled` sampai benar-benar ada kebutuhan passthrough PCI; VT-x diperlukan untuk akselerasi VM KVM.
