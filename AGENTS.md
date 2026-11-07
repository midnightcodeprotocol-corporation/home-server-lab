# AGENTS.md - panduan untuk AI (Claude, Gemini, ChatGPT, dan lainnya)

> **Peringatan kesegaran:** bagian “Fakta kunci” dan sejumlah catatan bab di bawah berisi snapshot historis yang sudah kedaluwarsa. Untuk keadaan aktual server, baca `STATUS.md` dan khususnya `docs/16-inventaris-live-2026-11-06.md` terlebih dahulu. Snapshot 6 Nov menyatakan CT121 berjalan, CT107 Nextcloud aktif, CT106 Jellyfin aktif, CT108 qBittorrent aktif, CT119 n8n aktif, serta ada guest tambahan; fakta lama yang menyebut hanya CT104 aktif tidak lagi berlaku. Cocokkan lagi dengan server sebelum setiap perubahan.

> English summary: this private repo is the complete knowledge base of a beginner's home-server project
> (Lenovo ThinkCentre M710q planned for Proxmox VE, MikroTik router, AdGuard Home on an STB, planned Tailscale, Docker services).
> This repository is a living project notebook for ideas, plans, data, experiments, obstacles, feasibility, and optimization. The handbook/PDF is an optional downstream presentation, not the repository's primary purpose. Read the files below as needed and answer in **Bahasa Indonesia**.

Anda membaca repo ini karena pengguna kehilangan riwayat chat atau memori. **Semua yang perlu Anda ketahui ada di sini.** Jangan menebak: bila sesuatu tidak ada di repo, tanyakan ke pengguna.

## 1. Baca berurutan

| Urut | Berkas | Isi |
|---|---|---|
| 1 | `STATUS.md` | Posisi terakhir, langkah berikutnya, masalah terbuka |
| 1a | `laboratorium/README.md` | Cara mengumpulkan ide, rencana, data, percobaan, kendala, kelayakan dan optimasi |
| 1b | `docs/16-inventaris-live-2026-11-06.md` | Snapshot live terakhir yang terdokumentasi; bukan status saat ini tanpa audit ulang |
| 1c | `docs/11-rencana-kerja-ai-ssh.md` | Serah-terima/koordinasi bila akses SSH memang diminta |
| 2 | `docs/10-konteks-proyek.md`, `docs/00-ide-awal.md`, `docs/01-ide-akhir.md` | Konteks, kebutuhan dan arsitektur target |
| 3 | `docs/02-rangkaian-koneksi.md`, `docs/03-pohon.md`, `docs/05-inventaris-perangkat.md`, `data/*.yaml` | Topologi, dependensi dan data terstruktur |
| 4 | `docs/07-port-dan-akses.md`, `docs/08-keputusan.md`, `docs/13-matriks-rencana-aktual.md` | Akses, keputusan, rencana dan aktual |
| 5 | `docs/04-board.md`, `catatan/hasil-uji.md`, `laboratorium/` | Pekerjaan, hasil eksperimen, kendala dan evaluasi |
| 6 | `konfigurasi/` | Konfigurasi contoh (bukan rahasia; bukan otomatis live) |
| 7 | `catatan/belum-pasti.md`, `catatan/kasus-nyata-lab.md` | Ketidakpastian dan masalah nyata |
| 8 | `docs/bab/`, `tools/book_builder/` | Materi buku/PDF turunan opsional; bukan catatan sumber tunggal |

Mesin pencari cepat: `data/guest.yaml` (VMID, IP, RAM, port), `data/perangkat.yaml`, `docs/07-port-dan-akses.md`.

## 2. Fakta kunci (jangan dilanggar)

- Pengguna **pemula**, berbahasa Indonesia, laptop Windows, HP Android (instruksi harus mencakup **Android dan iPhone**).
- Server: **Lenovo ThinkCentre M710q**, Core i5-6500T (4 core/4 thread). Per 2 November 2026, Proxmox VE 9.2.24 berjalan; kernel terakhir tercatat `7.0.14-26-pve`, RAM 16+8 GB dan Linux melaporkan 23 GiB, BIOS/MemTest86 belum diverifikasi. NVMe Samsung MZALQ512HALU-000L2 476,9 GB; VT-x/KVM aktif; VT-d Disabled. Host `192.168.88.10/24`, DNS `.3`; `apt update` terbaru berhasil dari Debian dan repo Proxmox, dan tiga update security (`libnss3`, `vim-common`, `vim-tiny`) telah diterapkan 2 Nov. Gangguan sementara sebelumnya ke `117.120.5.231` tidak berulang pada apt update. Kabel Proxmox ke switch port 3, switch port 1 ke MikroTik ether4; ether2 kosong sebagai calon WAN2. DHCP Network MikroTik terlihat memakai `192.168.88.0/24`, gateway `.1`, DNS `.3`. CT101 dan VM201 stopped/onboot=0; CT104 running dengan lease sementara `.101`, hanya Portainer aktif. PVE SSH audit berhasil menggunakan HostKeyAlias lama yang telah diverifikasi; MikroTik SSH belum berhasil. HDD Seagate 2 TB sedang tidak dipasang (konfirmasi pengguna 2 Nov); saat terpasang 1 Nov terlihat NTFS/SMART PASSED. HDD kedua menunggu enclosure. Jangan menganggap konfigurasi buku sebagai keadaan aktual tanpa pemeriksaan.
- Guest per audit SSH 2 Nov: CT101 dan VM201 stopped/onboot=0; CT104 running pada lease DHCP sementara `.101` (bukan alokasi final), hanya Portainer aktif. IP target guest lainnya adalah rencana dan tidak boleh dianggap aktual. `lsblk` hanya menemukan NVMe; HDD 2 TB yang tampak di screenshot Proxmox sehari sebelumnya kini tidak terdeteksi [BELUM PASTI: sebab].
- Jaringan: IndiHome (WiFi) -> TL-WR840N (WISP) -> MikroTik RB750GL `192.168.88.1/24` -> AP TL-WR820N, STB, Proxmox `.10`, guest memakai DHCP. WinBox DHCP Network menunjukkan DNS `.3`; AdGuard utama di STB HG680 `.3` (static DHCP lease; di luar Proxmox).
- Akses jarak jauh untuk administrasi dan layanan privat **direncanakan lewat Tailscale**; saat ini Tailscale belum diterapkan. Tidak ada port forwarding. `tailscale funnel` tidak dipakai. Cloudflare Tunnel hanya opsi untuk menerbitkan situs statis dari VM 210.
- Rencana penempatan di beberapa bab berbeda dari rencana status/Data; rekonsiliasi dulu sebelum instalasi. Jangan anggap layanan rencana sudah dipasang. Setiap bab pemasangan dibuka dengan **Kotak Penempatan**.
- Host Proxmox **tanpa Docker dan tanpa aplikasi**.
- Domain lokal `*.home.arpa` (Caddy, CA lokal). Layanan sensitif (Vaultwarden, Navidrome, Pocket ID, Immich) lewat Tailscale Serve `*.ts.net`.
- Nomor VM, IP, dan RAM: pakai `data/guest.yaml` dan Bab 48.3. **Jangan mengarang nilai.**

## 3. Cara membantu pengguna

1. **Satu langkah, konfirmasi hasil, baru lanjut.** Jangan memberi 20 perintah sekaligus.
2. Perintah **tanpa `sudo`** (SSH sebagai user biasa lalu `su -`, atau sebagai root di Proxmox).
3. Setiap penjelasan memuat **sisi server dan sisi klien** (Windows, Android, iPhone).
4. Perintah di kotak kode, satu perintah per kotak, dengan penjelasan singkat.
5. Tandai hal yang tidak pasti dengan **[BELUM PASTI]** dan jujur bila belum diverifikasi. Periksa dokumentasi resmi sebelum menulis perintah baru.
6. Catat hasil uji ringkas di `catatan/hasil-uji.md`; percobaan panjang memakai `laboratorium/percobaan/TEMPLATE.md`. Sanitasi pesan error sebelum dicatat.
7. Kumpulkan ide, laporan kendala, evaluasi kelayakan, dan optimasi memakai indeks/template di `laboratorium/`. Jangan mencampur ide dengan keputusan atau rencana dengan hasil yang benar-benar dijalankan.
8. Perbarui pengetahuan bertahap. Handbook/PDF boleh dirapikan jika diminta atau bermanfaat, tetapi jangan menjadikannya sasaran yang memaksa semua temuan masuk ke bab buku.
9. Perintah destruktif (instal Proxmox, format disk, wipe, `qm destroy`, firewall, SSH hanya kunci) **wajib diperingatkan dulu**, dengan jalur darurat.

## 4. Keamanan

- Repo ini private dan **tidak boleh berisi rahasia**: kata sandi, token (Tailscale, Cloudflare, Forgejo, Renovate, Gotify, Telegram), kunci SSH/age, `ENCRYPTION_KEY`, kunci enkripsi backup, arsip `/etc/pve`. `.gitignore` menolaknya.
- Jangan pernah meminta pengguna menempelkan rahasia ke chat. Minta mereka menyimpannya di Vaultwarden.
- Berkas `*.example` hanya berisi contoh. Nilai asli diisi pengguna sendiri.

## 5. Keterbatasan repo yang perlu Anda tahu

- `docs/bab/` dan PDF adalah materi panduan turunan dan dapat tertinggal dari catatan sumber. Sebagian blok konfigurasi kehilangan indentasi/pagar kode; gunakan `konfigurasi/` sebagai contoh yang dirapikan, lalu tetap validasi sebelum pemakaian.
- Isi buku **belum seluruhnya diuji**. Bukti pengamatan dan eksperimen ada di `docs/16-inventaris-live-2026-11-06.md`, `catatan/hasil-uji.md`, dan laporan `laboratorium/percobaan/`. Jangan menganggap perintah atau isi buku pasti benar.
- Butir [BELUM PASTI] terkumpul di `catatan/belum-pasti.md`.
- Lembar Revisi 1 (errata E1-E6) tidak ada di repo; lihat `catatan/kasus-nyata-lab.md` untuk ringkasannya.

## 6. Memperbarui repo setiap sesi

1. Ubah `STATUS.md` (posisi, langkah berikutnya, masalah terbuka, tanggal).
2. Catat pengamatan/data dengan tanggal dan sumber; bedakan live, laporan, historis, rencana, dan belum diverifikasi.
3. Catat hasil percobaan/kendala/evaluasi di kategori yang sesuai; tautkan ke rencana, data, dan keputusan terkait.
4. Pindahkan kartu `docs/04-board.md` bila prioritas/tahap kerja berubah.
5. Bila ada keputusan baru, tambahkan ke `docs/08-keputusan.md` dengan alasan dan tanggal.
6. Perbarui `docs/bab/` atau bangun PDF hanya bila handbook diminta atau perubahan itu memang membantu penyajian; pertahankan catatan sumber di kategorinya.
7. Pesan commit menjelaskan isi, misalnya `catatan: hasil uji DNS 2026-11-07` atau `docs: rencana backup bind mount`.
