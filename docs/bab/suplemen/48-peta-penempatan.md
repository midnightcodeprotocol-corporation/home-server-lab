# Bab 48. Peta Penempatan: Siapa Tinggal di Mana

## 48.1 Mengapa dipisah, dan harganya

• Dampak kebobolan terbatas. Bila WordPress diretas, penyerang berada di VM web, bukan di VM yang berisi  
kata sandi atau kredensial n8n.  
• Backup dan pemulihan per layanan. PBS (Bab 50) mencadangkan dan memulihkan satu VM tanpa  
menyentuh yang lain.  
• Firewall per guest. Aturan di Proxmox (Bab 51) bisa menutup port satu VM dari VM lain.  
• Pembaruan terpisah. Nextcloud harus naik satu mayor demi satu mayor; itu tidak boleh menahan layanan  
lain.  
Harganya: setiap VM membawa sistem operasinya sendiri (RAM dan disk), ada lebih banyak mesin untuk  
diperbarui, dan Caddy tidak lagi menjangkau layanan lewat nama container tetapi lewat IP:port. Karena itu ada  
kelompok yang sengaja digabung dan mode hemat di 48.6.  

## 48.2 Empat pertanyaan penempatan

Pertanyaan Bila jawabannya ya Contoh  
Memakai Docker? Guest berupa VM. Dokumentasi Proxmox menyarankan  
menjalankan container aplikasi seperti Docker di dalam VM  
QEMU, bukan di LXC atau di host  
Semua layanan buku ini  
Hanya layanan Linux ringan tanpa  
Docker?  
Boleh LXC (ringan, berbagi kernel host) Tailscale router (CT103),  
AdGuard kedua (CT101),  
Samba (CT102)  
Menyimpan rahasia (kata sandi,  
kredensial layanan lain)?  
VM sendiri vault, n8n, git (token  
Renovate, kunci deploy)  
Menghadap internet? VM sendiri dan paling terisolasi web-public  
Data besar atau siklus pembaruan  
berbeda?  
VM sendiri nextcloud, pbs  
Ringan, saling bergantung, dan  
harus menjangkau semua guest?  
Gabung dalam satu VM infrastruktur Caddy, Gotify, Uptime  
Kuma, Homepage,  
Beszel hub, Portainer  
CATATAN  
Proxmox VE 9.1 menambah dukungan image OCI (Docker) sebagai container aplikasi di LXC, tetapi masih berstatus  
tech preview menurut dokumentasi dan tulisan pihak ketiga. Buku ini tidak memakainya; VM tetap pilihan untuk  
Docker. Host Proxmox tidak menjalankan Docker sama sekali.  

## 48.3 Peta guest dan alamat

Host Proxmox (192.168.88.10) - tanpa Docker dan tanpa aplikasi  
201 docker-core  
.20 Caddy  
204 git  
.23 Forgejo  
205 vault  
.24 Vaultwarden  
206 affine  
.25 AFFiNE  
207 nextcloud  
.26 Nextcloud  
213 sso  
.32 Pocket ID  
208 n8n  
.27 n8n  
209 web  
.28 situs, WP  
210 web-public  
.29 internet  
211 music  
.31 Navidrome  
212 pbs  
.30 backup  
214 immich  
.33 Immich  
CT103 ts-router  
LXC, Tailscale (nanti STB 2)  
STB 1 .253  
AdGuard Home (perangkat sendiri)  
VM 9100 tpl  
templat Debian + Docker (mati)  
Gambar 48.1 - Host Proxmox dengan guest terpisah (VM 202 HAOS, 203 k3s, CT101 dan CT102 dari Edisi 2 tidak digambar); STB 1  
dan CT103 di luar kelompok VM Docker.  
VMID Nama Jenis IP Isi Bab  
9100 tpl-debian-docker VM (templat) - Debian 13 + Docker + agen tamu; tidak  
pernah dinyalakan (beda dari templat  
cloud-init 9000 Edisi 2)  
49  
201 docker-core VM .20 Caddy (gerbang HTTPS), Portainer,  
Gotify, Uptime Kuma, Beszel hub,  
Homepage, adguardhome-sync  
31-38  
202 haos VM .21 Home Assistant OS Edisi 2  
203 k3s VM .22 Kubernetes k3s + Flux Edisi 2  
204 git VM .23 Forgejo + Renovate (pindah dari VM  
201 Edisi 2)  
Edisi 2,  
48.8  
205 vault VM .24 Vaultwarden + node Tailscale lab-vault 44-45  
206 affine VM .25 AFFiNE (+ Postgres, Redis) 46  
207 nextcloud VM .26 Nextcloud (+ Postgres, Redis, cron) 47  
208 n8n VM .27 n8n (+ Postgres) 42  
209 web VM .28 Situs statis privat, WordPress (+  
MariaDB)  
40-41  
210 web-public VM .29 cloudflared + situs statis publik 43  
211 music VM .31 Navidrome (streaming musik) + disk  
pustaka  
53  
212 pbs VM .30 Proxmox Backup Server 50  
213 sso VM .32 Pocket ID (SSO passkey) + node  
Tailscale lab-sso  
54  
214 immich VM .33 Immich (foto) + disk foto kedua + node  
Tailscale lab-immich  
55  
101 adguard2 LXC .11 AdGuard Home kedua (failover DNS) Edisi 2  
102 files LXC .12 Samba (folder jaringan) Edisi 2  
103 ts-router LXC (lihat Edisi 2) Tailscale subnet router (nanti pindah ke  
STB 2)  
26  
- STB 1 perangkat .253 AdGuard Home (DNS rumah), terpisah  
dari Proxmox  
Edisi 2  
Semua alamat berada di LAN 192.168.88.0/24 milik MikroTik. VM 201-210 mengikuti urutan alamat .20-.29; VM  
211 (music, .31) dan 212 (pbs, .30) ditambahkan belakangan sehingga urutannya bertukar. CT101-105 dan  
alamat .11-.14 tetap seperti Lampiran B Edisi 2. Ganti bila bentrok dengan VM lain Anda; yang penting konsisten  
di semua bab.  

## 48.4 Aturan menerjemahkan bab lama

Sebelum pemisahan, banyak bab menulis "VM Docker 192.168.88.20" dan memakai jaringan Docker proxy  
bersama. Revisi 2 Suplemen 3 sampai 6 sudah memakai aturan di bawah. Gunakan tabel ini bila Anda  
menambah layanan sendiri atau membaca bab lama yang belum direvisi.  
Teks lama Ganti dengan Alasan  
VM Docker 192.168.88.20 untuk  
layanan X  
Guest X menurut tabel 48.3 Setiap layanan punya tempatnya  
networks: proxy (external) pada  
layanan di VM lain  
Hapus. Layanan hanya memakai jaringan  
internalnya  
Jaringan Docker tidak melintasi VM  
reverse_proxy nama-container:port reverse_proxy IP-VM:port-yang-dibuka Caddy dan layanan berada di VM  
berbeda  
ports: 127.0.0.1:PORT:PORT ports: PORT:PORT (terbuka di LAN VM itu) Caddy di VM lain harus bisa  
menjangkaunya; dikunci firewall  
Proxmox (Bab 51)  
TRUSTED_PROXIES: 172.16.0.0/12 TRUSTED_PROXIES: 192.168.88.20 Permintaan tiba dari alamat  
docker-core  
http://gotify:80 (dari layanan lain) http://192.168.88.20:8070 Gotify di VM lain  
Monitor Uptime Kuma ke nama  
container  
Monitor ke IP:port VM atau ke alamat  
Caddy  
Kuma di docker-core  
Agen Beszel hanya di satu VM Agen di setiap VM; hub menghubungi tiap  
agen  
Setiap VM dipantau sendiri  
Contoh hasil akhir: Caddyfile di docker-core setelah semua layanan berpindah (blok gembok, header, dan redir  
seperti di bab masing-masing):  

**/opt/stacks/caddy/Caddyfile (ringkas)** | Gambaran akhir

```
web.home.arpa { reverse_proxy 192.168.88.28:8082 }
wp.home.arpa { reverse_proxy 192.168.88.28:8081 }
n8n.home.arpa { reverse_proxy 192.168.88.27:5678 }
affine.home.arpa { reverse_proxy 192.168.88.25:3010 }
git.home.arpa { reverse_proxy 192.168.88.23:3000 }
nextcloud.home.arpa {
 header Strict-Transport-Security "max-age=15552000"
 redir /.well-known/carddav /remote.php/dav/ 301
 redir /.well-known/caldav /remote.php/dav/ 301
 reverse_proxy 192.168.88.26:8080
}
```

CATATAN  
Vaultwarden tidak muncul di Caddyfile: ia hanya terbuka lewat Tailscale Serve di VM vault. Navidrome (VM 211) juga  
hanya lewat Tailscale Serve. Situs publik (VM 210) tidak lewat Caddy; ia keluar lewat Cloudflare Tunnel.  

## 48.5 Pemetaan bab lama ke guest

Bab Layanan Guest Yang berubah dari teks asli  
Edisi 2 AdGuard Home STB 1 (.253) Tidak ada: sengaja di luar Proxmox  
Edisi 2 Debian + Docker, Portainer,  
Homepage, adguardhome-sync  
VM 201 (templat 9100  
dibuat di Bab 49)  
VM Debian pertama menjadi  
docker-core atau sumber templat  
(Bab 49); Homepage pindah port  
(48.8)  
Edisi 2, Bab 15 dan  
22  
Forgejo, Renovate VM 204 (.23) Pindah dari VM 201; lihat 48.8  
Edisi 2, Bab 16 Nextcloud Dilewati; pakai Suplemen 6  
Bab 47 (VM 207)  
Bab 16 Edisi 2 tidak dikerjakan; lihat  
48.8  
Edisi 2, Bab 17  
sampai 21  
Samba, Home Assistant, k3s,  
Flux  
CT102, VM 202, VM 203 Tidak ada; hanya alamat Forgejo di  
Flux (48.8)  
Suplemen 1, Bab 25 Pengerasan dasar Semua guest + host UFW tidak mengatur port Docker;  
tambahkan firewall Proxmox (Bab 51)  
Suplemen 1, Bab 26 Tailscale subnet router CT103 (LXC) Pilihan B (VM Docker) tidak dipakai;  
pakai C  
Suplemen 2, Bab  
27-30  
Proxmox di ThinkCentre M710q Host Tidak ada; host tanpa aplikasi  
Suplemen 3, Bab  
31-34  
Uptime Kuma, Gotify, Beszel VM 201; agen Beszel di  
semua VM  
Agen dipasang saat VM dibuat  
Suplemen 4, Bab  
35-38  
Caddy, sertifikat VM 201 Teruskan ke IP:port VM lain  
Suplemen 5, Bab  
39-43  
Situs statis, WordPress, n8n,  
tunnel  
VM 209, 208, 210 Sudah ditulis ulang di Revisi 2  
Suplemen 6, Bab  
44-47  
Vaultwarden, AFFiNE, Nextcloud VM 205, 206, 207 Sudah ditulis ulang di Revisi 2; node  
Tailscale lab-vault, tcp:443  
Suplemen 8, Bab 53 Navidrome (musik) VM 211 Baru; node Tailscale lab-music,  
tcp:443  
Suplemen 9, Bab  
54-56  
Pocket ID (SSO), Immich (foto),  
profil RAM  
VM 213, 214 Baru; node Tailscale lab-sso dan  
lab-immich, tcp:443; profil untuk  
mesin 16 GB di Bab 56  

## 48.6 Mode hemat dan perkiraan RAM

Proxmox menjalankan sistem operasi lengkap per VM, jadi RAM total = jumlah RAM semua VM + kebutuhan  
host. Angka awal di bawah adalah perkiraan saya [BELUM PASTI] dan bukan angka resmi; ukur dengan Beszel  
lalu sesuaikan. Sisakan RAM untuk host Proxmox sendiri.  
VM RAM awal (MB) Boleh digabung?  
201 docker-core 2048 Inti; tidak digabung  
204 git 1024 Tidak (menyimpan token dan kunci deploy)  
205 vault 1024 Tidak pernah  
206 affine 2048 Ya, ke "apps" (VM 206)  
207 nextcloud 2048 Tidak (data besar, pembaruan sendiri)  
208 n8n 1536 Ya, ke "apps" (VM 206)  
209 web 1536 Ya, ke "apps" (VM 206)  
210 web-public 768 Tidak pernah  
211 music 1024 Ya, ke "apps" (VM 206)  
VM RAM awal (MB) Boleh digabung?  
212 pbs 2048 Tidak pernah (backup terpisah dari yang dicadangkan)  
213 sso 1024 Tidak pernah (memegang kunci masuk ke layanan lain)  
214 immich 6144 (4096 tanpa ML) Tidak (database vektor, ML, dan foto sendiri)  
Jumlah (terpisah penuh) 22.272 MB (sekitar  
21,8 GB)  
Belum termasuk host Proxmox, HAOS, dan k3s  
Mode hemat: apps 3072 MB  
menggantikan 206+208+209+211  
19.200 MB (sekitar  
18,8 GB)  
Menghemat sistem operasi tiga VM  
Bersama VM Edisi 2 (HAOS 2048 MB,  
k3s 3072 sampai 4096 MB)  
27.392 sampai 28.416  
MB (26,8 sampai 27,8  
GB); mode hemat  
24.320 sampai 25.344  
MB  
Edisi 2 membuat VM 201 dengan 4096 MB; 2048 MB  
adalah sasaran setelah Forgejo dan Nextcloud pindah  
[BELUM PASTI]  
PERINGATAN  
Mesin utama (ThinkCentre M710q, i5-6500T) dilaporkan memakai RAM 24 GB (16+8) per 31 Oktober 2026; BIOS dan MemTest86 belum dikonfirmasi (Bab 27.1).  
Profil pemakaian lama disusun untuk 16 GB dan 32 GB. Pada 24 GB, gunakan baseline konservatif dan tambah beban bertahap sesuai Bab 56.8; jangan menyalakan semua VM sekaligus tanpa pemantauan.  
Bila memakai mode hemat Perubahan  
n8n, web, music, affine menjadi VM 206 "apps"  
(192.168.88.25)  
Ganti IP di Caddyfile: 8081, 8082, 5678, 3010 semuanya di  
192.168.88.25; port sama, tidak ada bentrok  
Kotak Penempatan bab 40, 41, 42, 46, 53 Jalankan langkah di VM apps, tanpa membuat VM 208, 209, dan 211  
(disk musik menjadi disk kedua VM apps)  
Firewall (Bab 51) Aturan untuk 206 menggabungkan port 3010, 5678, 8081, 8082 dari  
192.168.88.20  

## 48.7 Cara membaca Kotak Penempatan

Di awal setiap bab pemasangan Anda akan melihat kotak ungu seperti di bawah. Ia menjawab satu pertanyaan:  
buat guest baru, atau gabung ke yang sudah ada?  
PENEMPATAN - BARU - VM sendiri  
Tempat: VM 208 n8n (192.168.88.27): qm clone 9100 208 --name n8n --full 1.  
Alasan: Satu kalimat mengapa dipisah atau digabung.  
Mode hemat: Bila ada, guest mana yang boleh menampungnya bersama layanan lain.  
Label di kotak Artinya  
BARU Buat VM atau LXC baru (perintah qm clone atau pct create diberikan)  
GABUNG Pasang di guest yang sudah ada; nama dan IP guest disebut  
HOST Dikerjakan di host Proxmox; bukan di guest  
TIDAK ADA GUEST Bab konsep, langkah klien, atau pengujian  
SEMUA GUEST Dikerjakan di setiap guest (pengerasan, audit)  

## 48.8 Penyesuaian Edisi 2

Edisi 2 (halaman 1-122) tidak diubah. Ia menaruh Docker, Portainer, Homepage, Forgejo, dan Nextcloud di satu  
VM 201. Tiga keputusan di buku ini mengubah sebagian isinya: Forgejo dan Renovate pindah ke VM 204 git,  
Nextcloud Edisi 2 Bab 16 dilewati dan diganti Suplemen 6 Bab 47, dan Homepage berpindah port sebelum  
Caddy dipasang. Baca bagian Edisi 2 di bawah dengan nilai pada kolom kanan.  
Bagian Edisi 2 Yang tertulis Dibaca sebagai  
Bab 15.2 sampai 15.5  
(Forgejo)  
VM Debian di 192.168.88.20; Server  
Domain, Base URL, dan alamat clone  
memakai .20  
VM 204 git (192.168.88.23) dari templat 9100 (Bab  
49.4). Compose dan folder /opt/stacks/forgejo  
sama. Base URL http://192.168.88.23:3000/, clone  
ssh://git@192.168.88.23:2222/USER/homelab.git  
Bab 21.2 (flux bootstrap) ssh://git@192.168.88.20:2222/USERNA  
ME/homelab.git  
ssh://git@192.168.88.23:2222/USERNAME/homela  
b.git  
Bab 22.2 (Renovate) RENOVATE_ENDPOINT=http://192.168.  
88.20:3000/api/v1/, dijalankan di VM  
Debian  
http://192.168.88.23:3000/api/v1/, dijalankan di VM  
204 (Docker sudah ada dari templat)  
Bab 16 (Nextcloud) Nextcloud, MariaDB, Redis di VM 201,  
port 8080  
Dilewati. Pasang dengan Suplemen 6 Bab 47 di  
VM 207 (192.168.88.26). Migrasi data dari Bab 16  
tidak dibahas  
Bab 19.1 (Homepage) ports "80:3000"; HOMEPAGE_ALLOWE  
D_HOSTS=192.168.88.20,home.lan  
ports "3002:3000"; HOMEPAGE_ALLOWED_HOS  
TS=192.168.88.20:3002,dash.home.arpa. Port 80  
dan 443 dikosongkan untuk Caddy  
Bab 19.2 dan 19.4 (kartu,  
DNS)  
Kartu dan rewrite Forgejo serta Nextcloud  
menunjuk .20  
Forgejo ke 192.168.88.23:3000 (git.home.arpa  
lewat Caddy), Nextcloud ke 192.168.88.26:8080.  
Nama .lan Edisi 2 boleh tetap berdampingan  
dengan \*.home.arpa  
Bab 11.2 (VM 201) Memory 4096 MiB Boleh diturunkan ke 2048 MB setelah Forgejo dan  
Nextcloud tidak lagi di VM 201 [BELUM PASTI]  
Bab 11.7 (templat 9000) Templat cloud-init untuk VM k3s Tetap untuk VM 203. Templat 9100 (Bab 49)  
terpisah, untuk VM layanan  
Bab 13.4  
(adguardhome-sync)  
Jalan di VM 201 Tidak berubah  
Lampiran B Rencana IP dan ID Edisi 2 Tidak ada ID atau IP yang diubah; ditambah VM  
204 sampai 212, alamat .23 sampai .31, dan  
templat 9100 (tabel 48.3)  
PERINGATAN  
Homepage memakai port 3002, bukan 3001: Uptime Kuma (Suplemen 3 Bab 31) sudah memakai 3001 di VM 201,  
sehingga dua layanan tidak bisa berbagi port itu sebelum Caddy dipasang.  

**TERMINAL VM DOCKER-CORE** | VM 201, sebagai root (setelah su -)

```
cd /opt/stacks/homepage && nano compose.yaml
```
> Penjelasan: Ubah baris ports dan HOMEPAGE_ALLOWED_HOSTS seperti tabel di atas.
```
docker compose up -d
```
> Penjelasan: Membuat ulang container dengan port baru.
```
ss -tlnp | grep -E ":(80|3002)\b"
```
> Penjelasan: Port 3002 dipakai Homepage; port 80 harus bebas untuk Caddy.

