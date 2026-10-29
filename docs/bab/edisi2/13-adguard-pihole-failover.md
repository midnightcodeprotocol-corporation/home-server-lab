# Bab 13. Pemblokir Iklan: AdGuard atau Pi-hole, dan Rancangan 3 Server

Bab ini menjawab dua pertanyaan: mana yang cocok, AdGuard Home atau Pi-hole, dan apakah ide  
memakai 3 aplikasi (2 bekerja, 1 sebagai balancer) masuk akal. Setelah itu dipasang pasangan  
AdGuard di Proxmox dan failover-nya.  

## 13.1 AdGuard Home vs Pi-hole

Keduanya adalah DNS sinkhole: perangkat bertanya alamat sebuah domain ke mereka, dan domain  
iklan/pelacak dijawab 0.0.0.0 sehingga iklan tidak termuat.  
Aspek AdGuard Home Pi-hole  
Pemasangan Satu berkas program (Go); skrip resmi satu  
baris  
Skrip instalasi; memasang beberapa  
komponen (FTL berbasis dnsmasq)  
Antarmuka Modern, satu halaman, banyak pengaturan Sederhana, berfokus pada statistik dan  
daftar blokir  
DNS terenkripsi ke upstream  
(DoH/DoT/DoQ)  
Bawaan Perlu tambahan (misalnya Unbound atau  
cloudflared)  
Pengaturan per  
perangkat/klien  
Bawaan, mudah (aturan, kategori, jadwal) Ada lewat Groups, lebih manual  
Server DHCP bawaan Ada Ada  
Daftar blokir dan aturan  
kustom  
Ya, sintaks aturan mirip filter adblock Ya, daftar domain dan regex  
Pemakaian sumber daya Sangat ringan Ringan  
Sinkronisasi dua server adguardhome-sync (pihak ketiga) Gravity Sync atau Nebula Sync (pihak  
ketiga)  
Komunitas dan dokumentasi Besar Sangat besar dan lama  
Cocok untuk Pemula sampai menengah yang ingin fitur  
lengkap  
Yang ingin sederhana dan sangat teruji  
TIPS  
Rekomendasi untuk proyek ini: AdGuard Home. Sudah berjalan di STB, sangat ringan, punya DoH/DoT  
bawaan dan pengaturan per klien. Memakai satu jenis di kedua server juga membuat sinkronisasi pengaturan  
lebih mudah. Pi-hole tetap pilihan bagus; cara memasangnya ada di 13.9.  

## 13.2 Memikirkan ide: 3 aplikasi, 2 bekerja dan 1 sebagai balancer

Ada tiga cara menyusun lebih dari satu server DNS. Ide Anda sesuai Opsi 3.  
Opsi 1 (disarankan)  
DHCP memberi 2 DNS  
Klien  
Opsi 2  
DNS + IP virtual (keepalived)  
Klien  
Opsi 3 (ide balancer)  
3 server, 1 sebagai pembagi  
Klien  
AdGuard 1  
STB  
AdGuard 2  
LXC  
Klien memakai kedua DNS  
Satu mati, yang lain jalan  
IP virtual 192.168.88.5  
AdGuard 1  
MASTER  
AdGuard 2  
BACKUP  
IP pindah otomatis  
dnsdist (pembagi)  
AdGuard 1  
STB  
AdGuard 2  
LXC  
Jika pembagi mati,  
semua DNS ikut mati  
Gambar 13.1 - Tiga cara menyusun server DNS.  
Opsi Cara kerja Kelebihan Kekurangan  
1. Dua DNS di  
DHCP  
MikroTik membagikan dua  
alamat DNS; klien memakai  
salah satunya  
Sederhana, tanpa komponen  
tambahan, tidak ada titik gagal  
baru  
Bukan pembagian beban yang  
sempurna; sebagian klien  
butuh beberapa detik beralih  
saat server mati  
2. IP virtual  
(keepalived)  
Dua server berbagi satu IP; IP  
pindah ke server yang hidup  
Satu IP tetap; peralihan cepat Perlu keepalived di kedua  
server; kadang tidak stabil di  
WiFi  
3. Balancer  
(dnsdist)  
Server ketiga menerima semua  
kueri lalu membagi ke dua  
AdGuard  
Pembagian beban nyata,  
pemeriksaan kesehatan,  
cache, latihan bagus  
Balancer itu sendiri menjadi  
titik gagal tunggal; statistik  
AdGuard hanya melihat IP  
balancer; tambahan latensi  
Kesimpulan  
• Untuk rumah: Opsi 1. Dua AdGuard sudah memberi ketahanan, tanpa menambah komponen.  
• Opsi 3 tepat sebagai latihan (konsep load balancing dan health check). Di rumah, balancer yang mati  
justru mematikan seluruh DNS, sehingga hasilnya lebih rapuh dari Opsi 1, kecuali balancer sendiri  
dibuat redundan (dua dnsdist + keepalived).  
• Gabungan yang masuk akal: STB (AdGuard utama) + LXC (AdGuard kedua) + dua DNS di DHCP,  
dan opsional dnsdist di LXC untuk latihan.  
CATATAN  
Pada Opsi 3, AdGuard akan menganggap semua kueri datang dari alamat dnsdist, sehingga statistik per  
perangkat dan pengaturan per klien tidak lagi berguna.  

## 13.3 Memasang AdGuard Home kedua (LXC 101)

1. Buat CT 101 adguard2 (Bab 10), IP 192.168.88.11 lewat static lease.  
> Penjelasan: Container ringan cocok untuk DNS.
2. Masuk konsol CT 101 sebagai root.  
> Penjelasan: Tanpa sudo.

**TERMINAL (login sebagai root)** | Console CT 101 (root)

```
apt update && apt install -y curl
```
> Penjelasan: Memasang curl (jika belum).
2  
# U=https://raw.githubusercontent.com/AdguardTeam/AdGuardHome/master/scripts  
 curl -s -S -L $U/install.sh | sh -s -- -v  
> Penjelasan: Memasang AdGuard Home di /opt/AdGuardHome.
```
ss -tulpn | grep :53
```
> Penjelasan: Memeriksa apakah port 53 sudah dipakai program lain. Jika ya, bebaskan seperti di Bab 12.3.
1. Buka http://192.168.88.11:3000 dan jalankan wizard seperti di Gambar 12.1 (admin port 80, DNS  
port 53).  
2. Atur upstream dan blocklist sama persis dengan AdGuard di STB (12.3).  
> Penjelasan: Agar kedua server memblokir hal yang sama. Otomatisnya dengan adguardhome-sync (13.4).

## 13.4 Menyamakan pengaturan dengan adguardhome-sync

adguardhome-sync menyalin daftar blokir, aturan kustom, klien, dan DNS rewrites dari server utama  
(origin) ke server cadangan (replica). Dijalankan di Docker pada VM Debian 13 (Bab 14); jalankan bagian  
ini setelah Docker terpasang.  

**BERKAS: /opt/stacks/adguard-sync/compose.yaml** | VM Debian 13 (192.168.88.20)

```
services:
  adguardhome-sync:
    image: ghcr.io/bakito/adguardhome-sync:latest
    container_name: adguardhome-sync
    command: run
    restart: unless-stopped
    environment:
      - ORIGIN_URL=http://192.168.88.253
      - ORIGIN_USERNAME=admin
      - ORIGIN_PASSWORD=GANTI
      - REPLICA1_URL=http://192.168.88.11
      - REPLICA1_USERNAME=admin
      - REPLICA1_PASSWORD=GANTI
      - CRON=*/15 * * * *
      - RUNONSTART=true
```

**TERMINAL (login sebagai root)** | VM Debian 13 (root)

```
mkdir -p /opt/stacks/adguard-sync && cd /opt/stacks/adguard-sync
```
> Penjelasan: Membuat folder untuk stack ini.
```
nano compose.yaml
```
> Penjelasan: Tempel isi di atas. Ganti password.
```
docker compose up -d
```
> Penjelasan: Menjalankan layanan sinkronisasi.
```
docker compose logs -f
```
> Penjelasan: Melihat log. Harus ada baris sinkronisasi sukses.
TIPS  
Pada pemakaian jangka panjang, tulis versi image yang tetap (bukan latest) lalu biarkan Renovate (Bab 22)  
mengusulkan pembaruannya.  

## 13.5 Opsi 1: dua DNS di DHCP MikroTik

**TERMINAL MIKROTIK** | WinBox &gt; New Terminal

```
/ip dhcp-server network print
```
> Penjelasan: Melihat nomor baris jaringan DHCP (biasanya 0).
```
/ip dhcp-server network set 0 dns-server=192.168.88.253,192.168.88.11
```
> Penjelasan: Mengisi dua DNS: STB (utama) lalu LXC (cadangan).
```
/ip dns set servers=192.168.88.253,192.168.88.11 allow-remote-requests=no
```
> Penjelasan: DNS untuk router sendiri.

**COMMAND PROMPT WINDOWS** | Windows (laptop)

```
ipconfig /renew
```
> Penjelasan: Memperbarui lease DHCP di laptop.
```
ipconfig /all
```
> Penjelasan: Harus tampil dua DNS Server (.253 dan .11).
```
nslookup doubleclick.net 192.168.88.253
```
> Penjelasan: Tes AdGuard utama: jawaban 0.0.0.0.
```
nslookup doubleclick.net 192.168.88.11
```
> Penjelasan: Tes AdGuard kedua: jawaban 0.0.0.0.
Uji failover  
1. Di Proxmox, Shutdown CT 101.  
> Penjelasan: Mensimulasikan server cadangan mati.
2. Dari laptop buka beberapa situs baru.  
> Penjelasan: Internet harus tetap normal lewat STB.
3. Nyalakan CT 101, lalu hentikan layanan AdGuard di STB (/opt/AdGuardHome/AdGuardHome -s  
stop) dan ulangi uji.  
> Penjelasan: Menguji arah sebaliknya. Jangan lupa menyalakan lagi (-s start).
PERINGATAN  
Jangan menambahkan DNS publik (8.8.8.8) sebagai DNS ketiga di DHCP, karena sebagian klien akan lolos  
dari pemblokiran iklan.  

## 13.6 Opsi 2: IP virtual dengan keepalived

Hasilnya satu alamat (misalnya 192.168.88.5) yang selalu hidup. Pasang di STB dan di LXC 101, lalu klien  
memakai 192.168.88.5 sebagai satu-satunya DNS.  

**TERMINAL (login sebagai root)** | STB dan LXC 101 (root)

```
apt install -y keepalived
```
> Penjelasan: Memasang keepalived di kedua server.
```
ip -br a
```
> Penjelasan: Mencatat nama kartu jaringan (eth0 di LXC, end0/eth0 di STB).
```
nano /etc/keepalived/keepalived.conf
```
> Penjelasan: Membuat konfigurasi (isi di bawah).
```
systemctl enable --now keepalived
```
> Penjelasan: Menyalakan dan mengaktifkan setiap boot.
```
ip -br a
```
> Penjelasan: Pada server MASTER, alamat 192.168.88.5 harus muncul di kartu jaringan.

**BERKAS: /etc/keepalived/keepalived.conf** | STB = MASTER (priority 150), LXC 101 = BACKUP (priority 100)

```
vrrp_instance DNS_VIP {
state MASTER # di server cadangan ganti BACKUP
interface eth0 # nama kartu jaringan
virtual_router_id 51
priority 150 # di server cadangan pakai 100
advert_int 1
authentication {
auth_type PASS
auth_pass GANTI8
}
virtual_ipaddress {
192.168.88.5/24
}
}
```

**TERMINAL MIKROTIK** | WinBox &gt; New Terminal

```
/ip dhcp-server network set 0 dns-server=192.168.88.5
```
> Penjelasan: Membagikan IP virtual sebagai satu-satunya DNS.
CATATAN  
VRRP kadang bermasalah di jaringan WiFi. Uji di jaringan kabel. Jika tidak stabil,  
kembali ke Opsi 1.  

## 13.7 Opsi 3: balancer dengan dnsdist (latihan)

Tujuan: LXC 104 dnsdist (alamat 192.168.88.13) menerima semua kueri lalu membaginya ke dua  
AdGuard (STB dan LXC 101) dengan pemeriksaan kesehatan otomatis.  
1. Buat CT 104 dnsdist (1 core, 256 MB, 4 GB), IP 192.168.88.13 lewat static lease.  
2. Di dalam CT, pasang dnsdist dan atur konfigurasinya.  
> Penjelasan: dnsdist adalah pembagi beban DNS resmi dari PowerDNS.

**TERMINAL (login sebagai root)** | Console CT 104 (root)

```
apt update && apt install -y dnsdist
```
> Penjelasan: Memasang dnsdist dari repository Debian.
```
nano /etc/dnsdist/dnsdist.conf
```
> Penjelasan: Mengisi konfigurasi (isi di bawah).
```
systemctl restart dnsdist
```
> Penjelasan: Menerapkan konfigurasi.
```
systemctl status dnsdist
```
> Penjelasan: Memastikan layanan berjalan (active).
```
dnsdist -c
```
> Penjelasan: Membuka konsol dnsdist. Ketik showServers() untuk melihat status tiap server, quit untuk
keluar.  

**BERKAS: /etc/dnsdist/dnsdist.conf** | Konfigurasi dnsdist

```
setLocal("0.0.0.0:53")
addACL("192.168.88.0/24")
newServer({address="192.168.88.253:53", name="adguard-stb",
checkInterval=5, maxCheckFailures=3})
newServer({address="192.168.88.11:53", name="adguard-lxc",
checkInterval=5, maxCheckFailures=3})
setServerPolicy(leastOutstanding)
```

Baris Arti  
setLocal(...) dnsdist mendengarkan di port 53 pada semua alamat.  
addACL(...) Hanya jaringan 192.168.88.0/24 yang boleh bertanya (mencegah DNS  
terbuka).  
newServer(...) Mendaftarkan satu server tujuan (AdGuard) dan memeriksa  
kesehatannya tiap 5 detik.  
setServerPolicy(leastOutstanding) Mengirim kueri ke server yang paling sedikit antreannya. Alternatif:  
roundrobin, firstAvailable.  

**COMMAND PROMPT WINDOWS** | Windows (laptop)

```
nslookup doubleclick.net 192.168.88.13
```
> Penjelasan: Tes lewat dnsdist: harus menjawab 0.0.0.0.
```
nslookup google.com 192.168.88.13
```
> Penjelasan: Tes jawaban normal.

**TERMINAL MIKROTIK** | WinBox &gt; New Terminal

```
/ip dhcp-server network set 0 dns-server=192.168.88.13
```
> Penjelasan: Mengarahkan seluruh klien ke dnsdist.
PERINGATAN  
Jika CT 104 mati, seluruh DNS rumah ikut mati karena hanya satu alamat yang dibagikan. Untuk menguji,  
kembalikan DHCP ke Opsi 1 (dns-server=192.168.88.253,192.168.88.11) kapan saja. Jika port 53  
sudah dipakai di LXC, bebaskan seperti di Bab 12.3.  

## 13.8 Subnet router Tailscale cadangan (opsional)

Untuk berjaga bila STB mati, pasang Tailscale juga di container LXC (misalnya CT 103) dengan akses ke  
perangkat TUN.  

**TERMINAL (login sebagai root)** | Shell Proxmox

```
pct shutdown 103
```
> Penjelasan: Mematikan CT 103 sebelum mengubah konfigurasi.
```
nano /etc/pve/lxc/103.conf
```
> Penjelasan: Tambahkan dua baris di akhir berkas (isi di bawah).
```
pct start 103
```
> Penjelasan: Menyalakan kembali.

**BERKAS: /etc/pve/lxc/103.conf** | Tambahkan di akhir berkas

```
lxc.cgroup2.devices.allow: c 10:200 rwm
lxc.mount.entry: /dev/net/tun dev/net/tun none bind,create=file
```

Lalu di dalam CT 103 pasang Tailscale seperti Bab 12.4 dan setujui rute yang sama; Tailscale beralih  
otomatis jika satu perangkat mati.  

## 13.9 Memasang Pi-hole (jika memilih Pi-hole)

**TERMINAL (login sebagai root)** | Console CT (root), contoh CT 105 192.168.88.14

```
apt update && apt install -y curl
```
> Penjelasan: Memasang curl.
```
curl -sSL https://install.pi-hole.net | bash
```
> Penjelasan: Menjalankan installer resmi Pi-hole. Ikuti wizard teks: pilih interface, upstream DNS, blocklist, dan
catat password admin.  
```
pihole setpassword
```
> Penjelasan: Mengubah password admin web.
Web admin di http://192.168.88.14/admin. Pengaturan MikroTik sama (isi DNS di DHCP). Jangan  
menjalankan Pi-hole dan AdGuard di mesin yang sama karena bentrok port 53.  

## 13.10 Opsional: mencegah perangkat memakai DNS lain

Sebagian aplikasi atau TV memakai DNS bawaan (misalnya 8.8.8.8) sehingga lolos dari pemblokiran.  
MikroTik dapat memblokir permintaan DNS ke internet kecuali dari server AdGuard.  

**TERMINAL MIKROTIK** | WinBox &gt; New Terminal (opsional)

```
/ip firewall address-list add list=dns-servers address=192.168.88.253
```
> Penjelasan: Daftar server DNS yang diizinkan: STB.
```
/ip firewall address-list add list=dns-servers address=192.168.88.11
```
> Penjelasan: Server DNS kedua.
3  
&gt; /ip firewall filter add chain=forward action=drop protocol=udp dst-port=53 \  
 out-interface=ether1 src-address-list=!dns-servers place-before=0 \  
 comment="blok DNS UDP luar"  
> Penjelasan: Menjatuhkan DNS UDP ke internet kecuali dari AdGuard.
4  
&gt; /ip firewall filter add chain=forward action=drop protocol=tcp dst-port=53 \  
 out-interface=ether1 src-address-list=!dns-servers place-before=0 \  
 comment="blok DNS TCP luar"  
> Penjelasan: Sama untuk DNS TCP.
PERINGATAN  
Aturan ini memutus perangkat yang tidak memakai DNS dari DHCP. Uji dulu, dan siapkan cara membatalkan  
(/ip firewall filter remove [find comment~"blok DNS"]). DNS-over-HTTPS (port 443) di browser  
tidak terblokir oleh aturan ini.  
KASUS NYATA - Satu perangkat masih menampilkan iklan  
Gejala: Sebagian perangkat tidak memblokir iklan.  
Penyebab: Perangkat memakai DNS sendiri (Secure DNS di browser, DNS tetap, lease lama).  
Solusi: Matikan Secure DNS di browser, setel DNS otomatis, ipconfig /renew, atau gunakan aturan di  
13.10.
