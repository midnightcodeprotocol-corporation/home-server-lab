# 04 - Board proyek

Papan kanban. Perbarui dengan mencentang atau memindah baris. Status per 3 November 2026.

## Sedang dikerjakan
- [x] **Fase A: sambungan dasar ke MikroTik.** Host Proxmox `.10` dan gateway `.1` saling terjangkau; DNS dan `apt update` berhasil. AdGuard STB `.3` melayani kueri langsung; WinBox DHCP Network menunjukkan gateway `.1` dan DNS `.3`. Kabel host lewat switch port 3.

## Siap berikutnya (Backlog Fase A, urut)
- [ ] Verifikasi RAM 24 GB (16+8) di BIOS, lalu jalankan MemTest86 (Bab 27.1, 27.3)
- [ ] Atur BIOS Lenovo (Bab 27.5)
- [x] Instal Proxmox pada M710q dan boot pertama
- [x] DNS host diperbaiki untuk jaringan sementara `192.168.0.0/24`; apt update dan upgrade berhasil, kernel `7.0.14-26-pve` aktif
- [x] APT update pada 2 Nov berhasil mengakses repo Debian dan Proxmox; konektivitas internet host terverifikasi. Gangguan sementara ke `117.120.5.231` sebelumnya tidak terulang; penyebabnya tidak diketahui. Simulasi upgrade hanya mencakup tiga update security (`libnss3`, `vim-common`, `vim-tiny`), tanpa paket baru/dihapus.
- [x] Terapkan tiga update security yang sudah ditinjau (`libnss3`, `vim-common`, `vim-tiny`); console kembali ke prompt root tanpa error yang terlihat.
- [x] Audit baca-saja Proxmox melalui SSH: CT101 dan VM201 stopped/onboot=0; CT104 running dengan lease DHCP sementara `.101`; hanya Portainer berjalan. MikroTik DHCP Network dilihat di WinBox; koneksi SSH MikroTik belum berhasil, tidak ada perubahan router.
- [x] Setelah update Proxmox, cek KVM/VT-x: `lscpu` menunjukkan VT-x dan `/dev/kvm` tersedia setelah perbaikan `thinklmi` (Bab 9.6, 27.5)
- [x] Audit dan perbaiki template Debian 13 CT 100/VM 200 setelah clone menemukan identitas bersama; clone uji lulus dan artefak sementara sudah dibersihkan. Lihat Revisi 7.
- [x] Uji clone sementara di jaringan router: CT lulus DHCP/DNS/SSH; VM lulus DHCP/DNS, QEMU Guest Agent, SSH, dan identitas unik. Semua guest uji dihapus setelah pengujian.
- [ ] Bab 30: sensor dan Wake-on-LAN dari STB
- [x] HDD unit 1 diaudit read-only (NTFS root hanya System Volume Information, 159 MB), SMART attributes PASSED (USB bridge status incomplete), lalu dibuat ext4 storage `backup-disk`; keputusan terbaru: kedua HDD untuk aplikasi, backup ditunda, HDD unit 2 menunggu enclosure (Bab 27.4, 9.9)
- [x] Bab 10-11: buat CT 101 `adguard2` dan VM 201 `docker-core` dari template bersih; boot DHCP sementara berhasil
- [x] Bab 13: CT101 `.11` statis, `onboot=1`, wizard selesai; port 53 listen; tes DNS dari Proxmox dan laptop lulus. Upstream Quad9 DoH + bootstrap independen dari STB untuk domain internet; private reverse DNS default masih ke `.3`. DHCP membagikan `.3` + `.11`, kueri default lulus via `.3`; failover belum diuji.
- [x] CT102 Samba `.12` aktif; share Media/Files mengarah ke HDD unit 1, konfigurasi `testparm` valid. Pengguna melaporkan password Samba `labshare` sudah ditetapkan; uji Windows masih pending.
- [x] CT103 Tailscale 1.104.4 online, forwarding/TUN aktif, route `192.168.88.0/24` tampil pada PrimaryRoutes; uji dari klien HP/laptop masih pending. Lease DHCP `.104` bersifat dinamis.
- [x] Buat CT104 `docker-services` dari CT100 sebagai Docker host (Debian 13 unprivileged + nesting); Docker/Compose aktif, Portainer CE berjalan pada HTTPS 9443
- [x] CT104 statis `.20/24` diterapkan di konfigurasi CT (di luar pool DHCP; tidak ada reservation MikroTik); Portainer HTTPS 9443 HTTP 200 dan Jellyfin healthy TCP 8096 diverifikasi setelah restart.
- [x] CT105 `portainer` dibuat dari CT100 Debian 13; unprivileged + nesting, 1 vCPU/1 GiB RAM/8 GiB, onboot=1. Docker CE 29.9.2 + Compose 5.7.0 aktif; Portainer CE LTS HTTPS 9443 HTTP 200; lease DHCP `.105` sementara, tidak ada static IP/reservasi; setup admin menunggu pengguna. Portainer CT104 dipertahankan selama transisi.
- [x] Immich Compose di CT104; media di HDD `/srv/media/immich`, database di `/opt/immich/postgres`; empat container healthy. Pengguna melaporkan upload selesai. Dump DB post-upload lulus `gzip -t`; folder Immich 18.194 GiB masuk PBS terenkripsi sebagai `host/immich-data/2026-11-03T15:00:28Z`. Restore penuh lulus; dump hasil restore lolos gzip dan SHA-256 cocok dengan sumber. Rekonsiliasi hitungan ponsel (total lama 12.923) dengan database (10.638 baris) masih perlu sebelum migrasi Immich. Salinan asli ponsel tetap dipertahankan.
- [x] Nextcloud 35.0.2.2 aktif di CT104 `.20:8080` dengan MariaDB/Redis sehat; pengguna melaporkan login awal, penggantian password, login ulang, serta uji upload/download satu berkas berhasil. Uji dari klien ponsel/jaringan luar belum dilakukan.
- [x] VM202 HAOS 18.4 dibuat dari image resmi dengan checksum cocok dan running (2 vCPU, 2 GiB, UEFI, disk 32 GiB, onboot); lease DHCP `.21` serta onboarding HTTP 200 terverifikasi, admin selesai menurut pengguna.
- [x] Prometheus 3.15.1 + PVE exporter 3.11.0 + Grafana 13.3.0 di CT104; target Prometheus/PVE `up`; dashboard `Home Server Overview` tampil dengan delapan panel (CPU/RAM host & guest, status target, pemakaian storage dan disk guest). File dashboard tervalidasi JSON dan telah dimuat setelah restart Grafana.
- [ ] Suplemen 1 (Bab 25-26): keamanan dasar dan Tailscale
- [x] Uptime Kuma 2.5.9 aktif di CT104 `.20:3001`; 13 monitor aktif termasuk Beszel, dan riwayat downtime dipertahankan. Samba menggunakan TCP 445. Immich belum ditambahkan ke monitor Kuma.
- [x] Gotify terpasang di CT104 `.20:8070`; Compose tervalidasi, container healthy, endpoint `/health` HTTP 200. Pengguna melaporkan login admin dan penggantian password selesai.
- [x] Pengguna membuat token aplikasi Gotify dan target `gotify-proxmox` PVE; pengguna mengonfirmasi tes target berhasil. Matcher `gotify-all` dibuat dan diarahkan ke target tersebut; matcher email bawaan dipertahankan. Penerimaan event PVE nyata dan notifikasi Uptime Kuma → Gotify masih belum diuji/dikonfigurasi.
- [x] Beszel hub terpasang di CT104 `.20:8090`; halaman `/_/` HTTP 200, akun pertama dibuat pengguna, agent Proxmox dan CT104 tersambung lewat WebSocket, dan monitor Beszel aktif di Kuma. Pembacaan SMART masih perlu diselesaikan; target/matcher PVE → Gotify sudah aktif, sedangkan event nyata dan integrasi Kuma → Gotify masih pending.
- [ ] Suplemen 4 (Bab 35-38): Caddy dan sertifikat lokal
- [ ] Bab 15, 21, 22: Forgejo, Flux, Renovate
- [ ] Suplemen 5 (Bab 39-43): web, WordPress, n8n, tunnel
- [ ] Suplemen 6 (Bab 44-47): Vaultwarden, AFFiNE; Nextcloud sudah dialihkan ke CT104 dan lulus pemeriksaan awal
- [x] PBS VM212 berjalan dengan disk sementara 100 GiB di NVMe. Storage `pbs-store1` aktif; jadwal `home-lab-daily` pukul 00.00 WIB untuk CT101–104 dan VM202 dibuat (snapshot/ZSTD, keep-last=7; PBS VM dan bind-mount `backup=0` dikecualikan). Enkripsi sisi klien aktif untuk backup mendatang; pengguna melaporkan paperkey disimpan dan salinan sementara dihapus. Backup uji CT101 terenkripsi berhasil dan arsip terlihat di PBS. Backup manual sebelumnya belum terenkripsi.
- [ ] Verifikasi job harian pertama untuk seluruh guest. Uji restore arsip terenkripsi CT101 ke CT109 sementara lulus (CT boot dengan NIC terputus, AdGuard aktif, HTTP 302); CT109 dan disk uji sudah dihapus. Backup Immich kini ada di PBS dan restore penuh lulus; rekonsiliasi jumlah asset masih pending.
- [ ] Suplemen 8 (Bab 53): Navidrome
- [ ] Suplemen 9 (Bab 54-56): Pocket ID, Immich, profil RAM

Setiap bab: hasil (lulus / gagal / perlu revisi), pesan error persis, dan butir [BELUM PASTI] yang dicek (`catatan/belum-pasti.md`, `catatan/hasil-uji.md`).

## Selesai
- [x] Jaringan: TL-WR840N mode WISP -> MikroTik RB750GL (RouterOS 6.49.23, DHCP .100-.254)
- [x] MikroTik: layanan tak terpakai dimatikan, WinBox/SSH dibatasi LAN, MAC server dimatikan, backup awal
- [x] TL-WR820N mode Access Point di belakang MikroTik
- [x] STB HG680: Armbian v25.05.0 dipindah ke eMMC; static lease dipindah dari .253 ke .3
- [x] AdGuard Home di STB; tes `nslookup` langsung ke .3 lulus; MikroTik membagikan DNS .3
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
- [ ] Atas permintaan pengguna (3 Nov 2026): tunda menghubungkan share Samba `Files` ke Nextcloud (external storage SMB/CIFS) dan mengatur akses Samba dari HP; ingatkan kembali nanti, waktu belum ditentukan.
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
