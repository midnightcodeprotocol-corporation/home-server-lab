# Bab 15. Git Pribadi dengan Forgejo

## 15.1 Ringkasan

Item Isi  
Fungsi Forgejo adalah layanan Git yang dijalankan sendiri (mirip GitHub) untuk menyimpan kode,  
proyek, dan konfigurasi server.  
Tempat Docker di VM Debian 13 (192.168.88.20)  
Port Web 3000, SSH Git 2222  
Sumber daya Sekitar 200-300 MB RAM; database SQLite cukup untuk pemakaian pribadi  
Dokumentasi: forgejo.org.  

## 15.2 Instalasi

**TERMINAL (login sebagai root)** | VM Debian 13 (root)

```
mkdir -p /opt/stacks/forgejo && cd /opt/stacks/forgejo
```
> Penjelasan: Membuat folder khusus aplikasi dan masuk ke dalamnya.
```
nano compose.yaml
```
> Penjelasan: Membuat berkas compose. Isinya ada di bawah.

**BERKAS: /opt/stacks/forgejo/compose.yaml** | Ganti &lt;VERSI-MAYOR&gt; dengan versi mayor terbaru (cek halaman rilis Forgejo)

```
services:
 server:
 image: codeberg.org/forgejo/forgejo:<VERSI-MAYOR>
 container_name: forgejo
 restart: always
 environment:
 - USER_UID=1000
 - USER_GID=1000
volumes:
 - ./forgejo:/data
 - /etc/timezone:/etc/timezone:ro
 - /etc/localtime:/etc/localtime:ro
 ports:
 - "3000:3000"
 - "2222:22"
```

Baris Arti  
image: ... Image Forgejo. Pakai versi tetap (mis. 11) agar tidak berubah mendadak;  
Renovate akan mengusulkan pembaruan.  
restart: always Hidup kembali otomatis setelah reboot.  
volumes: ./forgejo:/data Seluruh data (repo, database, konfigurasi) disimpan di folder forgejo di  
samping compose.yaml.  
3000:3000 Web Forgejo di port 3000 host.  
Baris Arti  
2222:22 SSH Git di port 2222 host (port 22 host dipakai SSH VM).  

**TERMINAL (login sebagai root)** | Folder /opt/stacks/forgejo (root)

```
docker compose up -d
```
> Penjelasan: Menjalankan Forgejo di latar belakang.
```
docker compose logs -f
```
> Penjelasan: Memantau log sampai muncul pesan siap. Tekan Ctrl+C untuk berhenti melihat log.

## 15.3 Konfigurasi awal di web

Forgejo - Initial Configuration (http://192.168.88.20:3000)  
Database Type SQLite3  
Site Title Git Rumah  
1 Server Domain 192.168.88.20  
2 SSH Server Port 2222  
Forgejo HTTP Listen Port 3000  
3 Forgejo Base URL http://192.168.88.20:3000/  
4 Administrator Account admin / password / email  
Install Forgejo  
Gambar 15.1 - Ilustrasi halaman instalasi. (1) Domain = IP VM. (2) Port SSH 2222 agar alamat clone benar. (3) Base URL.  
(4) Akun administrator.  
1. Buka http://192.168.88.20:3000. Halaman instalasi awal muncul.  
> Penjelasan: Jika tidak terbuka, periksa docker compose logs.
2. Database Type: SQLite3.  
> Penjelasan: Tidak perlu server database terpisah untuk pemakaian pribadi.
3. Server Domain: 192.168.88.20 (atau git.lan setelah Bab 19). Base URL:  
http://192.168.88.20:3000/.  
> Penjelasan: Dipakai Forgejo untuk membuat tautan.
4. SSH Server Port: ubah menjadi 2222.  
> Penjelasan: Port yang benar-benar dibuka ke luar. Jika dibiarkan 22, alamat clone SSH akan salah.
5. Buka Administrator Account Settings, isi username, email, dan password. Klik Install Forgejo.  
> Penjelasan: Akun ini adalah admin pertama.

## 15.4 Repository dan kunci SSH

**POWERSHELL WINDOWS** | PowerShell (laptop)

```
ssh-keygen -t ed25519 -C "email@contoh.com"
```
> Penjelasan: Membuat pasangan kunci SSH di laptop (tekan Enter untuk semua pertanyaan).
```
type $env:USERPROFILE\.ssh\id_ed25519.pub
```
> Penjelasan: Menampilkan kunci publik untuk ditempel di Forgejo.
1. Forgejo: foto profil &gt; Settings &gt; SSH / GPG Keys &gt; Add Key, tempel isi berkas .pub.  
> Penjelasan: Memberi Forgejo kunci publik agar laptop bisa login tanpa password.
2. + &gt; New Repository: nama homelab, Create Repository.  
> Penjelasan: Repository ini dipakai untuk GitOps (Bab 21).

**TERMINAL (user biasa)** | Git Bash / PowerShell (laptop)

```
git clone ssh://git@192.168.88.20:2222/USERNAME/homelab.git
```
> Penjelasan: Menyalin repository ke laptop. Ganti USERNAME. Perhatikan port 2222.
```
cd homelab
```
> Penjelasan: Masuk ke folder repository.
```
echo "# homelab" > README.md
```
> Penjelasan: Membuat berkas pertama.
```
git add . && git commit -m "awal" && git push
```
> Penjelasan: Menyimpan dan mengirim ke Forgejo.

## 15.5 Konfigurasi di MikroTik dan jaringan

• Tidak perlu aturan firewall; akses dari jaringan lokal. Alamat 192.168.88.20 sudah direservasi.  
• Tambahkan DNS rewrite git.lan -&gt; 192.168.88.20 di AdGuard (Bab 19).  
• Akses dari luar rumah hanya lewat Tailscale (ssh://git@192.168.88.20:2222/... tetap bisa  
dipakai).  

## 15.6 Backup

**TERMINAL (login sebagai root)** | VM Debian 13 (root)

```
cd /opt/stacks/forgejo && docker compose down
```
> Penjelasan: Menghentikan Forgejo agar data konsisten.
```
tar czf /root/forgejo-backup.tgz forgejo compose.yaml
```
> Penjelasan: Mengarsipkan folder data dan compose.
```
docker compose up -d
```
> Penjelasan: Menyalakan kembali.
Selain itu, backup seluruh VM 201 lewat Proxmox (Bab 23).  
KASUS NYATA - Alamat clone SSH salah (port 22, bukan 2222)  
Gejala: Forgejo menampilkan ssh://git@host/... tanpa port sehingga clone gagal.  
Penyebab: Field SSH Server Port tidak diubah menjadi 2222 saat instalasi.  
Solusi: Edit forgejo/gitea/conf/app.ini pada bagian [server]: SSH_PORT = 2222, lalu docker  
compose restart.
