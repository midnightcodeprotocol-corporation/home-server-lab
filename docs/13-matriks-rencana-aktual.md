# Matriks rencana aplikasi vs kondisi aktual

**Audit dokumen:** 4 November 2026. Ini membandingkan rencana buku dengan kondisi yang sudah diverifikasi; rencana lama tidak dianggap sebagai instalasi.

## Ringkasan

- Host Proxmox 9.2.24 aktif. Audit live 4 Nov menunjukkan CT101–105, CT109–112 dan VM202/VM212 berjalan; CT100/VM200 adalah template stopped dan VM201 `docker-core` sengaja stopped.
- CT104 `docker-services` (`192.168.88.20`) masih host Docker untuk layanan yang belum dipindahkan. Prometheus dan Grafana telah dipisahkan ke CT110/111; CT104 dipertahankan sebagai rollback.
- Aplikasi inti yang sudah berjalan: AdGuard Home, Samba, Tailscale, Docker/Portainer, Jellyfin, Immich, Nextcloud, Uptime Kuma, Prometheus, Grafana, Gotify, Beszel, Home Assistant OS, dan Proxmox Backup Server.
- “Berjalan” tidak selalu berarti penggunaannya sudah tuntas: ada pengujian klien, backup data, notifikasi, dan integrasi yang masih menunggu.
- Keputusan pengguna (3 Nov): Nextcloud menjadi layanan file utama keluarga; Samba melengkapi akses share PC/laptop; TrueNAS ditunda sebagai opsi pengelola storage. Lihat [rencana susunan guest dan keputusan NAS](14-usulan-isolasi-guest.md).

## Layanan aktif dan pekerjaan tersisa

| Layanan / rencana | Kondisi aktual terverifikasi | Status dan pekerjaan tersisa |
|---|---|---|
| Proxmox VE | PVE 9.2.24 di host `.10`; CT101–105, CT109–111, VM202, dan VM212 berjalan pada audit 4 Nov. | Aktif. Audit konfigurasi firewall, BIOS/MemTest86, dan dokumentasi pemulihan host masih tersisa. |
| AdGuard Home utama | STB HG680 `.3`; kueri DNS langsung berhasil. | Aktif di luar Proxmox. Failover DNS saat resolver utama mati belum diuji. |
| AdGuard Home kedua (CT101) | CT101 `.11`; UI dan port DNS aktif, kueri langsung berhasil. DHCP dilaporkan membagikan `.3` dan `.11`. | Aktif. Uji failover klien belum dilakukan. |
| Samba / NAS (CT102) | CT102 `.12`, Samba aktif dengan share `Media` dan `Files`; pengguna melaporkan password `labshare` sudah dibuat. | Layanan siap, tetapi uji login/akses dari Windows belum dicatat. Menghubungkan share ke Nextcloud dan akses dari ponsel ditunda atas permintaan pengguna. Samba sendiri tidak memiliki web UI. |
| Tailscale subnet router | CT103 aktif; alamat `.104` adalah lease DHCP yang teramati, bukan IP final. Route LAN muncul pada status node. Dari laptop, Immich `.20:2283` kini menjawab `pong`. | Berfungsi untuk jalur laptop yang diuji. Tailscale di ponsel harus tetap tersambung; uji ulang aplikasi Immich dari ponsel masih perlu dilakukan. Pemindahan router ke STB 2 tetap rencana setelah perangkat tersedia. |
| Docker dan Portainer | CT104 `.20` menjalankan Docker dan Portainer lama; CT105 Portainer Server baru aktif di lease DHCP `.105`, Docker CE 29.9.2/Compose 5.7.0, UI HTTPS `:9443` HTTP 200. Dashboard Portainer menunjukkan CT112-Gotify di `tcp://192.168.88.109:9001`, Agent 2.45.3, 2/2 container berjalan. VM201 `docker-core` stopped. | CT105 khusus untuk Portainer Server; setup admin selesai. Agent guest dibatasi hanya untuk source `.105`; koneksi tanpa signature memberi HTTP 403. `.105` static lease dilaporkan pengguna, DHCP guest tetap aktif. |
| Jellyfin | Container di CT104 sehat; port `:8096`. | Aktif. Pustaka dan alur akses klien dapat dilengkapi sesuai kebutuhan. |
| Immich | Container server, PostgreSQL, Redis, dan machine learning berjalan; server sehat. Endpoint `/api/server/ping` dari laptop mengembalikan `pong`. Data berada di HDD melalui `/srv/media/immich`. | Pengguna melaporkan upload selesai. Audit menghitung 10.638 baris asset vs catatan layar lama 12.923; rekonsiliasi masih perlu sebelum migrasi Immich. Dump DB baru lolos `gzip -t`; backup file terenkripsi masuk PBS (`host/immich-data/2026-11-03T15:00:28Z`). Restore penuh arsip lulus; dump hasil restore lolos gzip dan SHA-256 cocok dengan sumber. Immich belum masuk monitor Uptime Kuma. |
| Nextcloud | Nextcloud 35.0.2.2 di CT104 `:8080`, MariaDB/Redis sehat; pengguna melaporkan login ulang dan uji upload/download satu file berhasil. | Aktif. Akses ponsel/jaringan luar belum diverifikasi; share Samba belum disambungkan (ditunda). VM207 tidak dibuat. |
| Uptime Kuma | CT109 `.106:3001`, versi 2.5.9, container healthy; UI mengembalikan HTTP 302. Data dipindahkan dari CT104, SQLite integrity `ok`, 14 monitor tersalin. Monitor Gotify `.109:8070/health` memberi HTTP 200. | Aktif di guest khusus. Monitor self-check diarahkan ke `.106:3001`, Grafana ke `.108:3000`. Notifikasi default Gotify memakai `.109:8070`; Test memberi sukses. Immich belum dimonitor. Lease static `.106` dilaporkan pengguna, alamat guest aktif diverifikasi. |
| Prometheus + PVE exporter | CT110 `.107`, Prometheus 3.15.1 dan exporter 3.11.0 berjalan. API port 9090 hanya menerima CT104 `.20` dan CT111 `.108`. Dari Grafana CT111, kedua target scrape `prometheus`/`proxmox` berstatus `up`. | Aktif di guest khusus. Pengguna melaporkan static lease `.107`; alamat aktif `.107` dikonfirmasi dari CT110. RouterOS tidak diaudit langsung. Container lama CT104 stopped sebagai rollback. |
| Grafana | CT111 `.108:3000`, versi 13.3.0; `/api/health` HTTP 200. API menampilkan dashboard `Home Server Overview` dan datasource `Prometheus` mengarah ke `.107:9090`. Database SQLite integrity `ok`; pengguna mengonfirmasi login berhasil 4 Nov. | Aktif di guest khusus. Pengguna melaporkan static lease `.108`; alamat aktif `.108` dikonfirmasi dari CT111. RouterOS tidak diaudit langsung. Grafana lama CT104 stopped sebagai rollback; monitor Kuma ke `.108:3000` terverifikasi. |
| Gotify | CT112 `.109:8070`, versi 3.1.1 healthy; `/health` menyatakan health/database green, SQLite integrity `ok`. Data final disalin konsisten saat CT104 berhenti; SHA-256 cocok. PVE target `gotify-proxmox` mengarah `.109`, matcher `gotify-all` aktif, PVE test sukses. Test Uptime Kuma sukses; monitor Gotify HTTP 200. Portainer environment berjalan 2/2 container. Backup PBS terenkripsi pascamigrasi sukses. CT104 Gotify stopped sebagai rollback. | Pengguna perlu memperbarui dan menguji aplikasi Gotify Android/iPhone sebelum melepas rollback. Setelah konfirmasi, Homepage CT115 menjadi tahap berikutnya; IP belum dialokasikan. Lease `.109` dilaporkan static; `D` WebFig adalah tombol disable. |
| Beszel | Hub CT104 `:8090`; agent Proxmox dan CT104 terhubung; ada monitor Beszel di Kuma. | Aktif. Log pembacaan SMART pernah menunjukkan kegagalan pada NVMe dan `/dev/sda`; data SMART belum terverifikasi. |
| Home Assistant | VM202 `haos` berjalan di `.21`; wizard selesai menurut pengguna. | OS aktif. Integrasi perangkat rumah dan pemantauan dari luar belum dicatat tuntas. |
| PBS | VM212 `.30`; datastore `store1` dan storage PVE `pbs-store1` aktif. Job harian pukul 00.00 WIB untuk CT101–105, CT109–111, dan VM202, enkripsi sisi klien, retensi 7. Backup manual terenkripsi CT109–111 berhasil 4 Nov. | Aktif. Bind mount data aplikasi `backup=0` tidak ikut backup guest. Datastore 100 GiB berada di NVMe yang sama dengan PVE. Backup Immich file terpisah sudah ada dan restore arsip berhasil. Peringatan thin-pool overcommit perlu ditangani; pemakaian aktual terakhir 29.99%. |

## Rencana lama yang belum dipasang

| Aplikasi / VM target lama | Status sekarang |
|---|---|
| Caddy + sertifikat lokal | Belum dipasang; layanan saat ini diakses dengan IP/port masing-masing. |
| Homepage | Belum dipasang; tahap berikutnya setelah uji ponsel Gotify. Target CT115, IP belum dialokasikan. |
| k3s + Flux (VM203) | Belum dibuat/dipasang. |
| Forgejo + Renovate (VM204) | Belum dibuat/dipasang. |
| Password manager Vaultwarden (VM205) | Belum dipasang. Pengguna ingin menambahkan password manager nanti; rencana Vaultwarden masih perlu dipilih/dikonfirmasi saat waktunya. |
| AFFiNE (VM206) | Belum dibuat/dipasang. |
| n8n (VM208) | Belum dibuat/dipasang. |
| Situs privat / WordPress (VM209) | Belum dibuat/dipasang. |
| Cloudflare Tunnel / situs statis (VM210) | Opsional, belum dibuat. |
| Navidrome (VM211) | Belum dibuat/dipasang. |
| Pocket ID (VM213) | Belum dibuat/dipasang. |
| OnlyOffice | Belum dipasang; masih ada pada wishlist/roadmap. |
| AMP + playit.gg, Ollama, TrueNAS, server cetak, pemantauan listrik/panel surya | Wishlist atau opsi fase lanjut; belum dipasang. |

## Perubahan penempatan dari rencana

- **VM201 docker-core:** tetap stopped; sebagian besar layanan Docker dipindahkan/dikonsolidasikan di CT104 `.20`.
- **VM207 Nextcloud dan VM214 Immich:** tidak dibuat; kedua aplikasi berjalan di CT104.
- **Tailscale router:** saat ini CT103 di Proxmox, bukan STB 2. STB 2 masih belum tersedia.
- **PBS:** VM212 aktif, tetapi datastore sementara 100 GiB ditempatkan pada NVMe host. Pengguna menetapkan HDD untuk data aplikasi dan backup akan diperluas kemudian.

## Urutan pekerjaan yang disarankan

1. Setelah layanan baru diuji dari Android dan iPhone, lanjutkan Homepage di CT115; kemudian tambah monitor Immich ke Uptime Kuma.
2. Verifikasi hasil job harian PBS berikutnya dan event notifikasi Gotify. Rencanakan thin-pool autoextend setelah memeriksa prosedur resmi yang sesuai dengan Proxmox VE terpasang.
3. Rekonsiliasi hitungan ponsel Immich 12.923 vs 10.638 baris asset sebelum migrasi; pertahankan backup file/dump yang sudah diverifikasi.
4. Uji akses Immich dari ponsel melalui Tailscale; salinan asli ponsel tetap disimpan sampai hasil backup dan akses diverifikasi.
5. Uji akses share Samba dari Windows. Integrasi Samba–Nextcloud dan akses Samba dari ponsel tetap ditunda sampai pengguna meminta dilanjutkan.
6. **Gotify server selesai:** data sinkron, health/DB/PVE/Kuma/Portainer lulus dan backup pascamigrasi selesai. Pengguna perlu mengubah URL Gotify Android/iPhone menjadi `http://192.168.88.109:8070` dan menguji tiap klien. Pertahankan CT104 sebagai rollback hingga terkonfirmasi. Sesudahnya siapkan Homepage di CT115 (IP belum ditetapkan), baru lanjut ke Beszel, Jellyfin, Nextcloud, dan Immich terakhir.

Sumber utama status: `STATUS.md`, `data/guest.yaml`, `docs/04-board.md`, dan `catatan/hasil-uji.md`. Bila status matriks ini berbeda dari audit server terbaru, audit terbaru menjadi acuan dan matriks harus diperbarui.
