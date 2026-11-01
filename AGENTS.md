# AGENTS.md - panduan untuk AI (Claude, Gemini, ChatGPT, dan lainnya)

> English summary: this private repo is the complete knowledge base of a beginner's home-server project
> (Lenovo ThinkCentre M710q planned for Proxmox VE, MikroTik router, AdGuard Home on an STB, planned Tailscale, Docker services).
> Read the files in the order below, then continue the work. Answer the user in **Bahasa Indonesia**.

Anda membaca repo ini karena pengguna kehilangan riwayat chat atau memori. **Semua yang perlu Anda ketahui ada di sini.** Jangan menebak: bila sesuatu tidak ada di repo, tanyakan ke pengguna.

## 1. Baca berurutan

| Urut | Berkas | Isi |
|---|---|---|
| 1 | `STATUS.md` | Posisi terakhir, langkah berikutnya, masalah terbuka |
| 1a | `docs/11-rencana-kerja-ai-ssh.md` | Serah-terima dan koordinasi bila Codex/Claude mengakses server lewat SSH |
| 2 | `docs/10-konteks-proyek.md` | Siapa pengguna, riwayat proyek, preferensi kerja |
| 3 | `docs/00-ide-awal.md`, `docs/01-ide-akhir.md` | Tujuan dan target arsitektur |
| 4 | `docs/02-rangkaian-koneksi.md`, `docs/03-pohon.md` | Kabel, alamat, alur, ketergantungan |
| 5 | `docs/05-inventaris-perangkat.md`, `data/*.yaml` | Perangkat dan daftar VM/LXC (terstruktur) |
| 6 | `docs/07-port-dan-akses.md`, `docs/08-keputusan.md` | Port, akses, keputusan dan alasannya |
| 7 | `docs/04-board.md`, `catatan/hasil-uji.md` | Papan kerja dan hasil uji |
| 8 | `docs/bab/` | Isi buku per bab (Bab 1-56), `docs/bab/REVISI-4.md` untuk perubahan audit terbaru |
| 9 | `konfigurasi/` | Berkas konfigurasi siap pakai (indentasi benar) |
| 10 | `catatan/belum-pasti.md`, `catatan/kasus-nyata-lab.md` | Hal tak pasti dan masalah nyata |

Mesin pencari cepat: `data/guest.yaml` (VMID, IP, RAM, port), `data/perangkat.yaml`, `docs/07-port-dan-akses.md`.

## 2. Fakta kunci (jangan dilanggar)

- Pengguna **pemula**, berbahasa Indonesia, laptop Windows, HP Android (instruksi harus mencakup **Android dan iPhone**).
- Server: **Lenovo ThinkCentre M710q**, Core i5-6500T (4 core/4 thread). Per 1 November 2026, Proxmox VE 9.2.24 sudah diperbarui dan berjalan; kernel aktif `7.0.14-26-pve`, tanpa unit systemd gagal. RAM 16+8 GB dan Linux melaporkan 23 GiB; BIOS/MemTest86 belum diverifikasi. NVMe Samsung MZALQ512HALU-000L2 terdeteksi sebesar 476,9 GB. VT-x/KVM aktif setelah perbaikan lewat thinklmi tanpa monitor; VT-d tetap Disabled. Jaringan host sementara `192.168.0.200/24`; alamat rumah `.88.10` belum diterapkan. Dua HDD Seagate Surveillance 2 TB belum tersambung; enclosure single-bay ditemukan tetapi belum diuji. Template Debian 13 VM 200 `Template-VM` dan CT 100 `Template-CT` sudah dibuat; paket VM dan hasil clone belum diverifikasi. **Tidak ada VMware** dan tidak ada "instal ke disk dulu" (dihapus di Revisi 3).
- Jaringan: IndiHome (WiFi) -> TL-WR840N (WISP) -> MikroTik RB750GL `192.168.88.1/24` -> AP TL-WR820N, STB, Proxmox `.10`, VM `.20-.33`. AdGuard utama di STB HG680 `.253` (di luar Proxmox).
- Akses jarak jauh untuk administrasi dan layanan privat **direncanakan lewat Tailscale**; saat ini Tailscale belum diterapkan. Tidak ada port forwarding. `tailscale funnel` tidak dipakai. Cloudflare Tunnel hanya opsi untuk menerbitkan situs statis dari VM 210.
- Satu layanan = satu VM/LXC (kecuali kelompok ringan di `docker-core`). Setiap bab pemasangan dibuka dengan **Kotak Penempatan**.
- Host Proxmox **tanpa Docker dan tanpa aplikasi**.
- Domain lokal `*.home.arpa` (Caddy, CA lokal). Layanan sensitif (Vaultwarden, Navidrome, Pocket ID, Immich) lewat Tailscale Serve `*.ts.net`.
- Nomor VM, IP, dan RAM: pakai `data/guest.yaml` dan Bab 48.3. **Jangan mengarang nilai.**

## 3. Cara membantu pengguna

1. **Satu langkah, konfirmasi hasil, baru lanjut.** Jangan memberi 20 perintah sekaligus.
2. Perintah **tanpa `sudo`** (SSH sebagai user biasa lalu `su -`, atau sebagai root di Proxmox).
3. Setiap penjelasan memuat **sisi server dan sisi klien** (Windows, Android, iPhone).
4. Perintah di kotak kode, satu perintah per kotak, dengan penjelasan singkat.
5. Tandai hal yang tidak pasti dengan **[BELUM PASTI]** dan jujur bila belum diverifikasi. Periksa dokumentasi resmi sebelum menulis perintah baru.
6. Catat setiap penyimpangan dan pesan error persis ke `catatan/hasil-uji.md`.
7. Untuk pembaruan buku: bertahap (fase), **bukan tulis ulang total**.
8. Perintah destruktif (instal Proxmox, format disk, wipe, `qm destroy`, firewall, SSH hanya kunci) **wajib diperingatkan dulu**, dengan jalur darurat.

## 4. Keamanan

- Repo ini private dan **tidak boleh berisi rahasia**: kata sandi, token (Tailscale, Cloudflare, Forgejo, Renovate, Gotify, Telegram), kunci SSH/age, `ENCRYPTION_KEY`, kunci enkripsi backup, arsip `/etc/pve`. `.gitignore` menolaknya.
- Jangan pernah meminta pengguna menempelkan rahasia ke chat. Minta mereka menyimpannya di Vaultwarden.
- Berkas `*.example` hanya berisi contoh. Nilai asli diisi pengguna sendiri.

## 5. Keterbatasan repo yang perlu Anda tahu

- Isi `docs/bab/` diekstrak dari teks buku. Sebagian blok konfigurasi kehilangan indentasi atau pagar kode; gunakan `konfigurasi/` untuk konfigurasi siap pakai dan jangan menganggap teks bab sebagai berkas yang dapat langsung ditempel.
- Seluruh isi buku **belum diuji**. Hasil uji ada di `catatan/hasil-uji.md`. Jangan menganggap perintah pasti benar.
- Butir [BELUM PASTI] terkumpul di `catatan/belum-pasti.md`.
- Lembar Revisi 1 (errata E1-E6) tidak ada di repo; lihat `catatan/kasus-nyata-lab.md` untuk ringkasannya.

## 6. Memperbarui repo setiap sesi

1. Ubah `STATUS.md` (posisi, langkah berikutnya, masalah terbuka, tanggal).
2. Isi `catatan/hasil-uji.md` (lulus / gagal / perlu revisi, error persis).
3. Pindahkan kartu di `docs/04-board.md`.
4. Bila ada keputusan baru, tambahkan ke `docs/08-keputusan.md`.
5. Bila isi bab berubah, ubah berkas di `docs/bab/` dan catat di `docs/bab/REVISI-3.md` (atau buat `REVISI-4.md`).
6. Pesan commit: `bab X: hasil uji` atau `status: tanggal`.
