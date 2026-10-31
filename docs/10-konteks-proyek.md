# 10 - Konteks proyek

Ringkasan agar AI atau orang baru langsung paham. Tanggal 2026.

## Pengguna
- Pemula di dunia server, belajar dari nol, berbahasa Indonesia.
- Perangkat: laptop Windows (AMD Ryzen 3 4300U) untuk administrasi (WinBox, browser, SSH); HP Android (ingin langkah Android **dan** iPhone di buku).
- Ingin buku panduan yang lengkap: penjelasan tiap perintah, sisi server dan sisi klien, masalah nyata dari proyek ini beserta solusinya.

## Preferensi kerja (dinyatakan pengguna)
- Pembaruan buku: **bertahap (fase)**, bukan sekaligus dan bukan tulis ulang total.
- Setiap bab: sisi server dan sisi klien (Windows, Android, iPhone); perintah tanpa `sudo`; periksa dokumentasi resmi; tandai hal tak pasti.
- Aturan penempatan (20 Okt): setiap aplikasi/container/Docker dipisah di VM atau container Proxmox sendiri; **setiap bab pemasangan dibuka dengan penjelasan: buat baru atau gabung ke yang sudah ada**.
- Sesi pengujian: satu langkah, konfirmasi hasil, baru lanjut; catat setiap penyimpangan; jangan menebak RAM/ID/IP, cek Lampiran B Edisi 2 dan Bab 48.3.
- Rencana buku: Edisi 2 + Suplemen 1-9 -> pengujian dari nol (Fase A) -> revisi dari log uji (Fase B) -> Suplemen 10 opsional (Fase C) -> mesin utama (Fase D) -> proyek daftar keinginan (Fase E).
- Keputusan penting (18 Okt): akses luar hanya lewat Tailscale; OnlyOffice untuk office; AFFiNE untuk catatan; Cloudflare Tunnel hanya opsi tambahan untuk situs statis.

## Garis waktu
| Tanggal | Peristiwa |
|---|---|
| 9-13 Okt | Mulai dari nol: AdGuard Home di STB HG680. Router bertingkat dibenahi: IndiHome (WiFi) -> TL-WR840N (WISP) -> MikroTik RB750GL -> AP TL-WR820N. STB dipindah ke eMMC, IP .253. AdGuard terpasang dan tes DNS lulus |
| 13-14 Okt | MikroTik di-hardening (layanan dimatikan, WinBox/SSH dibatasi LAN, backup awal). Tailscale ditunda menunggu STB 2 |
| 16 Okt | Rencana lab Proxmox nested di VMware (laptop + HDD 2 TB) karena mesin utama belum ada; buku pertama dibuat |
| 17 Okt | Edisi 2: kotak kode terpisah, tiga model instal Proxmox, Debian 13, tanpa sudo |
| 18-22 Okt | Suplemen 1-9 ditulis (Bab 25-56): keamanan dan Tailscale, Proxmox komputer bekas, monitoring, Caddy, hosting web dan n8n, Vaultwarden/AFFiNE/Nextcloud, peta penempatan dan PBS dan firewall dan audit, Navidrome, Pocket ID dan Immich dan profil RAM |
| 22 Okt | Rencana pengujian Fase A-E dibuat; prompt sesi pengujian dan templat catatan |
| 23-27 Okt | Pengujian lab VMware: bridged gagal (layanan `vmnetbridge` error 1060), Windows diinstal ulang, VMnet0 Bridged ke adaptor USB-LAN berhasil, lalu VM gagal menyala karena Hyper-V/Virtual Machine Platform aktif (dimatikan) |
| 24 Okt | Lembar Revisi 1 (errata E1-E6 dan kasus nyata) ditambahkan ke PDF |
| 28 Okt | **Mesin asli tiba: Lenovo ThinkCentre M710q.** Model A (VMware) dan Model C dihapus dari buku (Revisi 3). Repo GitHub dibuat sebagai basis pengetahuan lengkap |
| 31 Okt | RAM bawaan 8 GB × 2; modul pertama diganti dengan 16 GB sehingga kapasitas terpasang diperkirakan 24 GB (16+8). NVMe M.2 500 GB dipasang di slot 1. Verifikasi BIOS/MemTest86 dan instalasi Proxmox belum dicatat |

## Pelajaran dari lab VMware (sudah dihentikan)
Lab nested VMware memakan banyak waktu karena adaptor bridged, Hyper-V, dan instalasi VMware rusak sebagian. Detailnya ada di `catatan/kasus-nyata-lab.md`. Tidak diperlukan lagi karena Proxmox dipasang langsung di mesin asli.

## Daftar keinginan jangka panjang (urutan pengguna)
1. Home Assistant (plus buku perangkat yang kompatibel: kategori, foto, fungsi, kelebihan dan kekurangan)
2. NAS dengan Nextcloud / TrueNAS
3. Server hosting
4. Cetak dari mana saja (TP-Link MR3020)
5. Server backup
6. Code studio di browser
7. Server LLM (hanya bila perlu)
8. Internet kedua sebagai failover
9. Monitor listrik rumah
10. Panel surya

Ide lain: VM gaming PC (GPU passthrough), CubeCoders AMP + playit.gg, Ollama, Wake-on-LAN dari STB.

