# 04 - Board proyek

Papan kanban. Perbarui dengan mencentang atau memindah baris. Status per 31 Oktober 2026.

## Sedang dikerjakan
- [ ] **Fase A: pengujian di mesin asli (ThinkCentre M710q)**, satu langkah per giliran. Proxmox sudah terpasang dan diperbarui; berikutnya buat template VM dan CT dasar sesuai `docs/09-mulai-di-m710q.md`.

## Siap berikutnya (Backlog Fase A, urut)
- [ ] Verifikasi RAM 24 GB (16+8) di BIOS, lalu jalankan MemTest86 (Bab 27.1, 27.3)
- [ ] Atur BIOS Lenovo (Bab 27.5)
- [x] Instal Proxmox pada M710q dan boot pertama
- [x] DNS host diperbaiki untuk jaringan sementara `192.168.0.0/24`; apt update dan upgrade berhasil, kernel `7.0.14-26-pve` aktif
- [ ] Sambungkan host kembali ke MikroTik dan tetapkan IP manajemen final; SSH TCP 22 dari Windows sudah terjangkau pada jaringan sementara
- [x] Setelah update Proxmox, cek KVM/VT-x: `lscpu` menunjukkan VT-x dan `/dev/kvm` tersedia setelah perbaikan `thinklmi` (Bab 9.6, 27.5)
- [ ] Buat template VM 9100 dan CT 9200 sebelum guest layanan, lalu clone dengan nama/IP/resource unik (Bab 49)
- [ ] Bab 30: sensor dan Wake-on-LAN dari STB
- [ ] Uji enclosure single-bay lama yang ditemukan; identifikasi satu HDD sebelum menentukan peruntukan atau memformat (Bab 27.4, 9.9)
- [ ] Bab 10-11: buat LXC dan VM aplikasi dari template
- [ ] Bab 13: AdGuard kedua + failover DNS
- [ ] Bab 14: Docker dan Portainer
- [ ] Suplemen 1 (Bab 25-26): keamanan dasar dan Tailscale
- [ ] Suplemen 3 (Bab 31-34): Gotify, Uptime Kuma, Beszel
- [ ] Suplemen 4 (Bab 35-38): Caddy dan sertifikat lokal
- [ ] Bab 15, 21, 22: Forgejo, Flux, Renovate
- [ ] Suplemen 5 (Bab 39-43): web, WordPress, n8n, tunnel
- [ ] Suplemen 6 (Bab 44-47): Vaultwarden, AFFiNE, Nextcloud
- [ ] Suplemen 7 (Bab 48-52): peta, templat 9100, PBS, firewall, audit
- [ ] Suplemen 8 (Bab 53): Navidrome
- [ ] Suplemen 9 (Bab 54-56): Pocket ID, Immich, profil RAM

Setiap bab: hasil (lulus / gagal / perlu revisi), pesan error persis, dan butir [BELUM PASTI] yang dicek (`catatan/belum-pasti.md`, `catatan/hasil-uji.md`).

## Selesai
- [x] Jaringan: TL-WR840N mode WISP -> MikroTik RB750GL (RouterOS 6.49.23, DHCP .100-.254)
- [x] MikroTik: layanan tak terpakai dimatikan, WinBox/SSH dibatasi LAN, MAC server dimatikan, backup awal
- [x] TL-WR820N mode Access Point di belakang MikroTik
- [x] STB HG680: Armbian v25.05.0 dipindah ke eMMC, IP .253 (static lease)
- [x] AdGuard Home di STB; tes `nslookup` lulus; DHCP MikroTik membagikan DNS .253
- [x] Backup `AdGuardHome.yaml` ke PC
- [x] Buku: Edisi 2 + Suplemen 1-9 (Bab 1-56) ditulis (belum diuji)
- [x] Mesin asli tiba: Lenovo ThinkCentre M710q
- [x] **Revisi 3:** Model A (VMware) dan Model C dihapus dari buku
- [x] **Revisi 4:** koreksi kebijakan Tailscale, volume PostgreSQL 18, dan signup Vaultwarden dicatat
- [x] Repo GitHub sebagai basis pengetahuan (AGENTS.md, STATUS.md, data, konfigurasi)

## Dihentikan
- [x] Lab Proxmox nested di VMware (laptop): dihentikan karena mesin asli sudah ada. Pelajaran: `catatan/kasus-nyata-lab.md`
- [x] Pemakaian PC HP lama (RAM 2 GB) sebagai server: tidak dipakai

## Ditunda / menunggu
- [ ] Tailscale subnet router di STB 2 (belum tiba; alamat usulan .250); sementara CT103 di Proxmox (Bab 26)
- [x] RAM 16 GB + 8 GB dipasang; total yang diharapkan 24 GB, verifikasi BIOS/MemTest86 masih perlu dilakukan
- [ ] HDD kedua ditunda; enclosure yang tersedia single-bay. Rencana awal memakai satu unit lebih dahulu

## Fase lanjutan (rencana)
Roadmap manfaat, keamanan, backup, monitoring, dan segmentasi: `docs/12-roadmap-manfaat-keamanan.md`.
**Fase B. Revisi dari log uji**
- [ ] Daftar errata dari hasil uji; jawab semua butir [BELUM PASTI]; Revisi 4 bertahap, bukan tulis ulang

**Fase C. Suplemen 10 (opsional)**
- [ ] CubeCoders AMP + playit.gg
- [ ] Ollama (butuh RAM besar; 32 GB membantu, tetapi CPU 4 thread terbatas)
- [ ] Katalog layanan kecil (tiap layanan VM/LXC sendiri + kotak penempatan)

**Fase D. Penyempurnaan setelah instalasi di M710q**
- [ ] Evaluasi penambahan RAM setelah kapasitas 24 GB diverifikasi dan beban layanan diukur
- [ ] OnlyOffice
- [ ] Tailscale subnet router dipindah ke STB 2
- [ ] Perbarui profil RAM Bab 56 sesuai pemakaian nyata

**Fase E. Proyek dari daftar keinginan**
- [ ] Home Assistant (+ buku perangkat yang kompatibel: kategori, foto, fungsi, kelebihan dan kekurangan)
- [ ] NAS Nextcloud / TrueNAS
- [ ] Hosting server
- [ ] Cetak dari mana saja (TP-Link MR3020)
- [ ] Server backup
- [ ] Code studio di browser
- [ ] Server LLM (hanya bila perlu)
- [ ] Internet kedua sebagai failover
- [ ] Monitor listrik rumah
- [ ] Panel surya
- [ ] (Ide) VM gaming PC dengan GPU passthrough (i5-6500T hanya iGPU; kemungkinan besar tidak cocok)

## Aturan kerja sesi pengujian
Satu langkah, konfirmasi hasil, baru lanjut. Catat setiap penyimpangan. Jangan menebak nilai RAM / ID / IP; cek `data/guest.yaml` dan Bab 48.3. Perintah tanpa `sudo`. Sisi server dan sisi klien (Windows, Android, iPhone).
