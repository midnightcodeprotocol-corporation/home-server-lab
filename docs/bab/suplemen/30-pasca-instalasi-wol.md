# Bab 30. Pasca-Instalasi di Mesin Asli, Wake-on-LAN, dan Memindahkan Isi Lab

PENEMPATAN - HOST. Tempat: pengaturan setelah instalasi dilakukan di host Proxmox (ThinkCentre M710q). Aplikasi tetap di guest.

## 30.1 Urutan kerja

| Urutan | Tindakan | Rujukan |
|---|---|---|
| 1 | Pasang RAM tambahan, uji MemTest86 | Bab 27.1 |
| 2 | Atur BIOS | Bab 27.5 |
| 3 | Instal Proxmox dari USB | Bab 6, 8, 28 |
| 4 | Pengaturan awal: DNS, repository no-subscription, update | Bab 9.4 sampai 9.6 |
| 5 | Sensor suhu dan kesehatan disk | Bab 30.4 |
| 6 | Wake-on-LAN dari STB | Bab 30.5 |
| 7 | Pasang HDD 2 TB sebagai disk data/backup | Bab 27.4 |
| 8 | Keamanan (akun admin, 2FA, SSH kunci, firewall) dan Tailscale | Bab 25 dan 26 |
| 9 | Templat VM 200 dan layanan | Bab 49 dan seterusnya |
| 10 | PBS dan backup terjadwal, uji pulih | Bab 50 |

## 30.2 Pengaturan dasar mesin asli

Kerjakan Bab 9.4 sampai 9.8 (DNS, repository, update, antarmuka, kebiasaan baik) seperti biasa.

## 30.3 Penempatan fisik, kipas, dan suhu

M710q adalah PC kecil tanpa baterai dan tanpa layar, jadi tidak ada pengaturan "tutup layar". Yang perlu diperhatikan:

- Letakkan di tempat berventilasi, jauhkan dari tumpukan barang; jangan ditutup. Boleh berdiri atau rebah sesuai dudukan.
- Pantau suhu CPU dan NVMe (Bab 30.4). Sebagai pedoman, di atas 80 derajat berarti perlu pembersihan debu atau perbaikan aliran udara.
- Pakai catu daya bawaan (adaptor eksternal) dan colokkan ke stabilizer/UPS kecil bila ada (monitor listrik ada di daftar rencana).
- Beri label di mesin: nama, IP 192.168.88.10, dan MAC kartu LAN.

## 30.4 Sensor suhu dan kesehatan disk

**TERMINAL PROXMOX** | Shell Proxmox (root)

```
apt install -y lm-sensors
```
> Penjelasan: Memasang pembaca sensor suhu dan kipas.
```
sensors-detect --auto
```
> Penjelasan: Mendeteksi sensor yang tersedia dan menerima pilihan bawaan.
```
sensors
```
> Penjelasan: Menampilkan suhu CPU dan kipas. Catat suhu saat diam; sebagai pedoman, di atas 80 derajat berarti
perlu pembersihan atau pendinginan.  
```
smartctl -H /dev/sda
```
> Penjelasan: Memeriksa kesehatan SSD atau HDD. Hasil yang diharapkan: PASSED. Untuk NVMe pakai
/dev/nvme0.  
```
smartctl -a /dev/sda | head -40
```
> Penjelasan: Melihat detail SMART, termasuk jam pemakaian dan sektor bermasalah.
CATATAN  
smartmontools biasanya sudah terpasang di Proxmox; jika perintah tidak dikenali, jalankan apt install -y  
smartmontools. Data suhu inilah yang nanti dibaca oleh Beszel atau Prometheus di suplemen monitoring (suhu tidak  
terbaca di VM).  

## 30.5 Wake-on-LAN: menyalakan Proxmox dari STB

Wake-on-LAN (WoL) menyalakan komputer yang mati dengan mengirim paket khusus (magic packet) ke kartu  
LAN-nya. STB yang selalu hidup bisa menjadi pengirimnya. Paket WoL berupa broadcast, jadi pengirim harus  
berada di LAN yang sama; dari luar rumah, Anda masuk ke STB lewat Tailscale lalu menjalankan perintahnya di  
STB.  
CATATAN  
WoL tidak sama dengan menyala otomatis setelah listrik padam. Itu pengaturan BIOS Restore on AC Power Loss  
(Bab 27.5). Keduanya sebaiknya aktif.  
A. Di BIOS ThinkCentre M710q  
Aktifkan Wake on LAN atau Power On by PCI-E, dan nonaktifkan ErP/Deep Sleep (Bab 27.5). Pada laptop,  
WoL hanya bekerja lewat kabel LAN, tidak lewat WiFi, dan sebagian laptop tidak mendukungnya saat mati total.  
B. Di Proxmox: mengaktifkan WoL pada kartu LAN  

**TERMINAL PROXMOX** | Shell Proxmox (root)

```
apt install -y ethtool
```
> Penjelasan: Memasang alat pengatur kartu jaringan.
```
ip -br link
```
> Penjelasan: Mencari nama kartu LAN (contoh enp0s31f6). Catat juga alamat MAC-nya
(AA:BB:CC:DD:EE:FF), dibutuhkan nanti.  
```
ethtool enp0s31f6 | grep -i wake
```
> Penjelasan: Ganti enp0s31f6 dengan nama kartu Anda. "Supports Wake-on" harus memuat huruf g, dan "Wake-on: d"
berarti masih mati.  
```
ethtool -s enp0s31f6 wol g
```
> Penjelasan: Menyalakan WoL sekarang (tidak permanen sampai reboot).
```
nano /etc/network/interfaces
```
> Penjelasan: Menambahkan baris agar WoL aktif setiap kali menyala. Edit blok kartu fisik seperti kotak di bawah.

**/etc/network/interfaces (bagian kartu fisik)** | Ganti enp0s31f6 sesuai nama kartu

```
iface enp0s31f6 inet manual
 post-up /usr/sbin/ethtool -s enp0s31f6 wol g
```

**TERMINAL PROXMOX** | Shell Proxmox (root)

```
ifreload -a
```
> Penjelasan: Menerapkan konfigurasi.
```
ethtool enp0s31f6 | grep "Wake-on"
```
> Penjelasan: Harus menampilkan "Wake-on: g".
C. Di STB: mengirim magic packet  

**TERMINAL STB** | SSH ke 192.168.88.253 (root)

```
apt update && apt install -y wakeonlan
```
> Penjelasan: Memasang pengirim magic packet.
```
nano /usr/local/bin/nyalakan-proxmox
```
> Penjelasan: Membuat skrip singkat. Isi seperti kotak di bawah; ganti MAC dengan milik Proxmox.

**/usr/local/bin/nyalakan-proxmox** | Isi berkas

```
#!/bin/sh
wakeonlan AA:BB:CC:DD:EE:FF
```

**TERMINAL STB** | SSH ke 192.168.88.253 (root)

```
chmod +x /usr/local/bin/nyalakan-proxmox
```
> Penjelasan: Membuat skrip dapat dijalankan.
D. Uji  
1. Di web Proxmox pilih node, klik Shutdown. Tunggu sampai komputer benar-benar mati (lampu mati; LED  
LAN biasanya tetap redup).  
2. Di STB jalankan nyalakan-proxmox.  
3. Komputer harus menyala dalam beberapa detik dan web Proxmox terbuka lagi setelah satu sampai dua  
menit.  
KASUS NYATA  
Gejala: WoL berhasil dari kondisi tidur tetapi gagal dari mati total. Penyebab: kartu LAN diputus dayanya (ErP atau  
Deep Sleep aktif) atau driver mereset pengaturan saat mati. Solusi: nonaktifkan ErP/Deep Sleep di BIOS, pastikan  
Wake-on: g setelah boot, dan ulangi uji. Bila tetap gagal, perangkat keras komputer itu mungkin tidak mendukung WoL  
dari mati total.  
KEAMANAN  
Magic packet tidak memakai password dan hanya berlaku di LAN. Karena itu perintah penyalaan dijalankan dari STB  
(akses SSH-nya sudah berkunci, Bab 25.7), bukan dengan membuka layanan WoL ke internet.  
TIPS  
Dari HP, aplikasi SSH seperti Termius (Android dan iPhone) bisa menjalankan nyalakan-proxmox lewat Tailscale ke  
192.168.88.253. Nanti perintah ini dapat dipasang sebagai tombol di Home Assistant atau alur n8n.


## 30.6 Memulihkan backup setelah instal ulang

Bila Proxmox diinstal ulang (disk rusak atau upgrade besar), pulihkan VM dan container dari backup. Prosedur lengkap ada di Bab 23.5; bila memakai PBS, restore dari antarmuka Proxmox (Datacenter > Storage > pbs-home) seperti di Bab 50.12. **Kunci enkripsi backup** wajib ada, atau backup tidak bisa dipulihkan.

Setelah restore, MAC VM tetap sama sehingga reservasi IP di MikroTik (192.168.88.20 dan seterusnya) tetap berlaku.

## 30.7 Mengulang keamanan di mesin asli

Kerjakan Bab 25.3 sampai 25.5 (akun admin, 2FA, SSH kunci, firewall Proxmox), 25.6 untuk setiap VM, dan Bab 26 untuk Tailscale. Pengaturan akun, 2FA, dan firewall tersimpan di mesin, bukan di buku.

## 30.8 Checklist dan masalah umum

| No | Uji | Hasil yang diharapkan |
|---|---|---|
| 1 | Web Proxmox terbuka dari laptop | Login root berhasil |
| 2 | `lscpu` menunjukkan Virtualization | VT-x terdeteksi |
| 3 | `free -h` | 16 GB (atau 32 GB setelah RAM ditambah) terbaca |
| 4 | `sensors` menampilkan suhu | Suhu diam wajar |
| 5 | `smartctl -H /dev/nvme0` | PASSED |
| 6 | Wake-on-LAN dari STB | Mesin menyala setelah Shutdown |
| 7 | Mesin menyala sendiri setelah listrik padam | After Power Loss = Power On bekerja |
| 8 | HDD 2 TB terbaca di Node > Disks | Muncul dengan ukuran benar |
