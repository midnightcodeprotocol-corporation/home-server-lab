# Bab 9. Konfigurasi Awal Proxmox di Jaringan MikroTik

> **Periksa jaringan yang sedang dipakai sebelum menyalin alamat di bab ini.** Host saat ini sementara berada di `192.168.0.200/24` dengan gateway dan DNS `192.168.0.1`. Alamat `192.168.88.10`, gateway `.88.1`, dan DNS AdGuard `.88.253` baru dipakai setelah host kembali ke MikroTik. Jangan memakai gateway atau DNS dari subnet lain; sesuaikan juga `/etc/hosts` saat mengganti alamat host.

## 9.1 Memastikan koneksi jaringan

Dari konsol atau Shell Proxmox, uji koneksi bertahap: gateway, internet, lalu DNS.  
Pada jaringan sementara, gunakan `192.168.0.1` sebagai gateway; contoh `.88.1` di bawah berlaku ketika server terhubung ke MikroTik.

**TERMINAL (login sebagai root)** | Shell Proxmox

```
ping -c 3 192.168.88.1
```
> Penjelasan: Menguji MikroTik (gateway). Gagal = masalah kabel/bridge/IP.
```
ping -c 3 8.8.8.8
```
> Penjelasan: Menguji internet tanpa DNS. Gagal tetapi gateway berhasil = masalah di MikroTik/uplink.
```
ping -c 3 deb.debian.org
```
> Penjelasan: Menguji DNS. Gagal tetapi 8.8.8.8 berhasil = DNS salah (lihat 9.4).
Dari sisi MikroTik, pastikan Proxmox terlihat:  

**TERMINAL MIKROTIK** | WinBox &gt; New Terminal

```
/ping 192.168.88.10 count=3
```
> Penjelasan: Mengirim ping dari router ke Proxmox.
```
/ip arp print where address=192.168.88.10
```
> Penjelasan: Menampilkan MAC address Proxmox pada tabel ARP router. Muncul = terhubung di LAN.

## 9.2 Mencatat Proxmox di MikroTik

**TERMINAL MIKROTIK** | WinBox &gt; New Terminal

```
/ip firewall address-list add list=servers address=192.168.88.10 comment="proxmox"
```
> Penjelasan: Mencatat Proxmox di daftar alamat bernama servers. Berguna untuk dokumentasi dan aturan
firewall nanti.  
CATATAN  
Proxmox memakai IP statis (192.168.88.10, di luar pool DHCP), jadi tidak perlu static lease. Perangkat lain (VM,  
LXC, STB) memakai static lease (Bab 3.5).  

## 9.3 Mengubah IP/gateway/DNS bila instal di jaringan lain

Jika saat instalasi Proxmox diberi alamat jaringan lain (misalnya 192.168.100.2 atau 192.168.2.x) dan  
sekarang Anda pindah ke jaringan MikroTik, ubah tiga hal: /etc/network/interfaces, /etc/hosts, dan  
DNS. Tidak perlu instal ulang.  

**TERMINAL (login sebagai root)** | Konsol VM atau Shell Proxmox

```
ls /etc/network/
```
> Penjelasan: Memeriksa nama berkas yang benar: harus ada interfaces (dengan huruf s di akhir).
```
cat -n /etc/network/interfaces
```
> Penjelasan: Menampilkan isi berkas dengan nomor baris sebelum diubah.
```
nano /etc/network/interfaces
```
> Penjelasan: Membuka editor. Ubah hanya address dan gateway.

**BERKAS: /etc/network/interfaces** | Ubah baris address dan gateway (nama enp0s31f6 sesuaikan dengan milik Anda)

```
auto lo
```

 2 iface lo inet loopback  
 3   
 4 iface enp0s31f6 inet manual  
 5   
 6 auto vmbr0  
 7 iface vmbr0 inet static  
 8 address 192.168.88.10/24  
 9 gateway 192.168.88.1  
10 bridge-ports enp0s31f6  
11 bridge-stp off  
12 bridge-fd 0  
13   
14 source /etc/network/interfaces.d/\*  
Tombol nano Fungsi  
Panah Pindah kursor  
Ctrl+O lalu Enter Simpan (Write Out)  
Ctrl+X Keluar  
Ctrl+W Cari teks  
Ctrl+K / Ctrl+U Potong / tempel satu baris  

**TERMINAL (login sebagai root)** | Konsol VM atau Shell Proxmox

```
nano /etc/hosts
```
> Penjelasan: Ganti IP lama pada baris hostname menjadi 192.168.88.10.
```
hostname --ip-address
```
> Penjelasan: Harus menampilkan 192.168.88.10 (cocok dengan /etc/hosts).
```
reboot
```
> Penjelasan: Menerapkan semua perubahan. Alternatif tanpa reboot: ifreload -a.

**BERKAS: /etc/hosts** | Baris hostname harus berisi IP yang benar

```
127.0.0.1 localhost.localdomain localhost
192.168.88.10 pve.lab.local pve
```

PERINGATAN  
Jika IP di /etc/hosts berbeda dari IP asli, layanan Proxmox (pveproxy, pve-cluster) bisa gagal start dan  
web tidak terbuka.  
Gambar 9.1 - Kasus nyata: judul nano tertulis /etc/network/interface (tanpa huruf s), sehingga editor kosong. Keluar  
(Ctrl+X) lalu buka /etc/network/interfaces.  
Alternatif lewat antarmuka web  
1. Node pve &gt; System &gt; Network.  
2. Klik vmbr0 &gt; Edit; ubah IPv4/CIDR dan Gateway &gt; OK.  
3. Klik Apply Configuration.  
> Penjelasan: Koneksi web akan terputus sebentar; buka alamat baru.
4. Perbarui /etc/hosts seperti di atas.  
> Penjelasan: Perubahan lewat web tidak memperbarui berkas hosts.

## 9.4 Mengatur DNS

1. Node pve &gt; System &gt; DNS &gt; Edit.  
2. Isi DNS server 1 192.168.88.253 (AdGuard), DNS server 2 1.1.1.1.  
> Penjelasan: DNS ke-2 publik hanya dipakai oleh host Proxmox sendiri agar update tetap jalan jika AdGuard
sedang mati.  
3. Klik OK.  

**TERMINAL (login sebagai root)** | Shell Proxmox

```
cat /etc/resolv.conf
```
> Penjelasan: Memeriksa isi akhir: harus ada baris nameserver 192.168.88.253.

## 9.5 Repository: ganti ke no-subscription

Proxmox memakai repository enterprise (berbayar) secara bawaan sehingga apt update gagal. Untuk  
lab dan rumah, pakai repository no-subscription (gratis).  
1. Pilih node pve di panel kiri.  
2. Di kolom menu kedua klik Updates (ikon panah melingkar), lalu Repositories tepat di  
bawahnya.  
> Penjelasan: Menu ini ada di bawah Updates, bukan di Datacenter.
3. Pilih baris pve-enterprise &gt; Disable. Lakukan juga pada ceph-enterprise.  
> Penjelasan: Repository enterprise butuh langganan; jika dibiarkan aktif akan memunculkan error 401.
4. Klik Add &gt; pilih No-Subscription &gt; Add.  
> Penjelasan: Ini repository gratis yang dipakai di rumah.
5. Periksa hasil seperti di Gambar 9.2.  
Gambar 9.2 - Hasil yang benar. (1) ceph-enterprise disabled. (2) pve-no-subscription aktif. (3)  
pve-enterprise disabled. Repository Debian (trixie, trixie-updates, trixie-security) aktif. Peringatan kuning  
"no-subscription is not recommended for production" aman diabaikan di rumah.  
CATATAN  
Proxmox VE 9 berbasis Debian 13 (nama kode trixie). Daftar repository memakai format .sources di  
/etc/apt/sources.list.d/.  

## 9.6 Update dan upgrade

**TERMINAL (login sebagai root)** | Shell Proxmox

```
apt update
```
> Penjelasan: Mengunduh daftar paket terbaru dari repository. Harus berakhir tanpa baris Err:.
```
apt full-upgrade -y
```
> Penjelasan: Memperbarui semua paket. full-upgrade (bukan upgrade) yang disarankan pada Proxmox
karena paket dependensi bisa berubah.  
```
pveversion
```
> Penjelasan: Memeriksa versi setelah pembaruan.
```
reboot
```
> Penjelasan: Dibutuhkan bila kernel diperbarui. Tunggu 1 sampai 2 menit lalu buka web lagi.
Atau lewat web: Updates &gt; Refresh (harus berakhir TASK OK), lalu Upgrade.  
Setelah pembaruan dan reboot, **sebelum membuat template atau guest**, verifikasi akselerasi KVM:

```
lscpu | grep -i virtualization
```
> Penjelasan: Pada M710q harus menampilkan `Virtualization: VT-x`. Jika tidak ada baris, VT-x mungkin mati di BIOS; lihat Bab 27.5.

```
ls -l /dev/kvm
```
> Penjelasan: Perangkat KVM harus ada. Bila tidak ada, jangan lanjut membuat template VM; selesaikan pemeriksaan VT-x dahulu.

Jika `apt update` gagal dengan `Temporary failure resolving`, periksa DNS dan kecocokan jaringan host sebelum melanjutkan. Contoh jaringan sementara `192.168.0.0/24` dicatat pada STATUS dan Bab 24. Jangan gunakan DNS rumah yang tidak terjangkau dari jaringan aktif.
TIPS  
Jika unduhan lambat (9 KB/s pada kasus nyata): pakai kabel LAN, update di jam sepi, atau ganti URIs: di  
/etc/apt/sources.list.d/debian.sources ke mirror Debian terdekat dari daftar resmi mirror. Baris Ign:  
lalu Get: pada log adalah percobaan ulang, bukan error.  

## 9.7 Mengenal antarmuka

Gambar 9.3 - Antarmuka Proxmox 9.2.2, node pve. (1) Menu Updates &gt; Repositories ada di kolom menu kedua. (2) Panel  
Tasks di bawah: baris merah adalah error (di sini apt-get update yang gagal karena DNS).  
Bagian Isi  
Panel kiri (Server View) Pohon Datacenter &gt; node pve &gt; VM, container, dan storage.  
Panel tengah Menu objek yang dipilih (Summary, Console, Hardware, Backup, Snapshots, dan  
seterusnya).  
Panel bawah (Tasks) Riwayat tugas. Klik dua kali untuk melihat log lengkap. Merah = error.  
Kanan atas Tombol Create VM, Create CT, Reboot, Shutdown, Shell.  
Datacenter &gt; Storage Daftar storage: local (ISO, template, backup) dan local-lvm (disk VM/CT).  
Node &gt; System &gt; Network Bridge vmbr0 yang menghubungkan VM/CT ke LAN.  
Node &gt; Disks Disk fisik dan pembuatan LVM, LVM-Thin, Directory, ZFS.  

## 9.8 Kebiasaan baik

• Matikan dengan benar: node &gt; Shutdown di web, atau poweroff di Shell. Jangan menekan tombol power lama atau mencabut kabel daya  
saat VM berjalan.  
• Penomoran proyek: CT 100 untuk template dan CT 101+ untuk layanan; VM 200 untuk template dan VM 201+ untuk layanan. VM 9000 tetap dicadangkan untuk template cloud-init. Catat di Lampiran B.  
• Ambil snapshot Proxmox (VM &gt; Snapshots) pada titik penting: sebelum upgrade, sebelum eksperimen besar.  
• Snapshot bukan backup. Jangan menumpuk banyak snapshot karena disk membengkak dan VM  
melambat.  

## 9.9 Menambah disk data (opsional)

Pasang HDD/SSD kedua (bay 2,5" atau USB, lihat Bab 27.4). Disk muncul di  
Node &gt; Disks (contoh /dev/sdb).  
1. Disks &gt; Directory &gt; Create: Directory, pilih disk, filesystem ext4, beri nama.  
> Penjelasan: Membuat storage direktori yang otomatis terdaftar di Datacenter &gt; Storage.
2. Atur Content storage itu (Datacenter &gt; Storage &gt; Edit): centang Disk image, Container,  
VZDump backup file sesuai tujuan.  
> Penjelasan: Menentukan jenis data yang boleh disimpan.
PERINGATAN  
Membuat Directory/LVM/ZFS pada disk menghapus isinya. Pastikan memilih disk yang benar.  

## 9.11 Kasus nyata pada konfigurasi awal

KASUS NYATA - Proxmox tidak bisa dibuka dari browser  
Gejala: Browser gagal tersambung ke https://192.168.100.2:8006.  
Penyebab: Saat instalasi laptop tidak terhubung ke jaringan rumah; IP Proxmox (192.168.100.x) beda jaringan  
dengan laptop (192.168.2.106 gateway 192.168.2.1).  
Solusi: Cocokkan tiga angka depan: ubah IP Proxmox ke jaringan laptop atau ke 192.168.88.10 setelah laptop  
dipindah ke jaringan MikroTik (9.3).  
KASUS NYATA - apt update: Temporary failure resolving  
Gejala: Log berisi Err: ... Temporary failure resolving untuk semua repository dan tugas merah di  
panel Tasks.  
Penyebab: DNS Proxmox kosong atau masih alamat jaringan lama.  
Solusi: Isi DNS di System &gt; DNS (9.4), uji ping deb.debian.org, lalu Refresh lagi.  
KASUS NYATA - Tidak menemukan menu Repositories  
Gejala: Menu tidak terlihat.  
Penyebab: Letaknya di bawah Updates di kolom menu kedua.  
Solusi: Node &gt; Updates &gt; Repositories (Gambar 9.3).
