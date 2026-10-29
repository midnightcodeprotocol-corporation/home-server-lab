# Bab 51. Firewall Proxmox antar-guest

PENEMPATAN - HOST - tidak ada guest baru  
Tempat: Aturan dibuat di host Proxmox (web Proxmox atau berkas /etc/pve/firewall) dan berlaku untuk semua guest.  
Alasan: Firewall Proxmox bekerja di jembatan jaringan, di luar guest. Port yang dibuka Docker di dalam VM tidak  
bisa menembusnya, tidak seperti UFW di dalam VM.  
PERINGATAN  
Firewall Proxmox mati secara bawaan. Setelah dinyalakan di tingkat Datacenter, lalu lintas ke host diblokir kecuali  
web (8006) dan SSH (22) dari jaringan lokal (menurut dokumentasi). Buka sesi SSH ke host sebelum  
mengaktifkannya, dan ikuti urutan di 51.3. Konsol web VM (noVNC) tetap berfungsi bila aturan VM salah.  

## 51.1 Tiga tingkat

Tingkat Tempat Fungsi  
Datacenter Datacenter &gt; Firewall Saklar utama, daftar IPSet, kelompok aturan;  
aturannya ikut berlaku untuk host  
Node (host) Node &gt; Firewall Aturan khusus host; lebih diutamakan daripada  
aturan Datacenter  
VM / CT VM &gt; Firewall, dan kotak Firewall pada Network  
Device  
Aturan per guest. Tanpa kotak itu pada kartu  
jaringan, aturan VM tidak berlaku  

## 51.2 Matriks akses: siapa boleh ke mana

Tujuan Port Boleh dari Alasan  
201 docker-core 80, 443 Seluruh LAN 192.168.88.0/24 Pintu semua layanan (Caddy)  
201 docker-core 8070 (Gotify) host .10, n8n .27, pbs .30 Peringatan Proxmox, PBS, dan n8n  
204 git 3000 (web) docker-core .20 Web Forgejo hanya lewat Caddy  
(git.home.arpa)  
204 git 2222 (SSH Git) IPSet admin dan VM 203 k3s .22 Clone dari laptop dan Flux (Edisi 2 Bab  
21)  
202 haos 8123 Seluruh LAN 192.168.88.0/24 Aplikasi HP dan peramban; dari luar  
rumah lewat Tailscale (alamat CT103)  
203 k3s 6443 IPSet admin kubectl dari laptop  
206 affine 3010 docker-core .20 Hanya lewat Caddy  
207 nextcloud 8080 docker-core .20 Hanya lewat Caddy  
208 n8n 5678 docker-core .20 Hanya lewat Caddy  
209 web 8081, 8082 docker-core .20 Hanya lewat Caddy  
205 vault (tidak ada) - Hanya lewat Tailscale Serve (koneksi  
keluar)  
210 web-public (tidak ada) - Hanya koneksi keluar lewat tunnel;  
keluar ke LAN diblokir  
211 music (tidak ada) - Hanya lewat Tailscale Serve (koneksi  
keluar); berkas aturan di Bab 53.6  
213 sso (tidak ada) - Hanya lewat Tailscale Serve (koneksi  
keluar); berkas aturan di Bab 54.7  
214 immich (tidak ada) - Hanya lewat Tailscale Serve (koneksi  
keluar); berkas aturan di Bab 55.8  
212 pbs 8007 host .10 dan admin Antarmuka dan sinkron PVE  
Semua VM 22 (SSH) IPSet admin Pengelolaan  
Semua VM port agen Beszel docker-core .20 Hub menghubungi agen (port:  
Suplemen 3 Bab 33)  
Host .10 8006, 22 IPSet admin Pengelolaan Proxmox  
IPSet admin berisi perangkat yang boleh mengelola: PC kabel (192.168.88.252), laptop Anda, dan alamat  
CT103 (router-vm). Perangkat yang masuk lewat Tailscale tiba dari alamat CT103 (subnet router menyamarkan  
sumbernya [BELUM PASTI]), jadi tanpa itu SSH dari luar rumah akan diblokir. Kendali siapa yang boleh lewat  
Tailscale ada di kebijakan tailnet.  

## 51.3 Urutan menyalakan (agar tidak terkunci)

1. Buka SSH ke host (ssh root@192.168.88.10) dan biarkan terbuka. Siapkan juga konsol web VM.  
2. Reservasi alamat tetap untuk laptop Anda di MikroTik (seperti Bab 49.4) agar IPSet tidak basi.  
3. Datacenter &gt; Firewall &gt; IPSet &gt; Create admin; tambahkan 192.168.88.252, alamat laptop, dan alamat CT103.  
4. Datacenter &gt; Firewall &gt; Options: Firewall Yes, Input Policy DROP, Output Policy ACCEPT. Uji bahwa web  
Proxmox (8006) dan SSH host tetap terbuka dari laptop.  
5. Aktifkan firewall per VM satu demi satu, mulai dari yang paling sederhana (VM 205). Setiap kali: Options VM:  
Firewall Yes, Input DROP, Output ACCEPT; kotak Firewall pada Hardware &gt; Network Device; tambah aturan;  
uji (51.6).  
6. Biarkan opsi IP filter dan MAC filter pada setelan bawaannya; laporan pengguna menyebut IP filter yang aktif  
bisa membuat VM tak terjangkau.  

## 51.4 Aturan per VM

Contoh berikut mengikuti matriks di 51.2 dan contoh berkas di `konfigurasi/firewall/`. Port agen Beszel adalah `45876` menurut `docs/07-port-dan-akses.md`. Sesuaikan hanya setelah memeriksa port aktual pada guest; aktifkan firewall per guest satu per satu dan uji dari klien.

Berkas docker-core:

**/etc/pve/firewall/201.fw** | Isi berkas

```
[OPTIONS]
enable: 1
policy_in: DROP
policy_out: ACCEPT
dhcp: 1
[RULES]
IN ACCEPT -source +dc/admin -p tcp -dport 22
IN ACCEPT -source 192.168.88.0/24 -p tcp -dport 80,443
IN ACCEPT -source 192.168.88.10 -p tcp -dport 8070
IN ACCEPT -source 192.168.88.27 -p tcp -dport 8070
IN ACCEPT -source 192.168.88.30 -p tcp -dport 8070
IN ACCEPT -p icmp
```

VM aplikasi di belakang Caddy (contoh VM 206 AFFiNE):

**/etc/pve/firewall/206.fw** | Isi berkas

```
[OPTIONS]
enable: 1
policy_in: DROP
policy_out: ACCEPT
dhcp: 1
[RULES]
IN ACCEPT -source +dc/admin -p tcp -dport 22
IN ACCEPT -source 192.168.88.20 -p tcp -dport 3010
IN ACCEPT -source 192.168.88.20 -p tcp -dport 45876
IN ACCEPT -p icmp
```

Untuk VM 207, 208, dan 209, ganti port layanan dengan nilai pada matriks 51.2: `8080`, `5678`, dan `8081,8082`. Jika memakai mode hemat dan layanan digabung ke VM 206, aturan harus mencakup seluruh port layanan yang benar-benar dipakai VM tersebut.

VM git: web hanya dari Caddy; SSH Git dari admin dan VM k3s:

**/etc/pve/firewall/204.fw** | Isi berkas

```
[OPTIONS]
enable: 1
policy_in: DROP
policy_out: ACCEPT
dhcp: 1
[RULES]
IN ACCEPT -source +dc/admin -p tcp -dport 22
IN ACCEPT -source +dc/admin -p tcp -dport 2222
IN ACCEPT -source 192.168.88.22 -p tcp -dport 2222
IN ACCEPT -source 192.168.88.20 -p tcp -dport 3000
IN ACCEPT -source 192.168.88.20 -p tcp -dport 45876
IN ACCEPT -p icmp
```

VM web-public: izinkan SSH admin, DNS keluar ke AdGuard, lalu blokir akses ke LAN:

**/etc/pve/firewall/210.fw** | Isi berkas

```
[OPTIONS]
enable: 1
policy_in: DROP
policy_out: ACCEPT
dhcp: 1
[RULES]
IN ACCEPT -source +dc/admin -p tcp -dport 22
OUT ACCEPT -dest 192.168.88.253 -p udp -dport 53
OUT ACCEPT -dest 192.168.88.253 -p tcp -dport 53
OUT DROP -dest 192.168.88.0/24
```

Untuk VM 205, 211, 213, dan 214, jangan buka port layanan pada LAN; layanan diakses melalui Tailscale Serve. Untuk VM 212 PBS, izinkan port 8007 hanya dari host Proxmox dan perangkat admin. Aturan VM 202 Home Assistant dan VM 203 k3s mengikuti matriks 51.2.

> [!WARNING]
> Contoh ini mengasumsikan IPSet Datacenter bernama `admin` dan sintaks `+dc/admin` diterima oleh versi Proxmox yang dipakai. Bagian ini masih perlu diuji pada host sebelum firewall diaktifkan. Jangan mengaktifkan aturan massal; uji satu guest dan pastikan akses konsol serta jalur pemulihan tersedia.

**TERMINAL HOST PROXMOX** | Shell node Proxmox (host), sebagai root

```
pve-firewall status
```
> Penjelasan: Memastikan layanan firewall berjalan dan aktif.
```
qm config 206 | grep net0
```
> Penjelasan: Menampilkan baris kartu jaringan. Aktifkan firewall pada kartu itu bila belum (langkah berikut).
```
qm set 206 --net0 "virtio=AA:BB:CC:DD:EE:FF,bridge=vmbr0,firewall=1"
```
> Penjelasan: Menulis ulang net0 dengan firewall=1. Salin nilai MAC dan bridge dari baris sebelumnya; atau pakai
kotak Firewall di antarmuka web.  

## 51.5 Sisi klien

1. Windows: buka https://affine.home.arpa, https://nextcloud.home.arpa, https://n8n.home.arpa,  
https://wp.home.arpa. Semua tetap terbuka karena lewat Caddy (443).  
2. Android dan iPhone: buka alamat yang sama di browser (rumah atau Tailscale). Hasil harus sama dengan di  
laptop.  
3. Kini alamat langsung seperti http://192.168.88.25:3010 dari laptop atau HP tidak boleh terbuka lagi. Itu  
tandanya firewall bekerja.  

## 51.6 Uji

**POWERSHELL WINDOWS** | PowerShell (laptop)

```
Test-NetConnection 192.168.88.25 -Port 3010
```
> Penjelasan: Harus TcpTestSucceeded: False (diblokir). Laptop tidak termasuk 192.168.88.20.
```
Test-NetConnection 192.168.88.20 -Port 443
```
> Penjelasan: Harus True (gerbang Caddy terbuka).

**TERMINAL VM DOCKER-CORE** | VM docker-core, sebagai root

```
timeout 3 bash -c '</dev/tcp/192.168.88.25/3010' && echo terbuka || echo tertutup
```
> Penjelasan: Dari docker-core ke AFFiNE: harus terbuka.
```
timeout 3 bash -c '</dev/tcp/192.168.88.26/22' && echo terbuka || echo tertutup
```
> Penjelasan: Dari docker-core ke SSH nextcloud: harus tertutup (docker-core bukan IPSet admin).

**TERMINAL VM WEB-PUBLIC** | VM web-public (210), sebagai root

```
timeout 3 bash -c '</dev/tcp/192.168.88.20/443' && echo terbuka || echo tertutup
```
> Penjelasan: Harus tertutup: VM publik tidak boleh menjangkau LAN.
```
curl -sI https://example.com | head -1
```
> Penjelasan: Harus berhasil (internet tetap bisa, termasuk untuk tunnel dan pembaruan).
TIPS  
Terkunci? Buka konsol web VM di Proxmox (tidak lewat jaringan VM), atau di VM: Firewall &gt; Options &gt; Firewall No,  
perbaiki aturan, lalu nyalakan lagi.
