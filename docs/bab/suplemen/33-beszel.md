# Bab 33. Beszel: CPU, RAM, Disk, dan Suhu

PENEMPATAN - GABUNG hub, BARU agen per guest  
Tempat: Hub Beszel di VM 201 docker-core (192.168.88.20). Agen dipasang di setiap VM saat VM itu dibuat (dan di  
host Proxmox bila diinginkan).  
Alasan: Satu dasbor, satu agen per mesin. Hub menghubungi tiap agen, sehingga firewall Proxmox harus  
mengizinkan 192.168.88.20 ke port agen (Bab 51).  
Beszel terdiri dari hub (halaman web dengan grafik dan pengaturan peringatan) dan agen kecil di setiap mesin  
yang dipantau. Agen membaca CPU, RAM, disk, jaringan, suhu, dan statistik Docker. Beszel dibuat ringan,  
dengan agen yang memakai RAM sangat sedikit.  
Mesin Cara pasang agen Yang terbaca  
VM Debian (192.168.88.20) Docker (sekaligus lokasi hub) CPU, RAM, disk VM, statistik tiap container; suhu tidak  
ada (VM)  
Proxmox (192.168.88.10) Binary (skrip pemasang) CPU, RAM, disk, jaringan, suhu (mesin asli)  
STB (192.168.88.253) Binary (opsional) CPU, RAM, disk, suhu SoC  
MikroTik Tidak bisa dipasangi agen Dipantau lewat ping di Uptime Kuma  

## 33.1 Memasang hub

**TERMINAL VM DEBIAN** | Sebagai root

```
mkdir -p /opt/stacks/beszel/beszel_data && cd /opt/stacks/beszel
```
> Penjelasan: Membuat folder aplikasi.
```
nano compose.yaml
```
> Penjelasan: Membuat berkas Compose. Isi seperti kotak di bawah.

**/opt/stacks/beszel/compose.yaml** | Isi berkas

```
services:
  beszel:
    image: henrygd/beszel:latest
    container_name: beszel
    restart: unless-stopped
    extra_hosts:
      - host.docker.internal:host-gateway
    ports:
      - "8090:8090"
    volumes:
      - ./beszel_data:/beszel_data
```

**TERMINAL VM DEBIAN** | Sebagai root di /opt/stacks/beszel

```
docker compose up -d
```
> Penjelasan: Menyalakan hub.
```
docker compose ps
```
> Penjelasan: Status harus running.
1. Buka http://192.168.88.20:8090. Kunjungan pertama meminta Anda membuat akun admin (email, password  
kuat). Email boleh berupa alamat apa saja, misalnya admin@lab.local.  
2. Setelah login, klik Add System. Dialog menampilkan Public Key hub dan perintah pemasangan agen.  
Biarkan dialog terbuka atau salin kuncinya; dipakai di bawah.  
CATATAN  
Hub membuat pasangan kunci sendiri saat pertama dijalankan. Kunci publiknya dipakai agen untuk memastikan  
hanya hub Anda yang boleh meminta data.  

## 33.2 Agen di VM Debian (Docker)

Agen perlu mode jaringan host agar dapat membaca statistik kartu jaringan. Hub dan agen berada di mesin yang  
sama tetapi di jaringan Docker berbeda, karena itu hub menjangkau agen lewat nama host.docker.internal.  

**TERMINAL VM DEBIAN** | Sebagai root

```
mkdir -p /opt/stacks/beszel-agent && cd /opt/stacks/beszel-agent
```
> Penjelasan: Folder terpisah untuk agen.
```
nano compose.yaml
```
> Penjelasan: Isi seperti kotak di bawah; ganti KUNCI dengan Public Key dari dialog Add System. Sebaiknya salin
isi Compose dari dialog langsung bila tampilannya berbeda dengan contoh.  

**/opt/stacks/beszel-agent/compose.yaml** | Isi berkas

```
services:
  beszel-agent:
    image: henrygd/beszel-agent:latest
    container_name: beszel-agent
    restart: unless-stopped
    network_mode: host
    volumes:
      - ./beszel_agent_data:/var/lib/beszel-agent
      - /var/run/docker.sock:/var/run/docker.sock:ro
    environment:
      PORT: "45876"
      KEY: "ssh-ed25519 AAAA...GANTI-DENGAN-KUNCI-DARI-HUB"
```

**TERMINAL VM DEBIAN** | Sebagai root di /opt/stacks/beszel-agent

```
docker compose up -d
```
> Penjelasan: Menyalakan agen.
```
ufw allow from 172.16.0.0/12 to any port 45876 proto tcp
```
> Penjelasan: Hanya bila UFW aktif: mengizinkan hub (yang berada di jaringan Docker 172.x) menjangkau agen.
Tanpa ini hub akan gagal terhubung.  
1. Di dialog Add System isi Name: vm-debian, Host / IP: host.docker.internal, Port: 45876, lalu klik Add  
system.  
2. Dalam beberapa detik sistem berubah menjadi hijau dan grafik mulai muncul. Klik namanya untuk melihat  
CPU, RAM, disk, jaringan, dan daftar container.  
KEAMANAN  
Agen memakai docker.sock (hanya baca) untuk membaca statistik container. Walau hanya baca, akses ini membuka  
informasi seluruh container; pasang hanya agen resmi dan perbarui rutin.  

## 33.3 Agen di Proxmox (mesin asli)

1. Di hub klik Add System. Isi Name: proxmox, Host / IP: 192.168.88.10, Port: 45876. Pilih tab Binary dan salin  
perintah pemasangan yang tampil (jangan klik Add system dulu).  
2. Buka Shell Proxmox (root) dan tempel perintah itu. Skrip mengunduh agen, membuat pengguna khusus  
bernama beszel, dan menyalakannya sebagai layanan. Bentuk umumnya: curl -sL https://get.beszel.dev -o  
/tmp/install-agent.sh && chmod +x /tmp/install-agent.sh && /tmp/install-agent.sh diikuti opsi kunci dan  
port dari dialog.  

**TERMINAL PROXMOX** | Shell Proxmox (root)

```
systemctl status beszel-agent --no-pager
```
> Penjelasan: Memastikan layanan agen aktif (active running).
```
ss -tlnp | grep 45876
```
> Penjelasan: Memastikan agen mendengarkan di port 45876.
1. Karena firewall Proxmox aktif (Suplemen 1 Bab 25.5), buka Datacenter &gt; Firewall &gt; Rules &gt; Add: Direction  
in, Action ACCEPT, Protocol tcp, Source 192.168.88.20, Dest. port 45876, Comment "Beszel hub", Enable,  
Add.  
2. Kembali ke dialog di hub dan klik Add system. Proxmox muncul hijau. Buka halamannya dan cari panel  
Temperature.  
CATATAN  
Suhu hanya muncul bila mesin memiliki sensor yang terbaca. Pastikan sensors menampilkan data (Suplemen 2 Bab  
30.4).  
TIPS  
Bila tidak ingin membuka port masuk, hub mendukung token universal: aktifkan di Settings &gt; Tokens &  
Fingerprints (versi baru), dan agen menyambung keluar ke hub tanpa aturan firewall masuk. Gunakan perintah yang  
disediakan hub; tampilan bisa berbeda antar versi.  

## 33.4 Agen di STB (opsional)

STB adalah DNS seluruh rumah, jadi tambahkan hal baru dengan hati-hati. Agen Beszel sangat kecil, tetapi bila  
Anda ragu, lewati dan biarkan Uptime Kuma memantau STB lewat ping dan DNS (Bab 32.3).  
1. Di hub klik Add System: Name stb, Host / IP 192.168.88.253, Port 45876, tab Binary, salin perintah.  
2. SSH ke STB (root, dengan kunci) dan tempel perintah itu. Periksa dengan systemctl status beszel-agent  
--no-pager.  
3. Klik Add system di hub. STB tidak memiliki firewall bawaan di buku ini, jadi tidak ada aturan tambahan.  

## 33.5 Peringatan

1. Di hub buka Settings &gt; Notifications dan tambahkan alamat notifikasi (format Shoutrrr) dari kotak di bawah.  
Gunakan tombol uji bila tersedia.  
2. Buka halaman sebuah sistem, klik ikon lonceng, lalu aktifkan peringatan sesuai tabel. Ulangi untuk tiap  
sistem.  
Alamat notifikasi (Shoutrrr) | Pilih salah satu atau keduanya; ganti nilai huruf besar  
gotify://192.168.88.20:8070/TOKEN-APLIKASI-BESZEL?DisableTLS=yes  
telegram://TOKEN-BOT@telegram?channels=CHAT-ID  
Peringatan Nilai awal Jika terpicu  
Status (sistem mati) Aktif Cek mesin dan jaringan  
CPU Di atas 80% selama 10 menit Cari proses atau container yang rakus  
Memori Di atas 90% selama 10 menit Kurangi VM atau tambah RAM  
Peringatan Nilai awal Jika terpicu  
Disk Di atas 85% Bersihkan atau tambah disk; jangan biarkan  
100%  
Suhu Di atas 80 derajat Bersihkan debu, perbaiki ventilasi  
CATATAN  
Bila alamat Gotify ditolak karena parameter, ikuti dokumentasi Shoutrrr untuk layanan Gotify, atau pakai Telegram.  
Perhatikan huruf besar kecil pada nama parameter.  

## 33.6 Memperbarui dan masalah umum

**TERMINAL VM DEBIAN** | Sebagai root

```
cd /opt/stacks/beszel && docker compose pull && docker compose up -d
```
> Penjelasan: Memperbarui hub. Backup folder dulu (Bab 34.3).
```
cd /opt/stacks/beszel-agent && docker compose pull && docker compose up -d
```
> Penjelasan: Memperbarui agen di VM.
Agen binary di Proxmox dan STB dapat diperbarui dengan menjalankan ulang skrip pemasang atau perintah  
update agen yang dijelaskan di dokumentasi Beszel.  
Gejala Penyebab Solusi  
Sistem tetap abu-abu atau merah di  
hub  
Port 45876 terblokir (UFW atau firewall  
Proxmox)  
Tambahkan aturan Bab 33.2 dan 33.3; uji:  
telnet alamat 45876  
Hub gagal menjangkau agen di VM  
yang sama  
Memakai 192.168.88.20 bukannya  
host.docker.internal  
Gunakan host.docker.internal pada Host / IP  
Tidak ada panel suhu VM, atau sensor tidak terbaca Periksa sensors di mesin asli; VM memang  
tidak punya suhu  
Tidak ada statistik container docker.sock tidak terpasang pada agen Pastikan baris /var/run/docker.sock ada di  
compose  
Peringatan tidak sampai Alamat Shoutrrr salah Uji alamat; bandingkan dengan format  
dokumentasi
