# Bab 52. Audit Keamanan

PENEMPATAN - SEMUA GUEST - baca-saja  
Tempat: Skrip audit dijalankan di setiap VM (dan bagian host di shell node Proxmox). Tidak ada guest baru, tidak ada  
layanan baru.  
Alasan: Setiap guest dapat berbeda keadaannya. Hasil audit dicatat per guest supaya temuan jelas milik siapa.  
Prinsip: Skrip hanya membaca dan mencetak; tidak mengubah apa pun.  
Audit adalah pemeriksaan berkala bahwa keadaan sebenarnya sama dengan yang Anda kira. Bab ini memberi  
daftar, satu skrip untuk VM, dan tabel laporan. Hasilnya bukan jaminan aman; ia hanya menunjukkan apa yang  
terlihat dari alat yang dipakai.  

## 52.1 Daftar pemeriksaan per lapisan

Lapisan Pemeriksaan Cara Hasil yang diharapkan  
MikroTik Tidak ada port forward; layanan  
terbatas  
/ip firewall nat print; /ip service  
print  
Hanya masquerade; layanan  
dibatasi 192.168.88.0/24 (Edisi  
2)  
Tailscale Funnel tidak aktif; perangkat  
dikenal; key expiry  
tailscale funnel status (di tiap  
node); konsol admin Machines  
Funnel kosong; tidak ada  
perangkat asing  
Tailscale Kebijakan tailnet Editor kebijakan Hanya entri yang Anda pahami  
(Suplemen 1 Bab 26.6, 44.3)  
Host Proxmox Tidak ada Docker; pembaruan; port which docker; apt list  
--upgradable; ss -tlnp  
docker tidak ada; port hanya  
8006, 22, layanan Proxmox  
Host Proxmox Firewall aktif; 2FA untuk root pve-firewall status; Datacenter &gt;  
Permissions &gt; Two Factor  
Aktif; TOTP terpasang  
Setiap VM Port mendengarkan dan port  
Docker  
Skrip 52.2 Hanya yang ada di matriks 51.2  
Setiap VM Kontainer privileged; docker.sock Skrip 52.2 Kosong, atau risiko dicatat  
(Portainer)  
Setiap VM Berkas .env Skrip 52.2 Tidak dapat dibaca orang lain  
(mode 600)  
Setiap VM SSH: kunci saja, tanpa root Skrip 52.2; 52.4 passwordauthentication no;  
permitrootlogin no  
Setiap VM Pembaruan keamanan otomatis systemctl is-enabled  
unattended-upgrades  
enabled  
Lynis Skor dan saran 52.3 Dibaca, bukan diterapkan buta  
Backup Job terakhir berhasil; uji pulih; kunci  
tersimpan; salinan kedua  
Datacenter &gt; Backup; Bab 50 Semua ya, bertanggal  
Publik Hanya tunnel VM 210 yang  
menghadap internet  
Dasbor Cloudflare: daftar route Hanya hostname situs publik  

## 52.2 Skrip audit untuk VM

**TERMINAL VM** | Setiap VM, sebagai root (setelah su -)

```
nano /root/audit-vm.sh
```
> Penjelasan: Isi seperti kotak di bawah.

**/root/audit-vm.sh** | Isi berkas

```
#!/bin/bash
# Audit baca-saja. Mencetak temuan, tidak mengubah apa pun.
echo "== Host: $(hostname) | $(date '+%F %T')"
echo "== Port mendengarkan selain loopback"
ss -tulnH | awk '$5 !~ /^127\.|^\[::1\]/ {print $1, $5}'
if command -v docker >/dev/null; then
 echo "== Port Docker yang dipublikasikan"
 docker ps --format '{{.Names}}: {{.Ports}}' | grep -- '->'
 echo "== Kontainer privileged (idealnya kosong)"
```

 docker ps -q | xargs -r docker inspect \  
 --format '{{.Name}} {{.HostConfig.Privileged}}' | grep true  
 echo "== Kontainer yang memasang docker.sock"  
 docker ps -q | xargs -r docker inspect \  
 --format '{{.Name}} {{range .Mounts}}{{.Source}} {{end}}' | grep docker.sock  
fi  
echo "== Berkas .env terbaca orang lain (idealnya kosong)"  
find /opt/stacks -maxdepth 2 -name .env -perm /077 2&gt;/dev/null  
echo "== Pengaturan SSH"  
sshd -T 2&gt;/dev/null | grep -E '^(permitrootlogin|passwordauthentication) '  
echo "== Pembaruan otomatis"  
systemctl is-enabled unattended-upgrades 2&gt;/dev/null || echo "tidak aktif"  
echo "== Jumlah paket menunggu pembaruan"  
apt list --upgradable 2&gt;/dev/null | grep -vc '^Listing'  

**TERMINAL VM** | Setiap VM, sebagai root

```
chmod 700 /root/audit-vm.sh && /root/audit-vm.sh | tee /root/audit-$(date +%F).txt
```
> Penjelasan: Menjalankan skrip dan menyimpan hasilnya bertanggal untuk laporan 52.7.
Bagian keluaran Cara membacanya  
Port mendengarkan Cocokkan dengan matriks 51.2. Port yang tidak Anda kenal: cari prosesnya dengan ss -tulnp  
Port Docker Setiap tanda 0.0.0.0:PORT-&gt; adalah port terbuka di LAN VM; pastikan firewall Proxmox  
membatasinya  
Privileged / docker.sock Kontainer dengan docker.sock setara akses root ke VM. Portainer dan agen Beszel biasanya  
memerlukannya; catat sebagai risiko diterima (52.7)  
SSH Targetnya permitrootlogin no dan passwordauthentication no setelah 52.4  
Pembaruan Angka besar berarti VM jarang diperbarui; jalankan apt update && apt upgrade dan periksa  

## 52.3 Lynis (opsional tetapi berguna)

**TERMINAL VM** | Satu VM dulu (misalnya docker-core), sebagai root

```
apt install -y lynis
```
> Penjelasan: Memasang pemindai audit dari repositori Debian (versinya bisa lebih lama dari rilis terbaru proyeknya
[BELUM PASTI]).  
```
lynis audit system
```
> Penjelasan: Memindai sistem (beberapa menit). Di akhir tercetak Hardening index dan daftar saran.
```
grep -E "^(warning|suggestion)" /var/log/lynis-report.dat | head -40
```
> Penjelasan: Mencetak peringatan dan saran dari laporan.
PERINGATAN  
Jangan menerapkan semua saran Lynis secara buta; sebagian mengubah perilaku sistem (misalnya mematikan  
layanan atau mengunci kernel) dan bisa merusak Docker atau agen tamu. Baca satu per satu, terapkan yang Anda  
pahami, catat yang ditolak.  

## 52.4 SSH dengan kunci (tanpa kata sandi)

**POWERSHELL WINDOWS** | PowerShell (laptop)

```
ssh-keygen -t ed25519
```
> Penjelasan: Membuat pasangan kunci di folder .ssh Anda. Beri frasa sandi pada kunci.
```
scp $env:USERPROFILE\.ssh\id_ed25519.pub <USER>@192.168.88.24:/tmp/
```
> Penjelasan: Menyalin kunci publik ke VM (ganti &lt;USER&gt; dan IP; ulangi untuk tiap VM).

**TERMINAL VM** | VM tujuan, sebagai pengguna biasa (bukan root)

```
mkdir -p ~/.ssh && cat /tmp/id_ed25519.pub >> ~/.ssh/authorized_keys
```
> Penjelasan: Mendaftarkan kunci.
```
chmod 700 ~/.ssh && chmod 600 ~/.ssh/authorized_keys
```
> Penjelasan: Izin yang disyaratkan SSH.
Uji dulu dari jendela PowerShell kedua (ssh &lt;USER&gt;@IP) sampai masuk tanpa kata sandi akun. Baru kunci  
sandi, dengan sesi lama tetap terbuka:  

**TERMINAL VM** | VM tujuan, sebagai root (setelah su -)

```
nano /etc/ssh/sshd_config.d/10-hardening.conf
```
> Penjelasan: Isi dua baris seperti kotak di bawah.

**/etc/ssh/sshd_config.d/10-hardening.conf** | Isi berkas

```
PasswordAuthentication no
PermitRootLogin no
```

**TERMINAL VM** | VM tujuan, sebagai root

```
sshd -t && systemctl reload ssh
```
> Penjelasan: Memeriksa sintaks, lalu memuat ulang SSH. Jangan menutup sesi lama sebelum uji sesi baru
berhasil.  
CATATAN  
Konsol web Proxmox tetap menjadi jalur darurat bila SSH terkunci. Untuk Android dan iPhone, SSH ke VM tidak  
diperlukan; pekerjaan itu dilakukan dari laptop.  

## 52.5 Pembaruan otomatis dan pembaruan host

**TERMINAL VM** | Setiap VM, sebagai root

```
dpkg-reconfigure -plow unattended-upgrades
```
> Penjelasan: Mengaktifkan pembaruan keamanan otomatis Debian (jawab Yes). Ini tidak memperbarui image
Docker; image diperbarui manual dengan docker compose pull (dengan backup lebih dulu).  
```
unattended-upgrade --dry-run -d 2>&1 | tail -5
```
> Penjelasan: Uji kering: menunjukkan apa yang akan dilakukan tanpa menjalankannya.
Host Proxmox: node &gt; Updates &gt; Refresh lalu Upgrade, dan jadwalkan pemeriksaan bulanan. Buat backup (Bab  
50) sebelum pembaruan besar.  

## 52.6 Tailscale, Cloudflare, MikroTik, PBS

1. Di setiap node tailnet (router-vm, lab-vault): tailscale funnel status harus kosong, dan tailscale serve status  
hanya memuat layanan yang Anda niatkan.  
2. Konsol admin Tailscale &gt; Machines: cabut perangkat yang tidak dikenali; periksa tanggal kedaluwarsa kunci  
(server dinonaktifkan expiry-nya).  
3. Cloudflare (bila Bab 43 dikerjakan): daftar route tunnel hanya berisi hostname situs publik; token pernah  
dirotasi bila ada kecurigaan.  
4. MikroTik: /ip firewall nat print tidak memuat dst-nat; layanan IP sesuai Edisi 2.  
5. PBS: akun root memakai 2FA (Access Control &gt; Two Factor); pengguna pve@pbs hanya berperan  
DatastoreBackup.  

## 52.7 Laporan audit

Isi satu baris per guest setiap audit. Simpan keluaran skrip bertanggal di VM masing-masing.  
Guest Tanggal Port sesuai  
matriks  
Privileged /  
docker.sock  
SSH kunci Update  
otomatis  
Skor Lynis  
201 docker-core  
204 git  
205 vault  
206 affine  
207 nextcloud  
208 n8n  
209 web  
210 web-public  
211 music  
212 pbs  
213 sso  
214 immich  
Host Proxmox -  
Risiko yang diterima (isi dengan sadar)  
Temuan Alasan diterima Tinjau kembali  
Portainer memasang docker.sock  
(docker-core)  
Fungsinya memang mengelola Docker; terbatas pada VM  
docker-core dan hanya dapat dijangkau dari LAN via  
Caddy  
Tiap audit  
Agen Beszel memasang docker.sock  
(bila dipakai)  
Untuk membaca statistik kontainer Tiap audit  
(tambahkan sendiri)  

## 52.8 Sisi klien dan jadwal

Perangkat Pemeriksaan berkala  
Windows Jalankan skrip audit lewat SSH; perbarui Windows dan Tailscale; pastikan kunci SSH berfrasa sandi  
Android Buka aplikasi Tailscale dan pastikan hanya perangkat Anda yang tersambung; periksa notifikasi Gotify  
masih tiba; perbarui Android, Bitwarden, DAVx5  
iPhone Sama: periksa Tailscale dan Gotify; perbarui iOS dan aplikasi; kunci layar aktif  
Jadwal: audit penuh setiap bulan, ditambah satu audit singkat (skrip 52.2 pada VM terkait) setiap kali menambah  
atau mengubah layanan. Catat tanggalnya di laporan 52.7.
