# Matriks rencana aplikasi vs kondisi aktual

**Audit dokumen:** 5 November 2026 (form intake magnet aktif dan redirect login terverifikasi; uji E2E menunggu magnet legal).

## Ringkasan

- Host Proxmox 9.2.24 aktif. Audit live 4 Nov menunjukkan CT104–107, CT109–112, CT115 berjalan; `backup-disk` dan `pbs-store1` aktif. PBS 42.38% terpakai; thin-pool `pve/data` 37.93% data / 1.69% metadata.
- CT104 `docker-services` (`192.168.88.20`) tetap host Docker untuk layanan yang belum dipindahkan. Jellyfin di CT106; Nextcloud dipindahkan ke CT107; monitoring ke CT109–111. CT104 app Nextcloud lama berhenti dan dipertahankan sebagai rollback.
- Aplikasi inti yang sudah berjalan: AdGuard Home, Samba, Tailscale, Docker/Portainer, Jellyfin, Immich, Nextcloud, Uptime Kuma, Prometheus, Grafana, Gotify, Beszel, Home Assistant OS, dan Proxmox Backup Server.
- “Berjalan” tidak selalu berarti penggunaannya sudah tuntas: ada pengujian klien, backup data, notifikasi, dan integrasi yang masih menunggu.
- Keputusan pengguna (3 Nov): Nextcloud menjadi layanan file utama keluarga; Samba melengkapi akses share PC/laptop; TrueNAS ditunda sebagai opsi pengelola storage. Lihat [rencana susunan guest dan keputusan NAS](14-usulan-isolasi-guest.md).

## Layanan aktif dan pekerjaan tersisa

| Layanan / rencana | Kondisi aktual terverifikasi | Status dan pekerjaan tersisa |
|---|---|---|
| Proxmox VE | PVE 9.2.24 di host `.10`; audit lanjutan live menunjukkan CT102, CT104, CT105, CT109–112, CT115 dan VM202 running; `backup-disk` aktif. | CT102/104 sempat gagal start ketika HDD belum muncul, lalu pulih setelah mount. Audit firewall, BIOS/MemTest86, dan dokumentasi pemulihan host masih tersisa. |
| AdGuard Home utama | STB HG680 `.3`; kueri DNS langsung berhasil. | Aktif di luar Proxmox. Failover DNS saat resolver utama mati belum diuji. |
| AdGuard Home kedua (CT101) | CT101 `.11`; UI dan port DNS aktif, kueri langsung berhasil. DHCP dilaporkan membagikan `.3` dan `.11`. | Aktif. Uji failover klien belum dilakukan. |
| Samba / NAS (CT102) | CT102 `.12`, `testparm` lulus, `smbd` aktif. `Media` menunjuk hanya `/srv/media/jellyfin`, `Immich` hanya `/srv/media/immich`, `Files` tetap `/srv/files`; `labshare` dapat menulis. | Pemisahan live lulus; autentikasi klien Windows belum diuji. Berkas contoh ada di `konfigurasi/server/etc/samba/smb.conf.media.example`. |
| Tailscale subnet router | CT103 aktif; alamat `.104` adalah lease DHCP yang teramati, bukan IP final. Route LAN muncul pada status node. Dari laptop, Immich `.20:2283` kini menjawab `pong`. | Berfungsi untuk jalur laptop yang diuji. Tailscale di ponsel harus tetap tersambung; uji ulang aplikasi Immich dari ponsel masih perlu dilakukan. Pemindahan router ke STB 2 tetap rencana setelah perangkat tersedia. |
| Docker dan Portainer | CT104 `.20` menjalankan Docker dan Portainer lama; CT105 Portainer Server baru aktif di lease DHCP `.105`, Docker CE 29.9.2/Compose 5.7.0, UI HTTPS `:9443` HTTP 200. Dashboard Portainer menunjukkan CT112-Gotify di `tcp://192.168.88.109:9001`, Agent 2.45.3, 2/2 container berjalan. VM201 `docker-core` stopped. | CT105 khusus untuk Portainer Server; setup admin selesai. Agent guest dibatasi hanya untuk source `.105`; koneksi tanpa signature memberi HTTP 403. `.105` static lease dilaporkan pengguna, DHCP guest tetap aktif. |
| Jellyfin | CT106 `.111:8096` healthy, `/System/Info/Public` HTTP 200. Mount HDD hanya folder Jellyfin ke `/srv/jellyfin`, lalu `/media` read-only; share Immich tidak terlihat di guest. | Pengguna mengonfirmasi Movies `/media/Movies`, Shows `/media/Shows`, pemantauan realtime, uji SMB Windows dan playback, environment Portainer serta akses klien sudah selesai. CT104 tetap rollback; backup CT tidak mencakup media `backup=0`. |
| Immich | Container server, PostgreSQL, Redis, dan machine learning berjalan sehat; endpoint `/api/server/ping` dari PVE mengembalikan `pong`. Data berada di HDD melalui `/srv/media/immich`. | Monitor Kuma `Immich` sudah ada dan heartbeat terakhir `Up / 200 - OK`. Pengguna melaporkan upload selesai. Rekonsiliasi 10.638 baris asset vs catatan ponsel lama 12.923 masih perlu sebelum migrasi. Backup media terenkripsi masuk PBS (`host/immich-data/2026-11-03T15:00:28Z`) dan restore penuh lulus; backup basis data tersedia. |
| Nextcloud | Nextcloud 35.0.2.2 aktif di CT107 `.112:8080`, MariaDB/Redis healthy; `occ status` installed, maintenance false, `needsDbUpgrade=false`; `status.php` HTTP 200 dari guest/PVE/laptop Windows. Lease static `.112` dan MAC cocok terlihat di WebFig. Data pada bind mount HDD `/srv/nextcloud-data`, owner www-data mode 750. Homepage `.110` dan Kuma monitor ID 8 mengarah ke `.112`; heartbeat Up. | Server cutover selesai; Portainer 4 container running, 2 healthy, 0 unhealthy. Backup akhir sumber dan backup CT107 pascamigrasi terenkripsi PBS sukses. Pengguna mengonfirmasi login dan unduh/uji klien pascamigrasi berhasil. CT104 app berhenti dan dipertahankan sebagai rollback; data bind mount `backup=0` tidak masuk backup CT. PBS ada pada NVMe host yang sama. Integrasi Samba–Nextcloud tetap ditunda. |
| Uptime Kuma | CT109 `.106:3001`, versi 2.5.9, container healthy; UI mengembalikan HTTP 302. Data dipindahkan dari CT104, SQLite integrity `ok`, 14 monitor tersalin. Monitor Gotify `.109:8070/health` memberi HTTP 200. | Aktif di guest khusus. Monitor self-check diarahkan ke `.106:3001`, Grafana ke `.108:3000`. Notifikasi default Gotify memakai `.109:8070`; Test memberi sukses. Monitor Immich telah ada dan heartbeat terakhir Up / HTTP 200. Lease static `.106` dilaporkan pengguna, alamat guest aktif diverifikasi. |
| Prometheus + PVE exporter | CT110 `.107`, Prometheus 3.15.1 dan exporter 3.11.0 berjalan. API port 9090 hanya menerima CT104 `.20` dan CT111 `.108`. Dari Grafana CT111, kedua target scrape `prometheus`/`proxmox` berstatus `up`. | Aktif di guest khusus. Pengguna melaporkan static lease `.107`; alamat aktif `.107` dikonfirmasi dari CT110. RouterOS tidak diaudit langsung. Container lama CT104 stopped sebagai rollback. |
| Grafana | CT111 `.108:3000`, versi 13.3.0; `/api/health` HTTP 200. API menampilkan dashboard `Home Server Overview` dan datasource `Prometheus` mengarah ke `.107:9090`. Database SQLite integrity `ok`; pengguna mengonfirmasi login berhasil 4 Nov. | Aktif di guest khusus. Pengguna melaporkan static lease `.108`; alamat aktif `.108` dikonfirmasi dari CT111. RouterOS tidak diaudit langsung. Grafana lama CT104 stopped sebagai rollback; monitor Kuma ke `.108:3000` terverifikasi. |
| Gotify | CT112 `.109:8070`, versi 3.1.1 healthy; `/health` menyatakan health/database green, SQLite integrity `ok`. Data final disalin konsisten saat CT104 berhenti; SHA-256 cocok. PVE target `gotify-proxmox` mengarah `.109`, matcher `gotify-all` aktif, PVE test sukses. Test Uptime Kuma sukses; monitor Gotify HTTP 200. Portainer environment berjalan 2/2 container. Backup PBS terenkripsi pascamigrasi sukses. CT104 Gotify stopped sebagai rollback. | Pengguna mengonfirmasi URL Android/iPhone sudah diperbarui dan notifikasi uji diterima. CT104 tetap dipertahankan sebagai rollback. Lease `.109` dilaporkan static; `D` WebFig adalah tombol disable. |
| Homepage | CT115 `.110:3000`, Homepage 2.7.0 container healthy dan HTTP 200; Agent 2.45.3 aktif pada 9001 dengan firewall hanya mengizinkan CT105. MAC `BC:24:11:3C:42:DC`; lease static dilaporkan pengguna. | Aktif, konfigurasi tautan layanan/layout selesai. Portainer menampilkan `CT115-Homepage` Up, 2/2 container. Backup PBS terenkripsi pasca-setup sukses. |
| qBittorrent | CT108 `.114`, Debian 13 unprivileged, Docker CE 29.9.3/Compose 5.7.0, qBittorrent 5.3.0 dan Agent 2.45.3 Up. WebUI HTTP 200. Default `/inbox` menuju Inbox Jellyfin; temp `/downloads/incomplete` menuju staging HDD terpisah. Mount CT tidak mencakup Movies/Shows atau Immich. Firewall Agent mengizinkan CT105 saja; probe CT105 204 dan CT104 timeout. Homepage card live HTTP 200. Portainer CT108 Up 2/2; Kuma monitor ID 15 Up/HTTP 200. DHCP static dilaporkan pengguna; alamat/MAC cocok di guest. Pengguna melaporkan password sudah diganti dan unduhan legal uji selesai; belum diverifikasi di daftar WebUI. Backup terakhir tercatat `ct/108/2026-11-05T05:02:52Z`, guest masuk job harian. | Instalasi/integrasi dasar lulus. Intake n8n belum diaktifkan dan belum ada uji torrent end-to-end. Bind mount Inbox/staging `backup=0`; PBS berada pada NVMe host yang sama. |
| Beszel | Hub CT104 `:8090`; agent Proxmox dan CT104 terhubung; ada monitor Beszel di Kuma. | Aktif. Log pembacaan SMART pernah menunjukkan kegagalan pada NVMe dan `/dev/sda`; data SMART belum terverifikasi. |
| Home Assistant | VM202 `haos` running di `.21`; ping dan MAC neighbor cocok. Observer `:4357` menyatakan Supervisor Connected dan Health Healthy; UI Core di HTTP `:80` merespons 200 dan `/auth/providers` mengembalikan Home Assistant Local. | Akses tersedia melalui `http://192.168.88.21/`. TCP 8123 tertutup [BELUM PASTI: penyebab port non-standar]; monitor Kuma ke port 80 Up. Integrasi perangkat dan akses luar belum tuntas. |
| PBS | VM212 `.30`; datastore `store1` dan storage PVE `pbs-store1` aktif, 43.03% terpakai pada audit live 5 Nov. Job harian `home-lab-daily` pukul 00.00 WIB meliputi CT101–112, CT115, CT119, VM202; snapshot/ZSTD, enkripsi sisi klien, retensi 7. Backup terenkripsi CT119 `ct/119/2026-11-05T06:26:52Z` sukses dan snapshot dihapus; CT108 terakhir tercatat `ct/108/2026-11-05T05:02:52Z`. | Aktif. Bind mount data Nextcloud/Jellyfin/Immich/Inbox/staging berflag `backup=0` tidak ikut backup guest dan perlu strategi backup file terpisah. Datastore 100 GiB berada pada NVMe yang sama dengan PVE. Thin-pool live 39.01% data/1.72% metadata; warning autoextend/overcommit tetap perlu ditangani. |

## Rencana lama yang belum dipasang

| Aplikasi / VM target lama | Status sekarang |
|---|---|
| Caddy + sertifikat lokal | Belum dipasang; layanan saat ini diakses dengan IP/port masing-masing. |
| Homepage | Sudah dipasang pada CT115 `.110:3000`, container healthy, HTTP 200; environment Portainer Up, Agent 2.45.3, 2/2 container. |
| k3s + Flux (VM203) | Belum dibuat/dipasang. |
| Forgejo + Renovate (VM204) | Belum dibuat/dipasang. |
| Password manager Vaultwarden (VM205) | Belum dipasang. Pengguna ingin menambahkan password manager nanti; rencana Vaultwarden masih perlu dipilih/dikonfirmasi saat waktunya. |
| AFFiNE (VM206) | Belum dibuat/dipasang. |
| n8n (CT119) | CT119 `.113` aktif; n8n 2.46.6, PostgreSQL 18, helper healthy; HTTP 200. Helper internal tanpa port host, mount terbatas ke media Jellyfin; Immich tidak terlihat. Helper kini rekursif dengan batas 16 tingkat; isolated test nested listing/move, byte match, dan traversal lulus. Parser film/episode/Review lulus. Live: tiga workflow tersimpan; intake magnet aktif, dua workflow lain nonaktif. Form Trigger 2.6 memakai n8n User Auth + execute permission. URL production `http://192.168.88.113:5678/form/media-torrent-intake`; GET tanpa login HTTP 302 ke autentikasi. Node webhookId terisi, path terdaftar setelah publish/restart. Form memvalidasi BTIH dan mengirim magnet ke qB `/inbox` dengan paused=true. | Akses form terverifikasi tetapi E2E qB belum diuji dan belum ada magnet pengguna yang diproses. Scheduler folder masih nonaktif; direct download tetap memerlukan guardrail SSRF/ukuran/tipe; ffprobe dan metadata/catalog/AI belum tersedia. Gunakan magnet legal yang dipilih pengguna dan periksa item paused sebelum memulai unduhan. Backup CT119 `ct/119/2026-11-05T06:26:52Z`; PBS satu NVMe dengan PVE. |
| Situs privat / WordPress (VM209) | Belum dibuat/dipasang. |
| Cloudflare Tunnel / situs statis (VM210) | Opsional, belum dibuat. |
| Navidrome (VM211) | Belum dibuat/dipasang. |
| Pocket ID (VM213) | Belum dibuat/dipasang. |
| OnlyOffice | Belum dipasang; masih ada pada wishlist/roadmap. |
| AMP + playit.gg, Ollama, TrueNAS, server cetak, pemantauan listrik/panel surya | Wishlist atau opsi fase lanjut; belum dipasang. |

## Perubahan penempatan dari rencana

- **VM201 docker-core:** tetap stopped; sebagian besar layanan Docker dipindahkan/dikonsolidasikan di CT104 `.20`.
- **VM207 Nextcloud dan VM214 Immich:** tidak dibuat; Nextcloud aktif di CT107 dan Immich tetap di CT104.
- **Tailscale router:** saat ini CT103 di Proxmox, bukan STB 2. STB 2 masih belum tersedia.
- **PBS:** VM212 aktif, tetapi datastore sementara 100 GiB ditempatkan pada NVMe host. Pengguna menetapkan HDD untuk data aplikasi dan backup akan diperluas kemudian.

## Urutan pekerjaan berikutnya (arahan pengguna, 4 November 2026)

1. **Selesai menurut konfirmasi pengguna:** login/unduh dan pengujian klien Nextcloud pascamigrasi berhasil. Simpan CT104 sebagai rollback sampai backup serta masa observasi dinilai cukup.
2. **Sedang berjalan:** implementasikan n8n CT119 untuk tiga intake (link download, link torrent, folder kumpulan) secara bertahap. CT108 qBittorrent sudah berjalan sebagai guest terpisah; koneksi API baca-saja lulus menurut laporan pengguna/live execution. Helper hanya mengakses folder Jellyfin. Intake magnet sekarang aktif dengan autentikasi n8n dan validasi BTIH; URL dan redirect login diuji. Berikutnya uji magnet legal pilihan pengguna lalu scheduler folder sebelum mengaktifkan pemindahan media.
3. Verifikasi hasil job harian PBS berikutnya dan event notifikasi Gotify. Rencanakan thin-pool autoextend setelah memeriksa prosedur resmi yang sesuai dengan Proxmox VE terpasang.
4. Rekonsiliasi hitungan ponsel Immich 12.923 vs 10.638 baris asset sebelum migrasi; pertahankan backup file/dump yang sudah diverifikasi.
5. Uji akses Immich dari ponsel melalui Tailscale; salinan asli ponsel tetap disimpan sampai hasil backup dan akses diverifikasi.
6. Uji akses share Samba dari Windows. Integrasi Samba–Nextcloud dan akses Samba dari ponsel tetap ditunda sampai pengguna meminta dilanjutkan.
7. Portainer Homepage dan monitor Immich Kuma sudah terverifikasi. Home Assistant bisa diakses di `http://192.168.88.21/`; penyebab port 8123 tertutup belum diketahui dan tidak menghalangi akses web saat ini.
8. Lanjutkan aplikasi lain menurut plan terbaru setelah otomasi media diuji; pertahankan guest sumber sebagai rollback sesuai tahap migrasi.

Sumber utama status: `STATUS.md`, `data/guest.yaml`, `docs/04-board.md`, dan `catatan/hasil-uji.md`. Bila status matriks ini berbeda dari audit server terbaru, audit terbaru menjadi acuan dan matriks harus diperbarui.
