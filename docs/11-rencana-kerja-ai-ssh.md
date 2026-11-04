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

## Riwayat status host — 4 November 2026 (sebelum cutover Nextcloud)

### Migrasi Jellyfin — 4 November 2026 malam

CT106 `.111` dengan MAC `BC:24:11:9E:13:F4` aktif; static lease dilaporkan pengguna. Jellyfin sehat pada `:8096`, mount media read-only. Konfigurasi/cache disalin dari CT104 ketika sumber berhenti dan arsip cocok SHA-256. Homepage dan monitor Kuma ID 7 sudah mengarah ke CT106; heartbeat monitor `Up / 200 - OK`. Backup manual CT106 terenkripsi sukses dan job harian mencakup VMID 106. CT104 Jellyfin berhenti sebagai rollback. Pekerjaan tersisa sebelum Nextcloud: daftarkan Agent CT106 ke Portainer dan konfirmasi endpoint baru dari aplikasi klien. Pengguna menyetujui Connect; browser UI gagal mengambil frame karena `window crop is outside captured monitor`, dan daftar Portainer live tetap tidak mencantumkan CT106. Lease MikroTik belum diaudit langsung.

Audit live lanjutan: Proxmox VE 9.2.24 di `.10`; CT102, CT104–106, CT109–112, CT115 dan VM202 running. Storage `backup-disk` aktif; `/dev/sda1` ext4 ter-mount, 1.7 TiB tersedia. CT102/104 sempat gagal start sebelum HDD terdeteksi; keduanya sekarang running. CT104 Nextcloud/DB/Redis sehat dan Immich empat container sehat; Jellyfin dipindah ke CT106 `.111` dan CT104 berhenti sebagai rollback; Beszel dan Portainer berjalan. CT112 Gotify `/health` green; pengguna mengonfirmasi aplikasi Android/iPhone pindah ke `.109:8070` dan notifikasi uji diterima. CT115 Homepage healthy HTTP 200; dashboard Portainer menampilkan `CT115-Homepage` Up, Agent 2.45.3, 2/2 container. Monitor Kuma Immich ada dan heartbeat Up / 200 OK. Kuma monitor Home Assistant `.21:80` juga Up. HAOS Observer `:4357` menyatakan Supervisor Connected/Health Healthy, UI Core menjawab HTTP 200 di `.21:80`; TCP 8123 tertutup [BELUM PASTI: sebab]. File Homepage `services.yaml` telah disinkronkan dengan repo dan menambahkan kartu Home Assistant di `.21`. PBS job mencakup CT101–106, CT109–112, CT115, VM202; backup CT106 `ct/106/2026-11-04T12:54:52Z` sukses, PBS terbaru 38.61% terpakai; backup CT115 pasca-setup terbaru `ct/115/2026-11-04T11:41:45Z` sukses. PBS setelah backup CT106 38.61% terpakai di NVMe host yang sama; thin-pool 33.48% / metadata 1.54%.

Pembaruan awal 4 Nov malam (digantikan catatan cutover di bawah): pengguna mengonfirmasi Jellyfin tuntas (library Movies/Shows, realtime monitoring, SMB salin dan playback Windows, Portainer, serta klien). Pada saat catatan awal itu, Nextcloud CT107 belum dipindah.

## Status historis host — 2 November 2026

Audit SSH baca-saja Proxmox VE 9.2.24 di `192.168.88.10` berhasil dengan `HostKeyAlias=192.168.0.200` yang cocok dengan fingerprint host terverifikasi sebelumnya. Guest: CT101 `adguard2` stopped/onboot=0; CT104 `docker-services` running/onboot=1, DHCP lease sementara `.101`, Docker aktif, hanya Portainer pada 9443; VM201 `docker-core` stopped/onboot=0; CT100 dan VM200 template stopped. `local` dan `local-lvm` aktif. `lsblk` hanya menampilkan NVMe; HDD `/dev/sda` 2 TB NTFS yang tampak di screenshot 1 Nov tidak muncul pada audit 2 Nov [BELUM PASTI: penyebab]. Jangan format. WinBox DHCP Network menampilkan `192.168.88.0/24`, gateway `.1`, DNS `.3`. SSH ke MikroTik ditolak saat negosiasi algoritme lama; percobaan kompatibilitas terbatas tetap diputus RouterOS saat KEX sebelum autentikasi. Tidak ada konfigurasi router yang diubah. Update security Proxmox sudah selesai. Sebelum instal aplikasi, tetapkan IP final CT104, pastikan HDD secara fisik, dan selaraskan penempatan layanan yang berbeda antara status/data dan buku. Jangan simpan rahasia atau menganggap rencana sebagai keadaan aktual.

## Status host terkini — cutover Nextcloud CT107, 4 November 2026 malam

Pengguna mengonfirmasi static lease MikroTik; WebFig menampilkan komentar `CT107-Nextcloud`, IP `192.168.88.112`, MAC `BC:24:11:0F:DA:1F`. CT107 running dengan Docker CE 29.9.3 dan Compose 5.7.0. Nextcloud 35.0.2.2 + MariaDB/Redis aktif; `occ status` menunjukkan installed=true, maintenance=false, `needsDbUpgrade=false`; `status.php` HTTP 200 dari CT107 dan PVE. Data bind mount HDD `/srv/nextcloud-data` owner www-data mode 750, `backup=0`. Database MariaDB lulus `mariadb-check`; 164 entri `oc_appconfig` terverifikasi setelah restore final. CT104 `nextcloud_app` berhenti; DB/Redis lama tetap hidup sebagai rollback.

Portainer environment `CT107-Nextcloud` (Agent `192.168.88.112:9001`) tampil di dashboard: 4 container running, 2 healthy, 0 unhealthy. Homepage live dan repo menunjuk `.112:8080`, HTTP 200. Kuma SQLite integrity `ok`; monitor ID 8 menggunakan `http://192.168.88.112:8080/status.php`, tiga heartbeat terakhir status Up. Backup final sumber ada dalam PBS snapshot terenkripsi CT104 `ct/104/2026-11-04T15:10:14Z`; backup CT107 pasca-setup `ct/107/2026-11-04T15:30:38Z` sukses, snapshot sementara dibersihkan. Job harian mencakup CT107. PBS tetap berada pada NVMe host yang sama; data bind mount `backup=0` tidak masuk backup guest. Thin-pool pada audit akhir 35.84% data / 1.62% metadata, PBS 39.49% terpakai, dengan peringatan autoextend/overcommit.

**Tindakan pengguna berikutnya:** perbarui klien sinkronisasi Windows serta aplikasi Android/iPhone ke `http://192.168.88.112:8080`, lalu uji login, buka file, unggah, dan unduh. Jangan matikan/hapus rollback CT104 sebelum semua klien lulus. Setelah konfirmasi klien, prioritas berikut adalah otomasi media Jellyfin sesuai `docs/14-usulan-isolasi-guest.md`; jangan instal aplikasi lain dahulu.
## Audit CT108 qBittorrent — 5 November 2026

- Sebelum perubahan, audit read-only memastikan Proxmox VE 9.2.24, VMID 108 kosong dan menjadi nextid, storage `backup-disk`/`local-lvm`/`pbs-store1` aktif. CT108 dibuat Debian 13 unprivileged (1 vCPU, 1 GiB RAM, 512 MiB swap, rootfs 8 GiB); DHCP aktif `.114`, MAC `BC:24:11:B9:6B:9D`, lease static dikonfirmasi pengguna.
- CT108 memasang hanya bind mount Inbox Jellyfin ke `/srv/media-inbox` dan staging `/srv/torrent`; dua mount `backup=0`. Tidak ada mount `/srv/media/Movies`, `/srv/media/Shows`, atau Immich. Host menyimpan staging pada HDD, incomplete mode group-writable untuk UID/GID container 1000:2000.
- Docker CE 29.9.3/Compose 5.7.0 lulus `hello-world`. qBittorrent 5.3.0 dan Agent 2.45.3 berjalan; WebUI `.114:8080` HTTP 200. Konfigurasi diperbaiki dari default `/downloads` yang belum terpetakan ke default `/inbox`; temp path diaktifkan `/downloads/incomplete`. Compose tervalidasi `docker compose config --quiet` dan service kembali Up setelah recreate.
- Firewall Agent persisten di CT108 hanya izinkan CT105 `.105` ke TCP 9001. Probe CT105 `https://192.168.88.114:9001/ping` HTTP 204; probe CT104 timeout (curl HTTP 000), tidak ada routing tambahan ke guest lain.
- Homepage CT115 `services.yaml` diperbarui dengan kartu `.114:8080`; Homepage merespons HTTP 200. Job PBS harian memasukkan CT108. Backup manual terenkripsi `ct/108/2026-11-04T19:05:33Z` sukses; akar guest 1.693 GiB, snapshot dibersihkan. Bind mount media/torrent tidak tercakup oleh desain `backup=0`; PBS berada pada NVMe host yang sama.
- PBS `pbs-store1` aktif 42.55% pada pemeriksaan awal sesi; thin-pool `pve/data` 38.84% data/1.69% metadata. Warning berulang: `You have not turned on protection against thin pools running out of space.`; `Set activation/thin_pool_autoextend_threshold below 100 to trigger automatic extension of thin pools before they get full.`; `Sum of all thin volume sizes (440.00 GiB) exceeds the size of thin pool pve/data and the amount of free space in volume group (16.00 GiB).`
- Belum ada torrent/download pengguna diuji; jangan klaim e2e. Password WebUI awal harus diganti langsung dari UI qBittorrent. Environment Portainer CT108 dan monitor Kuma belum diverifikasi. Workflow n8n tetap tidak aktif sampai tiga intake selesai dan diuji.
- Deviasi/perintah yang diperbaiki tanpa perubahan data aplikasi: `pct clone --help; pct set --help` menghasilkan `Unknown option: help` dan `400 unable to parse option`; probe `docker exec qbittorrent qbittorrent-nox --version` menghasilkan `OCI runtime exec failed: exec failed: unable to start container process: exec: "qbittorrent-nox": executable file not found in $PATH` (diagnostik path binary salah; container tetap Up). `pvesm list` yang dikirim lewat stdin PowerShell membawa CR pada argumen VMID dan menghasilkan `400 Parameter verification failed. vmid: type check ('integer') failed - got '108\r'`; direct invocation `pvesm list pbs-store1 --vmid 108` berhasil. Dua sintaks inspeksi shell PowerShell salah menghasilkan `ParserError: Missing statement block after 'end'.` dan `The term 'SavePath' is not recognized as a name of a cmdlet, function, script file, or executable program.`; pemeriksaan ulang menggunakan pipeline lokal untuk menampilkan hanya path yang aman.
- Computer Use mengikuti skill resmi; perubahan konfigurasi router tidak dibuat. Awal sesi Chrome melaporkan `user input was detected in this window; call get_window_state before continuing`; klik tanpa screenshot segar menghasilkan `coordinate input geometry is unavailable`. Setelah capture screenshot segar, navigasi keyboard dan klik koordinat screenshot bekerja. Portainer `CT108-qBittorrent` tampil Up dengan 2/2 container, dan Kuma monitor ID 15 `qBittorrent` Up/HTTP 200. Password tidak ditampilkan atau dibaca.
