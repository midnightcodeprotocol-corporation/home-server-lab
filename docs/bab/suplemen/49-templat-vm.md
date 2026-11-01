# Bab 49. Template VM Debian dan CT Debian serta Cara Mengklon Guest

PENEMPATAN - BARU - VM 200 (templat), lalu klon per layanan  
Tempat: VM 200 Template-VM di host Proxmox. Templat tidak pernah dinyalakan setelah jadi; ia hanya  
disalin.  
Alasan: Satu sumber yang sama untuk semua VM Docker: cepat, seragam, dan pembaruan keamanan dasar sudah  
ada. Setiap layanan lalu mendapat salinan penuh yang berdiri sendiri.  
Tidak termasuk: Tailscale (setiap node harus punya identitas sendiri) dan layanan apa pun.  

Bab ini menjelaskan dua sumber dasar yang bisa dipakai berulang: VM 200 untuk aplikasi berbasis VM/Docker, dan CT 100 untuk layanan Linux ringan tanpa Docker. Keduanya sudah dibuat dengan Debian 13 di Proxmox pada 1 November 2026. SSH baca-saja mengonfirmasi VM 200: 1 vCPU, RAM 2 GiB, disk 32 GiB, QEMU Agent aktif pada konfigurasi; CT 100: 1 vCPU, RAM/swap 512 MiB, disk 8 GiB, unprivileged, nesting, DHCP. Nama aktual tertulis `Tamplate-VM` dan `Tamplate-CT` (kemungkinan typo). Paket guest VM 200 belum diperiksa; periksa sebelum memakai template sebagai sumber guest Docker. Template adalah sumber yang tidak dijalankan; buat clone untuk setiap layanan, lalu atur nama, IP, resource, dan aplikasinya sendiri.

**Prasyarat sebelum mulai:** pembaruan Proxmox selesai dan host sudah reboot. Jalankan verifikasi pasca-update di Bab 9.6; `lscpu` harus menunjukkan VT-x dan `/dev/kvm` harus ada sebelum membuat template VM. Jika pemeriksaan gagal, perbaiki firmware mengikuti Bab 27.5. Template VM 200 dan CT 100 sudah tercatat dibuat; jangan buat ulang jika ID tersebut masih ada.

## 49.1 Rencana: dari mana templat dibuat

Template yang sudah tampak pada UI adalah VM 200 `Tamplate-VM` dan CT 100 `Tamplate-CT`; pengguna mengonfirmasi keduanya memakai Debian 13. Paket dasar VM 200 belum dicatat. Jangan jalankan ulang langkah pembuatan atau mengubah template berisi data; gunakan bagian 49.2–49.3 hanya bila perlu membangun ulang dari awal setelah memastikan template lama memang boleh diganti.

## 49.2 Membuat dan mengisi VM dasar

Pemasangan Debian secara rinci ada di Edisi 2 (Debian 13, ISO netinst, tanpa lingkungan desktop). Ringkasnya  
di Proxmox:  
1. Di web Proxmox klik Create VM. VM ID 200, Name Template-VM. Pada OS pilih ISO Debian 13 netinst.  
2. System: biarkan bawaan dan centang QEMU Agent. Disks: Bus SCSI, ukuran 24 GiB (Debian + Docker dan  
layanan kecil; data besar nanti pakai disk kedua). CPU 2 inti. Memory 2048.  
3. Network: bridge vmbr0, model VirtIO. Selesaikan, jalankan, dan pasang Debian lewat konsol: hanya SSH  
server dan standard system utilities yang dipilih.  
4. Setelah masuk sebagai root (su -), lanjutkan di bawah.  

**TERMINAL VM TEMPLAT** | VM 200, sebagai root (setelah su -)

apt update && apt upgrade -y
```
> Penjelasan: Memperbarui paket dasar.
```
apt install -y qemu-guest-agent unattended-upgrades ca-certificates curl nano
```
> Penjelasan: Agen tamu (Proxmox bisa membekukan sistem berkas saat backup), pembaruan keamanan otomatis,
dan alat dasar.  
```
install -m 0755 -d /etc/apt/keyrings
```
> Penjelasan: Folder kunci repositori.
```
curl -fsSL https://download.docker.com/linux/debian/gpg -o /etc/apt/keyrings/docker.asc
```
> Penjelasan: Mengunduh kunci repositori resmi Docker.
```
chmod a+r /etc/apt/keyrings/docker.asc
```
> Penjelasan: Membuat kunci bisa dibaca apt.
```
nano /etc/apt/sources.list.d/docker.sources
```
> Penjelasan: Isi seperti kotak di bawah.

**/etc/apt/sources.list.d/docker.sources** | Isi berkas

```
Types: deb
URIs: https://download.docker.com/linux/debian
Suites: trixie
Components: stable
Signed-By: /etc/apt/keyrings/docker.asc
```

**TERMINAL VM TEMPLAT** | VM 200, sebagai root

```
apt update
apt install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
```
> Penjelasan: Memasang Docker Engine dan Compose dari repositori resmi. Ketersediaan paket dan langkah
pemasangan Debian 13 perlu dicocokkan lagi dengan dokumentasi resmi saat instalasi.

```
docker run --rm hello-world
```
> Penjelasan: Uji: harus mencetak pesan sukses. Mengunduh image sekali.
```
systemctl status qemu-guest-agent --no-pager
```
> Penjelasan: Agen harus aktif setelah opsi QEMU Agent di Proxmox diaktifkan dan VM dimulai ulang sekali.
```
mkdir -p /opt/stacks
```
> Penjelasan: Folder induk semua layanan Docker (konvensi Suplemen 3 Bab 31).
KEAMANAN  
Jangan memasang Tailscale, Docker Compose layanan, atau akun layanan di templat. Templat harus polos; setiap  
klon memberi identitasnya sendiri.  

## 49.3 Membersihkan dan menjadikan templat

**TERMINAL VM TEMPLAT** | VM 200, sebagai root

```
apt clean
mkdir -p /etc/systemd/system/ssh.service.d
cat > /etc/systemd/system/ssh.service.d/10-generate-host-keys.conf <<'EOF'
[Service]
ExecStartPre=
ExecStartPre=/usr/bin/ssh-keygen -A
ExecStartPre=/usr/sbin/sshd -t
EOF
systemctl daemon-reload
rm -f /etc/ssh/ssh_host_*
```
> Penjelasan: Membersihkan cache dan kunci lama. Drop-in menjalankan ssh-keygen -A sebelum sshd -t,
sebab urutan bawaan Debian memeriksa konfigurasi lebih dulu dan SSH gagal jika belum ada kunci host.
```
truncate -s 0 /etc/machine-id
rm -f /var/lib/dbus/machine-id
ln -s /etc/machine-id /var/lib/dbus/machine-id
```
> Penjelasan: Mengosongkan identitas mesin dan menyatukan jalur D-Bus sebagai symlink. Debian membuat
machine ID baru pada boot pertama clone. Jangan tinggalkan salinan ID lama di template.
```
history -c && poweroff
```
> Penjelasan: Menghapus riwayat sesi dan mematikan VM.
1. Di Proxmox klik kanan VM 200 &gt; Convert to template (atau di shell host: qm template 200). Setelah ini  
VM tidak bisa dinyalakan, hanya disalin.  
2. Opsional: di Options templat, matikan Start at boot.  

## 49.4 Penyiapan awal setiap VM hasil klon

Prosedur ini dipakai oleh semua bab yang membuat VM baru (kotak penempatan menyebut "Bab 49.4"). Contoh di bawah untuk VM 205 vault; ganti ID, nama, dan IP sesuai peta 48.3. Saat server masih di jaringan sementara, biarkan jaringan clone memakai DHCP dan jangan membuat reservasi MikroTik atau menetapkan IP `192.168.88.x`. Setelah host tersambung kembali ke MikroTik, ikuti langkah reservasi alamat di bawah.

**Pilih Full Clone untuk guest layanan permanen.** Clone ini memiliki disk independen sehingga lebih mudah dipindah dan dipelihara. Linked Clone lebih hemat ruang untuk guest uji sementara, tetapi tetap membutuhkan disk dasar/template dan tidak boleh diperlakukan sebagai salinan mandiri. `local-lvm` mendukung linked clone, tetapi contoh proyek ini memakai Full Clone untuk layanan.

**TERMINAL HOST PROXMOX** | Shell node Proxmox (host), sebagai root

```
qm clone 200 205 --name vault --full 1
```
> Penjelasan: Salinan penuh (bukan terkait) sehingga VM berdiri sendiri dan templat bisa dihapus tanpa
merusaknya.  
```
qm set 205 --memory 1024 --cores 1 --onboot 1
```
> Penjelasan: RAM, inti, dan nyalakan otomatis saat host hidup.
```
qm start 205
```
> Penjelasan: Menyalakan klon. Buka Console VM 205 di web Proxmox.
```
qm config 205 | grep net0
```
> Penjelasan: Menampilkan alamat MAC VM (nilai setelah virtio=). Dibutuhkan untuk reservasi IP di MikroTik.

**TERMINAL VM BARU** | Konsol VM baru (205), login lalu su -

```
hostnamectl set-hostname vault
```
> Penjelasan: Memberi nama host sesuai peta.
```
nano /etc/hosts
```
> Penjelasan: Ganti nama lama pada baris 127.0.1.1 menjadi vault.
```
systemctl status ssh --no-pager
ssh-keygen -lf /etc/ssh/ssh_host_ed25519_key.pub
cat /etc/machine-id
```
> Penjelasan: Pastikan SSH aktif, fingerprint kunci host dibuat, dan machine ID terisi. Keduanya harus
berbeda dari template maupun VM lain.
Setelah host dan VM tersambung ke MikroTik, alamat tetap lewat reservasi DHCP MikroTik (DNS otomatis dari DHCP, sehingga menunjuk AdGuard). Dari Terminal di WinBox atau SSH ke MikroTik:

**TERMINAL MIKROTIK** | Terminal WinBox atau SSH ke 192.168.88.1

```
/ip dhcp-server print
```
> Penjelasan: Melihat nama server DHCP (misalnya defconf) untuk dipakai di bawah.
```
/ip dhcp-server lease add address=192.168.88.24 mac-address=AA:BB:CC:DD:EE:FF server=defconf comment=vault
```
> Penjelasan: Mereservasi 192.168.88.24 untuk MAC VM. Ganti MAC dan nama server. Alamat di luar rentang pool 100-254 untuk lease statis umumnya diterima [BELUM PASTI]; bila ditolak, atur IP statis di Debian.  

**TERMINAL VM BARU** | Konsol VM baru, sebagai root

```
systemctl restart networking
```
> Penjelasan: Meminta alamat baru. Bila tidak berubah, jalankan reboot.
```
ip -4 -br a
```
> Penjelasan: Memastikan alamat 192.168.88.24 dipakai.
```
ping -c1 192.168.88.253 && ping -c1 1.1.1.1
```
> Penjelasan: Uji DNS lokal dan internet.
TIPS  
Pasang agen Beszel (Suplemen 3 Bab 33) pada setiap VM baru dan tambahkan monitor di Uptime Kuma. Disk besar  
untuk data (misalnya Nextcloud kelak) sebaiknya disk kedua, bukan memperbesar disk sistem.  

## 49.5 Sisi klien: mengelola VM dari Windows, Android, iPhone

Perangkat Cara Catatan  
Windows Browser ke https://192.168.88.10:8006 untuk Proxmox;  
PowerShell: ssh &lt;USER&gt;@192.168.88.24 untuk VM  
Konsol web (noVNC) tetap bisa dipakai bila  
SSH terkunci firewall  
Android Chrome ke alamat Proxmox lewat Tailscale (rute subnet dari  
router-vm aktif)  
Cukup untuk melihat status, menyalakan  
atau mematikan VM; pekerjaan panjang di  
laptop  
iPhone Safari ke alamat yang sama dengan Tailscale aktif;  
peringatan sertifikat Proxmox perlu disetujui  
Sama seperti Android  
CATATAN  
Aplikasi pihak ketiga untuk Proxmox ada di toko aplikasi, tetapi tidak dibahas di sini karena kebijakan buku ini  
memakai alat resmi dan peramban.

## 49.6 Template CT Debian dasar dan cara mengklon

### Bedakan template unduhan dan template CT

Proxmox memakai arsip OS CT saat membuat container baru. Arsip unduhan itu belum menjadi CT yang siap diklon. Bagian ini membuat satu CT dasar bernama `Template-CT`, memasang pembaruan dan alat umum, lalu mengubah CT itu menjadi template Proxmox.

Gunakan CT untuk layanan Linux ringan tanpa Docker. Layanan yang memakai Docker tetap ditempatkan di VM Debian. Template CT memakai mode unprivileged sebagai pilihan awal. Jangan memasang layanan, Tailscale, kunci, token, atau data pribadi ke template.

### A. Unduh arsip Debian

Di web Proxmox pilih storage `local` > CT Templates > Templates. Cari Debian 13/Trixie standard amd64 terbaru yang tersedia, lalu unduh. Nama berkas dapat berubah mengikuti rilis.

### B. Buat CT dasar

1. Pilih Create CT. Gunakan CTID `100` dan hostname `Template-CT`.
2. Pilih template Debian yang baru diunduh.
3. Pilih storage `local-lvm` untuk disk root 8 GiB.
4. Pertahankan unprivileged container. Berikan 1 core dan RAM 512 MiB sebagai baseline.
5. Hubungkan ke bridge `vmbr0` dengan IPv4 DHCP. Jangan menanam IP layanan pada template.
6. Selesaikan wizard, nyalakan CT, lalu buka Console.

Jika server masih di jaringan sementara, DHCP membuat template bisa diperbarui tanpa memakai IP rumah yang belum terhubung. IP final diatur pada clone setelah MikroTik aktif.

### C. Perbarui sistem dasar

**TERMINAL CT DASAR** | Console CT 100, login root

```
apt update && apt full-upgrade -y
```
> Penjelasan: Memasang pembaruan dan perbaikan keamanan dasar.

```
apt install -y ca-certificates curl nano openssh-server
```
> Penjelasan: Memasang alat umum minimum termasuk server SSH agar prosedur pembuatan kunci host
berlaku pada setiap clone.

```
mkdir -p /etc/systemd/system/ssh.service.d
cat > /etc/systemd/system/ssh.service.d/10-generate-host-keys.conf <<'EOF'
[Service]
ExecStartPre=
ExecStartPre=/usr/bin/ssh-keygen -A
ExecStartPre=/usr/sbin/sshd -t
EOF
systemctl daemon-reload
rm -f /etc/ssh/ssh_host_*
truncate -s 0 /etc/machine-id
rm -f /var/lib/dbus/machine-id
ln -s /etc/machine-id /var/lib/dbus/machine-id
poweroff
```
> Penjelasan: Pasang generator host key, hapus kunci dan ID lama, lalu matikan CT. Clone test kami
memastikan kunci SSH baru muncul saat CT hasil clone boot.

### D. Jadikan CT sebagai template

Pastikan CT 100 berhenti. Di UI pilih CT 100 > More > Convert to template. Alternatif pada shell host Proxmox:

**TERMINAL HOST PROXMOX** | Shell node sebagai root

```
pct template 100
```
> Penjelasan: Mengunci CT dasar sebagai sumber clone. Jangan menyalakan atau memasang aplikasi langsung pada template.

### E. Klon untuk layanan

Contoh membuat CT 101 untuk AdGuard kedua. Jalankan setelah host tersambung ke jaringan rumah dan pastikan IP `.11` belum digunakan:

```
pct clone 100 101 --full 1
```
> Penjelasan: Membuat salinan penuh yang berdiri sendiri dari template CT 100.

```
pct set 101 --hostname adguard2 --cores 1 --memory 512 --net0 name=eth0,bridge=vmbr0,ip=192.168.88.11/24,gw=192.168.88.1
```
> Penjelasan: Mengatur nama, resource, dan jaringan clone. Ganti CTID, hostname, CPU/RAM, dan IP sesuai peta guest.

```
pct start 101
pct exec 101 -- hostname
pct exec 101 -- ip -4 -br address
```
> Penjelasan: Menyalakan CT dan memeriksa hostname serta IP sebelum memasang aplikasi.

Untuk CT 102 Samba, ulangi proses clone dengan CTID `102`, nama `files`, dan IP `192.168.88.12`. Jangan memakai alamat `192.168.88.x` ketika host masih di jaringan sementara; gunakan DHCP atau tunggu sampai MikroTik tersambung.

### Catatan pembaruan template

Template tidak menerima pembaruan otomatis setelah dibuat. Untuk baseline baru, perbarui dan uji clone sementara, lalu buat template versi baru. Setiap clone perlu identitas SSH, hostname, alamat jaringan, dan resource yang unik.
