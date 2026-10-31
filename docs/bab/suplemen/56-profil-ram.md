# Bab 56. Profil Pemakaian RAM (16 GB, 24 GB, dan 32 GB)

> **Pembaruan 31 Oktober 2026.** M710q dilaporkan memakai **1×16 GB + 1×8 GB (total 24 GB)** setelah modul 8 GB pada slot pertama diganti dengan 16 GB. BIOS/OS dan MemTest86 belum dikonfirmasi. Bagian 56.1–56.6 adalah baseline konservatif 16 GB; 56.7 membahas opsi 32 GB; 56.8 memberi batas awal sementara untuk konfigurasi 24 GB. Jangan menganggap semua VM aman menyala bersamaan sebelum diukur.

PENEMPATAN - HOST - mesin fisik  
Tempat: Pengaturan di host Proxmox (skrip profil dan jadwal PBS). Tidak ada VM baru.  
Aturan: Host tetap hanya menjalankan Proxmox; skrip kecil di /root bukan aplikasi.  
Baseline konservatif 16 GB dipakai agar host tetap punya ruang untuk bekerja. Konfigurasi fisik terbaru dilaporkan 24 GB, tetapi harus diverifikasi di BIOS/Proxmox. Semua VM di buku ini bila menyala bersamaan  
membutuhkan jauh lebih banyak (Suplemen 7 Bab 48.6 dan 56.6). Solusinya bukan memaksa semuanya  
menyala, tetapi membagi VM menjadi profil: sekelompok VM yang menyala untuk satu keperluan, sementara  
yang lain dimatikan.  

## 56.1 Anggaran RAM

Bagian Perkiraan Catatan  
RAM fisik 16384 MB (16 GB)  
Host Proxmox sekitar 1 sampai 2 GB Perkiraan [BELUM PASTI]; ukur di Summary node  
Cache ZFS (bila memakai ZFS) bawaan 10% RAM, maksimum  
16 GiB  
Sekitar 1,6 GiB di mesin 16 GB. Dokumentasi  
Proxmox: pemasangan baru sejak 8.1 menetapkan  
batas ini; kolam ZFS yang dibuat belakangan atau  
instalasi lama mungkin memakai batas lain (periksa  
di bawah)  
Batas jumlah RAM VM yang menyala 12288 MB (12 GB) Sisakan sekitar 4 GB untuk host, cache, dan  
lonjakan. Angka kebijakan buku ini [BELUM PASTI]  

**TERMINAL HOST PROXMOX** | Shell node Proxmox (host), sebagai root

```
free -m
```
> Penjelasan: Melihat RAM terpakai dan tersedia. Kolom available adalah yang bisa dipakai VM baru.
```
cat /sys/module/zfs/parameters/zfs_arc_max
```
> Penjelasan: Hanya bila memakai ZFS: batas cache dalam byte (0 berarti nilai bawaan OpenZFS [BELUM PASTI]).
Berkas /etc/modprobe.d/zfs.conf menyimpan batas yang ditetapkan saat instalasi.  
PERINGATAN  
Proxmox tidak menolak menyalakan VM yang melebihi RAM. Bila jumlahnya melampaui RAM fisik, sistem  
mematikan proses (OOM) dan VM bisa terhenti mendadak. Jaga jumlah RAM VM aktif di bawah batas 56.1 dan  
pantau lewat Beszel.  

## 56.2 Daftar VM dan profilnya

Tabel memakai mode hemat (Suplemen 7 Bab 48.6): n8n, web, AFFiNE, dan musik digabung dalam VM 206  
apps, sehingga VM 208, 209, dan 211 tidak dibuat.  
VM Nama RAM (MB) Menyala pada profil  
201 docker-core 2048 harian, kerja, foto, backup, belajar  
202 haos 2048 harian, kerja, foto, backup  
205 vault 1024 semua profil  
213 sso 1024 semua profil  
207 nextcloud 2048 harian, kerja, backup  
204 git 1024 kerja, belajar  
206 apps (n8n, web, AFFiNE, musik) 3072 kerja  
VM Nama RAM (MB) Menyala pada profil  
203 k3s 3072 belajar  
214 immich 6144 (4096 tanpa ML) foto  
212 pbs 2048 backup  
210 web-public 768 opsional; tambahkan ke profil mana  
pun bila situs publik perlu hidup  
Profil VM yang menyala Jumlah RAM Keperluan  
harian 201, 202, 205, 207, 213 8192 MB (8,0 GB) Pemakaian sehari-hari: dashboard,  
rumah pintar, kata sandi, SSO,  
berkas  
kerja harian + 204, 206 12288 MB (12,0 GB) Git, AFFiNE, n8n, situs web, musik  
foto 201, 202, 205, 213, 214 12288 MB (12,0 GB) Cadangan dan pencarian foto  
(Immich); Nextcloud dimatikan  
backup harian + 212 10240 MB (10,0 GB) Malam hari saat PBS  
mencadangkan  
belajar 201, 203, 204, 205, 213 8192 MB (8,0 GB) Latihan Kubernetes dan GitOps  
Dengan Immich 4096 MB (machine learning mati), profil foto menjadi 10240 MB. Menambahkan VM 210  
web-public (768 MB) ke profil harian menghasilkan 8960 MB. Semua angka RAM VM adalah perkiraan [BELUM  
PASTI]; sesuaikan setelah mengukur dengan Beszel.  

## 56.3 Skrip pergantian profil

Skrip kecil di host Proxmox mematikan VM yang tidak termasuk profil dan menyalakan yang termasuk. Ia hanya  
memakai perintah qm bawaan dan tidak memasang aplikasi.  

**TERMINAL HOST PROXMOX** | Shell node Proxmox (host), sebagai root

```
nano /root/profil.sh
```
> Penjelasan: Isi seperti kotak di bawah.
```
chmod 700 /root/profil.sh
```
> Penjelasan: Hanya root yang boleh menjalankan.

**/root/profil.sh** | Isi berkas

```
#!/bin/bash
# Ganti profil pemakaian. Pakai: profil.sh harian|kerja|foto|backup|belajar
ALL="201 202 203 204 205 206 207 210 212 213 214"
case "${1:-}" in
 harian) ON="201 202 205 207 213" ;;
 kerja) ON="201 202 205 207 213 204 206" ;;
 foto) ON="201 202 205 213 214" ;;
 backup) ON="201 202 205 207 213 212" ;;
 belajar) ON="201 203 204 205 213" ;;
 *) echo "pakai: $0 harian|kerja|foto|backup|belajar"; exit 1 ;;
esac
if pgrep -f vzdump >/dev/null; then
 echo "vzdump masih berjalan; ditunda"; exit 1
fi
for id in $ALL; do
 case " $ON " in *" $id "*) continue ;; esac
 if qm status "$id" 2>/dev/null | grep -q running; then
 qm shutdown "$id" --timeout 120
 fi
done
for id in $ON; do
 if ! qm status "$id" 2>/dev/null | grep -q running; then
 qm start "$id"
 fi
done
qm list
```

Bagian Fungsi  
ALL Semua VM yang diatur skrip (ganti bila nomor VM Anda berbeda atau ada VM  
tambahan)  
ON Daftar VM yang harus menyala pada profil itu  
pgrep -f vzdump Menolak berganti profil selagi backup berjalan agar PBS tidak dimatikan di tengah  
jalan [BELUM PASTI]  
qm shutdown ... --timeout 120 Mematikan dengan bersih; menunggu sampai 120 detik  
2&gt;/dev/null Menyembunyikan galat untuk VM yang belum dibuat (misalnya 206 bila Anda  
belum memakai mode hemat)  

**TERMINAL HOST PROXMOX** | Shell node Proxmox (host), sebagai root

```
/root/profil.sh foto
```
> Penjelasan: Contoh: beralih ke profil foto. Pantau Tasks di web Proxmox; Immich butuh beberapa menit untuk
siap.  
```
free -m
```
> Penjelasan: Memastikan RAM tersedia masih cukup setelah berganti profil.

## 56.4 Hanya VM harian yang menyala otomatis

Saat host dinyalakan ulang, VM yang diberi --onboot 1 ikut menyala. Pada mesin 16 GB hanya VM profil harian  
yang boleh begitu.  

**TERMINAL HOST PROXMOX** | Shell node Proxmox (host), sebagai root

```
for id in 201 202 205 207 213; do qm set $id --onboot 1; done
```
> Penjelasan: Menyalakan otomatis lima VM profil harian.
```
for id in 203 204 206 210 212 214; do qm set $id --onboot 0; done
```
> Penjelasan: Mematikan penyalaan otomatis VM lain. Abaikan galat untuk nomor yang belum dibuat.
```
qm config 214 | grep onboot
```
> Penjelasan: Memeriksa satu VM (onboot: 0 berarti tidak otomatis).
CATATAN  
AdGuard kedua (CT101) dan Samba (CT102) berupa LXC kecil (Edisi 2) dan tetap menyala otomatis. Atur urutan  
nyala di Start/Shutdown order sesuai Edisi 2 Bab 23.  

## 56.5 PBS dan backup malam hari

Backup terjadwal berjalan pukul 02:00 (Suplemen 7 Bab 50.10) dan membutuhkan VM pbs menyala. Di mesin 16  
GB pbs tidak menyala sepanjang hari, jadi ganti profil sebelum dan sesudah backup memakai cron di host.  

**TERMINAL HOST PROXMOX** | Shell node Proxmox (host), sebagai root

```
crontab -e
```
> Penjelasan: Membuka jadwal root; tambahkan dua baris di bawah.

**crontab (host Proxmox)** | Isi berkas

```
45 1 * * * /root/profil.sh backup
30 6 * * * /root/profil.sh harian
```

Baris Arti  
45 1 \* \* \* Pukul 01:45 beralih ke profil backup (PBS menyala; VM kerja atau foto dimatikan)  
30 6 \* \* \* Pukul 06:30 kembali ke profil harian (PBS dimatikan)  
PERINGATAN  
Pantau durasi backup di Tasks selama beberapa malam sebelum mengandalkan jam ini. Backup pertama (terutama  
disk foto Immich) bisa jauh lebih lama dari jeda 02:00 sampai 06:30. Skrip menolak berganti profil selagi vzdump  
berjalan, tetapi bila backup belum selesai pukul 06:30 profil harian tidak akan terpasang sampai Anda menjalankannya  
lagi. Prune, garbage collection, dan verifikasi PBS (Bab 50.10) harus dijadwalkan sebelum PBS dimatikan; sesuaikan  
jamnya atau jalankan manual [BELUM PASTI].  

## 56.6 Saat RAM naik

Jumlah RAM VM bila semuanya menyala (mode terpisah penuh, tanpa mode hemat), menurut tabel Suplemen 7  
Bab 48.6 ditambah VM 213 dan 214:  
Konfigurasi RAM VM (MB) RAM VM (GB) Dengan 16 GB  
VM 201 dan 204 sampai 214, terpisah penuh 22272 21,8 Tidak muat  
Ditambah HAOS (2048) dan k3s (3072 sampai 4096) 27392 sampai 28416 26,8 sampai 27,8 Tidak muat  
Mode hemat (apps 3072 menggantikan 206, 208, 209, 211) 19200 18,8 Tidak muat  
Mode hemat ditambah HAOS dan k3s 24320 sampai 25344 23,8 sampai 24,8 Tidak muat  
Dari tabel ini: 32 GB cukup untuk menyalakan hampir semuanya sekaligus dalam mode hemat, dan terpisah  
penuh hanya pas dengan sisa sangat tipis [BELUM PASTI]. Saat RAM ditambah, langkahnya: (1) pasang RAM  
dan periksa free -m; (2) naikkan RAM VM yang terasa sempit (qm set ID --memory ...); (3) ubah profil menjadi  
lebih besar atau berhenti memakai skrip; (4) atur --onboot 1 untuk VM yang kini boleh menyala otomatis; (5)  
perbarui batas ZFS bila perlu (56.1).

## 56.7 Jika RAM ditingkatkan menjadi 32 GB (16 + 16)

Jika tersedia modul 16 GB yang kompatibel, ganti modul 8 GB dengan modul 16 GB (Bab 27.1), uji MemTest86, lalu periksa dengan `free -m` di host (total sekitar 32.000 MB). Ini rencana masa depan, bukan kondisi saat ini.

| Konfigurasi | RAM VM (MB) | Sisa dari 32.768 MB |
|---|---|---|
| Mode hemat (apps menggantikan 206, 208, 209, 211) + HAOS + k3s | 24.320 sampai 25.344 | sekitar 7,4 sampai 8,4 GB (untuk host dan lonjakan) |
| Terpisah penuh + HAOS + k3s | 27.392 sampai 28.416 | sekitar 4,3 sampai 5,4 GB (pas-pasan) |

Mode hemat dapat dipertimbangkan setelah hasil pemantauan memastikan sisa RAM host cukup. Jangan menyalakan semua VM hanya karena kapasitas teoritis tampak cukup. Langkah penyalaan otomatis di bawah ini baru diterapkan setelah VM masing-masing diuji:

1. Atur penyalaan otomatis untuk semua VM yang dipakai: `for id in 201 202 204 205 206 207 212 213 214; do qm set $id --onboot 1; done` (sesuaikan daftar dengan VM yang sudah dibuat; abaikan galat untuk nomor yang belum ada). Biarkan `203` (k3s) dan `210` (web-public) sesuai kebutuhan.
2. PBS (VM 212) boleh menyala terus; cron `profil.sh backup` dan `profil.sh harian` di 56.5 tidak diperlukan lagi.
3. Skrip `profil.sh` tetap berguna untuk sesi latihan: `belajar` mematikan layanan yang tidak dipakai sehingga CPU dan RAM lebih lega.
4. **Batas berikutnya adalah CPU**: i5-6500T hanya 4 thread. Jangan memberi banyak core ke setiap VM; mulai 1-2 core. Impor foto pertama di Immich dan machine learning akan memakan CPU lama; jalankan saat tidak sibuk.
5. Pantau di Beszel (Bab 33): RAM terpakai, beban CPU, suhu, dan ruang NVMe/HDD. Naikkan RAM VM hanya bila terbukti perlu.

## 56.8 Batas sementara untuk konfigurasi 24 GB (16 + 8)

Kapasitas 24 GB dilaporkan dari susunan 16 GB + 8 GB, tetapi belum dicatat dari BIOS atau hasil MemTest86. Setelah instalasi Proxmox, konfirmasi kapasitas dengan `free -h` dan catat konsumsi host saat tidak ada VM aktif.

Sampai ada hasil pengukuran, gunakan profil konservatif 16 GB di Bagian 56.1–56.5. Setelah itu, naikkan alokasi VM sedikit demi sedikit; jangan melebihi total alokasi 18 GB untuk VM yang aktif sebelum pemantauan membuktikan host tetap memiliki setidaknya 4–6 GB tersedia saat beban normal. Profil mode hemat yang menyalakan VM dengan total sekitar 19,2 GB atau lebih belum cocok untuk dijalankan serentak pada 24 GB tanpa pengukuran.

Jika RAM tersedia terus rendah, ballooning/oom muncul, atau VM tersendat, matikan guest yang tidak diperlukan dan kembali ke profil 16 GB. Catat profil yang dipakai serta nilai RAM available di `catatan/hasil-uji.md`.
