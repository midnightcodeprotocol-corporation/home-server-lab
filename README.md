# Home Server Lab

Buku panduan dan catatan konfigurasi home server pribadi di **Lenovo ThinkCentre M710q**: Proxmox VE, jaringan MikroTik, AdGuard Home, Tailscale, Docker, Caddy, Vaultwarden, Nextcloud, Immich, Proxmox Backup Server, dan lainnya.

> **Repo ini PRIVATE dan tidak boleh berisi rahasia.** Kata sandi, token, kunci SSH/age, `ENCRYPTION_KEY`, dan arsip backup tidak pernah di-commit (lihat `.gitignore`). Nilai asli disimpan di Vaultwarden. Di repo hanya ada contoh (`*.example`).

## Status (28 Oktober 2026)

- Mesin asli ada: **Lenovo ThinkCentre M710q**, Core i5-6500T (4 core/4 thread), RAM 16 GB terpasang, **cadangan RAM 16 GB dan 8 GB** (rencana 16+16 = 32 GB), **NVMe 500 GB**, HDD 2 TB sebagai disk data/backup.
- Buku di-**Revisi 3**: lab VMware (Model A) dan instal-ke-disk-dulu (Model C) dihapus. Lihat `docs/bab/REVISI-3.md`.
- Isi buku (Bab 1-56) sudah ditulis, **belum diuji di mesin asli**. Hasil uji dicatat di `catatan/hasil-uji.md`.

## Mulai dari sini

1. `docs/00-ide-awal.md` dan `docs/01-ide-akhir.md`
2. `docs/09-mulai-di-m710q.md` (urutan hari pertama: RAM, BIOS, USB, instal)
3. `docs/04-board.md` (papan kerja)
4. `docs/bab/` (isi buku per bab)

## Isi repo

| Folder / berkas | Isi |
|---|---|
| `docs/00-ide-awal.md` | Ide awal, prinsip, daftar keinginan |
| `docs/01-ide-akhir.md` | Target arsitektur, aturan penempatan, jalur akses |
| `docs/02-rangkaian-koneksi.md` | Kabel, alamat, alur DNS/akses/Tailscale/tunnel/backup/peringatan (diagram Mermaid) |
| `docs/03-pohon.md` | Pohon perangkat, ketergantungan, folder |
| `docs/04-board.md` | Board kanban |
| `docs/05-inventaris-perangkat.md` | Perangkat dan perannya |
| `docs/06-dasar-konsep.md` | Konsep dasar |
| `docs/07-port-dan-akses.md` | Tabel port dan matriks akses |
| `docs/08-keputusan.md` | Catatan keputusan |
| `docs/09-mulai-di-m710q.md` | Langkah pertama di mesin asli |
| `docs/11-rencana-kerja-ai-ssh.md` | Rencana koordinasi Codex dan Claude saat mengakses Proxmox lewat SSH |
| `docs/bab/edisi2/` | Bab 1-24 + lampiran (diekstrak dan direvisi) |
| `docs/bab/suplemen/` | Bab 25-56 + pengantar/penutup tiap bagian |
| `docs/bab/REVISI-3.md` | Daftar perubahan Revisi 3 |
| `docs/arsip/` | Teks buku sebelum Revisi 3 (tersimpan untuk riwayat) |
| `catatan/` | `belum-pasti.md`, `hasil-uji.md`, `kasus-nyata-lab.md` |
| `konfigurasi/server/` | Berkas konfigurasi sesuai jalur aslinya (`/opt/stacks/...`, `/etc/...`) |
| `konfigurasi/gitops/` | Manifest Flux, Kustomize, SOPS, Renovate |
| `konfigurasi/caddy`, `firewall`, `skrip`, `contoh-env` | Contoh Caddyfile, aturan firewall, skrip, `.env` |

**Catatan teknis penting.** Berkas YAML di `docs/bab/` dan `docs/arsip/` hasil ekstraksi teks kehilangan indentasinya. Gunakan `konfigurasi/` untuk berkas compose dan YAML: semuanya sudah dibuat ulang dengan indentasi benar dan lolos pemeriksaan sintaks YAML (belum dijalankan di server).

## Peta guest (Bab 48.3)

Jaringan `192.168.88.0/24` (MikroTik). Host Proxmox `192.168.88.10`, tanpa Docker dan tanpa aplikasi.

| VMID | Nama | IP | Isi |
|---|---|---|---|
| 9100 | tpl-debian-docker | - | Templat Debian 13 + Docker (tidak dinyalakan) |
| 201 | docker-core | .20 | Caddy, Portainer, Gotify, Uptime Kuma, Beszel hub, Homepage |
| 202 | haos | .21 | Home Assistant OS |
| 203 | k3s | .22 | Kubernetes + Flux |
| 204 | git | .23 | Forgejo + Renovate |
| 205 | vault | .24 | Vaultwarden (Tailscale Serve) |
| 206 | affine | .25 | AFFiNE |
| 207 | nextcloud | .26 | Nextcloud (kalender) |
| 208 | n8n | .27 | n8n |
| 209 | web | .28 | Situs statis, WordPress |
| 210 | web-public | .29 | Situs publik (opsional) |
| 211 | music | .31 | Navidrome |
| 212 | pbs | .30 | Proxmox Backup Server |
| 213 | sso | .32 | Pocket ID |
| 214 | immich | .33 | Immich |
| CT101 | adguard2 | .11 | AdGuard Home kedua |
| CT102 | files | .12 | Samba |
| CT103 | ts-router | - | Tailscale subnet router |
| STB 1 | - | .253 | AdGuard Home utama (di luar Proxmox) |

## Aturan kerja

- Perintah tanpa `sudo` (SSH sebagai user biasa lalu `su -`).
- Setiap bab memuat sisi server dan sisi klien (Windows, Android, iPhone).
- Setiap layanan di VM/LXC sendiri; bab pemasangan dibuka dengan Kotak Penempatan.
- Backup belum dianggap ada sebelum uji pulih berhasil (Bab 50.12).
- Uji satu langkah, catat hasil, baru lanjut.
