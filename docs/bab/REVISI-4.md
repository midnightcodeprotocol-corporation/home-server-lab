# Revisi 4: Perbaikan hasil audit

**Tanggal:** 30 Oktober 2026  
**Cakupan:** koreksi keamanan dan persistensi konfigurasi; tidak ada perubahan yang diterapkan ke server.

| Berkas / bab | Perbaikan |
|---|---|
| Bab 26 dan konfigurasi Tailscale | Akses ke subnet rumah dan node layanan dibatasi ke `group:home-admins`; anggota tailnet lain tidak mendapat akses LAN otomatis. Contoh ACL lama diperbaiki agar wildcard tidak memakai escape yang tidak valid. Ganti alamat contoh dengan akun Tailscale admin Anda sebelum memakai kebijakan. |
| Bab 44 | Contoh akses Tailscale Serve diselaraskan dengan grup admin dan keterangan `autogroup:self` diperjelas. |
| Bab 42 dan Compose n8n | Volume PostgreSQL 18 dipindahkan ke direktori induk yang benar dan `PGDATA` disetel ke `/var/lib/postgresql/18/docker`, agar data tetap berada pada volume yang dimaksud. |
| Compose Vaultwarden | Pendaftaran akun dimatikan pada konfigurasi referensi. Panduan instalasi masih menjelaskan kapan pendaftaran perlu dibuka sementara untuk membuat akun pertama, lalu ditutup. |
| `.gitignore` | Tambah perlindungan untuk nama umum kunci SSH, varian `.env`, arsip/dump database, dan state kredensial Cloudflare/Tailscale lokal. |

## Batas verifikasi

Perbaikan ini diperiksa secara statis. Server Proxmox belum terpasang, sehingga Compose, kebijakan Tailscale, firewall Proxmox, dan pemulihan backup belum diuji pada mesin nyata. Catat hasil pengujian pada `catatan/hasil-uji.md`.
