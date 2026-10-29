# Bab 17. Folder Jaringan (Samba)

## 17.1 Ringkasan

Samba membuat folder di server tampil sebagai folder jaringan di Windows (\\192.168.88.12\share).  
Dijalankan di container LXC kecil (CT 102 files, 192.168.88.12).  

## 17.2 Instalasi

1. Buat CT 102 files (Bab 10): 1 core, 256 MB RAM, disk 8 GB, IP lewat static lease  
192.168.88.12.  
> Penjelasan: Samba sangat ringan.
2. Masuk konsol CT 102 sebagai root.  

**TERMINAL (login sebagai root)** | Console CT 102 (root)

```
apt update && apt install -y samba
```
> Penjelasan: Memasang Samba.
```
mkdir -p /srv/share
```
> Penjelasan: Membuat folder yang akan dibagikan.
```
adduser --no-create-home --disabled-password --shell /usr/sbin/nologin userfile
```
> Penjelasan: Membuat user Linux khusus untuk Samba (tanpa login shell).
```
smbpasswd -a userfile
```
> Penjelasan: Membuat password Samba untuk user itu (dimasukkan dua kali).
```
chown -R userfile:userfile /srv/share
```
> Penjelasan: Menjadikan user itu pemilik folder.
```
nano /etc/samba/smb.conf
```
> Penjelasan: Menambahkan definisi share di akhir berkas (isi di bawah).
```
systemctl restart smbd
```
> Penjelasan: Menerapkan konfigurasi.

**BERKAS: /etc/samba/smb.conf** | Tambahkan di akhir berkas

```
[share]
path = /srv/share
browseable = yes
read only = no
valid users = userfile
```

## 17.3 Memakai dari Windows

1. File Explorer &gt; This PC &gt; Map network drive.  
2. Folder: \\192.168.88.12\share, centang Connect using different credentials.  
3. Login userfile dengan password Samba.  
> Penjelasan: Drive jaringan muncul seperti disk biasa.

## 17.4 Folder di disk lain (bind mount)

**TERMINAL (login sebagai root)** | Shell Proxmox

```
pct set 102 -mp0 /mnt/data,mp=/srv/share
```
> Penjelasan: Memasang folder /mnt/data di host Proxmox ke dalam container sebagai /srv/share.
CATATAN  
Pada container unprivileged, UID di dalam dan di host berbeda (offset 100000), jadi izin folder host perlu  
disesuaikan agar user di dalam container bisa menulis.  

## 17.5 MikroTik dan backup

• Reservasi 192.168.88.12 (Bab 3.5). Tidak perlu firewall tambahan; port 445 hanya di jaringan lokal.  
• Tambahkan rewrite files.lan -&gt; 192.168.88.12 (Bab 19).  
• Backup: vzdump 102 --storage local (container) dan salin folder data penting ke disk lain.
