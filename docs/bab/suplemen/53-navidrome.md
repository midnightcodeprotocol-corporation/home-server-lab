# Bab 53. Navidrome: Streaming Musik Pribadi

> **Revisi 3.** Disk contoh (musik 200 GiB) harus disesuaikan dengan NVMe 500 GB. Lihat Bab 27.4: kecilkan ukuran awal, dan taruh backup di HDD 2 TB.

PENEMPATAN - BARU - VM sendiri (dan disk data terpisah)  
Tempat: VM 211 music (192.168.88.31): qm clone 9100 211 --name music --full 1, ditambah disk data kedua untuk  
pustaka musik.  
Alasan: Pustaka musik tumbuh besar dan berganti-ganti; Navidrome ringan tetapi datanya berbeda sifat dari layanan  
lain, dan backup disk musiknya diperlakukan terpisah (backup=0).  
Tidak boleh: Digabung dengan vault atau n8n.  
Mode hemat: Boleh digabung ke VM 206 (apps); disk musik tetap dipasang sebagai disk kedua VM itu.  
Navidrome adalah server streaming musik sumber terbuka. Menurut dokumentasinya ia memakai image Docker  
resmi, menyimpan database dan cache di /data, dan membaca musik dari /music. Ia kompatibel dengan klien  
Subsonic, sehingga banyak aplikasi di Windows, Android, dan iPhone bisa dipakai.  
Keputusan Pilihan buku ini Alasan  
Sertifikat HTTPS Jalur 1: Tailscale Serve (nama  
lab-music.NAMA-TAILNET.ts.net)  
Banyak aplikasi musik pihak ketiga memakai  
penyimpanan sertifikat sendiri; sertifikat  
tepercaya menghindari masalah CA lokal  
seperti di Bab 44 [BELUM PASTI]  
Lewat Caddy? Tidak Satu alamat saja yang berlaku; sama seperti  
Vaultwarden  
Akses di rumah Tailscale tetap aktif di HP Nama .ts.net hanya terjawab lewat Tailscale;  
jalur langsung dalam LAN tetap dipakai  
Tailscale bila bisa  
Pustaka musik Disk data kedua, dipasang baca-saja untuk  
Navidrome  
Navidrome tidak bisa merusak berkas musik  
Anda  
Backup disk musik Dikecualikan dari PBS (backup=0); simpan  
salinan asli di tempat lain  
Pustaka besar dan biasanya bisa dibuat ulang  
dari sumber aslinya  
PERINGATAN  
Bila koleksi Anda tidak punya salinan lain (misalnya rekaman sendiri yang unik), jangan mengecualikan disk musik  
dari backup. Hapus opsi backup=0 di 53.1 atau salin pustaka ke disk USB secara berkala.  

## 53.1 Membuat VM music dan disk pustaka

**TERMINAL HOST PROXMOX** | Shell node Proxmox (host), sebagai root

```
qm clone 9100 211 --name music --full 1
```
> Penjelasan: Membuat VM 211 bernama music sebagai salinan penuh dari templat VM 9100 (Suplemen 7 Bab 49).
```
qm set 211 --memory 1024 --cores 2 --onboot 1
```
> Penjelasan: RAM (MB), inti, dan nyalakan otomatis. Angka awal adalah perkiraan [BELUM PASTI]; transkoding
membutuhkan CPU lebih.  
```
qm set 211 --scsi1 local-lvm:200,backup=0
```
> Penjelasan: Menambah disk kedua 200 GiB untuk pustaka musik dan menandainya tidak ikut backup. Ganti
local-lvm dengan nama penyimpanan Anda dan ukuran sesuai koleksi; sintaks disk [BELUM PASTI] pada versi  
Proxmox Anda.  
```
qm start 211
```
> Penjelasan: Menyalakan. Lakukan penyiapan awal di Suplemen 7 Bab 49.4 (nama host music, kunci SSH, alamat
192.168.88.31), lalu lanjut di bawah.  
Langkah berikut dijalankan di VM music. Disk kedua perlu diformat sekali:  

**TERMINAL VM MUSIC** | VM music (192.168.88.31), sebagai root (setelah su -)

```
lsblk -o NAME,SIZE,TYPE,MOUNTPOINT
```
> Penjelasan: Mengenali disk kedua (biasanya sdb, tanpa partisi dan tanpa mountpoint). Pastikan benar sebelum
memformat.  
```
mkfs.ext4 -L music /dev/sdb
```
> Penjelasan: Memformat disk (menghapus isinya). Ganti sdb bila berbeda.
```
mkdir -p /srv/music
echo "LABEL=music /srv/music ext4 defaults,nofail 0 2" >> /etc/fstab
```
> Penjelasan: Membuat titik pasang dan mendaftarkannya ke fstab agar terpasang saat boot. nofail mencegah VM macet bila disk hilang.  
```
mount -a && df -h /srv/music
```
> Penjelasan: Memasang dan memastikan ukurannya benar.
```
chown <USER>: /srv/music && id <USER>
```
> Penjelasan: Menjadikan pustaka milik pengguna biasa (ganti &lt;USER&gt;) agar bisa diunggah lewat scp. Catat
UID:GID dari perintah id untuk 53.2.  

## 53.2 Server Navidrome

**TERMINAL VM MUSIC** | VM music, sebagai root

```
mkdir -p /opt/stacks/music/data && cd /opt/stacks/music
```
> Penjelasan: Folder aplikasi dan folder data (database, cache).
```
chown 1000:1000 data
```
> Penjelasan: Data dimiliki UID:GID yang akan menjalankan Navidrome. Dokumentasi menyarankan memakai
UID:GID pemilik pustaka; ganti 1000:1000 bila perintah id di 53.1 menunjukkan angka lain.  
```
echo "ND_VERSION=latest" > .env
```
> Penjelasan: Nomor versi image. Dokumentasi resmi memakai latest; setelah berjalan, ganti dengan nomor rilis
tertentu agar pembaruan terkendali.  
```
nano compose.yaml
```
> Penjelasan: Isi seperti kotak di bawah.

**/opt/stacks/music/compose.yaml** | Isi berkas

```
services:
  navidrome:
    image: deluan/navidrome:${ND_VERSION}
    container_name: navidrome
    user: "1000:1000"
    restart: unless-stopped
    ports:
      - "127.0.0.1:4533:4533"
    environment:
      ND_SCANSCHEDULE: 1h
      ND_LOGLEVEL: info
      ND_BASEURL: ""
    volumes:
      - ./data:/data
      - /srv/music:/music:ro
```

Pengaturan Fungsi  
user "1000:1000" Menjalankan Navidrome sebagai pengguna biasa, bukan root  
127.0.0.1:4533:4533 Port hanya di dalam VM; Tailscale Serve meneruskan ke sini. Tidak terbuka di LAN  
ND_SCANSCHEDULE: 1h Memindai pustaka untuk lagu baru tiap jam  
/music:ro Pustaka dipasang baca-saja  

**TERMINAL VM MUSIC** | VM music, sebagai root di /opt/stacks/music

```
docker compose up -d && docker compose logs --tail=20
```
> Penjelasan: Menyalakan. Cari baris yang menyebut Navidrome mendengarkan di port 4533 dan tidak ada galat
izin.  

## 53.3 Tailscale Serve di VM music

**TERMINAL VM MUSIC** | VM music, sebagai root

```
curl -fsSL https://tailscale.com/install.sh | sh
```
> Penjelasan: Memasang Tailscale (sama seperti Suplemen 6 Bab 44.3).
```
tailscale up --hostname=lab-music --accept-dns=false
```
> Penjelasan: Mendaftarkan node bernama lab-music. Buka tautan login di browser laptop.
```
tailscale serve --bg --https=443 4533
```
> Penjelasan: HTTPS port 443 di nama lab-music diteruskan ke 127.0.0.1:4533. Sertifikat tepercaya diminta pada
kali pertama (beberapa detik).  
```
tailscale serve status
```
> Penjelasan: Memeriksa rute. Jangan menjalankan tailscale funnel.
1. Di konsol admin Tailscale (Machines) nonaktifkan key expiry untuk lab-music dan catat nama panjangnya.  
Entri grants tcp:443 dari Bab 44.3 sudah mencukupi.  

## 53.4 Akun pertama dan mengisi musik

1. Dari laptop (Tailscale aktif) buka https://lab-music.NAMA-TAILNET.ts.net. Halaman pertama meminta  
pembuatan akun admin (nama pengguna dan kata sandi kuat; simpan di Vaultwarden).  
2. Buat akun harian terpisah di menu pengguna Navidrome dan pakai akun itu di aplikasi; admin hanya untuk  
pengelolaan. Letak menu persis [BELUM PASTI].  
Menata berkas. Susun dengan pola Artis/Album/01 - Judul.flac dan pastikan tag (artis, album, nomor trek,  
sampul) benar. Di Windows, MusicBrainz Picard membantu merapikan tag. Navidrome membaca tag, bukan  
nama berkas, jadi tag yang rapi menentukan tampilan pustaka.  

**POWERSHELL WINDOWS** | PowerShell (laptop), di folder musik Anda

```
scp -r .\* <USER>@192.168.88.31:/srv/music/
```
> Penjelasan: Menyalin semua isi folder ke pustaka di VM music. Ganti &lt;USER&gt;. Untuk koleksi besar, proses ini
lama; jalankan sekali dan biarkan selesai.  
TIPS  
Navidrome memindai tiap jam (ND_SCANSCHEDULE). Untuk memaksa pindai, mulai ulang container: docker  
compose restart navidrome di VM music (Navidrome memindai saat mulai [BELUM PASTI]); atau cari tombol pindai  
di antarmuka web.  

## 53.5 Sisi klien

Windows  
1. Tanpa instalasi: buka https://lab-music.NAMA-TAILNET.ts.net di browser; pemutar web sudah ada.  
Opsional: Chrome/Edge Menu &gt; Instal sebagai aplikasi.  
2. Aplikasi desktop: Feishin (klien lintas-platform yang tercantum di halaman Apps & Players milik  
navidrome.org). Tambahkan server: tipe Navidrome, URL yang sama, nama pengguna dan kata sandi akun  
harian.  
Android  
1. Pastikan Tailscale aktif. Pilih satu klien: Symfonium (berbayar), Tempo, Ultrasonic, atau Substreamer,  
semuanya terdaftar sebagai klien Subsonic di navidrome.org. Pasang dari Play Store atau F-Droid.  
2. Tambahkan server: tipe Subsonic/Navidrome, alamat https://lab-music.NAMA-TAILNET.ts.net, nama  
pengguna, dan kata sandi akun harian.  
3. Agar pemutaran tidak berhenti saat layar terkunci, matikan penghematan baterai untuk aplikasinya:  
Pengaturan &gt; Aplikasi &gt; nama aplikasi &gt; Baterai &gt; Tanpa batasan. Laporan pengguna menyebut  
beberapa klien berhenti setelah satu lagu bila ini tidak diatur; perilaku tiap klien [BELUM PASTI].  
iPhone  
1. Pastikan Tailscale aktif. Pilih klien: Amperfy, Substreamer, Narjo, atau Navic (ada di navidrome.org).  
Pasang dari App Store.  
2. Tambahkan server dengan URL, nama pengguna, dan kata sandi yang sama.  
3. Izinkan pemutaran latar belakang dan unduhan offline bila ditawarkan; ketersediaan fitur berbeda antar  
aplikasi [BELUM PASTI].  
CATATAN  
Klien yang menolak sertifikat bukan masalah di sini, karena alamat .ts.net memakai sertifikat tepercaya. Bila aplikasi  
gagal tersambung, periksa Tailscale aktif dan alamat tanpa salah ketik.  

## 53.6 Backup, firewall, pemantauan

1. Proxmox Backup Server: tambahkan 211 ke job backup (Bab 50.10). Disk pustaka tidak ikut karena  
backup=0; sistem dan database Navidrome (playlist, akun) ikut.  
2. Firewall: buat /etc/pve/firewall/211.fw seperti kotak di bawah dan aktifkan kotak Firewall pada kartu jaringan  
(Bab 51).  
3. Pasang agen Beszel di VM music dan tambah monitor Uptime Kuma sesuai Suplemen 3.  

**/etc/pve/firewall/211.fw** | Isi berkas

```
[OPTIONS]
enable: 1
policy_in: DROP
policy_out: ACCEPT
dhcp: 1
[RULES]
IN ACCEPT -source +dc/admin -p tcp -dport 22
```

IN ACCEPT -source 192.168.88.20 -p tcp -dport PORT-AGEN-BESZEL  
IN ACCEPT -p icmp  
Tidak ada port layanan yang dibuka di LAN: Navidrome hanya terjangkau lewat Tailscale Serve. Salinan pustaka  
asli tetap Anda simpan sendiri di disk lain.  

## 53.7 Pembaruan

**TERMINAL VM MUSIC** | VM music, sebagai root di /opt/stacks/music

```
docker compose pull && docker compose up -d
```
> Penjelasan: Mengunduh image baru dan membuat ulang container. Baca catatan rilis Navidrome lebih dulu bila
memakai nomor versi tertentu; backup VM sudah dilakukan PBS tiap malam.
