# Bab 14. Docker dan Portainer

## 14.1 Ringkasan

Item Isi  
Fungsi Docker menjalankan aplikasi dalam wadah terisolasi. Portainer adalah antarmuka web untuk  
mengelola Docker.  
Tempat VM Debian 13 (VM 201), alamat 192.168.88.20  
Mengapa VM, bukan  
LXC  
Docker di dalam LXC sering bermasalah (izin, nesting, kernel). VM jauh lebih stabil.  
Port Portainer 9443 (HTTPS) dan 8000  

## 14.2 Instalasi Docker

Docker dipasang dari repository resmi Docker untuk Debian. Login sebagai root (su -), jadi perintah tanpa  
sudo.  

**TERMINAL (login sebagai root)** | VM Debian 13 (root)

```
apt update && apt install -y ca-certificates curl
```
> Penjelasan: Memasang paket yang dibutuhkan untuk mengunduh dan memverifikasi repository.
```
install -m 0755 -d /etc/apt/keyrings
```
> Penjelasan: Membuat folder penyimpanan kunci repository.
3  
# curl -fsSL https://download.docker.com/linux/debian/gpg \  
 -o /etc/apt/keyrings/docker.asc  
> Penjelasan: Mengunduh kunci GPG Docker untuk memverifikasi paket.
```
chmod a+r /etc/apt/keyrings/docker.asc
```
> Penjelasan: Agar kunci bisa dibaca apt.
Lalu tambahkan repository Docker dalam format .sources:  

**BERKAS: /etc/apt/sources.list.d/docker.sources** | Buat dengan: nano /etc/apt/sources.list.d/docker.sources

```
Types: deb
URIs: https://download.docker.com/linux/debian
Suites: trixie
Components: stable
Signed-By: /etc/apt/keyrings/docker.asc
```

**TERMINAL (login sebagai root)** | VM Debian 13 (root)

```
apt update
```
> Penjelasan: Memuat daftar paket Docker.
2  
# apt install -y docker-ce docker-ce-cli containerd.io \  
 docker-buildx-plugin docker-compose-plugin  
> Penjelasan: Memasang Docker Engine dan plugin Compose.
```
docker run --rm hello-world
```
> Penjelasan: Menjalankan container uji. Harus menampilkan "Hello from Docker!".
```
docker compose version
```
> Penjelasan: Memastikan plugin Compose terpasang.
CATATAN  
Karena Anda sudah root, tidak perlu menambahkan user ke grup docker. Jika ingin memakai user biasa:  
usermod -aG docker NAMAUSER lalu login ulang.  

## 14.3 Perintah Docker yang sering dipakai

Tujuan Perintah  
Container berjalan docker ps (tambah -a untuk semua)  
Lihat log docker logs -f NAMA  
Masuk ke container docker exec -it NAMA sh  
Naikkan stack docker compose up -d (di folder berisi compose.yaml)  
Turunkan stack docker compose down  
Perbarui image docker compose pull && docker compose up -d  
Bersihkan yang tak terpakai docker system prune (hati-hati)  
Biasakan satu folder per aplikasi di /opt/stacks/NAMA/compose.yaml. Dengan begitu mudah di-backup  
dan nanti diserahkan ke Git (Bab 15).  

## 14.4 Memasang Portainer

**TERMINAL (login sebagai root)** | VM Debian 13 (root)

```
docker volume create portainer_data
```
> Penjelasan: Membuat penyimpanan permanen untuk data Portainer.
2  
# docker run -d -p 8000:8000 -p 9443:9443 --name portainer --restart=always \  
 -v /var/run/docker.sock:/var/run/docker.sock \  
 -v portainer_data:/data portainer/portainer-ce:lts  
> Penjelasan: Menjalankan Portainer CE. --restart=always agar hidup kembali setelah reboot. Akses ke
docker.sock dibutuhkan agar Portainer bisa mengelola Docker.  
```
docker ps
```
> Penjelasan: Memastikan container portainer berstatus Up.
1. Buka https://192.168.88.20:9443 dan lewati peringatan sertifikat.  
> Penjelasan: Sertifikat dibuat sendiri oleh Portainer.
2. Buat user admin dengan password kuat dalam beberapa menit pertama.  
> Penjelasan: Setelah beberapa menit tanpa pendaftaran, Portainer menutup halaman ini demi keamanan (lihat
kasus di bawah).  
3. Pilih Get Started untuk mengelola Docker lokal. Menu: Containers, Images, Volumes, Networks,  
Stacks.  
> Penjelasan: Stacks adalah cara memasang aplikasi dari berkas compose.
4. Memasang aplikasi: Stacks &gt; Add stack, tempel isi compose.yaml, Deploy the stack.  
> Penjelasan: Alternatif dari terminal docker compose up -d.
Konfigurasi di MikroTik dan jaringan  
• Alamat 192.168.88.20 sudah direservasi (Bab 11.6). Tidak ada aturan firewall tambahan; akses hanya  
dari jaringan lokal.  
• Nama lokal portainer.lan dibuat di Bab 19 (DNS rewrites) lalu dipakai di dashboard.  
• Akses dari luar rumah hanya lewat Tailscale.  
Backup dan pemulihan  
• Backup VM 201 lewat Proxmox (Bab 23) mencakup Docker, Portainer, dan semua volume.  
• Data aplikasi ada di folder /opt/stacks/\* dan volume Docker (/var/lib/docker/volumes).  
KASUS NYATA - Portainer: instance timed out for security  
Gejala: Halaman meminta restart karena batas waktu pembuatan admin terlampaui.  
Penyebab: Pendaftaran admin awal ditutup bila tidak diisi dalam beberapa menit.  
Solusi: Jalankan docker restart portainer, buka lagi https://192.168.88.20:9443, dan segera buat  
admin.  
KASUS NYATA - docker: permission denied while trying to connect to the Docker daemon socket  
Gejala: Perintah docker ... ditolak.  
Penyebab: Dijalankan sebagai user biasa yang belum masuk grup docker.  
Solusi: Jadilah root (su -), atau usermod -aG docker NAMAUSER lalu login ulang.
