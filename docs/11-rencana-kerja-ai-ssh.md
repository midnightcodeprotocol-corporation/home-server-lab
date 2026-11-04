# Rencana kerja AI melalui SSH ke Proxmox

Catatan ini menetapkan cara kerja bila pengguna memakai Codex dan Claude untuk memeriksa atau mengelola server Proxmox melalui SSH. Koneksi masing-masing asisten terpisah; akses dan status sesi tidak otomatis dibagikan.

## Prinsip koordinasi

1. **Satu operator yang mengubah server pada satu waktu.** Asisten lain boleh meninjau rencana atau hasil, tetapi jangan menjalankan perubahan bersamaan.
2. **Mulai dengan pemeriksaan baca-saja.** Kumpulkan keadaan aktual sebelum menyarankan perubahan: versi Proxmox, node, RAM, disk, jaringan, VM/LXC, tugas dan status backup.
3. **Tinjau sebelum mengubah.** Jelaskan tujuan, perintah yang akan dijalankan, dampak yang mungkin terjadi, dan cara memeriksa hasilnya. Untuk langkah berisiko atau dapat memutus akses, berhenti sebelum eksekusi dan pastikan pengguna memahami langkah serta jalur pemulihan.
4. **Satu langkah, lalu periksa hasil.** Jalankan perubahan satu per satu. Simpan keluaran atau pesan error yang relevan, verifikasi keadaan setelahnya, dan baru lanjut.
5. **Serah-terima dengan catatan.** Sebelum asisten lain melanjutkan, catat keadaan terakhir, waktu, perintah yang dijalankan, hasilnya, perubahan yang belum selesai, dan langkah berikutnya. Asisten berikutnya membaca catatan dan melakukan pemeriksaan baca-saja ulang sebelum bertindak.
6. **Jangan menaruh rahasia di chat atau GitHub.** Jangan meminta atau menempelkan kata sandi, private key SSH, token, kunci enkripsi, atau isi berkas rahasia. Kredensial tetap dikelola di perangkat pengguna atau Vaultwarden.

## Alur sesi

### A. Persiapan

- Pastikan target benar: host/node Proxmox dan akun SSH yang digunakan.
- Gunakan akses SSH yang dikendalikan pengguna. Jangan menganggap asisten berbagi koneksi atau kredensial dengan asisten lain.
- Periksa rencana cadangan dan jalur pemulihan sebelum perubahan yang berpengaruh pada jaringan, firewall, storage, autentikasi, atau VM.

### B. Audit awal baca-saja

Catat hasil pemeriksaan yang sesuai dengan tujuan sesi, misalnya:

- versi dan status node Proxmox;
- RAM, CPU, disk, dan kapasitas storage;
- antarmuka serta alamat jaringan;
- daftar VM/LXC dan statusnya;
- status serta waktu backup terakhir.

Jangan menjalankan perintah perubahan selama audit awal.

### C. Perubahan terkontrol

Untuk setiap perubahan:

1. nyatakan perubahan yang diusulkan dan dampaknya;
2. periksa prasyarat dan jalur pemulihan;
3. jalankan satu langkah;
4. catat keluaran persis yang relevan;
5. verifikasi layanan dan akses yang terkait;
6. hentikan pekerjaan bila hasil berbeda dari perkiraan, lalu dokumentasikan sebelum melanjutkan.

Perubahan seperti instalasi ulang, penghapusan atau pemformatan disk, perubahan firewall/jaringan/SSH, dan penghancuran VM dapat menyebabkan kehilangan data atau terkunci dari server. Jangan menjalankannya sebagai bagian dari audit baca-saja.

### D. Catatan dan serah-terima

Simpan catatan kerja di repo tanpa rahasia, atau di tempat privat bila keluaran memuat informasi sensitif. Catatan minimal:

- tanggal dan operator;
- tujuan sesi;
- keadaan awal yang relevan;
- perintah/perubahan;
- hasil dan verifikasi;
- masalah atau ketidakpastian;
- langkah berikutnya dan apakah perlu tindakan pengguna.

Perbarui `STATUS.md`, `catatan/hasil-uji.md`, dan `docs/04-board.md` bila sesi mengubah posisi proyek atau menguji langkah panduan, mengikuti aturan di `AGENTS.md`.

## Batas koordinasi

Codex dan Claude tidak saling mengirim status atau mengunci SSH secara otomatis. Pengguna menjadi koordinator: tentukan satu operator aktif, minta operator selesai atau berhenti, lalu berikan catatan serah-terima kepada asisten berikutnya. Jangan membiarkan dua sesi menjalankan perubahan pada host secara bersamaan.

## Status host saat ini — 4 November 2026 (pembaruan malam)

### Migrasi Jellyfin — 4 November 2026 malam

CT106 `.111` dengan MAC `BC:24:11:9E:13:F4` aktif; static lease dilaporkan pengguna. Jellyfin sehat pada `:8096`, mount media read-only. Konfigurasi/cache disalin dari CT104 ketika sumber berhenti dan arsip cocok SHA-256. Homepage sudah mengarah ke CT106. Backup manual CT106 terenkripsi sukses dan job harian kini mencakup VMID 106. CT104 Jellyfin berhenti sebagai rollback. Pekerjaan yang tersisa sebelum Nextcloud: update monitor Kuma ID 7 dari `.20:8096`, daftarkan Agent CT106 ke Portainer, dan konfirmasi endpoint baru dari aplikasi klien. Kontrol Chrome tidak tersedia karena local browser use dinonaktifkan di Work settings; lease MikroTik belum diaudit langsung.

Audit live lanjutan: Proxmox VE 9.2.24 di `.10`; CT102, CT104–106, CT109–112, CT115 dan VM202 running. Storage `backup-disk` aktif; `/dev/sda1` ext4 ter-mount, 1.7 TiB tersedia. CT102/104 sempat gagal start sebelum HDD terdeteksi; keduanya sekarang running. CT104 Nextcloud/DB/Redis sehat dan Immich empat container sehat; Jellyfin dipindah ke CT106 `.111` dan CT104 berhenti sebagai rollback; Beszel dan Portainer berjalan. CT112 Gotify `/health` green; pengguna mengonfirmasi aplikasi Android/iPhone pindah ke `.109:8070` dan notifikasi uji diterima. CT115 Homepage healthy HTTP 200; dashboard Portainer menampilkan `CT115-Homepage` Up, Agent 2.45.3, 2/2 container. Monitor Kuma Immich ada dan heartbeat Up / 200 OK. Kuma monitor Home Assistant `.21:80` juga Up. HAOS Observer `:4357` menyatakan Supervisor Connected/Health Healthy, UI Core menjawab HTTP 200 di `.21:80`; TCP 8123 tertutup [BELUM PASTI: sebab]. File Homepage `services.yaml` telah disinkronkan dengan repo dan menambahkan kartu Home Assistant di `.21`. PBS job mencakup CT101–106, CT109–112, CT115, VM202; backup CT106 `ct/106/2026-11-04T12:54:52Z` sukses, PBS terbaru 38.61% terpakai; backup CT115 pasca-setup terbaru `ct/115/2026-11-04T11:41:45Z` sukses. PBS setelah backup CT106 38.61% terpakai di NVMe host yang sama; thin-pool 33.48% / metadata 1.54%.

Tindak lanjut: verifikasi hasil job PBS harian berikutnya; akses Home Assistant kini berfungsi di `http://192.168.88.21/`, sedangkan sebab port 8123 tertutup belum diketahui; evaluasi thin-pool autoextend menggunakan prosedur resmi PVE 9.2.24. Lanjutkan satu stack pada satu waktu dan pertahankan CT104 sampai rollback tidak diperlukan. Bind mount data aplikasi `backup=0` memerlukan backup file terpisah.

## Status historis host — 2 November 2026

Audit SSH baca-saja Proxmox VE 9.2.24 di `192.168.88.10` berhasil dengan `HostKeyAlias=192.168.0.200` yang cocok dengan fingerprint host terverifikasi sebelumnya. Guest: CT101 `adguard2` stopped/onboot=0; CT104 `docker-services` running/onboot=1, DHCP lease sementara `.101`, Docker aktif, hanya Portainer pada 9443; VM201 `docker-core` stopped/onboot=0; CT100 dan VM200 template stopped. `local` dan `local-lvm` aktif. `lsblk` hanya menampilkan NVMe; HDD `/dev/sda` 2 TB NTFS yang tampak di screenshot 1 Nov tidak muncul pada audit 2 Nov [BELUM PASTI: penyebab]. Jangan format. WinBox DHCP Network menampilkan `192.168.88.0/24`, gateway `.1`, DNS `.3`. SSH ke MikroTik ditolak saat negosiasi algoritme lama; percobaan kompatibilitas terbatas tetap diputus RouterOS saat KEX sebelum autentikasi. Tidak ada konfigurasi router yang diubah. Update security Proxmox sudah selesai. Sebelum instal aplikasi, tetapkan IP final CT104, pastikan HDD secara fisik, dan selaraskan penempatan layanan yang berbeda antara status/data dan buku. Jangan simpan rahasia atau menganggap rencana sebagai keadaan aktual.
