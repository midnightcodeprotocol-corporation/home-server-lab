# Panduan Lengkap Home Server Lab

## Edisi Terpadu 1.0 · 30 Oktober 2026

Panduan pemula untuk membangun, mengamankan, memakai, merawat, dan memulihkan home server berbasis Lenovo ThinkCentre M710q dan Proxmox VE.

> **Status penting:** panduan ini mengikuti keadaan proyek terakhir yang tercatat. Jaringan rumah sudah berjalan. Proxmox belum dipasang. VM/LXC, backup, Tailscale, dan layanan aplikasi di bab-bab berikut masih rancangan sampai Anda sendiri menguji dan mencatat hasilnya. Panduan ini tidak mengubah server Anda.

## Cara membaca buku ini

Mulai dari Bab 1 dan ikuti fase secara berurutan. Jangan melompat ke bab aplikasi sebelum jaringan, akses admin, storage, dan pemulihan dasar beres. Kerjakan satu tindakan, periksa hasilnya, lalu lanjutkan. Jika hasil berbeda dari panduan, berhenti dan catat pesan yang muncul; jangan menebak perbaikan.

Di buku ini:

- **SUDAH BERJALAN** berarti dicatat sudah berfungsi pada jaringan rumah.
- **RENCANA** berarti belum dipasang atau belum dipastikan.
- **[BELUM PASTI]** berarti cocokkan dengan perangkat, versi perangkat lunak, atau layar Anda.
- **PERHATIAN DATA** berarti tindakan dapat menghapus atau membuat data tidak dapat diakses.
- Perintah Linux diberi label mesin tujuan dan pengguna yang menjalankannya. Di host Proxmox, login sebagai `root`; di VM Debian, gunakan akun biasa lalu `su -` bila perlu. Jangan menambahkan `sudo` pada perintah yang sudah berjalan sebagai `root`.
- Perintah dalam satu blok ditujukan untuk satu terminal. Jangan menyalin tanda `$` atau `#` di awal baris.

Setiap fase mempunyai tiga bagian: tujuan, langkah, dan syarat lulus. Simpan hasil di `catatan/hasil-uji.md`. Jika meminta bantuan, kirim nama fase, perangkat yang dipakai, langkah terakhir, dan pesan error persis. Jangan kirim password, token, private key, cookie, atau kode pemulihan.

## Daftar isi

1. Mengenal proyek dan cara kerja server
2. Jaringan rumah dan gambaran topologi
3. Akun, akses, dan dasar keamanan
4. Persiapan ThinkCentre dan pemeriksaan perangkat
5. Memasang Proxmox VE di M710q
6. Pengaturan pertama Proxmox
7. Storage, HDD 2 TB, dan perencanaan ruang
8. Membuat VM/LXC dengan aman
9. Docker Compose, reverse proxy, dan aplikasi
10. Akses dari luar rumah dengan Tailscale
11. Backup dan uji restore
12. Monitoring, pemeliharaan, dan pemulihan gangguan
13. Layanan yang bermanfaat dan urutan penerapan
14. Daftar periksa penerimaan proyek
Lampiran A. Peta IP dan guest
Lampiran B. Perintah yang sering dipakai
Lampiran C. Glosarium singkat
Lampiran D. Rujukan resmi

## 1. Mengenal proyek dan cara kerja server

### 1.1 Apa yang sedang dibangun?

Home server adalah komputer yang menyala di rumah dan menyediakan layanan untuk perangkat Anda. Proxmox VE adalah lapisan virtualisasi yang membagi komputer fisik menjadi beberapa komputer virtual (VM) dan container (LXC). Layanan seperti file sharing, dashboard, otomasi, foto, atau musik berjalan di dalam guest tersebut.

Host Proxmox sebaiknya tetap sederhana: hanya menjalankan hypervisor, pengelolaan storage, jaringan virtual, dan backup. Jangan memasang Docker atau aplikasi umum langsung di host. Jika sebuah aplikasi rusak, pemisahan per guest membuat pemulihan lebih mudah.

### 1.2 Keadaan nyata dan target

| Bagian | Keadaan terakhir yang tercatat | Target |
|---|---|---|
| Router | MikroTik RB750GL di `192.168.88.1/24` | Gateway, DHCP, firewall rumah |
| Wi-Fi/AP | TL-WR820N di `.2` | Access point; DHCP AP dimatikan |
| DNS | AdGuard Home di STB HG680 `.253` | DNS utama; AdGuard kedua kelak sebagai cadangan |
| Server | M710q, i5-6500T, RAM 16 GB, NVMe 500 GB | Proxmox diinstal langsung ke NVMe |
| HDD | Dua Seagate Surveillance 2 TB, 3,5 inci; enclosure single-bay tersedia | Mulai dengan satu drive setelah identitas dan kondisi dicek |
| Akses jauh | Belum diterapkan | Tailscale dengan akses admin terbatas |
| Aplikasi/backup | Belum berjalan di server | Dipilih bertahap; backup baru dianggap siap setelah restore berhasil |

Diagram memperlihatkan jaringan yang sudah ada dan server yang masih menjadi target.

[[ILUSTRASI:JARINGAN]]

**Cara membaca:** garis penuh menunjukkan jalur jaringan rumah yang dicatat sudah berjalan. Kotak bertanda target menunjukkan rencana. Cloudflare Tunnel hanya opsi untuk situs statis publik; bukan untuk membuka panel admin. Tidak ada port-forward admin yang direncanakan.

### 1.3 Istilah yang akan sering muncul

- **Host:** komputer fisik yang menjalankan Proxmox.
- **VM:** komputer virtual lengkap dengan kernel sendiri. Cocok untuk Docker, Home Assistant OS, PBS, dan layanan yang butuh batas isolasi lebih kuat.
- **LXC:** container Linux ringan yang berbagi kernel host. Cocok untuk layanan Linux sederhana setelah Anda memahami izin dan backup container.
- **Guest:** istilah umum untuk VM atau LXC.
- **IP statis:** alamat tetap yang tidak berubah setiap kali perangkat tersambung.
- **Gateway:** router yang mengantar paket dari jaringan lokal ke jaringan lain.
- **DNS:** layanan yang menerjemahkan nama seperti `contoh.home.arpa` menjadi alamat IP.
- **Reverse proxy:** pintu depan HTTPS yang meneruskan permintaan ke aplikasi yang benar.
- **Snapshot:** titik keadaan sementara. Snapshot di disk yang sama bukan backup.
- **Backup:** salinan yang bisa dipakai memulihkan data/guest. Backup belum terbukti sebelum restore diuji.

## 2. Jaringan rumah dan gambaran topologi

### 2.1 Jalur koneksi yang dicatat

Internet IndiHome hanya tersedia melalui Wi-Fi. TL-WR840N menerima Wi-Fi dalam mode WISP dan mengirim koneksi Ethernet ke MikroTik. MikroTik membuat LAN rumah `192.168.88.0/24`; AP dan switch membawa jaringan itu ke perangkat.

[[ILUSTRASI:ALUR]]

| Perangkat | Peran | Alamat yang dicatat |
|---|---|---:|
| TL-WR840N v6.20 | Penerima WISP; jaringan uplink | `192.168.0.1` |
| MikroTik RB750GL | Router utama | `192.168.88.1` |
| TL-WR820N | Access point | `192.168.88.2` |
| STB HG680 | Armbian + AdGuard Home utama | `192.168.88.253` |
| Laptop admin | Windows, adaptor USB-LAN | `192.168.88.252` |
| ThinkCentre M710q | Rencana host Proxmox | `192.168.88.10` |

Alamat pada tabel merupakan catatan proyek. Sebelum menetapkan perangkat baru, periksa tabel lease DHCP MikroTik agar tidak ada alamat yang sudah digunakan. Alamat server yang direncanakan berada di luar pool DHCP `.100–.254`.

### 2.2 DNS lokal dan nama layanan

AdGuard Home di STB HG680 `.253` adalah DNS utama yang tercatat. Nama lokal memakai domain khusus `home.arpa`; jangan menggunakan `.local` untuk nama layanan karena dapat berbenturan dengan mDNS. Caddy direncanakan menerima HTTPS pada VM 201 (`192.168.88.20`) dan mengirim permintaan ke aplikasi internal.

Contoh alur:

1. Laptop meminta alamat `dashboard.home.arpa` ke AdGuard.
2. DNS lokal menjawab `192.168.88.20`.
3. Browser membuka `https://dashboard.home.arpa`.
4. Caddy memilih aplikasi berdasarkan nama host dan meneruskan permintaan ke port internalnya.

Jika DNS belum siap, gunakan alamat IP hanya untuk pemeriksaan sementara. Jangan membuat aturan port-forward di router agar panel Proxmox dapat dibuka dari internet.

### 2.3 Pemeriksaan dasar dari Windows

Buka PowerShell di laptop yang tersambung ke Wi-Fi rumah atau Ethernet MikroTik.

```powershell
ipconfig
```

Temukan adapter yang aktif. Catat IPv4 dan Default Gateway. Gateway klien yang benar biasanya `192.168.88.1`. Jika laptop mendapat alamat `192.168.0.x`, ia mungkin tersambung ke jaringan uplink yang berbeda, bukan LAN MikroTik.

```powershell
Test-NetConnection 192.168.88.1
```

Ini memeriksa konektivitas TCP dasar ke router. Hasil gagal belum tentu berarti router mati; pastikan kabel, Wi-Fi, adapter, dan alamat berada pada subnet yang sama.

## 3. Akun, akses, dan dasar keamanan

### 3.1 Amankan identitas sebelum memasang server

1. Aktifkan MFA/passkey pada akun email utama, GitHub, dan Tailscale jika digunakan.
2. Simpan kode pemulihan secara offline atau di password manager yang sudah dilindungi.
3. Gunakan password unik dan panjang untuk router, Proxmox, dan aplikasi.
4. Hapus anggota tailnet atau akun yang tidak lagi dipakai.
5. Simpan rahasia di Vaultwarden atau password manager tepercaya; jangan menaruhnya di GitHub, README, screenshot, atau chat.

### 3.2 Aturan jaringan sederhana

- Jangan expose `8006` (Proxmox), `22` (SSH), `8291` (WinBox), database, atau Docker socket ke internet.
- Matikan UPnP bila tidak dibutuhkan dan tinjau aturan port-forward pada router.
- Akses jarak jauh admin direncanakan melalui Tailscale, bukan port-forward.
- Bedakan layanan privat (hanya pemilik/perangkat yang diizinkan) dan publik (dapat dibuka siapa pun di internet).
- Jika membuat aturan firewall, pastikan Anda punya akses konsol lokal dan catatan cara membatalkannya sebelum menekan Apply.
- Jangan menyalakan layanan publik sebelum memahami autentikasi, patch, backup, log, dan batas jaringan.

### 3.3 Kebijakan Tailscale proyek

Repo memiliki contoh kebijakan di `konfigurasi/tailscale-policy.hujson`. Contoh itu memakai grup `group:home-admins`, tetapi email masih berupa placeholder. Ganti dengan akun Tailscale admin yang benar sebelum digunakan. Baca seluruh kebijakan yang sudah ada di admin console, uji dengan fitur preview/policy tests, dan hindari menimpa aturan lain.

Kebijakan Tailscale mengatur akses antardevice di tailnet; ia tidak otomatis menjadi firewall seluruh LAN. Subnet route harus diiklankan dan disetujui, lalu diuji. Tailscale saat ini merekomendasikan `grants` untuk aturan baru; repo menggunakan `grants`. Batasi port dan tujuan secukupnya, jangan memberi akses lebih luas dari kebutuhan.

### 3.4 SSH dari Windows dengan aman

SSH adalah terminal jarak jauh. Untuk mengelola Proxmox, UI web biasanya lebih mudah; SSH dipakai hanya saat perlu. Jangan izinkan SSH dari internet.

Di PowerShell laptop admin, buat pasangan kunci:

```powershell
ssh-keygen -t ed25519 -C "home-server-admin"
```

Ikuti pertanyaan penyimpanan file. Kunci privat `id_ed25519` tetap di laptop dan jangan pernah dikirim. Kunci publik berakhiran `.pub` boleh dipasang pada akun server. Lindungi kunci privat dengan passphrase.

Saat koneksi pertama, pastikan IP server memang benar melalui jaringan lokal dan console fisik. Kemudian:

```powershell
ssh root@192.168.88.10
```

Perintah ini hanya untuk memastikan jalur SSH berjalan; jangan jadikan root/password sebagai akses harian tanpa rencana akun yang lebih aman. Jangan menonaktifkan password login atau root sebelum login dengan kunci berhasil diuji pada sesi kedua dan Anda masih punya jalur console lokal. Jika identitas host berubah setelah instal ulang, jangan langsung menerima fingerprint baru sebelum memastikan host memang diinstal ulang.

## 4. Persiapan ThinkCentre dan pemeriksaan perangkat

### 4.1 Cadangkan dan inventaris sebelum mengubah apa pun

Instalasi Proxmox akan menghapus disk target. Jika NVMe M710q masih berisi file yang dibutuhkan, salin ke perangkat lain dan buka beberapa file hasil salinan untuk memastikan backup dapat dibaca. Cabut HDD 2 TB dari komputer selama instalasi agar tidak salah pilih disk.

Catat model CPU, RAM tiap modul, model NVMe, dan kondisi HDD. Nomor serial dicatat lokal saja, jangan commit ke GitHub.

```powershell
Get-CimInstance Win32_Processor | Select-Object Name,NumberOfCores,NumberOfLogicalProcessors
```

```powershell
Get-CimInstance Win32_PhysicalMemory | Select-Object Capacity,Speed,Manufacturer
```

```powershell
Get-PhysicalDisk | Select-Object FriendlyName,MediaType,Size,HealthStatus
```

### 4.2 RAM: pasang, lalu uji

M710q memiliki dua slot SO-DIMM menurut inventaris proyek. Saat ini RAM 16 GB terpasang, dengan modul cadangan 16 GB dan 8 GB. Target yang direncanakan adalah 32 GB memakai pasangan yang cocok. Jangan menganggap dua modul kompatibel hanya karena bentuknya sama; periksa tipe, tegangan, kapasitas, dan dukungan model.

1. Matikan komputer sepenuhnya dan cabut adaptor daya.
2. Pasang modul sesuai panduan hardware Lenovo untuk varian unit Anda. Jangan paksa pengunci slot.
3. Nyalakan, masuk BIOS, lalu pastikan total RAM terbaca.
4. Jalankan MemTest86 dari USB setidaknya 1–2 putaran penuh tanpa error.
5. Jika muncul satu error pun, matikan dan uji modul satu per satu. Jangan instal hypervisor pada RAM yang gagal.

**PERHATIAN:** buka casing hanya saat perangkat terputus dari listrik. Menu dan urutan modul dapat berbeda; cocokkan dengan panduan servis Lenovo untuk machine type unit Anda.

### 4.3 Pemeriksaan kesehatan mesin

Periksa kipas, debu, adaptor daya, port Ethernet, tombol power, dan output HDMI. Jalankan diagnostik RAM. Periksa SMART NVMe menggunakan alat yang dapat membaca NVMe. HDD baru jangan dinilai hanya dari fakta bahwa Windows menampilkan atau tidak menampilkan partisi; disk tanpa partisi dapat tidak muncul di File Explorer.

### 4.4 BIOS/UEFI

Masuk BIOS M710q dengan menekan F1 saat logo Lenovo. Boot menu satu kali biasanya F12. Nama menu berbeda antarversi firmware **[BELUM PASTI]**. Cari pengaturan virtualization dan nyalakan Intel VT-x. VT-d boleh dinyalakan untuk kebutuhan passthrough di masa depan. Periksa mode boot dan urutan disk. Jangan mengubah opsi yang tidak dipahami.

Untuk Wake-on-LAN dan pemulihan setelah listrik padam, atur hanya setelah Proxmox stabil dan uji fungsi fisiknya. Simpan catatan nilai awal agar perubahan dapat dibatalkan. Secure Boot, AHCI, dan BIOS update harus dicocokkan dengan versi firmware dan installer resmi saat pelaksanaan.

## 5. Memasang Proxmox VE di M710q

### 5.1 Persiapan

Siapkan: M710q, monitor dan keyboard sementara, kabel LAN ke jaringan MikroTik, flashdisk kosong yang isinya boleh dihapus, laptop Windows, dan password root yang disimpan aman.

Unduh ISO Proxmox VE dari situs resmi Proxmox. Catat versinya dan bandingkan SHA-256 yang tercantum di halaman unduhan.

```powershell
Get-FileHash -Algorithm SHA256 "$env:USERPROFILE\Downloads\NAMA-FILE-ISO.iso"
```

Ganti `NAMA-FILE-ISO.iso` dengan nama file sebenarnya. Bila hash berbeda satu karakter pun, jangan gunakan file itu; unduh ulang.

### 5.2 Buat USB installer di Windows

Gunakan alat penulis image USB yang mendukung mode image mentah. Memilih perangkat USB yang salah akan menghapus datanya.

1. Colok flashdisk, lalu pastikan nama dan kapasitasnya benar.
2. Pilih ISO Proxmox yang hash-nya sudah cocok.
3. Tulis image. Jika diminta memilih mode ISO atau DD, pilih mode DD untuk image Proxmox.
4. Tunggu sampai selesai; keluarkan USB dengan aman.

### 5.3 Pastikan nilai jaringan sebelum instal

| Isian installer | Nilai rancangan |
|---|---|
| Hostname | Belum diputuskan final. Catatan lama memakai `pve.lab.local`; jangan anggap nilai itu final |
| IP/CIDR | `192.168.88.10/24` |
| Gateway | `192.168.88.1` |
| DNS | `192.168.88.253` jika AdGuard sedang sehat; bila tidak, gunakan resolver yang dapat dijangkau dan catat perubahan |
| Zona waktu | `Asia/Jakarta` |
| Disk target | NVMe 500 GB M710q yang sudah dipastikan lewat model/kapasitas |
| Filesystem | ext4 untuk rencana satu NVMe; jangan pilih ZFS mirror pada satu disk |

**[BELUM PASTI]** Repo belum mencatat hostname final yang disepakati. `pve.lab.local` adalah nilai lama; layanan memakai `home.arpa`. Tentukan satu FQDN sebelum instalasi dan tulis pilihan itu di status proyek. Jangan mengarang hostname saat layar installer muncul.

### 5.4 Jalankan installer dengan pemeriksaan dua kali

**PERHATIAN DATA — PENGHAPUSAN DISK.** Installer menghapus disk target. Jangan lanjut sebelum file penting sudah dibackup, drive target terlihat sebagai NVMe 500 GB, dan HDD data sudah dilepas.

1. Sambungkan M710q ke LAN memakai kabel Ethernet.
2. Nyalakan dan tekan F12 berulang kali. Pilih USB dengan awalan UEFI jika tersedia.
3. Pilih installer Proxmox VE. Jika layar grafis bermasalah, coba mode terminal installer.
4. Terima lisensi, pilih NVMe 500 GB, lalu pastikan kapasitas dan model disk sebelum melanjutkan.
5. Pilih zona waktu `Asia/Jakarta` dan keyboard yang sesuai.
6. Buat password root yang panjang dan isi email admin yang benar.
7. Pilih kartu Ethernet yang kabelnya terhubung. Isi IP, prefix `/24`, gateway, DNS dan hostname yang sudah ditentukan.
8. Di layar ringkasan, baca ulang setiap baris. Bila disk atau IP salah, kembali dan perbaiki.
9. Mulai instalasi. Setelah restart, cabut USB agar mesin boot dari NVMe.

Jangan menjalankan perintah format atau wipe dari terminal sebagai cara memperbaiki installer. Jika installer gagal, catat teks error dan berhenti.

### 5.5 Masuk pertama kali

Dari laptop di jaringan rumah, buka `https://192.168.88.10:8006`. Sertifikat awal mungkin self-signed; pastikan alamat dan jaringan benar sebelum melanjutkan. Login `root`, realm `Linux PAM standard authentication`, lalu password yang dibuat di installer.

Syarat lulus fase:

- halaman Proxmox dapat dibuka dari LAN admin;
- IP `192.168.88.10/24` dan gateway `192.168.88.1` benar;
- NVMe, CPU, dan RAM terlihat sesuai;
- tidak ada HDD data yang tanpa sengaja menjadi target instalasi.

## 6. Pengaturan pertama Proxmox

### 6.1 Konfirmasi jaringan dan nama host

Di Proxmox pilih node `pve`, lalu periksa System > Network dan DNS. Cocokkan IP, bridge, interface fisik, gateway, dan `/etc/hosts` dengan keadaan aktual. Jangan mengubah konfigurasi jaringan lewat editor tanpa akses konsol lokal dan catatan pemulihan.

Perintah baca-saja dari Shell Proxmox:

```bash
pveversion
```

```bash
ip -br address
```

```bash
ip route
```

```bash
lsblk -o NAME,SIZE,TYPE,MODEL
```

```bash
free -h
```

Jika perintah baca-saja menunjukkan nilai yang tidak sesuai, jangan lanjut ke pembuatan VM.

### 6.2 Update dan repository

Nama menu dan repositori Proxmox berubah antarversi. Gunakan panel Updates/Repositories pada versi yang benar-benar terpasang, baca panduan resmi untuk versi itu, lalu periksa bahwa sumber enterprise/no-subscription sesuai hak penggunaan. Jangan menyalin baris repo lama dari buku, forum, atau video tanpa mencocokkan versi Debian dan Proxmox.

Sebelum pembaruan besar:

1. Pastikan koneksi internet, DNS, dan ruang disk cukup.
2. Simpan backup guest penting.
3. Baca daftar paket yang akan diperbarui.
4. Jalankan pembaruan dari antarmuka atau prosedur resmi versi terpasang.
5. Reboot hanya jika diminta dan pastikan host kembali dapat diakses.

### 6.3 Akun admin dan autentikasi

Sesudah akses root awal berhasil, buat akun admin bernama sendiri sesuai dokumentasi Proxmox yang sesuai versi. Aktifkan faktor kedua (misalnya TOTP atau WebAuthn) dan simpan recovery code dengan aman. Uji login akun baru sebelum mengurangi penggunaan root.

### 6.4 Firewall

Firewall yang salah dapat mengunci Anda keluar. Sebelum mengaktifkan aturan:

1. Pastikan punya akses monitor/keyboard ke M710q.
2. Simpan ekspor atau catatan konfigurasi saat ini.
3. Tentukan perangkat admin yang harus tetap dapat masuk ke TCP 8006 dan SSH.
4. Aktifkan kebijakan bertahap, uji dari laptop, lalu uji bahwa guest biasa tidak dapat membuka panel admin.
5. Jangan memberi akses internet langsung ke panel admin.

Aturan firewall harus didasarkan pada IP perangkat yang benar, bukan contoh umum dari buku. Gunakan `docs/07-port-dan-akses.md` dan `konfigurasi/` sebagai daftar kerja, lalu verifikasi port yang benar-benar dipakai aplikasi.

## 7. Storage, HDD 2 TB, dan ruang

### 7.1 NVMe dan HDD punya tugas berbeda

NVMe 500 GB menjadi disk sistem dan disk guest pada tahap awal. Dua HDD Seagate Surveillance 2 TB berukuran 3,5 inci belum dipasang. Karena enclosure yang tersedia satu-bay, rencana awal hanya satu HDD. Enclosure perlu catu daya yang sesuai dan koneksi yang stabil.

Sebelum menggunakan HDD:

1. Catat model, kapasitas, dan serial di catatan privat lokal.
2. Pastikan tidak ada data yang perlu diselamatkan.
3. Hubungkan satu drive; identifikasi dengan model dan ukuran, bukan hanya nama `/dev/sdX`.
4. Periksa SMART jika enclosure melewatkan SMART. Jika tidak, kesehatan masih belum terverifikasi.
5. Tentukan tujuan disk dan backup tambahan sebelum membuat filesystem.

**PERHATIAN DATA:** membuat filesystem atau datastore dapat menghapus isi disk. Jangan menekan Initialize, Wipe, Format, Create GPT, atau Create Directory sebelum disk target dipastikan benar. Jangan mengikuti contoh perintah `mkfs` secara coba-coba.

### 7.2 Apa gunanya satu HDD?

Satu HDD dapat menjadi data bersama atau lokasi backup tambahan, tetapi ia bukan backup lengkap bila hanya terpasang pada server yang sama. Kebakaran, ransomware, kesalahan perintah, catu daya rusak, atau pencurian dapat mengenai host dan drive sekaligus. Ketika HDD kedua nanti dapat dipasang, lebih baik gunakan sebagai salinan terpisah/offline daripada menganggap dua disk di satu host otomatis aman.

### 7.3 Rencana kapasitas

Jangan berikan semua ruang NVMe ke VM di atas kertas. Image container, log, update, snapshot, dan backup sementara juga memakai ruang. Sisakan ruang kosong untuk operasi normal. Foto Immich, pustaka musik, data Nextcloud, dan datastore backup dapat tumbuh cepat; pilih hanya kebutuhan yang akan dipakai.

### 7.4 Aturan sederhana storage Proxmox

- `local` biasanya menyimpan ISO, template, dan backup berbasis file.
- `local-lvm` biasanya menyimpan disk VM berbasis block/thin.
- Directory storage pada HDD memerlukan filesystem dan mount yang konsisten.
- Jangan memasang HDD secara otomatis berdasarkan `/dev/sdb`; nama perangkat bisa berubah. Pakai UUID setelah konfigurasi dipahami.
- Jika storage hilang atau SMART menunjukkan masalah, hentikan job tulis dan salin data penting sebelum melakukan perbaikan.

## 8. Membuat VM/LXC dengan aman

### 8.1 Pilih VM atau LXC

Gunakan VM untuk Docker dan aplikasi kompleks, Home Assistant OS, Proxmox Backup Server, atau layanan penting yang perlu kernel terpisah. LXC bisa lebih ringan untuk layanan Linux sederhana seperti DNS sekunder atau Samba, tetapi perlu pemahaman tentang user ID, permission, dan akses host.

### 8.2 Pola umum membuat VM Debian

1. Unduh ISO Debian dari sumber resmi, verifikasi checksum.
2. Unggah ISO ke `local` di Proxmox.
3. Klik Create VM, pilih VMID dan nama sesuai peta proyek.
4. Pilih ISO, disk pada `local-lvm`, CPU sesuai kemampuan, RAM sesuai profil aktif, dan kartu jaringan pada bridge yang tepat.
5. Instal sistem operasi; buat akun biasa dan password admin.
6. Setelah reboot, pasang update sesuai panduan Debian; aktifkan SSH hanya jika diperlukan.
7. Atur IP reservation/static lease di MikroTik setelah MAC guest diketahui.
8. Catat IP, VMID, RAM, disk, layanan, port, serta backup.

Di dalam VM Debian, root shell:

```bash
ip -br address
```

```bash
ip route
```

```bash
free -h
```

Jangan menyalakan salinan VM hasil restore dengan jaringan tersambung sementara VM aslinya masih hidup; MAC, IP, nama, token, atau identitas Tailscale mungkin sama.

### 8.3 Rencana guest proyek

Peta lengkap ada di `data/guest.yaml` dan Bab 48. Isinya banyak, tetapi bukan berarti semua harus dipasang. Pada RAM 16 GB, jalankan Proxmox, DNS, monitoring ringan, backup dan satu kebutuhan utama. Bahkan pada 32 GB, CPU M710q hanya 4 core/4 thread; banyak layanan berat bersamaan tetap dapat lambat.

Sebelum membuat guest berikutnya, jawab empat pertanyaan:

1. Masalah apa yang diselesaikan layanan ini?
2. Data apa yang akan disimpan dan seberapa penting?
3. Siapa yang dapat mengaksesnya dari LAN dan dari luar?
4. Bagaimana backup, update, monitoring, dan restore-nya?

## 9. Docker Compose, reverse proxy, dan aplikasi

### 9.1 Tempat Docker yang benar

Docker berada di VM Debian, bukan host Proxmox. Buat satu direktori per stack di `/opt/stacks/nama-layanan`. Simpan Compose di Git, tetapi password/token asli berada di file `.env` lokal yang tidak ikut commit. Cek `.gitignore` sebelum menyimpan file baru.

Sebelum menyalakan stack:

1. Baca dokumentasi image dari penerbit resmi.
2. Gunakan image dan versi yang diketahui; hindari `latest` untuk layanan penting.
3. Pahami folder data dan backup.
4. Tentukan jaringan Docker. Port internal sebaiknya tidak dipublikasikan ke seluruh LAN jika Caddy menjadi gerbang.
5. Periksa Compose dengan Docker Compose versi yang terpasang, lalu baca hasilnya sebelum `up`.
6. Setelah berjalan, periksa log dan login awal; ubah password sementara.

Perintah pemeriksaan umum di VM Docker, dari direktori stack:

```bash
docker compose config
```

Perintah ini menampilkan konfigurasi gabungan. Pastikan tidak ada rahasia yang ikut masuk ke output yang akan dibagikan.

```bash
docker compose ps
```

```bash
docker compose logs --tail=100
```

Jalankan `docker compose up -d` hanya setelah file Compose dan `.env` diperiksa. Jangan menyalin contoh yang masih memakai placeholder.

### 9.2 Caddy dan HTTPS lokal

Caddy direncanakan berjalan di VM 201, alamat `192.168.88.20`, sebagai reverse proxy lokal. AdGuard mengarahkan nama `*.home.arpa` ke Caddy; Caddy meneruskan ke aplikasi berdasarkan hostname.

Contoh alur:

[[ILUSTRASI:PROXY]]

Sertifikat lokal memerlukan CA lokal dipercaya oleh perangkat klien. Jangan memasang sertifikat akar yang tidak Anda buat sendiri. Simpan kunci CA dengan sangat aman; kunci CA bocor dapat membuat sertifikat palsu yang dipercaya browser.

Langkah umum saat Caddy kelak diterapkan:

1. Pastikan DNS hostname diarahkan ke `.20`.
2. Pastikan backend aplikasi hanya dibuka pada jaringan internal yang diperlukan.
3. Tambahkan satu hostname ke konfigurasi Caddy.
4. Periksa sintaks konfigurasi dengan Caddy.
5. Reload, uji dari laptop, lalu uji dari ponsel di Wi-Fi.
6. Jika memakai CA lokal, pasang sertifikat akar melalui saluran resmi di Windows, Android, dan iPhone; jangan mengabaikan peringatan sertifikat sebagai kebiasaan.

### 9.3 Pilih aplikasi yang sesuai kebutuhan

Mulai dari satu aplikasi. Contoh yang masuk akal:

- **Samba:** berbagi berkas lokal; mulai dengan folder dan akun yang tidak sensitif.
- **Home Assistant:** otomasi rumah bila sudah ada perangkat pintar yang ingin dikendalikan.
- **Uptime Kuma + Gotify:** cek layanan dan kirim notifikasi.
- **Nextcloud:** sinkronisasi berkas/kalender bila benar-benar dibutuhkan dan backup data disiapkan.
- **Navidrome:** streaming koleksi musik sendiri.
- **Immich:** foto/video; pasang setelah lokasi data dan backup foto siap.
- **Vaultwarden:** password manager sensitif; matikan pendaftaran publik, wajib HTTPS privat, dan siapkan backup/restore sebelum menyimpan password utama.
- **n8n:** otomasi; database dan credential workflow perlu backup serta perlindungan akses.
- **k3s/Flux:** laboratorium Kubernetes; tunda bila tujuan hanya menjalankan beberapa aplikasi sederhana.

### 9.4 Urutan memasang satu stack Docker

Contoh berikut menggambarkan cara kerja aman untuk stack yang sudah memiliki berkas konfigurasi di `konfigurasi/server/opt/stacks/`. Setiap stack memiliki kebutuhan berbeda; selalu buka README bab dan file `.env.example`-nya sebelum menjalankan.

1. **Pastikan lokasi benar.** Login ke VM Debian yang memang dituju. Jalankan `hostnamectl` dan `ip -br address`; cocokkan nama dan IP dengan peta guest. Jangan jalankan Compose di host Proxmox.
2. **Siapkan folder.** Buat `/opt/stacks/nama-stack` dengan hak akses admin yang benar. Jika memakai Git, clone hanya repo yang dipercaya. Jika menyalin manual, gunakan WinSCP dari laptop dan verifikasi file tujuan sebelum mengganti berkas.
3. **Baca konfigurasi.** Periksa nama image, versi, port, volume, jaringan, user ID, healthcheck, dan lokasi data. Jangan menghapus volume untuk mengatasi error.
4. **Siapkan variabel.** Salin `.env.example` menjadi `.env` hanya bila stack menyediakan contoh tersebut. Isi nilai asli langsung di VM dengan editor lokal. Password database, API key, token, dan domain tidak boleh masuk ke commit.
5. **Validasi.** Dari direktori stack, jalankan `docker compose config`. Jika ada error placeholder atau variabel yang kosong, jangan lanjut. Ingat output gabungan mungkin menampilkan rahasia; jangan kirim output mentah.
6. **Jalankan.** Jalankan `docker compose up -d` hanya untuk stack yang sudah direview. Periksa `docker compose ps` dan `docker compose logs --tail=100`.
7. **Selesaikan setup aplikasi.** Buka alamat internal yang ditentukan, buat akun admin, matikan pendaftaran bebas, aktifkan autentikasi yang tersedia, lalu pasang reverse proxy bila memang diperlukan.
8. **Tes sebagai klien.** Dari Windows, uji nama DNS dan HTTPS. Ulangi dari Android dan iPhone pada Wi-Fi. Dari luar rumah, layanan privat semestinya belum dapat dibuka sampai Tailscale sengaja dikonfigurasi.
9. **Tes pemulihan.** Temukan data volume aplikasi, masukkan ke backup, lalu pulihkan salinan uji sebelum layanan dipakai untuk data penting.
10. **Catat hasil.** Catat tanggal, versi image, guest, IP/port, nama file konfigurasi, hasil tes, dan backup di `STATUS.md` serta `catatan/hasil-uji.md`.

### 9.5 Peta konfigurasi dan syarat tiap layanan

File konfigurasi di repo adalah bahan kerja, bukan bukti layanan sudah dijalankan. Path berikut relatif ke akar repo.

| Layanan | Tempat target | Berkas acuan | Sebelum dinyalakan | Syarat lulus awal |
|---|---|---|---|---|
| Caddy | VM 201 | `konfigurasi/server/opt/stacks/caddy/` | DNS lokal, CA, jaringan proxy, tujuan backend | HTTPS lokal valid pada laptop dan ponsel |
| Uptime Kuma | VM 201 | `konfigurasi/server/opt/stacks/uptime-kuma/` | Target monitor dan volume data | Alarm uji diterima di Gotify |
| Gotify | VM 201 | `konfigurasi/server/opt/stacks/gotify/` | URL internal, token aplikasi lokal | Notifikasi tes diterima; token tidak dibagikan |
| Beszel | VM 201 + agent | `konfigurasi/server/opt/stacks/beszel/` dan `beszel-agent/` | Host key/credential dan pembatasan port | Grafik host tampil dan tidak mengekspos agent ke WAN |
| Homepage | VM 201 | `konfigurasi/server/opt/stacks/homepage/` | Nama DNS dan alamat layanan | Tautan hanya menuju layanan yang dapat diakses |
| Vaultwarden | VM 205 | `konfigurasi/server/opt/stacks/vaultwarden/` | HTTPS privat, backup data, pendaftaran mati | Login, backup, dan pemulihan diuji sebelum menyimpan rahasia |
| n8n + PostgreSQL | VM 208 | `konfigurasi/server/opt/stacks/n8n/` | Password database, volume PostgreSQL 18, akses privat | Workflow uji berjalan; database termasuk backup |
| Nextcloud | VM 207 | `konfigurasi/server/opt/stacks/nextcloud/` | Database, domain tepercaya, disk data, backup | Upload, unduh, dan restore satu file berhasil |
| AFFiNE | VM 206 | `konfigurasi/server/opt/stacks/affine/` | Nilai `.env.example`, resource RAM dan database | Akun dapat login; data dipulihkan dari backup uji |
| Navidrome | VM 211 | `konfigurasi/server/opt/stacks/music/` | Pustaka musik dan akses privat | Pemutaran di LAN dan Tailscale sesuai policy |
| Pocket ID | VM 213 | `konfigurasi/server/opt/stacks/sso/` | Domain, HTTPS, recovery admin | Login uji berhasil sebelum SSO dipakai aplikasi lain |
| Immich | VM 214 | `konfigurasi/server/opt/stacks/immich/` | Storage foto, ruang disk, backup terpisah | Foto contoh diunggah dan dipulihkan dari salinan |
| Situs statis | VM 209 | `konfigurasi/server/opt/stacks/web/` | Data situs, Caddy, izin file | Situs privat hanya terbuka lewat jalur yang ditentukan |
| Cloudflare Tunnel | VM 210 | `konfigurasi/server/opt/stacks/tunnel-web/` | Token lokal dan isolasi VM publik | Dari VM 210 tidak ada rute ke LAN/admin |

Home Assistant OS, AdGuard kedua, Samba, Forgejo, k3s/Flux, WordPress, dan PBS memiliki bab serta konfigurasi khusus. Ikuti index buku lama per layanan hanya sebagai bahan, lalu cek `docs/bab/REVISI-4.md`, `STATUS.md`, peta penempatan, dan file konfigurasi terkini sebelum menerapkan. Jangan berasumsi seluruh Compose contoh sudah runtime-tested.

### 9.6 Setelah layanan berjalan

- Cek panel admin hanya dapat dibuka dari jaringan dan identitas yang memang diperlukan.
- Gunakan akun terpisah untuk administrasi; matikan pendaftaran pengguna yang tidak dibutuhkan.
- Simpan data persisten di path volume yang tercatat, bukan di lapisan container sementara.
- Jadwalkan pembaruan. Sebelum update image, simpan backup dan baca catatan versi/perubahan database.
- Jangan menjalankan `docker compose down -v` sebagai langkah troubleshooting awal. Opsi `-v` dapat menghapus volume.
- Setelah update, cek status, log, login, data lama, dan notifikasi. Jika gagal, rollback image sesuai prosedur yang sudah dicatat.

## 10. Akses dari luar rumah dengan Tailscale

### 10.1 Bedakan Tailscale, subnet route, dan Funnel

Tailscale menghubungkan perangkat yang Anda izinkan melalui tailnet. Subnet router dapat membuat perangkat Tailscale mencapai alamat LAN rumah. Tailscale Funnel menerbitkan layanan ke internet publik; proyek ini tidak merencanakan Funnel. Cloudflare Tunnel hanya opsi terpisah untuk situs statis publik di VM 210.

### 10.2 Tahapan aman

1. Pastikan akun Tailscale dilindungi MFA dan daftar perangkat dikenali.
2. Selesaikan Proxmox dan firewall lokal terlebih dahulu.
3. Terapkan kebijakan `grants` dari contoh repo hanya setelah email placeholder diganti dan policy test lulus.
4. Beri akses hanya ke grup admin dan port yang dibutuhkan.
5. Atur subnet route hanya pada router Tailscale yang benar; jangan mengiklankan seluruh jaringan sebelum memahami konsekuensinya.
6. Uji dari jaringan seluler: hanya perangkat admin yang boleh membuka resource yang ditentukan.
7. Jika gagal, gunakan jaringan rumah/lokal untuk memperbaiki konfigurasi; jangan membuka port admin ke internet sebagai jalan pintas.

Nama node, metode menjalankan subnet router, dan kebutuhan STB 2 belum final. Status proyek mencatat Tailscale ditunda sampai perangkat STB kedua tersedia; jangan menganggap panduan ini berarti akses jauh sudah aktif.

### 10.3 Windows, Android, dan iPhone

Pasang aplikasi Tailscale dari toko resmi pada perangkat milik sendiri, login ke akun yang benar, periksa nama perangkat di admin console, lalu aktifkan koneksi hanya saat diperlukan. Di Android/iPhone, cek ikon VPN dan pilih perangkat yang benar. Jika ponsel memakai DNS privat/Private Relay yang bertentangan dengan DNS lokal, matikan sementara untuk diagnosis dan aktifkan kembali setelah tes.

Untuk membuka layanan lokal dari ponsel:

1. Sambungkan ponsel ke Wi-Fi rumah.
2. Pastikan Wi-Fi menggunakan DNS AdGuard rumah. Android dengan Private DNS manual atau iPhone dengan konfigurasi DNS/relay khusus dapat melewati DNS lokal.
3. Buka URL HTTPS yang sudah ditetapkan. Jika CA lokal dipakai, ikuti panduan sistem operasi dan petunjuk pembuat sertifikat proyek; jangan menerima profil sertifikat dari sumber yang tidak dikenal.
4. Matikan Wi-Fi dan uji lewat data seluler hanya setelah Tailscale policy aktif. Catat layanan yang bisa/tidak bisa dijangkau.

Menu Android berbeda menurut merek dan versi. Pada iPhone, pemasangan sertifikat akar memerlukan profil tepercaya; membaca pesan bahwa profil terpasang tidak selalu berarti CA sudah diberi kepercayaan penuh. Verifikasi instruksi resmi sistem operasi yang sedang dipakai.

## 11. Backup dan uji restore

### 11.1 Prinsip backup

Snapshot membantu kembali dari perubahan, tetapi tidak menggantikan backup. Backup pada disk yang sama atau selalu terpasang di host yang sama tidak melindungi dari semua jenis kerusakan. Simpan beberapa salinan pada media berbeda dan satu salinan offline/offsite bila memungkinkan.

Diagram keputusan:

[[ILUSTRASI:BACKUP]]

### 11.2 Backup VM di Proxmox

Mulai setelah ada storage dengan ruang cukup. Di Proxmox, pilih VM/CT > Backup > Backup now; pilih storage, mode yang didukung workload, dan kompresi. Untuk database, pastikan mekanisme konsistensi aplikasi dipahami. Jadwalkan backup saat beban rendah dan aktifkan notifikasi.

Backup dianggap berhasil bila:

- job selesai tanpa error;
- ukuran dan waktu backup masuk akal;
- verifikasi berjalan bila didukung;
- satu VM uji atau satu file berhasil dipulihkan;
- salinan tidak hanya ada di NVMe host.

### 11.3 Proxmox Backup Server

PBS menyediakan deduplikasi, verifikasi, retensi, dan restore terintegrasi. Namun menjalankan PBS sebagai VM pada host yang sama dan menyimpan datastore di drive yang sama tetap punya risiko host tunggal. Untuk proyek ini, rencana storage PBS perlu diputuskan setelah HDD pertama dikenali dan skema backup tambahan dipilih.

Enkripsi backup sisi klien dapat membantu menjaga kerahasiaan, tetapi kunci yang hilang berarti data tak dapat dipulihkan. Simpan master key/recovery key dengan aman dan lakukan uji restore saat awal, bukan setelah darurat.

### 11.4 Latihan restore yang aman

1. Pilih guest non-sensitif dan buat backup.
2. Pulihkan dengan VMID uji baru, bukan menimpa guest aktif.
3. Putus koneksi jaringan pada guest hasil restore sebelum menyalakan, untuk mencegah duplikasi IP/MAC/Tailscale.
4. Buka console, pastikan OS dan data penting terbaca.
5. Matikan guest uji dan hapus hanya setelah memastikan guest asli dan backup tetap utuh.
6. Catat waktu restore, hasil, dan kendala.

Jangan uji restore pertama kali pada satu-satunya salinan layanan Vaultwarden, foto, atau database produksi.

### 11.5 Backup konfigurasi router dan host

Simpan konfigurasi MikroTik secara terenkripsi di tempat aman. Jangan commit file backup router atau arsip `/etc/pve` ke GitHub. Backup VM tidak mencakup semua konfigurasi host: catat IP, nama interface aktual, storage, firewall, akun, dan langkah pemulihan. Arsip host bisa mengandung rahasia; batasi aksesnya.

## 12. Monitoring, pemeliharaan, dan pemulihan gangguan

### 12.1 Monitoring minimum

Mulai dengan alarm yang Anda pahami:

- status host Proxmox dan ruang NVMe/storage;
- apakah DNS utama dapat menjawab;
- apakah Caddy dan aplikasi yang dipakai merespons;
- status backup terakhir;
- suhu CPU/NVMe dan SMART HDD;
- pemberitahuan listrik/UPS bila kelak tersedia.

Uptime Kuma memeriksa ketersediaan, Beszel menampilkan pemakaian host/guest, dan Gotify mengirim peringatan. Alert harus diuji dengan sengaja menghentikan monitor uji, lalu memastikan pemberitahuan benar-benar tiba di ponsel.

### 12.2 Jadwal rutin

| Kapan | Periksa |
|---|---|
| Mingguan | Dashboard host, ruang disk, update penting, alarm layanan |
| Bulanan | Hasil backup/verifikasi, pulihkan satu file contoh, SMART dan suhu, kapasitas |
| Tiap 3 bulan | Akun admin, MFA, perangkat tailnet, port-forward/UPnP, token yang tidak dipakai |
| Sebelum perubahan besar | Backup, catat konfigurasi, cara rollback, akses console tersedia |
| Setelah perubahan | Tes sisi server dan klien, diagram dan STATUS diperbarui |

### 12.3 Pohon diagnosis cepat

[[ILUSTRASI:DIAGNOSIS]]

Jika Proxmox tidak dapat dibuka:

1. Pastikan host menyala dan kabel LAN terpasang.
2. Dari laptop, cek alamat `ipconfig`; harus berada pada LAN `192.168.88.x` dengan gateway `.1`.
3. Buka `https://192.168.88.10:8006` (HTTPS dan port 8006).
4. Jika browser gagal, cek konsol lokal Proxmox dan perintah `ip -br address`, `ip route`.
5. Jangan mengubah firewall atau jaringan secara acak. Catat hasil dan gunakan konsol fisik bila akses jaringan hilang.

Jika aplikasi Docker gagal:

1. Periksa `docker compose ps`.
2. Periksa `docker compose logs --tail=100`.
3. Cek ruang disk dan apakah file `.env` tersedia.
4. Jangan hapus volume atau menjalankan `down -v` untuk sekadar mencoba; opsi itu dapat menghapus data aplikasi.
5. Pulihkan dari backup yang diketahui baik jika data penting terancam.

## 13. Layanan yang bermanfaat dan urutan penerapan

Roadmap penuh ada di `docs/12-roadmap-manfaat-keamanan.md`. Urutan praktis:

### P0 — keamanan akun dan router

MFA, recovery, tinjau anggota tailnet, port-forward, UPnP, backup terenkripsi MikroTik.

### P1 — fondasi host

RAM cocok dan MemTest lulus, BIOS diverifikasi, Proxmox terpasang di NVMe, akun admin dan firewall diuji.

### P2 — data dan pemulihan

Satu HDD pertama diperiksa model/SMART tanpa format tergesa-gesa; backup, retensi, dan restore berhasil.

### P3 — akses dan DNS tahan gangguan

AdGuard sekunder diuji saat DNS utama mati; Tailscale diterapkan terbatas bila prasyarat perangkat tersedia.

### P4 — aplikasi yang memberi manfaat nyata

Pilih Samba atau Home Assistant dulu, kemudian satu layanan berikutnya setelah backup dan monitoring ada.

### P5 — notifikasi dan daya

Uptime Kuma/Beszel/Gotify, lalu UPS setelah beban listrik server diukur dan prosedur shutdown diuji.

### P6 — segmentasi jaringan

Rencanakan jaringan admin/server, IoT, dan tamu. Jangan menerapkan VLAN sebelum MikroTik, AP TL-WR820N, serta switch LS1005 terbukti mendukung rancangan yang dibutuhkan. LS1005 tercatat unmanaged, jadi desain VLAN mungkin memerlukan perangkat lain.

## 14. Daftar periksa penerimaan proyek

Gunakan daftar berikut sebagai gerbang, bukan target yang harus selesai sekaligus.

### Gerbang A — siap instal

- [ ] File penting M710q sudah dicadangkan dan salinan diuji.
- [ ] RAM cocok; MemTest86 tidak menunjukkan error.
- [ ] Model disk NVMe dan HDD dicatat lokal.
- [ ] USB installer diverifikasi dan disk data dilepas.
- [ ] IP, gateway, DNS, hostname dan password sudah diputuskan.

### Gerbang B — Proxmox dasar

- [ ] UI hanya dapat diakses dari LAN admin.
- [ ] Host punya IP/gateway/DNS benar.
- [ ] Pembaruan dan repository cocok dengan versi terpasang.
- [ ] Akun admin dan faktor kedua diuji.
- [ ] Jalur console lokal tersedia sebelum mengubah firewall.

### Gerbang C — layanan pertama

- [ ] VM/CT punya catatan ID, IP, RAM, storage, owner dan tujuan.
- [ ] Tidak ada password/token di Git.
- [ ] Backup terjadwal dan notifikasi diuji.
- [ ] Restore guest/file uji berhasil.
- [ ] Klien Windows dan ponsel dapat mengakses dengan DNS/HTTPS yang benar.

### Gerbang D — akses dari luar dan layanan publik

- [ ] Tailscale policy diuji dan hanya memberi akses yang diperlukan.
- [ ] Admin Proxmox tidak dapat dicapai dari internet.
- [ ] Tidak ada port-forward/UPnP tak dikenal.
- [ ] Aplikasi publik dipisah dari jaringan admin dan memiliki update, autentikasi, log, serta backup.

Simpan tanggal, siapa yang menguji, perangkat klien, dan hasil nyata. Jangan memberi tanda centang berdasarkan rencana.

## Lampiran A. Peta IP dan guest

Alamat merupakan rancangan dan harus diselaraskan dengan `data/guest.yaml`.

| ID | Nama | Jenis | IP | Fungsi target |
|---:|---|---|---:|---|
| — | MikroTik | Router | `.1` | Gateway LAN |
| — | Access Point | AP | `.2` | Wi-Fi rumah |
| 101 | adguard2 | LXC | `.11` | DNS sekunder |
| 102 | files | LXC | `.12` | Samba |
| 201 | docker-core | VM | `.20` | Caddy, monitoring, dashboard |
| 202 | haos | VM | `.21` | Home Assistant OS |
| 203 | k3s | VM | `.22` | Kubernetes lab, opsional |
| 204 | git | VM | `.23` | Forgejo + Renovate |
| 205 | vault | VM | `.24` | Vaultwarden, akses privat |
| 206 | affine | VM | `.25` | AFFiNE; profil hemat dapat menggabungkan aplikasi |
| 207 | nextcloud | VM | `.26` | Nextcloud |
| 208 | n8n | VM | `.27` | n8n + PostgreSQL |
| 209 | web | VM | `.28` | web privat |
| 210 | web-public | VM | `.29` | situs statis publik opsional; isolasi dari LAN |
| 212 | pbs | VM | `.30` | Proxmox Backup Server |
| 211 | music | VM | `.31` | Navidrome |
| 213 | sso | VM | `.32` | Pocket ID |
| 214 | immich | VM | `.33` | Immich |
| — | STB HG680 | di luar PVE | `.253` | AdGuard utama |
| — | Laptop admin | klien | `.252` | administrasi LAN |

Alamat lengkap, RAM, port, dan catatan mode hemat terdapat di file data repo; jangan membuat ulang daftar secara terpisah tanpa memperbarui sumber tersebut.

## Lampiran B. Perintah yang sering dipakai

Semua contoh di bagian ini adalah pemeriksaan baca-saja, kecuali disebut lain.

### Windows PowerShell

```powershell
ipconfig
```
Alamat IP, gateway, dan adapter jaringan Windows.

```powershell
Test-NetConnection 192.168.88.10 -Port 8006
```
Memeriksa apakah laptop dapat mencapai layanan web Proxmox.

```powershell
Get-FileHash -Algorithm SHA256 "$env:USERPROFILE\Downloads\NAMA-FILE.iso"
```
Menghitung hash file ISO; cocokkan hasil dengan halaman unduhan resmi.

### Proxmox host (root)

```bash
pveversion
```
Versi Proxmox.

```bash
ip -br address
```
IP singkat per interface.

```bash
ip route
```
Rute dan gateway.

```bash
lsblk -o NAME,SIZE,TYPE,MODEL
```
Disk, ukuran, dan model. Gunakan ini sebelum operasi storage.

```bash
free -h
```
RAM dan swap.

### VM Debian (root atau akun yang berhak)

```bash
docker compose ps
```
Status container pada stack aktif.

```bash
docker compose logs --tail=100
```
Log terbaru stack. Saring rahasia sebelum dibagikan.

```bash
df -h
```
Ruang filesystem.

Jangan jalankan perintah destruktif dari internet tanpa memahami setiap opsi. Hati-hati khususnya `mkfs`, `wipefs`, `dd`, `rm -rf`, `docker compose down -v`, `qm destroy`, dan perubahan firewall/jaringan.

## Lampiran C. Glosarium singkat

| Istilah | Arti sederhana |
|---|---|
| 2FA/MFA | Bukti login tambahan selain password |
| CIDR `/24` | Penulisan ukuran jaringan; `192.168.88.10/24` berada pada jaringan `192.168.88.0/24` |
| DHCP | Layanan yang membagikan IP otomatis |
| FQDN | Nama host lengkap seperti `pve.example.internal` |
| HA | High Availability; failover otomatis antarmesin, tidak tersedia hanya dengan satu server |
| Image | Paket sistem operasi atau container dasar |
| LXC | Container Linux ringan yang memakai kernel host |
| MFA | Autentikasi dengan dua atau lebih faktor |
| NAS | Penyimpanan berkas di jaringan |
| PBS | Proxmox Backup Server |
| RAID | Gabungan disk untuk kinerja/ketahanan tertentu; bukan pengganti backup |
| SMART | Informasi kesehatan dan kesalahan disk |
| Snapshot | Keadaan disk/guest pada waktu tertentu; bukan salinan terpisah |
| VM | Mesin virtual dengan sistem operasi sendiri |
| VLAN | Pembagian jaringan logis untuk memisahkan perangkat |

## Lampiran D. Rujukan resmi

- Proxmox VE Administration Guide: https://pve.proxmox.com/pve-docs/pve-admin-guide.pdf
- Proxmox VE downloads: https://www.proxmox.com/en/downloads/proxmox-virtual-environment
- Proxmox Backup Server documentation: https://pbs.proxmox.com/docs/
- Tailscale grants and access control: https://tailscale.com/docs/features/access-control/grants
- Tailscale policy syntax: https://tailscale.com/docs/reference/syntax/policy-file
- MikroTik RouterOS backup and restore: https://help.mikrotik.com/docs/spaces/ROS/pages/40992852/Backup
- MikroTik configuration management: https://help.mikrotik.com/docs/spaces/ROS/pages/328155/Configuration+Management

Periksa dokumentasi resmi untuk versi yang benar-benar dipasang. Antarmuka, nama paket, image, persyaratan hardware, dan syntax dapat berubah. Catat versi aktual di `STATUS.md` dan hasil pemeriksaan di `catatan/hasil-uji.md`.

---

**Akhir panduan.** Lanjutkan pekerjaan berdasarkan board proyek dan roadmap. Server belum dianggap siap hanya karena panduan selesai dibaca; readiness ditentukan oleh pengujian nyata, backup yang dapat dipulihkan, dan akses yang dibatasi dengan benar.
