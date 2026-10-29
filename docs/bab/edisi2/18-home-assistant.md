# Bab 18. Home Assistant OS

## 18.1 Ringkasan

Item Isi  
Fungsi Otomasi rumah: lampu, sensor, saklar, dan perangkat pintar lainnya.  
Tempat VM sendiri di Proxmox (VM 202), alamat 192.168.88.21, web port 8123  
Sumber daya 2 core, 2 GB RAM, disk 32 GB  
Catatan Jika Proxmox mati, otomasi berhenti. Untuk tahap belajar itu aman.  
Unduh image dari halaman Releases Home Assistant OS (berkas haos_ova-VERSI.qcow2.xz). Panduan  
resmi: home-assistant.io/installation.  

## 18.2 Instalasi

**TERMINAL (login sebagai root)** | Shell Proxmox (root)

```
cd /var/lib/vz/template/iso
```
> Penjelasan: Pindah ke folder ISO Proxmox.
```
V=<VERSI>
```
> Penjelasan: Menyimpan nomor versi rilis dalam variabel (ganti dengan nomor versi terbaru).
```
URL=https://github.com/home-assistant/operating-system/releases/download/$V
```
> Penjelasan: Alamat dasar unduhan.
```
wget $URL/haos_ova-$V.qcow2.xz
```
> Penjelasan: Mengunduh image HAOS.
```
xz -d haos_ova-$V.qcow2.xz
```
> Penjelasan: Mengekstrak berkas (hasilnya haos_ova-VERSI.qcow2).

**TERMINAL (login sebagai root)** | Shell Proxmox (root)

1  
# qm create 202 --name haos --memory 2048 --cores 2 --cpu host \  
 --bios ovmf --machine q35 --ostype l26 --scsihw virtio-scsi-pci \  
 --agent enabled=1 --net0 virtio,bridge=vmbr0  
> Penjelasan: Membuat VM 202 kosong dengan UEFI (ovmf) dan jaringan VirtIO.
```
qm set 202 --efidisk0 local-lvm:1,efitype=4m,pre-enrolled-keys=0
```
> Penjelasan: Membuat disk UEFI tanpa kunci Secure Boot (wajib untuk HAOS).
```
qm importdisk 202 /var/lib/vz/template/iso/haos_ova-$V.qcow2 local-lvm
```
> Penjelasan: Mengimpor image sebagai disk VM.
```
qm config 202
```
> Penjelasan: Menampilkan konfigurasi. Cari baris unused0: local-lvm:vm-202-disk-1 (nama disk hasil
impor).  
```
qm set 202 --scsi0 local-lvm:vm-202-disk-1,discard=on,ssd=1
```
> Penjelasan: Memasang disk impor sebagai disk boot (sesuaikan nama dengan baris unused0).
```
qm set 202 --boot order=scsi0
```
> Penjelasan: Mengatur boot dari disk itu.
```
qm start 202
```
> Penjelasan: Menyalakan VM.
PERINGATAN  
HAOS tidak mau boot jika Secure Boot aktif. Opsi pre-enrolled-keys=0 memastikan hal itu.  

## 18.3 Memberi IP tetap dan membuka web

1. Proxmox: VM 202 &gt; Hardware &gt; Network Device, salin MAC address.  
2. MikroTik: reservasi 192.168.88.21, comment vm-haos (Bab 3.5).  
3. Reboot VM 202. Tunggu 5 sampai 20 menit sampai konsol  
menampilkan alamat IP.  
> Penjelasan: HAOS mengunduh komponen saat boot pertama.
4. Buka http://192.168.88.21:8123 dan ikuti onboarding: nama, akun admin, lokasi, unit.  
> Penjelasan: Perangkat di jaringan akan ditemukan otomatis.

## 18.4 Konfigurasi di Home Assistant

• Settings &gt; Devices & Services: tambahkan integrasi yang ditemukan otomatis (lampu, TV, printer,  
dan sebagainya).  
• Integrasi AdGuard Home (alamat 192.168.88.253) untuk melihat statistik dan mematikan  
pemblokiran dari HA.  
• Integrasi Tailscale, Proxmox VE (butuh API token), dan Uptime/Ping untuk memantau server.  
• Aplikasi Home Assistant di HP: Settings &gt; Companion app. Dari luar rumah akses lewat Tailscale  
(alamat 192.168.88.21).  
• Perangkat USB (dongle Zigbee/Z-Wave): VM 202 &gt; Hardware &gt; Add &gt; USB Device.  
Integrasi MikroTik (opsional)  
Integrasi MikroTik di HA memakai API router. Pada Bab 3.8 layanan api dimatikan. Aktifkan hanya untuk  
alamat HA dan buat user khusus read-only:  

**TERMINAL MIKROTIK** | WinBox &gt; New Terminal

```
/user group add name=ha-readonly policy=read,api
```
> Penjelasan: Membuat grup hak akses read-only yang boleh memakai API.
```
/user add name=hass group=ha-readonly password=GANTI_KUAT address=192.168.88.21
```
> Penjelasan: Membuat user yang hanya boleh login dari 192.168.88.21.
```
/ip service set api address=192.168.88.21/32 disabled=no
```
> Penjelasan: Mengaktifkan API hanya untuk alamat HA.
CATATAN  
Jika perintah grup ditolak karena versi RouterOS, buat grup lewat WinBox: System &gt; Users &gt; Groups, centang  
hanya read dan api.  

## 18.5 Backup

• Home Assistant: Settings &gt; System &gt; Backups &gt; Create backup; unduh berkasnya.  
• Proxmox: backup VM 202 (Bab 23).  
KASUS NYATA - HAOS tidak boot atau tidak muncul alamat IP  
Gejala: Layar tertahan di UEFI atau tidak menemukan disk.  
Penyebab: Disk belum menjadi boot device, atau efidisk memuat kunci Secure Boot.  
Solusi: Periksa qm config 202: boot: order=scsi0 dan bios: ovmf. Buat ulang efidisk dengan  
pre-enrolled-keys=0.
