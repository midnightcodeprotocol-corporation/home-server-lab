# 04 - Board proyek

Papan kanban. Perbarui dengan mencentang atau memindah baris. Status per 5 November 2026 (form magnet aktif dan akses login terverifikasi; E2E menunggu magnet legal pengguna).

## Sedang dikerjakan
- [x] **Uji klien Nextcloud pascamigrasi:** pengguna mengonfirmasi login dan unduh berkas berhasil. Server CT107 `.112:8080`, status OCC/HTTP, Portainer, Homepage/Kuma dan backup sudah diverifikasi. CT104 app berhenti dan masih disimpan sebagai rollback.
- [ ] **Otomasi media n8n CT119 + qBittorrent CT108:** helper recursive dan parser film/episode/review lulus uji terisolasi. Form production aktif di `http://192.168.88.113:5678/form/media-torrent-intake`; Form Trigger v2.6 mewajibkan login n8n serta execute permission, GET tanpa login HTTP 302. Workflow memvalidasi BTIH dan mengantrekan ke `/inbox` dalam keadaan paused. Setelah validator diperbaiki tanpa global `URL`, execution n8n terbaru ID 13 berstatus `success` dan node qB mengirim `paused=true` ke `/inbox`. Status item paused di WebUI belum dibaca langsung. Pengguna meminta satu form dengan pilihan sumber dan kategori (film/series/music/dokumen/game/other); routing tujuan selain Jellyfin butuh storage/mount terpisah. Scheduler folder, direct download ber-guardrail, ffprobe/katalog, dan routing kategori lain belum diuji. File film dari PC dapat disalin lewat SMB Media; Inbox belum auto-sort karena scheduler belum aktif. Backup CT119 `ct/119/2026-11-05T06:26:52Z`; CT108 terakhir `ct/108/2026-11-05T05:02:52Z`.
- [x] **Jellyfin CT106:** pengguna mengonfirmasi library Movies `/media/Movies` dan Shows `/media/Shows`, pemantauan realtime, salin dari Windows melalui SMB, pemutaran video, environment Portainer dan akses perangkat klien sudah selesai. CT104 tetap rollback.
- [x] **Gotify CT112 dan klien:** pengguna mengonfirmasi Android/iPhone memakai `http://192.168.88.109:8070` dan notifikasi uji diterima. Health/database, tes PVE, tes Kuma, dan backup terenkripsi lulus. CT104 Gotify tetap dihentikan sebagai rollback.
- [x] **Portainer CT115:** environment `CT115-Homepage` tampil `Up`; Portainer Agent 2.45.3 dan 2/2 container terdeteksi.
- [x] **Fase A: sambungan dasar ke MikroTik.** Host Proxmox `.10` dan gateway `.1` saling terjangkau; DNS dan `apt update` berhasil. AdGuard STB `.3` melayani kueri langsung; WinBox DHCP Network menunjukkan gateway `.1` dan DNS `.3`. Kabel host lewat switch port 3.

## Siap berikutnya (Backlog Fase A, urut)
- [x] Homepage khusus CT115 terpasang di `.110:3000`, HTTP 200/container healthy; link dashboard telah diarahkan ke layanan aktif; backup PBS pasca-setup berhasil.
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
- [x] CT105 `portainer` dibuat dari CT100 Debian 13; unprivileged + nesting, 1 vCPU/1 GiB RAM/8 GiB, onboot=1. Docker CE 29.9.2 + Compose 5.7.0 aktif; setup admin selesai. DHCP static lease `.105` dilaporkan pengguna; alamat aktif dan MAC CT105 dikonfirmasi dari PVE. Screenshot dashboard menunjukkan Agent 2.45.3 CT104 `Up` dengan 16/16 container. Firewall persistensi di CT104 mengizinkan hanya source `.105` ke TCP 9001, memblokir source IPv4 lain dan IPv6; pada 4 Nov pengguna mengonfirmasi environment tetap `Up` setelah firewall aktif. Portainer lama CT104 dipertahankan selama transisi.
- [x] CT109 `uptime-kuma` dibuat dari CT100 Debian 13 pada 4 Nov; 1 vCPU/1 GiB, rootfs diperbesar ke 16 GiB, static lease DHCP `.106` dilaporkan pengguna (MAC `BC:24:11:84:70:ED`), alamat aktif terverifikasi. Docker CE 29.9.2, Compose 5.7.0, Portainer Agent 2.45.3 aktif. Agent dibatasi ke CT105 `.105`; pengguna melaporkan environment CT109 ditambahkan ke Portainer. Uptime Kuma 2.5.9 dipindahkan ke CT109, SQLite integrity `ok`, 14 monitor tersalin, HTTP UI merespons 302, container healthy. CT104 lama dihentikan sebagai rollback.
- [x] CT110 `prometheus` dibuat dari CT100 Debian 13; 1 vCPU/1 GiB/512 MiB swap/rootfs 8 GiB, Docker CE 29.9.2 dan Compose 5.7.0 aktif. Prometheus 3.15.1 + PVE exporter 3.11.0 pindah dari CT104; kedua target `up` diverifikasi dari Grafana CT111. API Prometheus `.107:9090` hanya mengizinkan CT104 `.20` dan CT111 `.108`; Agent 2.45.3 hanya mengizinkan CT105 `.105`; environment CT110 dilaporkan terdaftar di Portainer; pengguna melaporkan static lease `.107`, RouterOS belum diaudit langsung. Backup terenkripsi CT110 sukses di PBS.
- [x] CT111 `grafana` dibuat dari CT100 Debian 13; 1 vCPU/1 GiB, rootfs diperbesar 8→12 GiB, Docker CE 29.9.2/Compose 5.7.0 dan Agent 2.45.3 aktif. Grafana 13.3.0 pindah ke `.108:3000`; API health HTTP 200, `Home Server Overview` muncul dan datasource `Prometheus` menunjuk `.107:9090`; pengguna mengonfirmasi login berhasil 4 Nov. Data SQLite integrity `ok`; firewall Agent hanya mengizinkan CT105 `.105`; environment CT111 dilaporkan terdaftar di Portainer. Pengguna melaporkan static lease `.108`; RouterOS belum diaudit langsung. Backup terenkripsi CT111 sukses di PBS. Grafana lama CT104 stopped untuk rollback.
- [x] Immich Compose di CT104; media di HDD `/srv/media/immich`, database di `/opt/immich/postgres`; empat container healthy. Pengguna melaporkan upload selesai. Dump DB post-upload lulus `gzip -t`; folder Immich 18.194 GiB masuk PBS terenkripsi sebagai `host/immich-data/2026-11-03T15:00:28Z`. Restore penuh lulus; dump hasil restore lolos gzip dan SHA-256 cocok dengan sumber. Rekonsiliasi hitungan ponsel (total lama 12.923) dengan database (10.638 baris) masih perlu sebelum migrasi Immich. Salinan asli ponsel tetap dipertahankan.
- [x] Nextcloud 35.0.2.2 dipindahkan ke CT107 `.112:8080`; server HTTP/OCC, Portainer, Homepage/Kuma, backup, rollback, dan uji klien pascamigrasi (menurut konfirmasi pengguna) selesai.
- [x] VM202 HAOS 18.4 dibuat dari image resmi dengan checksum cocok dan running (2 vCPU, 2 GiB, UEFI, disk 32 GiB, onboot); lease DHCP `.21` serta onboarding HTTP 200 terverifikasi, admin selesai menurut pengguna.
- [x] Prometheus 3.15.1 + PVE exporter 3.11.0 kini di CT110; Grafana 13.3.0 di CT111. Target Prometheus/PVE `up`, dashboard `Home Server Overview` tersedia dan datasource terhubung. Stack lama CT104 dihentikan untuk rollback.
- [ ] Suplemen 1 (Bab 25-26): keamanan dasar dan Tailscale
- [x] Uptime Kuma 2.5.9 aktif di CT109 `.106:3001`; 14 monitor/data dipertahankan saat migrasi. Monitor self-check Kuma `.106:3001` dan Grafana `.108:3000` diverifikasi; monitor Immich sudah ada dan heartbeat terakhir `Up / 200 - OK`.
- [x] Gotify 3.1.1 dipindahkan dari CT104 ke CT112 `.109:8070`; DB konsisten, SHA-256 cocok, SQLite integrity `ok`, health green. Pengguna mengonfirmasi URL Android/iPhone diperbarui dan uji notifikasi diterima. CT104 Gotify dihentikan sebagai rollback.
- [x] PVE endpoint/matcher Gotify diarahkan ke CT112 dan tes target berhasil. Notifikasi Uptime Kuma diarahkan ke `.109` dan tes sukses; monitor Gotify `/health` mendapat HTTP 200. Klien Android/iPhone diuji pengguna; CT104 tetap disimpan sementara sebagai rollback.
- [x] Beszel hub terpasang di CT104 `.20:8090`; halaman `/_/` HTTP 200, akun pertama dibuat pengguna, agent Proxmox dan CT104 tersambung lewat WebSocket, dan monitor Beszel aktif di Kuma. Pembacaan SMART masih perlu diselesaikan; target PVE → Gotify dan Uptime Kuma → Gotify telah diuji sukses.
- [ ] Suplemen 4 (Bab 35-38): Caddy dan sertifikat lokal
- [ ] Bab 15, 21, 22: Forgejo, Flux, Renovate
- [ ] Suplemen 5 (Bab 39-43): web, WordPress, n8n, tunnel
- [ ] Suplemen 6 (Bab 44-47): Vaultwarden, AFFiNE; Nextcloud sudah dipindah ke CT107 dan klien pascamigrasi dikonfirmasi lulus
- [x] PBS VM212 berjalan dengan disk sementara 100 GiB di NVMe. Storage `pbs-store1` aktif; jadwal `home-lab-daily` pukul 00.00 WIB mencakup CT101–105, CT109–112, CT115, dan VM202 (snapshot/ZSTD, keep-last=7; PBS VM dan bind-mount `backup=0` dikecualikan). Enkripsi sisi klien aktif. Backup CT115 pasca-setup berhasil. Peringatan thin-pool overcommit muncul; pemakaian aktual 31.39% data / 1.48% metadata, autoextend masih perlu ditangani.
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
