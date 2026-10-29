# Bab 11. VM Debian 13 (untuk Docker, Git, Nextcloud, dan lainnya)

Container tidak cocok untuk semuanya. Docker, Home Assistant, dan Kubernetes sebaiknya di VM. Bab  
ini membuat VM Debian GNU/Linux 13 "trixie" dari ISO, menginstalnya layar demi layar, dan  
memberinya IP tetap dari MikroTik.  

## 11.1 Mengunggah ISO Debian 13

ISO yang dipakai: debian-13.7.0-amd64-netinst.iso (ukuran sekitar 800 MB, perlu internet saat instalasi).  
Jika tautan itu 404, buka folder iso-cd dan pilih berkas debian-13.x.x-amd64-netinst.iso terbaru.  
1. Di Proxmox: storage local &gt; ISO Images &gt; Download from URL.  
> Penjelasan: Proxmox mengunduh langsung dari internet, tanpa lewat laptop.
2. Tempel URL ISO, klik Query URL, lalu Download.  
> Penjelasan: Query URL memeriksa nama berkas dan ukurannya.
3. Tunggu TASK OK. ISO muncul di daftar ISO Images.  
> Penjelasan: Alternatif: Upload berkas dari laptop.

## 11.2 Membuat VM lewat wizard

Create: Virtual Machine - System / Disks / CPU / Memory  
1 VM ID / Name 201 / debian-docker  
2 OS: ISO image debian-13.7.0-amd64-netinst.iso  
3 System: Qemu Agent [x] dicentang; SCSI: VirtIO SCSI single  
4 Disks: Bus / size SCSI / 40 GiB, Discard  
5 CPU: sockets / cores / type 1 / 2 / host  
6 Memory 4096 MiB  
7 Network: bridge / model vmbr0 / VirtIO  
Back Finish  
Gambar 11.1 - Ilustrasi pengaturan VM 201 (ringkasan dari semua tab wizard).  
1. Klik Create VM. General: VM ID 201, Name debian-docker.  
> Penjelasan: ID mengikuti rencana (VM 200-299).
2. OS: pilih ISO Debian 13, Type Linux, Version 6.x - 2.6 Kernel.  
> Penjelasan: Memberi tahu Proxmox jenis sistem tamu.
3. System: biarkan default (i440fx, SeaBIOS). Centang Qemu Agent. SCSI Controller VirtIO SCSI  
single.  
> Penjelasan: Qemu Agent membuat Proxmox bisa membaca IP VM dan mematikannya dengan bersih.
4. Disks: Bus SCSI, Storage local-lvm, Disk size 40 GiB, centang Discard.  
> Penjelasan: Docker, Nextcloud, dan Git butuh ruang; 40 GiB nyaman.
5. CPU: 1 socket, 2 cores, Type host.  
> Penjelasan: Type host memberi performa lebih baik karena fitur CPU diteruskan langsung.
6. Memory: 4096 MiB (minimal 2048).  
> Penjelasan: Docker + Nextcloud + Portainer + Git membutuhkan RAM lebih banyak.
7. Network: Bridge vmbr0, Model VirtIO (paravirtualized).  
> Penjelasan: VirtIO adalah kartu jaringan tercepat untuk VM Linux.
8. Confirm: Finish. Pilih VM 201 &gt; Start &gt; Console.  

## 11.3 Menginstal Debian 13, layar demi layar

Instalasi memakai installer teks Debian (menu biru). Gunakan panah dan Enter, Tab untuk pindah tombol,  
spasi untuk mencentang.  
1. Menu awal: pilih Install (bukan Graphical Install).  
> Penjelasan: Installer teks lebih ringan dan stabil di konsol Proxmox.
2. Select a language: English (atau Indonesia). Location: Indonesia (jika tidak ada pilih "other" &gt;  
Asia &gt; Indonesia).  
> Penjelasan: Bahasa installer dan zona waktu.
3. Keymap: American English.  
> Penjelasan: Sesuai keyboard US.
4. Hostname: debian-docker. Domain name: lab.local.  
> Penjelasan: Nama server di jaringan.
5. Root password: isi password root dan ulangi.  
> Penjelasan: Jika diisi, root bisa login dan sudo tidak dipasang. Jangan dikosongkan kecuali ingin memakai
sudo.  
6. Create a user: nama lengkap, username (contoh admin), password.  
> Penjelasan: User biasa untuk SSH; login root lewat SSH ditolak secara bawaan.
7. Time zone: pilih Western Indonesia (Jakarta).  
> Penjelasan: Agar waktu log benar.
Debian GNU/Linux installer - Partition disks  
1 Partitioning method Guided - use entire disk  
2 Select disk SCSI3 (0,0,0) (sda) - 42.9 GB QEMU HARDDISK  
3 Partitioning scheme All files in one partition (recommended)  
4 Finish Finish partitioning and write changes to disk  
Go Back Continue  
Gambar 11.2 - Ilustrasi pemartisian disk Debian. Pilih urutan 1 sampai 4, lalu Yes pada konfirmasi Write the changes to  
disks.  
1. Partition disks: Guided - use entire disk &gt; pilih disk &gt; All files in one partition &gt; Finish  
partitioning &gt; Yes (Write changes).  
> Penjelasan: Pemartisian paling sederhana untuk VM. Hanya menghapus disk virtual 40 GB itu, bukan disk lain.
2. Scan another CD/DVD: No. Debian archive mirror country: Indonesia (atau negara terdekat),  
mirror deb.debian.org, HTTP proxy kosongkan.  
> Penjelasan: Mengatur sumber paket. Jika dilewati, berkas apt menyisakan baris cdrom yang menyebabkan
peringatan (lihat 11.5).  
3. Participate in the package usage survey: No.  
Debian GNU/Linux installer - Software selection  
1 Debian desktop environment [ ] (kosongkan)  
1 GNOME / Xfce / ... [ ] (kosongkan)  
web server [ ]  
2 SSH server [x] CENTANG  
3 standard system utilities [x] CENTANG  
Go Back Continue  
Gambar 11.3 - Ilustrasi Software selection. Server tidak memakai desktop. Pilih hanya (2) SSH server dan (3) standard  
system utilities.  
1. Software selection: hilangkan centang desktop environment dan GNOME. Centang SSH server  
dan standard system utilities (spasi mencentang).  
> Penjelasan: Tanpa desktop VM lebih ringan; SSH server untuk akses jarak jauh.
2. Install the GRUB boot loader: Yes &gt; pilih /dev/sda.  
> Penjelasan: GRUB adalah pemuat boot; tanpa ini VM tidak boot.
3. Installation complete: Continue. VM restart.  
> Penjelasan: Pastikan ISO tidak boot lagi (11.4).

## 11.4 Melepas ISO dan boot pertama

1. Di Proxmox: VM 201 &gt; Hardware &gt; CD/DVD Drive &gt; Edit &gt; Do not use any media &gt; OK.  
> Penjelasan: Mencegah installer berjalan lagi.
2. Jika VM kembali ke installer, Reset VM.  
3. Di Console, login root dengan password root.  
> Penjelasan: Prompt akan berakhiran #.

**TERMINAL (login sebagai root)** | Console VM 201 (root)

```
ip a
```
> Penjelasan: Mencatat IP sementara dari DHCP (contoh 192.168.88.150) dan nama kartu (ens18).
```
apt update && apt full-upgrade -y
```
> Penjelasan: Memperbarui sistem. Tanpa sudo, karena Anda sudah root.
```
apt install -y qemu-guest-agent curl nano ca-certificates
```
> Penjelasan: Memasang agen Proxmox, curl, nano, dan sertifikat.
```
systemctl enable --now qemu-guest-agent
```
> Penjelasan: Menyalakan agen sekarang dan setiap boot.
Di Proxmox, VM 201 &gt; Options &gt; QEMU Guest Agent &gt; pastikan Enabled. Setelah itu IP VM terlihat di  
tab Summary.  

## 11.5 Memperbaiki sumber apt (jika muncul peringatan cdrom)

**TERMINAL (login sebagai root)** | Console VM 201

```
grep -rn cdrom /etc/apt/
```
> Penjelasan: Mencari baris cdrom di berkas apt. Jika tidak ada hasil, lewati langkah ini.
```
nano /etc/apt/sources.list
```
> Penjelasan: Beri tanda # di awal baris yang mengandung cdrom, simpan (Ctrl+O, Enter, Ctrl+X). Jika baris ada
di /etc/apt/sources.list.d/\*.sources, edit berkas itu.  
```
apt update
```
> Penjelasan: Memastikan tidak ada lagi peringatan cdrom.

## 11.6 Memberi IP tetap lewat MikroTik

1. Proxmox: VM 201 &gt; Hardware &gt; Network Device, salin MAC (virtio=BC:24:11:...).  
2. MikroTik: buat reservasi (Bab 3.5) address 192.168.88.20, comment vm-debian-docker.  
3. Di VM: reboot (atau ifdown ens18 && ifup ens18).  
> Penjelasan: VM meminta IP lagi dan mendapat 192.168.88.20.
4. Dari laptop: ssh admin@192.168.88.20, lalu su - untuk menjadi root.  
> Penjelasan: Login root lewat SSH ditolak secara bawaan, jadi masuk sebagai user biasa lalu naik ke root.

**POWERSHELL WINDOWS** | PowerShell Windows (laptop)

```
ssh admin@192.168.88.20
```
> Penjelasan: Login SSH ke VM sebagai user biasa.

**TERMINAL (login sebagai root)** | Di dalam VM (SSH)

```
su -
```
> Penjelasan: Menjadi root. Masukkan password root. Prompt berubah menjadi #.
```
hostname -I
```
> Penjelasan: Memastikan IP VM adalah 192.168.88.20.

## 11.7 Template cloud-init (lanjutan, opsional)

Template membuat VM baru dari hasil kloning dalam hitungan detik. Gunakan image cloud resmi Debian  
13. Periksa nama berkas di cloud.debian.org/images/cloud/trixie sebelum mengunduh.  

**TERMINAL (login sebagai root)** | Shell Proxmox

```
cd /var/lib/vz/template/iso
```
> Penjelasan: Pindah ke folder ISO Proxmox.
```
URL=https://cloud.debian.org/images/cloud/trixie/latest
```
> Penjelasan: Menyimpan alamat dasar dalam variabel agar perintah berikutnya pendek.
```
wget $URL/debian-13-genericcloud-amd64.qcow2
```
> Penjelasan: Mengunduh image cloud Debian 13.
```
IMG=/var/lib/vz/template/iso/debian-13-genericcloud-amd64.qcow2
```
> Penjelasan: Menyimpan jalur image dalam variabel.
5  
# qm create 9000 --name debian13-template --memory 2048 --cores 2 --cpu host \  
 --net0 virtio,bridge=vmbr0 --scsihw virtio-scsi-pci  
> Penjelasan: Membuat VM kosong ID 9000.
```
qm set 9000 --scsi0 local-lvm:0,import-from=$IMG
```
> Penjelasan: Mengimpor image sebagai disk VM.
```
qm set 9000 --ide2 local-lvm:cloudinit
```
> Penjelasan: Menambah drive cloud-init untuk user, password, dan IP.
```
qm set 9000 --boot order=scsi0 --serial0 socket --vga serial0 --agent enabled=1
```
> Penjelasan: Mengatur boot dari disk, konsol serial, dan guest agent.
```
qm template 9000
```
> Penjelasan: Mengubah VM 9000 menjadi template (tidak bisa dinyalakan lagi, hanya dikloning).

**TERMINAL (login sebagai root)** | Shell Proxmox

```
qm clone 9000 203 --name k3s --full
```
> Penjelasan: Mengkloning template menjadi VM 203 bernama k3s.
```
qm set 203 --ciuser debian --cipassword 'GANTI_PASSWORD'
```
> Penjelasan: Mengisi user dan password lewat cloud-init.
```
qm set 203 --ipconfig0 ip=dhcp --nameserver 192.168.88.253
```
> Penjelasan: IP lewat DHCP (reservasi MikroTik akan memberi .22).
```
qm resize 203 scsi0 20G
```
> Penjelasan: Memperbesar disk menjadi 20 GB.
```
qm set 203 --memory 4096 --cores 2 && qm start 203
```
> Penjelasan: Mengatur RAM/CPU dan menyalakan VM.
CATATAN  
Image cloud tidak berisi qemu-guest-agent secara bawaan. Setelah VM hidup, jalankan apt install -y  
qemu-guest-agent seperti di 11.4.  
KASUS NYATA - VM tidak mau start: KVM tidak tersedia  
Gejala: Task Start gagal; pesan KVM virtualisation dikonfigurasi tetapi tidak tersedia.  
Penyebab: VT-x belum aktif di BIOS.  
Solusi: Aktifkan Intel Virtualization Technology di BIOS (Bab 27.5), lalu nyalakan VM. Cek ls -l /dev/kvm.  
KASUS NYATA - VM Debian sangat lambat  
Gejala: Instalasi atau boot memakan puluhan menit.  
Penyebab: RAM host penuh (swap) atau terlalu banyak VM menyala bersamaan.  
Solusi: Periksa free -m di host, pilih CPU type host, kurangi VM aktif (Bab 56).  
KASUS NYATA - sudo: command not found di VM Debian  
Gejala: Mengetik sudo apt update gagal.  
Penyebab: Debian diinstal dengan password root sehingga sudo tidak terpasang.  
Solusi: Ketik su - untuk menjadi root lalu jalankan perintah tanpa sudo (lihat Bab 1.7).
