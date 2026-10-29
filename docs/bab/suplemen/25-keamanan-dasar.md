# Bab 25. Keamanan Dasar Server

PENEMPATAN - SEMUA GUEST  
Tempat: Dikerjakan di setiap VM/LXC dan di host Proxmox, sesuai bagian bab. VM baru mewarisinya dari templat  
VM 9100 (Suplemen 7 Bab 49).  
Perhatian: UFW di dalam VM tidak mengatur port yang dipublikasikan oleh Docker. Pemisah antar-VM yang bisa  
diandalkan adalah firewall Proxmox (Suplemen 7 Bab 51).  
Bab ini membuat server rumah lebih sulit dimasuki dan lebih mudah dipulihkan. Tujuannya bukan keamanan  
sempurna, melainkan beberapa lapisan sederhana yang saling menutup kelemahan. Semua langkah ditulis untuk  
pemula, dengan penjelasan setiap perintah dan cara kembali bila terjadi kesalahan.  

## 25.1 Prinsip dan peta keamanan

Ada lima prinsip yang dipakai di seluruh buku: (1) kecilkan pintu masuk, hanya buka yang perlu; (2) akses dari  
luar hanya lewat Tailscale; (3) login memakai kunci dan 2FA, bukan password saja; (4) perbarui rutin; (5)  
cadangkan dan uji pemulihan.  
1 Internet  
tidak dipercaya; tidak ada port yang dibuka dari rumah  
2 WISP TL-WR840N + IndiHome  
NAT berlapis, tanpa port forwarding  
3 MikroTik RB750GL  
firewall input dan forward, layanan admin dibatasi ke LAN  
4 Tailscale  
satu-satunya jalan masuk dari luar, dengan kebijakan akses  
5 Proxmox dan VM  
firewall, akun admin terpisah, 2FA, SSH hanya kunci  
6 Aplikasi dan data  
update otomatis, backup 3-2-1, uji pemulihan  
Gambar 25.1 - Enam lapisan keamanan. Penyerang harus menembus lapisan dari luar ke dalam.  
Ancaman yang realistis di rumah  
Ancaman Contoh Pertahanan di buku ini  
Orang di internet mencoba  
masuk  
Memindai port di alamat IP publik Tidak ada port yang dibuka. Akses luar hanya lewat  
Tailscale.  
Perangkat di LAN yang tidak  
tepercaya  
HP tamu, perangkat IoT, laptop  
terinfeksi  
Firewall Proxmox, UFW di VM, akun admin dengan  
2FA. Pemisahan jaringan (VLAN) dibahas sebagai opsi  
nanti.  
Password ditebak atau bocor Login root SSH dengan password Kunci SSH, 2FA, password manager (Suplemen 4).  
Celah pada perangkat lunak  
lama  
Paket Debian atau Proxmox belum  
diperbarui  
Update rutin dan update keamanan otomatis.  
Kesalahan sendiri Salah ubah konfigurasi, salah  
hapus  
Backup, snapshot, Safe Mode MikroTik, jalur darurat.  
Perangkat hilang atau dicuri HP atau laptop berisi akses  
Tailscale  
Hapus perangkat dari konsol Tailscale, 2FA di akun  
email.  
Yang sudah ada di Edisi 2 dan yang ditambahkan  
Area Sudah ada (Edisi 2) Ditambahkan di Suplemen 1  
MikroTik Layanan tak terpakai dimatikan, WinBox dan SSH  
dibatasi LAN, MAC server dimatikan (Bab 3.8)  
Aturan firewall input dan forward, WebFig dibatasi  
LAN, mematikan layanan tambahan, Safe Mode,  
backup  
Proxmox Repository no-subscription, update (Bab 9) Akun admin terpisah, 2FA TOTP, SSH hanya kunci,  
firewall datacenter  
VM Debian Login root lewat konsol, sudo tidak dipasang (Bab  
1.7, 11)  
Login SSH pengguna biasa + kunci, root SSH  
dimatikan, UFW, update keamanan otomatis  
STB AdGuard Home, backup AdGuardHome.yaml (Bab  
12)  
SSH kunci, kebijakan update hati-hati  
Akses luar Tailscale subnet router (Bab 12.4, 13.8) Bab 26: kebijakan akses, DNS, klien laptop dan HP  

## 25.2 Persiapan: backup dan jalur darurat

Sebelum mengubah apa pun, simpan keadaan yang masih bekerja. Dengan begitu kesalahan apa pun bisa  
dibatalkan. Langkah ini hanya sekali dan memakan waktu beberapa menit.  

**TERMINAL MIKROTIK** | WinBox &gt; New Terminal

```
/export file=sebelum-suplemen1
```
> Penjelasan: Menyimpan seluruh konfigurasi sebagai berkas teks yang dapat dibaca.
```
/system backup save name=sebelum-suplemen1
```
> Penjelasan: Membuat backup biner yang bisa dipulihkan ke router yang sama.
Lalu unduh kedua berkas ke laptop: di WinBox buka menu Files, seret sebelum-suplemen1.rsc dan  
sebelum-suplemen1.backup ke folder di laptop.  

**TERMINAL PROXMOX** | Shell Proxmox (root)

```
mkdir -p /root/cadangan-sebelum-suplemen1
```
> Penjelasan: Membuat folder untuk salinan konfigurasi.
```
cp -a /etc/ssh /root/cadangan-sebelum-suplemen1/ssh
```
> Penjelasan: Menyalin konfigurasi SSH lama agar bisa dikembalikan.
```
tar czf /root/cadangan-sebelum-suplemen1/etc-pve.tgz /etc/pve
```
> Penjelasan: Mengarsipkan konfigurasi Proxmox (pengguna, firewall, definisi VM). Berkas ini berisi data sensitif,
simpan di tempat aman.  
```
ls -lh /root/cadangan-sebelum-suplemen1
```
> Penjelasan: Memastikan arsip terbentuk dan ukurannya tidak nol.

**POWERSHELL WINDOWS** | PowerShell (laptop)

```
scp -r root@192.168.88.10:/root/cadangan-sebelum-suplemen1 .
```
> Penjelasan: Menyalin folder cadangan dari Proxmox ke folder aktif di laptop. Salinan di luar server adalah intinya.
Snapshot VM Debian  
1. Di web Proxmox, klik VM Debian di panel kiri, lalu buka tab Snapshots.  
2. Klik Take Snapshot, beri nama sebelum-suplemen1, jangan centang Include RAM, klik Take Snapshot.  
3. Tunggu status Task OK. Bila tombol Take Snapshot abu-abu, penyimpanan VM tidak mendukung snapshot;  
gunakan Backup &gt; Backup now sebagai gantinya (Edisi 2 Bab 23).  
Jalur darurat (catat sebelum mulai)  
Perangkat Bila terkunci, masuk lewat Syarat  
Proxmox (mesin asli) Monitor dan keyboard langsung Login root dan password lokal  
VM Debian Tab Console di web Proxmox Login root dan password lokal  
MikroTik WinBox lewat kabel ke ether2 (IP 192.168.88.1);  
tombol reset sebagai pilihan terakhir  
Backup dari langkah di atas  
STB (Armbian) Monitor HDMI dan keyboard, atau PuTTY dari LAN Login root  
TIPS  
Konsol fisik Proxmox dan konsol web VM tidak memakai SSH, jadi aturan SSH yang dikeraskan di bab ini tidak mengunci jalur  
darurat tersebut.  

## 25.3 Akun admin Proxmox terpisah dan 2FA

Secara bawaan satu-satunya akun Proxmox adalah root@pam, akun yang sama dengan root di Linux. Siapa pun  
yang menebak password-nya menguasai seluruh server. Kita buat akun admin terpisah, lalu pasang 2FA (kode 6  
digit dari aplikasi autentikator) untuk kedua akun.  
Membuat akun admin  
1. Buka Datacenter &gt; Permissions &gt; Users lalu klik Add.  
2. Isi User name (contoh: adminlab), Realm pilih Proxmox VE authentication server, isi password yang kuat  
dan panjang, pastikan Enabled tercentang, klik Add.  
3. Buka Datacenter &gt; Permissions lalu klik Add &gt; User Permission.  
4. Isi Path = /, User = adminlab@pve, Role = Administrator, centang Propagate, klik Add.  
5. Klik nama pengguna di kanan atas &gt; Logout. Masuk lagi dengan adminlab, Realm Proxmox VE  
authentication server.  
CATATAN  
Akun ini hanya ada di Proxmox, bukan akun Linux. Karena itu ia tidak bisa dipakai untuk SSH, dan itu memang  
disengaja: SSH tetap lewat root dengan kunci (Bab 25.4).  
Memasang 2FA (TOTP)  
1. Pasang aplikasi autentikator di HP (misalnya Google Authenticator, Microsoft Authenticator, atau Aegis di  
Android).  
2. Buka Datacenter &gt; Permissions &gt; Two Factor lalu klik Add &gt; TOTP. (Pada beberapa versi, menu yang  
sama juga ada di nama pengguna kanan atas &gt; TFA.)  
3. Pilih User adminlab@pve, isi Description (contoh: HP utama), pindai kode QR dengan aplikasi autentikator.  
4. Ketik kode 6 digit yang muncul di aplikasi pada kolom Verify Code, isi Current Password (password akun  
itu), klik Add.  
5. Klik Add &gt; Recovery Keys, simpan seluruh kode yang tampil di password manager atau cetak dan simpan  
fisik. Kode ini satu-satunya jalan bila HP hilang.  
6. Ulangi langkah 2 sampai 5 untuk root@pam, supaya akun darurat juga terlindungi di web.  
7. Logout dan login lagi: sekarang setelah password diminta kode 6 digit.  
PERINGATAN  
2FA hanya melindungi login web. Login SSH dan konsol tidak memakai TOTP. Simpan Recovery Keys sebelum  
menutup halaman; tanpa itu dan tanpa HP, Anda harus memakai jalur darurat (Bab 25.11).  
KASUS NYATA  
Gejala: Kode TOTP selalu ditolak padahal benar. Penyebab: jam server menyimpang, misalnya NTP belum sinkron setelah mesin lama mati.  
Solusi: jalankan timedatectl status dan pastikan "System clock  
synchronized: yes"; bila tidak, tunggu sinkronisasi atau mulai ulang layanan waktu, lalu coba lagi.  

## 25.4 SSH Proxmox hanya dengan kunci

Kunci SSH berpasangan: kunci privat tinggal di laptop dan tidak pernah dikirim, kunci publik dipasang di server.  
Penyerang yang hanya tahu password tidak bisa masuk. Pasangan kunci sudah dibuat di Edisi 2 Bab 15.4; bila  
belum, langkah 1 di bawah membuatnya.  

**POWERSHELL WINDOWS** | PowerShell (laptop)

```
ssh-keygen -t ed25519 -C "laptop-rumah"
```
> Penjelasan: Membuat pasangan kunci. Jika sudah ada, jawab n saat ditanya menimpa berkas. Disarankan
mengisi passphrase agar kunci tercuri pun tidak langsung bisa dipakai.  
```
type $env:USERPROFILE\.ssh\id_ed25519.pub
```
> Penjelasan: Menampilkan kunci publik (satu baris yang diawali ssh-ed25519). Salin seluruh baris itu.

**TERMINAL PROXMOX** | SSH atau Shell Proxmox (root)

```
mkdir -p /root/.ssh
```
> Penjelasan: Memastikan folder kunci ada.
```
echo 'TEMPEL-KUNCI-PUBLIK-DI-SINI' >> /root/.ssh/authorized_keys
```
> Penjelasan: Menambahkan kunci publik. Ganti teks dalam tanda petik dengan baris yang disalin tadi. Perhatikan
tanda &gt;&gt; (dua), jangan satu, agar kunci lain tidak terhapus.  
```
chmod 600 /root/.ssh/authorized_keys
```
> Penjelasan: Membatasi izin berkas: hanya pemilik yang boleh membaca.
TIPS  
Di Proxmox, /root/.ssh/authorized_keys tertaut ke /etc/pve/priv/authorized_keys, jadi perintah di atas  
tetap berlaku. Pengguna PuTTY: buka PuTTYgen, Load kunci privat id_ed25519, Save private key (.ppk), lalu pakai di  
Connection &gt; SSH &gt; Auth &gt; Credentials.  
Uji login memakai kunci sebelum mematikan password  

**POWERSHELL WINDOWS** | Jendela PowerShell BARU

```
ssh root@192.168.88.10
```
> Penjelasan: Harus langsung masuk tanpa meminta password (atau hanya meminta passphrase kunci). Jika masih
meminta password server, kunci belum terpasang benar; jangan lanjut.  
Setelah berhasil, buat berkas pengaturan tambahan. Nama berkas berawalan 00- sengaja dipilih karena  
OpenSSH memakai nilai pertama yang dibacanya.  

**TERMINAL PROXMOX** | Shell Proxmox (root)

```
grep -n Include /etc/ssh/sshd_config
```
> Penjelasan: Memeriksa bahwa sshd_config memuat folder sshd_config.d (baris "Include
/etc/ssh/sshd_config.d/\*.conf").  
```
nano /etc/ssh/sshd_config.d/00-hardening.conf
```
> Penjelasan: Membuat berkas baru. Isi seperti kotak di bawah.

**/etc/ssh/sshd_config.d/00-hardening.conf** | Isi berkas

```
PasswordAuthentication no
KbdInteractiveAuthentication no
PermitRootLogin prohibit-password
MaxAuthTries 3
LoginGraceTime 30
```

Simpan di nano dengan Ctrl+O, Enter, lalu keluar dengan Ctrl+X. Arti barisnya: password dimatikan, login  
interaktif lain dimatikan, root hanya boleh dengan kunci, maksimal 3 percobaan, dan waktu login 30 detik.  

**TERMINAL PROXMOX** | Shell Proxmox (root)

```
sshd -t
```
> Penjelasan: Memeriksa sintaks. Tidak ada keluaran berarti benar. Jika ada pesan error, perbaiki berkas dulu.
```
systemctl reload ssh
```
> Penjelasan: Menerapkan pengaturan tanpa memutus sesi yang sedang berjalan.
```
sshd -T | grep -Ei "passwordauthentication|permitrootlogin|kbdinteractive"
```
> Penjelasan: Menampilkan nilai yang benar-benar berlaku. Harus: passwordauthentication no,
kbdinteractiveauthentication no, permitrootlogin without-password.  

**POWERSHELL WINDOWS** | PowerShell (laptop)

```
ssh -o PubkeyAuthentication=no root@192.168.88.10
```
> Penjelasan: Uji penolakan: memaksa login tanpa kunci. Hasil yang benar: "Permission denied (publickey)".
BAHAYA  
Jangan tutup sesi SSH lama sebelum uji login kunci di jendela baru berhasil. Bila terkunci, masuk lewat konsol (Bab  
25.2) dan hapus berkas dengan rm /etc/ssh/sshd_config.d/00-hardening.conf lalu systemctl reload  
ssh.  

## 25.5 Firewall Proxmox

Firewall Proxmox mati secara bawaan. Setelah dinyalakan, semua lalu lintas ke host diblokir kecuali web (8006)  
dan SSH (22) dari jaringan lokal. Kita nyalakan lalu menuliskan aturan yang eksplisit agar maksudnya jelas dan  
tidak berubah bila jaringan berubah.  
PERINGATAN  
Buka satu sesi SSH ke Proxmox sebelum menyalakan firewall (disarankan oleh dokumentasi Proxmox). Bila terputus,  
sesi itu masih hidup dan firewall dapat dimatikan dari sana.  

**TERMINAL PROXMOX** | Shell Proxmox (root)

```
pve-firewall localnet
```
> Penjelasan: Menampilkan jaringan yang dianggap "lokal". Harus memuat 192.168.88.0/24. Jika tampil jaringan
lain (misalnya 192.168.100.0/24 dari kasus Bab 9.11), sesuaikan aturan di bawah.  
```
pve-firewall status
```
> Penjelasan: Memeriksa status layanan firewall sebelum diubah (mati atau stopped).
Menyalakan dan menulis aturan  
1. Buka Datacenter &gt; Firewall &gt; Rules lalu klik Add. Isi: Direction in, Action ACCEPT, Protocol tcp, Source  
192.168.88.0/24, Dest. port 8006, Comment "web Proxmox dari LAN", centang Enable, klik Add.  
2. Ulangi dengan Dest. port 22, Comment "SSH dari LAN".  
3. Ulangi dengan Protocol icmp (tanpa port) agar ping tetap bekerja, Comment "ping dari LAN".  
4. Buka Datacenter &gt; Firewall &gt; Options, pilih baris Firewall, klik Edit, centang, OK. Pastikan Input Policy  
bernilai DROP dan Output Policy ACCEPT.  
5. Buka pve (node) &gt; Firewall &gt; Options dan pastikan Firewall bernilai yes.  
6. Dari laptop, buka ulang https://192.168.88.10:8006 dan SSH baru. Keduanya harus tetap berfungsi.  

**TERMINAL PROXMOX** | Shell Proxmox (root)

```
pve-firewall status
```
> Penjelasan: Harus menampilkan status enabled/running.
```
pve-firewall compile | head -40
```
> Penjelasan: Opsional: melihat aturan yang dihasilkan, untuk memastikan aturan 8006 dan 22 ada.
KEAMANAN  
Akses dari luar rumah lewat Tailscale tetap lolos aturan ini karena router Tailscale mengubah alamat sumber menjadi  
alamat LAN-nya (192.168.88.x). Bila suatu saat Tailscale dipasang langsung di Proxmox, tambahkan aturan dengan  
Source 100.64.0.0/10.  
BAHAYA  
Terkunci dari firewall: dari konsol (Bab 25.2) jalankan pve-firewall stop. Perintah ini menghapus semua aturan  
Proxmox dan membuat host tak terlindungi sampai pve-firewall start dijalankan. Alternatif: ubah enable: 1  
menjadi enable: 0 di /etc/pve/firewall/cluster.fw, bagian [OPTIONS].  
CATATAN  
Firewall tingkat VM dan container sengaja belum dinyalakan. Perlindungan VM Debian dikerjakan di dalam VM  
dengan UFW (Bab 25.6) agar mudah dipahami satu per satu.  

## 25.6 Mengeraskan VM Debian

VM Debian (192.168.88.20) menjalankan Docker, Portainer, Git, dan Nextcloud, jadi ia target paling menarik.  
Empat langkah: login SSH dengan kunci sebagai pengguna biasa, root SSH dimatikan, firewall UFW, dan update  
keamanan otomatis. Perintah tetap tanpa sudo: setelah login, jalankan su -.  
A. Login SSH pengguna biasa dengan kunci  

**POWERSHELL WINDOWS** | PowerShell (laptop)

```
ssh <USER>@192.168.88.20
```
> Penjelasan: Masuk sebagai pengguna biasa yang dibuat saat instalasi Debian (Bab 11.3). Ganti &lt;USER&gt; dengan
nama pengguna Anda. Saat ini masih memakai password.  
```
type $env:USERPROFILE\.ssh\id_ed25519.pub
```
> Penjelasan: Tampilkan kunci publik untuk disalin (di jendela PowerShell lain).

**TERMINAL VM DEBIAN** | SSH sebagai pengguna biasa

```
mkdir -p ~/.ssh
```
> Penjelasan: Membuat folder kunci milik pengguna ini.
```
chmod 700 ~/.ssh
```
> Penjelasan: Hanya pemilik yang boleh masuk folder.
```
echo 'TEMPEL-KUNCI-PUBLIK-DI-SINI' >> ~/.ssh/authorized_keys
```
> Penjelasan: Menambahkan kunci publik (ganti teksnya).
```
chmod 600 ~/.ssh/authorized_keys
```
> Penjelasan: Membatasi izin berkas kunci.

**POWERSHELL WINDOWS** | Jendela PowerShell BARU

```
ssh <USER>@192.168.88.20
```
> Penjelasan: Harus masuk tanpa password VM. Jika berhasil, lanjut ke bagian B.
B. Mematikan login root dan password lewat SSH  

**TERMINAL VM DEBIAN** | SSH sebagai pengguna biasa

```
su -
```
> Penjelasan: Menjadi root (masukkan password root). Prompt berubah menjadi #. Mulai di sini tanpa sudo.
```
nano /etc/ssh/sshd_config.d/00-hardening.conf
```
> Penjelasan: Membuat berkas pengaturan. Isi seperti kotak di bawah.

**/etc/ssh/sshd_config.d/00-hardening.conf** | Isi berkas

```
PasswordAuthentication no
KbdInteractiveAuthentication no
PermitRootLogin no
MaxAuthTries 3
LoginGraceTime 30
```

**TERMINAL VM DEBIAN** | Sebagai root (setelah su -)

```
sshd -t
```
> Penjelasan: Memeriksa sintaks; tanpa keluaran berarti benar.
```
systemctl reload ssh
```
> Penjelasan: Menerapkan pengaturan.
```
sshd -T | grep -Ei "passwordauthentication|permitrootlogin"
```
> Penjelasan: Harus menampilkan passwordauthentication no dan permitrootlogin no.

**POWERSHELL WINDOWS** | PowerShell (laptop)

```
ssh root@192.168.88.20
```
> Penjelasan: Harus ditolak (Permission denied). Itu hasil yang diharapkan.
```
ssh <USER>@192.168.88.20
```
> Penjelasan: Pengguna biasa dengan kunci tetap harus bisa masuk.
C. Firewall UFW  
UFW adalah antarmuka sederhana untuk firewall Linux. Aturan dasarnya: tolak semua yang masuk, terima yang  
keluar, lalu izinkan SSH hanya dari LAN.  

**TERMINAL VM DEBIAN** | Sebagai root

```
apt update && apt install -y ufw
```
> Penjelasan: Memasang UFW.
```
ufw default deny incoming
```
> Penjelasan: Semua koneksi masuk ditolak kecuali yang diizinkan.
```
ufw default allow outgoing
```
> Penjelasan: Koneksi keluar (update, Docker pull) tetap diizinkan.
```
ufw allow from 192.168.88.0/24 to any port 22 proto tcp
```
> Penjelasan: Mengizinkan SSH hanya dari LAN. Wajib sebelum mengaktifkan UFW.
```
ufw enable
```
> Penjelasan: Mengaktifkan UFW. Jawab y bila diminta. Sesi SSH yang berjalan tetap hidup karena aturan SSH
sudah ada.  
```
ufw status verbose
```
> Penjelasan: Memeriksa: Status active, Default deny (incoming), allow (outgoing), dan aturan SSH.
PERINGATAN - Perlu dipahami  
Docker melewati UFW. Port yang dipublikasikan Docker (misalnya -p 9443:9443 untuk Portainer) dipasang Docker  
langsung di firewall sehingga tetap terbuka dari seluruh LAN walau UFW menolaknya. UFW di sini melindungi layanan  
milik VM sendiri (SSH), bukan port container.  
Karena itu rumah Anda mengandalkan tiga hal: tidak ada port forwarding di MikroTik, akses luar hanya lewat Tailscale,  
dan nanti reverse proxy (Suplemen 3) yang menjadi pintu tunggal. Untuk melihat apa yang terbuka sekarang, jalankan  
ss -tlnp di VM dan catat setiap port selain 22. Hasilnya dipakai di audit Bab 38.  
D. Update keamanan otomatis  

**TERMINAL VM DEBIAN** | Sebagai root

```
apt install -y unattended-upgrades apt-listchanges
```
> Penjelasan: Memasang paket yang memasang update keamanan Debian secara otomatis.
```
nano /etc/apt/apt.conf.d/20auto-upgrades
```
> Penjelasan: Membuat berkas pengaktif. Isi seperti kotak di bawah.

**/etc/apt/apt.conf.d/20auto-upgrades** | Isi berkas

```
APT::Periodic::Update-Package-Lists "1";
APT::Periodic::Unattended-Upgrade "1";
```

**TERMINAL VM DEBIAN** | Sebagai root

```
unattended-upgrade --dry-run --debug 2>&1 | tail -15
```
> Penjelasan: Uji tanpa mengubah apa pun. Harus menampilkan asal paket yang diizinkan (Debian security) dan
tanpa error.  
```
systemctl status apt-daily-upgrade.timer --no-pager
```
> Penjelasan: Memastikan penjadwal harian aktif (active waiting).
```
[ -f /var/run/reboot-required ] && echo PERLU-REBOOT || echo aman
```
> Penjelasan: Memeriksa apakah ada update yang menunggu reboot.
CATATAN  
Hanya update keamanan dari repositori Debian yang otomatis, dan VM tidak mulai ulang sendiri. Paket dari repositori  
lain (termasuk Docker dan Tailscale) dan image container tidak ikut. Perbarui itu manual sebulan sekali dengan apt  
update && apt full-upgrade dan docker compose pull, setelah backup.  

## 25.7 STB Armbian: SSH kunci dan kebijakan update

STB (192.168.88.253) menjalankan AdGuard Home dan menjadi DNS seluruh rumah, sehingga stabilitasnya  
lebih penting dari fiturnya. Dua tindakan saja: SSH hanya dengan kunci, dan tidak memakai update otomatis.  

**POWERSHELL WINDOWS** | PowerShell (laptop)

```
type $env:USERPROFILE\.ssh\id_ed25519.pub
```
> Penjelasan: Tampilkan kunci publik untuk disalin.

**TERMINAL STB** | SSH ke 192.168.88.253 (root)

```
mkdir -p /root/.ssh
```
> Penjelasan: Memastikan folder kunci ada.
```
echo 'TEMPEL-KUNCI-PUBLIK-DI-SINI' >> /root/.ssh/authorized_keys
```
> Penjelasan: Menambahkan kunci publik.
```
chmod 600 /root/.ssh/authorized_keys
```
> Penjelasan: Membatasi izin.
```
grep -n Include /etc/ssh/sshd_config
```
> Penjelasan: Jika ada baris Include .../sshd_config.d/\*.conf, buat berkas seperti di Bab 25.4. Jika tidak ada, ubah
langsung baris terkait di /etc/ssh/sshd_config.  
Setelah uji login kunci dari jendela baru berhasil, isi pengaturan sama dengan Proxmox (PermitRootLogin  
prohibit-password dan PasswordAuthentication no), lalu sshd -t dan systemctl reload ssh.  
KEAMANAN  
Jangan memasang unattended-upgrades di STB. Pembaruan kernel atau berkas boot pada box Amlogic dapat  
membuat STB gagal boot (pengalaman eMMC di Edisi 2 Bab 12.2). Perbarui AdGuard Home dari menunya sendiri  
dan perbarui sistem secara manual hanya setelah backup AdGuardHome.yaml dan bila Anda siap menghadapi STB  
yang tidak boot.  

## 25.8 Mengeraskan MikroTik

Edisi 2 Bab 3.8 sudah mematikan layanan tak terpakai dan membatasi WinBox dan SSH. Tambahannya adalah  
aturan firewall yang menutup akses ke router dari sisi WAN (jaringan TL-WR840N), pembatasan WebFig, dan  
beberapa layanan tersembunyi.  
PERINGATAN - Selalu pakai Safe Mode  
Aktifkan Safe Mode sebelum mengubah firewall: klik tombol Safe Mode di WinBox (atau tekan Ctrl+X di terminal). Bila  
koneksi Anda terputus karena aturan salah, RouterOS membatalkan perubahan otomatis. Matikan Safe Mode setelah  
semua uji berhasil.  

**TERMINAL MIKROTIK** | WinBox &gt; New Terminal (RouterOS 6.49)

```
/ip firewall filter print
```
> Penjelasan: Melihat aturan yang sudah ada. Jika sudah ada aturan "drop all not coming from LAN" atau drop dari
ether1-gateway, jangan menambah aturan serupa (langkah 2 sampai 5); cukup periksa urutannya.  
2  
&gt; /ip firewall filter add chain=input action=accept connection-state=established,related  
place-before=0 comment="terima koneksi berjalan"  
> Penjelasan: Menerima balasan dari koneksi yang sudah berjalan. Harus paling atas.
3  
&gt; /ip firewall filter add chain=input action=drop connection-state=invalid place-before=1  
comment="buang paket tidak valid"  
> Penjelasan: Membuang paket yang tidak sah.
4  
&gt; /ip firewall filter add chain=input action=drop in-interface=ether1-gateway  
place-before=2 comment="tutup router dari sisi WAN"  
> Penjelasan: Menutup seluruh akses ke router dari arah internet/WR840N. Router tetap terbuka dari LAN.
5  
&gt; /ip firewall filter add chain=forward action=drop in-interface=ether1-gateway  
connection-state=new connection-nat-state=!dstnat comment="tolak koneksi baru dari WAN ke  
LAN"  
> Penjelasan: Menolak koneksi baru dari arah WAN ke jaringan rumah.
```
/ip firewall filter print
```
> Penjelasan: Memeriksa urutan: terima koneksi berjalan, buang tidak valid, tutup WAN, lalu forward.

**TERMINAL MIKROTIK** | WinBox &gt; New Terminal

```
/ip service set www address=192.168.88.0/24
```
> Penjelasan: Membatasi WebFig ke LAN. Akses dari luar rumah tetap bisa lewat Tailscale, karena router Tailscale
tampil di router sebagai alamat LAN.  
```
/ip proxy set enabled=no
```
> Penjelasan: Mematikan web proxy bawaan.
```
/ip socks set enabled=no
```
> Penjelasan: Mematikan SOCKS proxy.
```
/ip upnp set enabled=no
```
> Penjelasan: Mematikan UPnP (perangkat tidak boleh membuka port sendiri).
```
/tool bandwidth-server set enabled=no
```
> Penjelasan: Mematikan server uji bandwidth.
```
/ip cloud set ddns-enabled=no
```
> Penjelasan: Mematikan layanan DDNS bawaan MikroTik.
```
/ip ssh set strong-crypto=yes
```
> Penjelasan: Memakai algoritma SSH yang lebih kuat.
```
/user print
```
> Penjelasan: Memeriksa daftar pengguna. Pastikan hanya akun Anda dan tidak ada akun asing.

**TERMINAL MIKROTIK** | WinBox &gt; New Terminal

```
/export file=setelah-suplemen1
```
> Penjelasan: Menyimpan konfigurasi baru setelah semua uji berhasil.
```
/system backup save name=setelah-suplemen1
```
> Penjelasan: Backup biner baru.
CATATAN  
Pemisahan jaringan (VLAN) untuk memisahkan server, tamu, dan perangkat IoT sangat berguna tetapi bergantung  
pada kemampuan switch RB750GL dan perlu dicoba dulu. Itu dibahas sebagai opsi di suplemen berikutnya,  
bukan di sini.  

## 25.9 Backup dan pemulihan pengaturan keamanan

Yang disimpan Cara Simpan di  
Kunci privat SSH (id_ed25519) dan  
passphrase  
Salin ke flashdisk terenkripsi atau password  
manager  
Di luar laptop  
Recovery Keys 2FA Proxmox Dicetak atau di password manager Di luar server  
Konfigurasi MikroTik (.rsc dan .backup) Langkah di Bab 25.2 dan 25.8 Laptop dan HDD 2 TB  
/etc/pve dan /etc/ssh Proxmox Langkah di Bab 25.2 Laptop dan HDD 2 TB  
Snapshot VM Debian Tab Snapshots; hapus bila sudah tak dipakai Penyimpanan Proxmox  
AdGuardHome.yaml Edisi 2 Bab 12 Laptop  
Cadangan yang tidak pernah diuji belum berarti. Satu kali saja, praktikkan memulihkan snapshot VM Debian ke  
keadaan sebelum bab ini dan pastikan semua layanan hidup lagi.  

## 25.10 Checklist uji keamanan

No Uji Cara Hasil yang diharapkan  
1 SSH Proxmox tanpa kunci ditolak ssh -o PubkeyAuthentication=no  
root@192.168.88.10  
Permission denied (publickey)  
2 SSH Proxmox dengan kunci jalan ssh root@192.168.88.10 Masuk  
3 Root VM Debian ditolak ssh root@192.168.88.20 Permission denied  
4 Pengguna biasa VM masuk  
dengan kunci  
ssh &lt;USER&gt;@192.168.88.20 Masuk tanpa password  
5 Web Proxmox meminta kode 2FA Login adminlab dan root@pam Kode 6 digit diminta  
6 Firewall Proxmox aktif pve-firewall status enabled/running  
7 UFW VM aktif ufw status verbose Status: active  
8 Update otomatis siap unattended-upgrade --dry-run --debug Tanpa error  
9 MikroTik tertutup dari WAN /ip firewall filter print Aturan drop  
in-interface=ether1-gateway ada  
10 Layanan masih jalan Buka Portainer, Nextcloud, AdGuard Semua terbuka dari LAN  
11 Backup baru ada Berkas di laptop rsc, backup, etc-pve.tgz  

## 25.11 Masalah dan solusi

KASUS NYATA  
Gejala: Setelah mengubah SSH, muncul "Permission denied (publickey)" untuk akun yang benar. Penyebab: kunci  
publik belum masuk, salah izin berkas, atau salah akun. Solusi: masuk lewat konsol, cek ls -l  
~/.ssh/authorized_keys (izin 600) dan isi barisnya; sementara waktu hapus berkas 00-hardening.conf dan  
systemctl reload ssh.  
KASUS NYATA  
Gejala: Tidak bisa membuka web Proxmox setelah menyalakan firewall. Penyebab: alamat laptop di luar "jaringan  
lokal" menurut Proxmox. Solusi: dari konsol jalankan pve-firewall stop, periksa pve-firewall localnet,  
koreksi Source pada aturan 8006 dan 22, lalu pve-firewall start.  
KASUS NYATA  
Gejala: Kode 2FA ditolak dan Recovery Keys tidak ada. Solusi: dari konsol Proxmox (root) hapus faktor kedua akun  
itu, misalnya pveum user tfa delete root@pam; jika perintah tidak dikenali, periksa pveum help user. Lalu  
pasang 2FA baru dan simpan Recovery Keys.  
KASUS NYATA  
Gejala: Port container tetap bisa dibuka dari laptop padahal UFW menolaknya. Penyebab: Docker memasang aturan  
sendiri yang mendahului UFW. Solusi: ini perilaku normal; ikuti catatan Bab 25.6 dan audit Bab 38.  
KASUS NYATA  
Gejala: Terputus dari MikroTik setelah menambah aturan firewall. Solusi: bila Safe Mode aktif, perubahan otomatis  
dibatalkan; bila tidak, sambungkan kabel ke ether2, buka WinBox lewat 192.168.88.1, hapus aturan terakhir, atau  
pulihkan backup.
