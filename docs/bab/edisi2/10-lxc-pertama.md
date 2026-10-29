# Bab 10. Container LXC Pertama

LXC adalah container Linux yang ringan: berbagi kernel dengan Proxmox, sehingga memakai RAM jauh  
lebih sedikit daripada VM. Cocok untuk AdGuard Home dan layanan kecil lainnya.  

## 10.1 Mengunduh template

1. Panel kiri: pilih storage local (di bawah node pve).  
> Penjelasan: Template container disimpan di storage ini.
2. Buka CT Templates &gt; Templates.  
> Penjelasan: Daftar template resmi Proxmox dan TurnKey.
3. Pilih debian-13-standard &gt; Download. Tunggu TASK OK.  
> Penjelasan: Jika gagal, hampir pasti DNS Proxmox bermasalah (Bab 9.4).

## 10.2 Membuat container

Create: LXC Container - General  
Node pve  
1 CT ID 101  
2 Hostname adguard2  
3 Unprivileged container [x] dicentang  
4 Password \*\*\*\*\*\*\*\*  
Back Next  
Gambar 10.1 - Ilustrasi tab General. (1) ID unik. (2) Nama. (3) Unprivileged lebih aman. (4) Password root container.  
1. Klik Create CT (kanan atas).  
2. General: CT ID 101, Hostname adguard2, centang Unprivileged container, isi password root.  
> Penjelasan: Unprivileged: root di dalam container bukan root di host (lebih aman).
3. Template: pilih Debian 13 yang diunduh.  
4. Disks: storage local-lvm, ukuran 4 GB.  
> Penjelasan: Cukup untuk AdGuard Home.
5. CPU: 1 core. Memory: 256 MB, swap 256 MB.  
> Penjelasan: AdGuard sangat ringan.
6. Network: Name eth0, Bridge vmbr0, IPv4 DHCP.  
> Penjelasan: IP akan diatur lewat static lease MikroTik (10.4) agar semua alamat dikelola di satu tempat.
7. DNS: biarkan "use host settings".  
8. Confirm: centang Start after created, klik Finish.  

## 10.3 Memberi IP tetap lewat MikroTik

1. Pilih CT 101 &gt; Network (atau Hardware), salin MAC address (hwaddr=BC:24:11:...).  
> Penjelasan: DHCP mengenali perangkat dari MAC ini.
2. Di MikroTik buat reservasi: lihat Bab 3.5 dengan address 192.168.88.11 dan comment  
lxc-adguard2.  
3. Restart container (CT &gt; Shutdown lalu Start).  
> Penjelasan: Agar mendapat IP baru dari reservasi.

**TERMINAL MIKROTIK** | WinBox &gt; New Terminal

```
/ip dhcp-server lease add address=192.168.88.11 mac-address=BC:24:11:AA:BB:CC
```
> Penjelasan: Reservasi IP .11 untuk MAC container. Ganti MAC sesuai milik Anda.
```
/ip dhcp-server lease set [find address=192.168.88.11] comment="lxc-adguard2"
```
> Penjelasan: Memberi komentar.

## 10.4 Masuk dan memperbarui isi container

1. Pilih CT 101 &gt; tab Console, login root dengan password dari langkah 10.2.  
> Penjelasan: Tidak perlu sudo karena sudah root.

**TERMINAL (login sebagai root)** | Console container 101

```
ip a
```
> Penjelasan: Memastikan eth0 memiliki 192.168.88.11.
```
ping -c 3 deb.debian.org
```
> Penjelasan: Memastikan internet dan DNS bekerja dari dalam container.
```
apt update && apt full-upgrade -y
```
> Penjelasan: Memperbarui paket container.
```
apt install -y curl nano
```
> Penjelasan: Memasang curl (untuk mengunduh skrip instalasi) dan nano (editor).
TIPS  
Untuk masuk lewat SSH dari laptop: ssh root@192.168.88.11. Jika ditolak, itu karena login root dengan  
password dimatikan secara bawaan. Gunakan konsol Proxmox, atau izinkan sementara dengan mengubah  
PermitRootLogin yes di /etc/ssh/sshd_config lalu systemctl restart ssh.  

## 10.5 Operasi sehari-hari

Tujuan Cara (web) Cara (Shell Proxmox)  
Start / Stop Tombol Start / Shutdown pct start 101 / pct shutdown 101  
Masuk konsol Tab Console pct enter 101  
Tujuan Cara (web) Cara (Shell Proxmox)  
Ubah RAM / CPU Resources &gt; Edit pct set 101 -memory 512 -cores 2  
Backup Backup &gt; Backup now vzdump 101 --storage local --mode  
stop  
Hapus More &gt; Remove pct destroy 101  
KASUS NYATA - Container tidak mendapat IP / tidak ada internet  
Gejala: ip a di container tidak punya alamat atau ping gagal.  
Penyebab: Bridge belum benar, DHCP tidak membalas MAC baru (WiFi), atau reservasi MikroTik belum benar.  
Solusi: Cek lease print di MikroTik, pastikan Proxmox terhubung kabel LAN ke MikroTik, atau beri IP statis  
di tab Network container (192.168.88.11/24, gateway 192.168.88.1).
