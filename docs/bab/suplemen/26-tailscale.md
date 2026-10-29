# Bab 26. Tailscale: Akses Aman dari Mana Saja

PENEMPATAN - BARU - LXC sendiri, bukan VM Docker  
Tempat: LXC CT103 ts-router (dibuat di Edisi 2 Bab 13.8), tidak di VM 201. Nama Tailscale tetap router-vm.  
Alasan: Tailscale adalah pintu masuk dari luar. Bila digabung dengan Docker, kebobolan salah satu membuka yang  
lain. LXC ringan, hidup terpisah, dan nanti pindah ke STB 2.  
Perubahan: Pada tabel 26.2, pilihan B (VM 192.168.88.20) tidak dipakai lagi; pakai C. Langkah di bawah sama; LXC  
perlu perangkat /dev/net/tun (Edisi 2 Bab 13.8). Tailscale tetap tidak dipasang di host Proxmox.  
Tailscale membuat jaringan privat antar perangkat Anda lewat internet tanpa membuka port di router. Edisi 2 Bab  
12.4 sudah memasangnya di STB. Bab ini melengkapinya: memilih perangkat yang tepat, langkah di sisi server,  
langkah di sisi laptop dan HP, kebijakan akses, DNS, dan cara membuktikan bahwa semuanya bekerja dari luar  
rumah.  

## 26.1 Cara kerja dalam satu gambar

Setiap perangkat yang diberi Tailscale masuk ke satu jaringan privat bernama tailnet dan mendapat alamat  
100.x.y.z. Satu perangkat di rumah dijadikan subnet router: ia meneruskan lalu lintas dari tailnet ke seluruh  
jaringan 192.168.88.0/24. Dengan begitu Proxmox, MikroTik, dan VM tidak perlu dipasangi Tailscale satu per  
satu.  
Rumah (jaringan 192.168.88.0/24)  
HP / Laptop  
di luar rumah, Tailscale aktif  
Server koordinasi Tailscale  
hanya bertukar kunci  
Subnet router  
STB 2 / VM Debian / LXC  
Perangkat di LAN  
MikroTik .1 Proxmox .10  
VM Debian .20 STB .253  
terowongan WireGuard  
(langsung, atau lewat relay)  
meneruskan  
Tidak ada port yang dibuka  
di router rumah.  
Gambar 26.1 - HP atau laptop di luar rumah menjangkau LAN lewat subnet router.  
Istilah Arti sederhana  
Tailnet Jaringan privat milik akun Anda; hanya perangkat Anda di dalamnya.  
Subnet router Perangkat di rumah yang menjadi pintu ke seluruh LAN (dipakai di buku ini).  
WireGuard Teknologi enkripsi di balik terowongan; isi lalu lintas tidak terbaca pihak lain.  
Relay (DERP) Jalur cadangan lewat server Tailscale bila koneksi langsung tidak bisa dibuat (umum pada NAT  
berlapis seperti WISP dan IndiHome). Lebih lambat tetapi tetap terenkripsi.  
MagicDNS Nama otomatis untuk perangkat Tailscale, misalnya router-vm.  
Tag Label pada perangkat server (tag:router) agar aturan akses bisa dibedakan dari perangkat  
pribadi.  
Grants / ACL Aturan siapa boleh menjangkau apa di dalam tailnet.  
Istilah Arti sederhana  
Split DNS Hanya nama domain tertentu yang dijawab oleh DNS rumah (AdGuard) saat Anda di luar.  

## 26.2 Memilih perangkat subnet router

Subnet router harus hidup terus agar akses luar bekerja. Pilihan Anda saat ini:  
Pilihan Kapan Kelebihan Kekurangan  
A. STB 2 (target) Setelah STB 2 tiba Selalu hidup, terpisah dari Proxmox,  
STB 1 khusus AdGuard (keputusan  
Anda)  
Perlu perangkat, Armbian, dan IP  
tetap  
B. VM Debian  
192.168.88.20  
(sementara)  
Sekarang, selama  
STB 2 belum ada  
Tanpa perangkat baru, langkah  
sama dengan A  
Hidup hanya selama Proxmox  
hidup  
C. LXC CT103 (Edisi 2  
Bab 13.8)  
Sebagai cadangan  
permanen  
Ringan; Tailscale beralih otomatis  
bila router lain mati  
Ikut mati bila Proxmox mati  
D. STB 1 (Edisi 2 Bab  
12.4)  
Tidak disarankan  
sekarang  
Sudah selalu hidup STB 1 seharusnya khusus AdGuard  
agar DNS rumah stabil  
CATATAN  
Jalur yang dipakai buku ini: pilihan B sekarang, lalu pindah ke A saat STB 2 tiba (Suplemen 6), dengan C sebagai  
cadangan. Dua perangkat boleh mengumumkan rute yang sama; Tailscale memakai yang hidup. Langkah di bawah  
berlaku sama untuk A, B, dan C.  
KEAMANAN  
Tailscale tidak dipasang di host Proxmox. Host virtualisasi sebaiknya tidak memiliki jalan masuk tambahan; akses  
ke Proxmox cukup lewat subnet router.  

## 26.3 Menyiapkan akun dan konsol admin

1. Buka login.tailscale.com dan masuk memakai akun Google, Microsoft, Apple, atau GitHub Anda. Tailscale  
tidak menyimpan password sendiri; keamanan tailnet mengikuti akun ini.  
2. Aktifkan verifikasi dua langkah di akun email itu. Siapa pun yang menguasai akun tersebut menguasai  
tailnet Anda.  
3. Kenali empat halaman konsol admin: Machines (daftar perangkat), Access controls (aturan akses), DNS,  
dan Settings (kunci dan kedaluwarsa perangkat).  
4. Buka Settings &gt; Keys dan lihat berapa lama kunci perangkat berlaku sebelum kedaluwarsa. Perangkat  
pribadi sebaiknya tetap kedaluwarsa berkala; perangkat server tidak (lihat 26.6).  
KEAMANAN  
Catat alamat email yang dipakai di password manager nanti (Suplemen 4). Jangan memakai akun bersama atau akun  
tanpa verifikasi dua langkah.  

## 26.4 Sisi server: memasang subnet router

Contoh memakai VM Debian (pilihan B). Untuk STB 2 (Armbian) dan LXC langkahnya sama; khusus LXC baca  
Edisi 2 Bab 13.8 untuk izin /dev/net/tun. Semua perintah sebagai root.  

**TERMINAL VM DEBIAN** | Sebagai root (setelah su -)

```
apt update && apt install -y curl
```
> Penjelasan: Memastikan curl terpasang.
```
curl -fsSL https://tailscale.com/install.sh | sh
```
> Penjelasan: Mengunduh dan memasang Tailscale resmi untuk Debian. Skrip menambahkan repositori sehingga
pembaruan ikut apt.  
```
echo 'net.ipv4.ip_forward = 1' > /etc/sysctl.d/99-tailscale.conf
```
> Penjelasan: Mengaktifkan penerusan paket IPv4. Tanpa ini perangkat tidak bisa menjadi pintu ke LAN.
```
echo 'net.ipv6.conf.all.forwarding = 1' >> /etc/sysctl.d/99-tailscale.conf
```
> Penjelasan: Mengaktifkan penerusan IPv6 (dua tanda &gt;&gt;, menambah baris).
```
sysctl -p /etc/sysctl.d/99-tailscale.conf
```
> Penjelasan: Menerapkan pengaturan tanpa reboot.
```
tailscale up --advertise-routes=192.168.88.0/24 --accept-dns=false --hostname=router-vm
```
> Penjelasan: Menghubungkan ke akun dan mengumumkan LAN. --accept-dns=false menjaga DNS lokal agar
tidak diubah Tailscale. --hostname memberi nama yang mudah dikenali.  
Perintah terakhir menampilkan sebuah alamat https://login.tailscale.com/a/.... Buka di browser laptop, masuk  
dengan akun yang sama, dan setujui perangkat. Lalu setujui rute di konsol:  
1. Buka Machines, temukan router-vm (tertulis "Subnet router" dengan tanda peringatan).  
2. Klik ... di barisnya &gt; Edit route settings, centang 192.168.88.0/24, klik Save.  
3. Klik ... &gt; Disable key expiry agar router tidak perlu login ulang berkala (otomatis terpenuhi setelah diberi tag  
di 26.6).  

**TERMINAL VM DEBIAN** | Sebagai root

```
tailscale status
```
> Penjelasan: Menampilkan perangkat di tailnet dan statusnya. router-vm harus tertulis hidup.
```
tailscale ip -4
```
> Penjelasan: Menampilkan alamat Tailscale perangkat ini (100.x.y.z).
TIPS  
Untuk mengubah pengaturan Tailscale di kemudian hari gunakan tailscale set (misalnya tailscale set  
--advertise-routes=192.168.88.0/24). Mengulang tailscale up tanpa seluruh opsi sebelumnya akan ditolak  
dengan pesan yang meminta semua opsi disebut ulang.  
KASUS NYATA  
Gejala: Rute disetujui tetapi 192.168.88.x tidak terjangkau dari luar. Penyebab umum: penerusan paket belum aktif,  
atau firewall VM menolak penerusan. Solusi: jalankan sysctl net.ipv4.ip_forward (harus 1). Bila UFW aktif,  
lihat ip -br a untuk nama kartu jaringan (misalnya ens18), lalu coba ufw route allow in on tailscale0 out  
on ens18 dan ufw allow in on tailscale0. Tailscale memasang aturan penerusan sendiri; aturan UFW ini  
hanya bila masih terblokir.  

## 26.5 Sisi klien: laptop Windows dan HP

Setiap perangkat yang dipakai mengakses server dari luar harus memasang aplikasi Tailscale dan masuk ke  
akun yang sama. Windows, Android, dan iPhone menerima rute subnet secara bawaan (Edisi 2 Bab 12.4); bila  
192.168.88.x tidak terjangkau, periksa opsi Use Tailscale subnets di pengaturan aplikasi.  
A. Laptop Windows  
1. Unduh pemasang Windows dari tailscale.com/download dan jalankan sampai selesai.  
2. Ikon Tailscale muncul di area notifikasi (dekat jam). Klik ikon &gt; Log in; browser terbuka, masuk dengan akun  
yang sama.  
3. Klik ikon lagi: status harus Connected, dan nama router-vm terlihat di daftar perangkat.  
4. Biarkan opsi Run Tailscale when I log in aktif agar otomatis berjalan.  

**POWERSHELL WINDOWS** | PowerShell (laptop)

```
tailscale status
```
> Penjelasan: Menampilkan perangkat tailnet. Jika perintah tidak dikenali, tutup lalu buka PowerShell baru.
```
tailscale ping router-vm
```
> Penjelasan: Menguji jalur ke router. Hasilnya menyebut "via DERP" (relay) atau alamat langsung (direct).
```
ping 192.168.88.10
```
> Penjelasan: Menguji Proxmox lewat rute subnet (bermakna saat laptop di luar rumah atau di jaringan lain).
CATATAN  
Saat laptop berada di rumah, di jaringan 192.168.88.0/24 yang sama, Tailscale tidak diperlukan. Bila ada akses yang  
aneh di rumah, pilih Disconnect dulu untuk membedakan sumber masalahnya.  
B. HP Android  
1. Pasang Tailscale dari Google Play Store.  
2. Buka aplikasi, ketuk Get Started, lalu masuk dengan akun yang sama.  
3. Saat muncul permintaan koneksi VPN dari sistem, ketuk OK. Ini wajib; Tailscale bekerja sebagai VPN lokal di  
HP.  
4. Geser sakelar ke aktif. Ikon kunci/VPN muncul di bilah status, dan router-vm tampil di daftar.  
5. Buka Pengaturan &gt; Jaringan &gt; VPN, ketuk ikon roda gigi di Tailscale, aktifkan VPN selalu aktif. Jangan  
aktifkan "Blokir koneksi tanpa VPN" agar internet tetap hidup bila Tailscale mati. (Nama menu berbeda antar  
merek HP.)  
6. Buka Pengaturan &gt; Aplikasi &gt; Tailscale &gt; Baterai dan pilih Tidak dibatasi agar tidak dimatikan sistem  
untuk menghemat daya.  
C. iPhone  
1. Pasang Tailscale dari App Store.  
2. Buka aplikasi dan masuk dengan akun yang sama.  
3. Saat iOS meminta izin menambahkan konfigurasi VPN, ketuk Allow dan konfirmasi dengan Face ID atau  
kode.  
4. Aktifkan sakelar. Indikator VPN muncul di bilah status, dan router-vm tampil di daftar.  
PERINGATAN  
Android dan iPhone hanya bisa menjalankan satu VPN pada satu waktu. Bila Anda memakai VPN lain, matikan dulu  
sebelum menyalakan Tailscale.  
KEAMANAN  
Kunci layar HP dan laptop wajib aktif. Perangkat yang terhubung ke Tailscale yang hilang harus segera dihapus dari  
konsol (Bab 26.9).  

## 26.6 Kebijakan akses dan tag

Secara bawaan semua perangkat di tailnet boleh menghubungi semua perangkat lain. Kita batasi supaya  
perangkat server (router) tidak bisa memulai koneksi ke HP dan laptop Anda. Jika router suatu hari diretas,  
penyerang tidak otomatis mendapat jalan ke perangkat pribadi Anda.  
CATATAN  
Pada tailnet satu pengguna, manfaat utamanya adalah mengurung perangkat ber-tag. Aturan ini juga menjadi dasar  
bila kelak ada anggota keluarga yang diberi akses sebagian.  
1. Buka Access controls. Salin seluruh isi editor ke berkas teks di laptop sebagai cadangan.  
2. Tambahkan bagian tagOwners dan ganti bagian grants bawaan dengan isi di kotak bawah. Biarkan bagian  
lain apa adanya. Ganti alamat email dengan milik Anda.  
3. Klik Save. Editor menolak penyimpanan bila ada kesalahan sintaks.  

**Access controls (potongan)** | tailnet policy file (HuJSON)

```
 // Siapa yang boleh memberi tag router pada perangkat
 "tagOwners": {
 "tag:router": ["EMAIL-ANDA@gmail.com"],
 },
 // Anggota tailnet boleh menjangkau perangkat router dan LAN rumah.
 // Perangkat ber-tag router tidak diberi hak memulai koneksi ke HP atau laptop.
 "grants": [
 {
 "src": ["autogroup:member"],
 "dst": ["tag:router", "192.168.88.0/24"],
 "ip": ["*"],
 },
 ],
```

1. Buka Machines, klik ... pada router-vm &gt; Edit ACL tags, pilih tag:router, Save.  
2. Periksa ulang rute: Edit route settings harus masih tercentang. Perangkat ber-tag otomatis tidak  
kedaluwarsa kuncinya.  
3. Uji dari HP (data seluler): buka https://192.168.88.10:8006. Harus tetap berhasil.  
TIPS  
Jika editor menolak dst berupa rentang IP pada grants, pakai sintaks lama yang juga didukung: "acls": [{ "action":  
"accept", "src": ["autogroup:member"], "dst": ["tag:router:\*", "192.168.88.0/24:\*"] }].  
KEAMANAN  
Editor kebijakan dibuka lewat situs web Tailscale, bukan lewat tailnet, sehingga kesalahan aturan tidak mengunci jalur  
Anda untuk memperbaikinya. Tetap simpan salinan JSON lama.  

## 26.7 DNS: nama dan pemblokir iklan dari luar rumah

Ada tiga tingkat, dari paling aman ke paling berpengaruh. Mulailah dari A dan B; C opsional.  
A. MagicDNS  
1. Buka halaman DNS di konsol admin dan pastikan MagicDNS aktif.  
2. Uji dari laptop: tailscale ping router-vm memakai nama, bukan alamat.  
B. Split DNS: nama lokal dijawab AdGuard  
Dengan ini, nama berakhiran lab.local dijawab oleh AdGuard di rumah saat Anda di luar. Fondasi ini dipakai di  
Suplemen 3 untuk nama layanan.  
1. Di AdGuard Home (http://192.168.88.253) buka Filters &gt; DNS rewrites &gt; Add DNS rewrite: Domain  
pve.lab.local, IP 192.168.88.10.  
2. Di konsol Tailscale buka DNS &gt; Nameservers &gt; Add nameserver &gt; Custom.  
3. Isi 192.168.88.253, aktifkan Restrict to domain, isi domain lab.local, Save.  
4. Dari HP (data seluler, Tailscale aktif) buka https://pve.lab.local:8006. Harus terbuka.  
CATATAN  
Pertanyaan DNS dari HP tiba di AdGuard dengan alamat router Tailscale, bukan alamat HP. Statistik per perangkat di  
AdGuard tidak akan menampilkan HP saat di luar rumah.  
C. Opsional: pemblokir iklan di HP saat di luar rumah  
Di DNS &gt; Nameservers tambahkan 192.168.88.253 sebagai nameserver global dan aktifkan Override DNS  
servers (di sebagian tampilan disebut Override local DNS). Seluruh pertanyaan DNS perangkat Anda lewat  
AdGuard rumah.  
PERINGATAN  
Risiko: bila rumah mati listrik atau IndiHome putus, AdGuard tidak terjangkau dan HP Anda terlihat "tidak ada internet"  
selama Tailscale aktif. Menambah nameserver kedua (misalnya 1.1.1.1) sebagai cadangan mengurangi risikonya,  
tetapi urutan pemilihan nameserver tidak dijamin sehingga iklan bisa tidak terblokir sesekali.  
Saran: mulai dari A dan B saja. Aktifkan C hanya bila Anda siap mematikan Tailscale ketika internet terasa mati.  

## 26.8 Uji dari luar jaringan

Membuktikan akses dari luar tidak bisa dilakukan dari dalam rumah. Pakai data seluler HP, bukan WiFi rumah.  
No Perangkat dan jaringan Uji Hasil yang diharapkan  
1 HP, data seluler, Tailscale aktif Buka https://192.168.88.10:8006 Peringatan sertifikat (normal, sertifikat  
buatan sendiri), lalu login dan kode 2FA  
2 HP, data seluler Buka http://192.168.88.1 Halaman WebFig MikroTik  
3 HP, data seluler Buka http://192.168.88.253 Halaman AdGuard Home  
4 HP, data seluler Buka https://pve.lab.local:8006  
(setelah 26.7B)  
Halaman Proxmox  
5 HP, Tailscale mati Buka alamat nomor 1 Gagal. Ini membuktikan tidak ada port  
yang terbuka ke internet.  
6 Laptop di jaringan lain (hotspot  
HP kedua)  
ssh root@192.168.88.10 Masuk dengan kunci  
7 Laptop atau HP tailscale ping router-vm Hasil direct atau via DERP; keduanya  
berfungsi  

## 26.9 Operasional harian

Perintah atau tindakan Fungsi  
tailscale status Daftar perangkat dan keadaannya  
tailscale ping &lt;nama&gt; Menguji jalur; menunjukkan direct atau via DERP  
tailscale netcheck Memeriksa kualitas koneksi dan jarak ke server relay  
tailscale version Versi terpasang  
apt update && apt install -y --only-upgrade tailscale Memperbarui Tailscale di server Debian  
Machines &gt; ... &gt; Delete Menghapus perangkat yang hilang atau tidak dipakai lagi  
Machines &gt; ... &gt; Disable key expiry Hanya untuk perangkat server, bukan HP atau laptop  
KEAMANAN  
Bila HP atau laptop hilang: segera buka Machines dan Delete perangkat itu, lalu ganti password akun email dan  
periksa verifikasi dua langkahnya. Tinjau daftar Machines sebulan sekali dan hapus yang tidak dikenal.  

## 26.10 Checklist pengerasan Tailscale

Item Status yang diharapkan  
Verifikasi dua langkah pada akun email Aktif  
Subnet route hanya 192.168.88.0/24 Tidak ada rute lain yang disetujui  
Exit node Tidak dipakai  
Perangkat router memakai tag:router Ya, tanpa kedaluwarsa kunci  
Kebijakan akses Bukan lagi "semua ke semua"  
Tailscale di Proxmox host Tidak dipasang  
Port forwarding di MikroTik Tidak ada  
Daftar Machines Semua perangkat dikenali  

## 26.11 Masalah dan solusi

Gejala Penyebab Solusi  
192.168.88.x tidak terjangkau dari  
HP  
Rute belum disetujui; penerusan  
paket mati; klien menonaktifkan  
subnet  
Setujui rute di konsol, sysctl net.ipv4.ip_forward  
harus 1, cek Use Tailscale subnets di klien  
Koneksi lambat dari luar Memakai relay (DERP) karena NAT  
berlapis, atau upload IndiHome  
terbatas  
tailscale ping untuk melihat direct atau DERP;  
tunggu beberapa menit untuk koneksi langsung;  
kecepatan dibatasi upload rumah  
Internet HP mati setelah DNS  
global  
AdGuard tidak terjangkau Matikan Override DNS servers atau tambah  
nameserver cadangan (26.7C)  
Pesan Key expired Kunci perangkat habis masa berlaku Login ulang; untuk server pakai tag:router agar  
tidak kedaluwarsa  
tailscale up ditolak karena opsi Opsi sebelumnya tidak disebut ulang Pakai tailscale set, atau sebutkan semua opsi  
Tailscale gagal di LXC /dev/net/tun tidak tersedia Ikuti Edisi 2 Bab 13.8  
Web Proxmox ditolak dari luar Sumber lalu lintas bukan LAN, atau  
firewall Proxmox menolak  
Cek pve-firewall localnet dan aturan Source  
192.168.88.0/24 (Bab 25.5)  
Tailscale tidak bisa menyala di HP VPN lain aktif Matikan VPN lain, hanya satu VPN pada satu  
waktu  
Layanan terbuka dari luar tanpa  
Tailscale  
Tidak ada port forwarding, jadi  
seharusnya tidak mungkin  
Periksa MikroTik: /ip firewall nat print dan  
pastikan tidak ada dst-nat  

## 26.12 Pindah ke STB 2 dan cara menghapus

Rencana lengkap pemindahan ada di Suplemen 6. Ringkasnya, saat STB 2 tiba: pasang Tailscale dengan  
langkah 26.4 (hostname router-stb2), setujui rute, beri tag:router, uji, lalu kosongkan rute di VM Debian.  

**TERMINAL VM DEBIAN** | Sebagai root

```
tailscale set --advertise-routes=
```
> Penjelasan: Mengosongkan rute yang diumumkan VM setelah STB 2 aktif.
Untuk menghapus Tailscale sepenuhnya dari sebuah server:  

**TERMINAL VM DEBIAN** | Sebagai root

```
tailscale down
```
> Penjelasan: Memutus dari tailnet.
```
tailscale logout
```
> Penjelasan: Melepas perangkat dari akun.
```
apt purge -y tailscale
```
> Penjelasan: Menghapus paket.
```
rm /etc/sysctl.d/99-tailscale.conf
```
> Penjelasan: Menghapus pengaturan penerusan paket.
Lalu hapus perangkatnya dari halaman Machines bila masih tampil.
