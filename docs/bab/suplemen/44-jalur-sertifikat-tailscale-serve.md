# Bab 44. Jalur Sertifikat per Aplikasi dan Tailscale Serve

PENEMPATAN - BARU - VM vault dibuat di bab ini  
Tempat: VM 205 vault (192.168.88.24), dibuat di Bab 44.3 dengan qm clone 9100 205 --name vault --full 1. Node  
tailnet lab-vault ada di dalamnya; tidak ada lagi node untuk docker-core.  
Alasan: Setiap VM yang memakai Tailscale Serve mendapat nama .ts.net sendiri di port 443; tidak perlu port 8443,  
8444, dan seterusnya.  

## 44.1 Masalahnya: aplikasi HP tidak sama dengan browser

Di Suplemen 4 Anda memasang sertifikat akar Caddy di HP, dan browser mempercayainya. Tetapi aplikasi di  
Android sering memakai daftar sertifikat sendiri atau sistem saja. Untuk Bitwarden, laporan pengguna di forum  
Vaultwarden dan Bitwarden menyebut aplikasi Android gagal dengan galat "Trust anchor for certification path not  
found" walau sertifikat sudah dipasang; solusi yang berhasil bagi mereka adalah sertifikat publik. Dokumentasi  
Bitwarden sendiri menyatakan sertifikat buatan sendiri tidak dipercaya klien secara bawaan dan hanya disarankan  
untuk uji. Ini bukti dari laporan pengguna, bukan jaminan untuk perangkat Anda [BELUM PASTI].  
Aplikasi Yang diketahui tentang CA lokal Keputusan buku ini  
Bitwarden (Android, iPhone,  
ekstensi)  
Laporan kegagalan di Android; klien memerlukan  
kepercayaan sertifikat  
Jalur 1: sertifikat tepercaya dari  
Tailscale Serve  
AFFiNE (desktop, Android,  
iPhone)  
Tidak ada informasi yang saya temukan [BELUM PASTI] Jalur 2 (CA lokal); pindah ke Jalur  
1 bila aplikasi menolak  
DAVx5 (kalender Android) Mendukung sertifikat buatan sendiri; catatan rilisnya  
menyebut penanganan sertifikat khusus; ada laporan  
pengguna berhasil dengan CA sendiri di Android 14  
Jalur 2  
Kalender iPhone bawaan Memakai kepercayaan sistem; sertifikat akar yang Anda  
aktifkan di Bab 37.4 berlaku  
Jalur 2  
Thunderbird (Windows) Penyimpanan sertifikat sendiri; akar harus diimpor (lihat  
47.6)  
Jalur 2  
Jalur 1 - Vaultwarden: sertifikat tepercaya dari Tailscale Serve  
Jalur 2 - AFFiNE dan Nextcloud: CA lokal Caddy (Suplemen 4)  
HP / Laptop  
Tailscale aktif  
Tailscale Serve  
https://...ts.net  
127.0.0.1:8081  
hanya di dalam VM  
Vaultwarden  
kata sandi  
HP / Laptop  
rumah atau Tailscale  
AdGuard  
\*.home.arpa  
Caddy :443  
sertifikat CA lokal  
Layanan  
AFFiNE, Nextcloud  
Gambar 44.1 - Dua jalur HTTPS: Serve untuk kata sandi, Caddy untuk layanan lain.  

## 44.2 Tailscale Serve: HTTPS tepercaya tanpa membeli domain

Tailscale Serve memberi perangkat Anda sebuah nama di MagicDNS (berakhiran .ts.net), mengurus sertifikat  
yang dipercaya semua perangkat, dan meneruskan permintaan ke port lokal. Menurut dokumentasi Tailscale,  
Serve hanya dapat diakses anggota tailnet Anda dan tidak membuka layanan ke internet. Jangan dikacaukan  
dengan Funnel, yang memang membuka ke internet. Di buku ini Funnel tidak pernah dipakai.  
Hal Penjelasan  
Syarat MagicDNS dan HTTPS Certificates aktif di halaman DNS konsol admin Tailscale  
Alamat https://NAMA-PERANGKAT.NAMA-TAILNET.ts.net. Satu VM = satu nama. Karena setiap layanan  
sensitif berada di VM sendiri (lab-vault, dan lab-affine bila perlu), semuanya memakai port 443 tanpa  
port tambahan  
Akses Hanya perangkat di tailnet Anda dengan Tailscale aktif, termasuk saat di rumah  
Privasi Nama tailnet Anda tercantum di catatan sertifikat publik (Certificate Transparency); isi vault tidak ikut.  
Seperti dicatat di Suplemen 4 Bab 35.2  
Alternatif Tailscale Services memberi satu nama per layanan di port 443, tetapi membutuhkan pengaturan  
tambahan di konsol admin [BELUM PASTI] dan tidak dipakai di sini  

## 44.3 Membuat VM vault dan memasang Tailscale di dalamnya

Router-vm (CT103) hanya meneruskan LAN. Serve harus berjalan di mesin yang menjalankan layanannya, jadi  
VM vault yang baru menjadi perangkat tailnet kedua dengan nama lab-vault. Perangkat ini tidak  
mengumumkan rute. Buat VM-nya dulu:  

**TERMINAL HOST PROXMOX** | Shell node Proxmox (host), sebagai root

```
qm clone 9100 205 --name vault --full 1
```
> Penjelasan: Membuat VM 205 bernama vault sebagai salinan penuh dari templat VM 9100 (Suplemen 7 Bab 49).
```
qm set 205 --memory 1024 --cores 1
```
> Penjelasan: RAM (MB) dan inti. Vaultwarden ringan; angka awal adalah perkiraan [BELUM PASTI].
```
qm start 205
```
> Penjelasan: Menyalakan. Lakukan penyiapan awal di Suplemen 7 Bab 49.4 (nama host vault, kunci SSH, alamat
192.168.88.24), lalu lanjut di bawah.  

**TERMINAL VM VAULT** | VM vault (192.168.88.24), sebagai root (setelah su -)

```
curl -fsSL https://tailscale.com/install.sh | sh
```
> Penjelasan: Memasang Tailscale resmi (cara yang sama seperti Suplemen 1 Bab 26.3).
```
tailscale up --hostname=lab-vault --accept-dns=false
```
> Penjelasan: Menghubungkan ke akun dan memberi nama lab-vault. --accept-dns=false menjaga DNS server
tidak berubah. Buka tautan login yang tampil di browser laptop.  
```
tailscale status
```
> Penjelasan: lab-vault harus muncul hidup. Catat nama panjangnya (NAMA.TAILNET.ts.net) dari konsol admin
pada halaman Machines.  
1. Di konsol admin buka Machines, klik ... pada lab-vault &gt; Disable key expiry agar server tidak terputus ketika  
kunci kedaluwarsa.  
2. Buka halaman DNS: pastikan MagicDNS aktif dan aktifkan HTTPS Certificates (ada peringatan bahwa nama  
tailnet menjadi publik di catatan sertifikat; baca lalu setujui).  
3. Kebijakan terbaru di Suplemen 1 Bab 26.6 sudah memuat izin TCP 443 untuk node milik admin. Jika Anda memakai kebijakan lama, tambahkan aturan pada kotak berikut ke daftar `grants`; pastikan sumbernya hanya grup admin.  

**Tambahan pada tailnet policy (di dalam "grants")** | Tambahan

```
 {
 "src": ["group:home-admins"],
 "dst": ["autogroup:self"],
 "ip": ["tcp:443"],
 },
```

Tanpa entri ini lab-vault tidak terjangkau dari HP. `autogroup:self` membatasi tujuan ke perangkat yang dimiliki akun sumber; gunakan anggota grup admin yang sama dengan kebijakan Bab 26.6. Sintaks `ip` bernilai `tcp:443` dan  
`autogroup:self` didukung pada grants untuk membatasi tujuan ke perangkat milik akun sumber. Jika memakai ACL lama, gunakan sumber grup admin: "acls": [{  
"action": "accept", "src": ["group:home-admins"], "dst": ["autogroup:self:443"] }]. Karena tiap VM punya  
nama .ts.net sendiri di port 443, satu entri ini cukup untuk semua node Serve milik Anda.  
KEAMANAN  
Simpan salinan JSON kebijakan lama sebelum mengubah (Suplemen 1 Bab 26.6). Kesalahan kebijakan bisa  
memutus akses Anda sendiri.  

## 44.4 Sisi klien

Perangkat Yang perlu dipastikan  
Windows Tailscale berjalan (ikon di dekat jam). Uji: buka https://lab-vault.NAMA-TAILNET.ts.net setelah Bab 45  
Android Tailscale terpasang, VPN aktif (Suplemen 1 Bab 26.4). Biarkan aktif juga di rumah agar nama .ts.net  
terjawab  
iPhone Tailscale terpasang dan aktif (Suplemen 1 Bab 26.5). Aktif juga di rumah  
CATATAN  
Konsekuensinya: vault kata sandi hanya dapat disinkronkan saat Tailscale aktif. Aplikasi Bitwarden menyimpan  
salinan vault di perangkat, sehingga mengisi kata sandi tetap bisa saat offline; yang tertunda hanya sinkronisasi.
