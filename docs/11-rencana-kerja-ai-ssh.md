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

## Status host saat ini — 31 Oktober 2026

Proxmox berjalan di ThinkCentre M710q; kernel aktif `7.0.14-26-pve`, VT-x/KVM lulus pemeriksaan, dan belum ada VM/LXC atau template. Host sementara memakai `192.168.0.200/24` karena belum tersambung kembali ke MikroTik `192.168.88.0/24`; alamat target rumah `192.168.88.10` belum diterapkan. Windows pengguna dapat menjangkau TCP port 22 dan fingerprint ED25519 telah diverifikasi, tetapi akses SSH dari Codex belum terautentikasi. Enclosure single-bay lama ditemukan tetapi belum diuji; HDD belum tersambung. Sebelum SSH, pastikan komputer yang memulai koneksi memiliki rute ke host. Jangan membuka SSH dari internet atau mengirim kata sandi/private key di chat. Jangan menganggap IP atau konfigurasi buku sebagai keadaan aktual tanpa pemeriksaan.
