# Bab 2. Daftar Unduhan dan Alat

Semua perangkat lunak yang dipakai di buku ini beserta tautan resminya. Tautan bisa berubah; jika  
mendapat halaman 404, buka halaman induknya dan cari nama berkasnya.  

## 2.1 Sistem operasi dan ISO

Nama Fungsi Tautan  
Debian 13 (netinst, amd64) ISO instalasi VM server (Docker, k3s,  
dll)  
debian-13.7.0-amd64-netinst.iso  
Daftar rilis Debian Jika berkas di atas berganti versi, lihat  
daftarnya  
cdimage.debian.org/.../iso-cd/  
Proxmox VE ISO Server virtualisasi (unduh Proxmox VE  
9.2 atau lebih baru)  
proxmox.com/en/downloads  
Arsip ISO Proxmox Daftar langsung berkas ISO dan  
checksum  
enterprise.proxmox.com/iso/  
Image cloud Debian Untuk template cloud-init (opsional) cloud.debian.org/images/cloud/  
Home Assistant OS VM Home Assistant (berkas  
haos_ova-\*.qcow2.xz)  
github.com/home-assistant/operating-system/re  
leases  
Armbian untuk STB Image Armbian Amlogic (ophub) github.com/ophub/amlogic-s9xxx-armbian  
TrueNAS NAS (nanti, di mesin asli) truenas.com  

## 2.2 Alat di Windows

Nama Fungsi Tautan  
Rufus Membuat USB bootable dari ISO (Windows) rufus.ie  
balenaEtcher Membuat USB bootable (alternatif,  
Windows/Mac/Linux)  
etcher.balena.io  
Ventoy USB multi-ISO: salin ISO ke flashdisk tanpa  
menulis ulang  
ventoy.net  
WinBox Mengelola MikroTik mikrotik.com/download  
PuTTY SSH dari Windows chiark.greenend.org.uk/~sgtatham/putty  
WinSCP Menyalin berkas ke/dari server (SFTP) winscp.net  
Git untuk Windows Perintah git dan Git Bash git-scm.com  

## 2.3 Aplikasi server

Aplikasi Fungsi Tautan  
AdGuard Home DNS pemblokir iklan adguard.com/adguard-home  
Pi-hole Alternatif pemblokir iklan pi-hole.net  
Tailscale VPN mesh; konsol admin tailscale.com/download , admin  
Docker Engine Menjalankan container docs.docker.com/engine/install/debian  
Portainer Antarmuka web untuk Docker docs.portainer.io  
Forgejo Git pribadi forgejo.org  
Nextcloud Cloud pribadi nextcloud.com  
Home Assistant Otomasi rumah home-assistant.io  
Homepage Dashboard pintasan gethomepage.dev  
dnsdist Pembagi DNS (untuk ide balancer) dnsdist.org  
k3s Kubernetes ringan k3s.io  
Flux GitOps fluxcd.io  
Renovate Pembaruan otomatis docs.renovatebot.com  

## 2.4 Memverifikasi ISO yang diunduh

ISO yang rusak atau terpotong adalah penyebab umum instalasi gagal. Bandingkan nilai SHA256 berkas  
Anda dengan nilai yang tertulis di halaman unduhan.  

**COMMAND PROMPT WINDOWS** | Windows

```
certutil -hashfile "C:\Users\NAMA\Downloads\proxmox-ve_9.2-1.iso" SHA256
```
> Penjelasan: Menghitung sidik jari (hash) berkas. Hasilnya harus sama persis dengan SHA256 di halaman
unduhan Proxmox. Ganti jalur dan nama berkas sesuai milik Anda.
