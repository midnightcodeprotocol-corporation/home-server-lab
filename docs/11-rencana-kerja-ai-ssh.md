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

## Status host saat ini — 4 November 2026

Audit/migrasi terakhir: Proxmox VE 9.2.24 di `.10`; CT101–105 dan CT109–110 serta VM202/VM212 berjalan. CT104 `.20` tetap menjalankan layanan lain; Uptime Kuma lama di CT104 berhenti sebagai rollback. Kuma 2.5.9 aktif di CT109 `.106:3001` dengan 14 monitor, UI HTTP 302, SQLite integrity `ok`; CT109 rootfs 16 GiB. Pengguna melaporkan CT109 terdaftar sebagai environment di Portainer CT105 `.105`; alamat `.106` aktif terverifikasi, static reservation MikroTik dilaporkan pengguna tetapi belum diaudit langsung. CT110 `prometheus` di `.107` adalah lease DHCP sementara; Docker CE 29.9.2, Compose 5.7.0, Agent 2.45.3 dan firewall Agent siap; stack monitoring tetap di CT104 sampai lease dibuat static dan environment CT110 didaftarkan. Jadwal PBS harian `home-lab-daily` kini mencakup CT101–105, CT109–110, VM202; backup terenkripsi CT109 dan CT110 4 Nov sukses. Saat backup, Proxmox memperingatkan thin-pool overcommit; pemakaian aktual `pve/data` 27.20% / metadata 1.34%, autoextend belum dikonfigurasi.

Tindak lanjut segera: ubah monitor self-check “Uptime Kuma” dari `192.168.88.20:3001` ke `192.168.88.106:3001`; verifikasi dashboard Portainer menunjukkan CT109 `Up`; buat lease static `.107` dan daftarkan CT110 di Portainer; rencanakan autoextend thin-pool dengan prosedur yang sesuai versi PVE. Lanjutkan migrasi satu stack pada satu waktu, backup sebelum cutover, jangan hapus CT104 sampai rollback tidak lagi diperlukan. Bind mount data aplikasi dengan `backup=0` memerlukan backup file terpisah.

## Status historis host — 2 November 2026

Audit SSH baca-saja Proxmox VE 9.2.24 di `192.168.88.10` berhasil dengan `HostKeyAlias=192.168.0.200` yang cocok dengan fingerprint host terverifikasi sebelumnya. Guest: CT101 `adguard2` stopped/onboot=0; CT104 `docker-services` running/onboot=1, DHCP lease sementara `.101`, Docker aktif, hanya Portainer pada 9443; VM201 `docker-core` stopped/onboot=0; CT100 dan VM200 template stopped. `local` dan `local-lvm` aktif. `lsblk` hanya menampilkan NVMe; HDD `/dev/sda` 2 TB NTFS yang tampak di screenshot 1 Nov tidak muncul pada audit 2 Nov [BELUM PASTI: penyebab]. Jangan format. WinBox DHCP Network menampilkan `192.168.88.0/24`, gateway `.1`, DNS `.3`. SSH ke MikroTik ditolak saat negosiasi algoritme lama; percobaan kompatibilitas terbatas tetap diputus RouterOS saat KEX sebelum autentikasi. Tidak ada konfigurasi router yang diubah. Update security Proxmox sudah selesai. Sebelum instal aplikasi, tetapkan IP final CT104, pastikan HDD secara fisik, dan selaraskan penempatan layanan yang berbeda antara status/data dan buku. Jangan simpan rahasia atau menganggap rencana sebagai keadaan aktual.
