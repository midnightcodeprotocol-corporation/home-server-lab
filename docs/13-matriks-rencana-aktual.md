# Matriks rencana aplikasi vs kondisi aktual

**Audit dokumen:** 3 November 2026. Ini membandingkan rencana buku dengan kondisi yang sudah diverifikasi; rencana lama tidak dianggap sebagai instalasi.

## Ringkasan

- Host Proxmox 9.2.24 aktif. Audit live terakhir menunjukkan CT101–104 dan VM202/VM212 berjalan; CT100/VM200 adalah template stopped dan VM201 `docker-core` sengaja stopped.
- CT104 `docker-services` (`192.168.88.20`) kini menjadi host Docker bersama untuk sebagian besar aplikasi. Ini menggantikan rencana VM201 untuk Docker dan target VM khusus Nextcloud/Immich.
- Aplikasi inti yang sudah berjalan: AdGuard Home, Samba, Tailscale, Docker/Portainer, Jellyfin, Immich, Nextcloud, Uptime Kuma, Prometheus, Grafana, Gotify, Beszel, Home Assistant OS, dan Proxmox Backup Server.
- “Berjalan” tidak selalu berarti penggunaannya sudah tuntas: ada pengujian klien, backup data, notifikasi, dan integrasi yang masih menunggu.

## Layanan aktif dan pekerjaan tersisa

| Layanan / rencana | Kondisi aktual terverifikasi | Status dan pekerjaan tersisa |
|---|---|---|
| Proxmox VE | PVE 9.2.24 di host `.10`; CT101–104 dan VM202/212 berjalan pada audit 3 Nov. | Aktif. Audit konfigurasi firewall, BIOS/MemTest86, dan dokumentasi pemulihan host masih tersisa. |
| AdGuard Home utama | STB HG680 `.3`; kueri DNS langsung berhasil. | Aktif di luar Proxmox. Failover DNS saat resolver utama mati belum diuji. |
| AdGuard Home kedua (CT101) | CT101 `.11`; UI dan port DNS aktif, kueri langsung berhasil. DHCP dilaporkan membagikan `.3` dan `.11`. | Aktif. Uji failover klien belum dilakukan. |
| Samba / NAS (CT102) | CT102 `.12`, Samba aktif dengan share `Media` dan `Files`; pengguna melaporkan password `labshare` sudah dibuat. | Layanan siap, tetapi uji login/akses dari Windows belum dicatat. Menghubungkan share ke Nextcloud dan akses dari ponsel ditunda atas permintaan pengguna. Samba sendiri tidak memiliki web UI. |
| Tailscale subnet router | CT103 aktif; alamat `.104` adalah lease DHCP yang teramati, bukan IP final. Route LAN muncul pada status node. Dari laptop, Immich `.20:2283` kini menjawab `pong`. | Berfungsi untuk jalur laptop yang diuji. Tailscale di ponsel harus tetap tersambung; uji ulang aplikasi Immich dari ponsel masih perlu dilakukan. Pemindahan router ke STB 2 tetap rencana setelah perangkat tersedia. |
| Docker dan Portainer | CT104 `.20` menjalankan Docker; UI Portainer di `:9443` dan setup awal selesai menurut pengguna. VM201 `docker-core` stopped. | Aktif di CT104, bukan VM201. Tidak perlu menyalakan VM201 untuk stack yang sekarang. |
| Jellyfin | Container di CT104 sehat; port `:8096`. | Aktif. Pustaka dan alur akses klien dapat dilengkapi sesuai kebutuhan. |
| Immich | Container server, PostgreSQL, Redis, dan machine learning berjalan; server sehat. Endpoint `/api/server/ping` dari laptop mengembalikan `pong`. Data berada di HDD melalui `/srv/media/immich`. | Aplikasi berjalan dan upload ponsel pernah dimulai; penyelesaian upload belum dikonfirmasi. Backup file media belum dilakukan; dump database perlu diperbarui setelah upload selesai. Immich belum masuk monitor Uptime Kuma. |
| Nextcloud | Nextcloud 35.0.2.2 di CT104 `:8080`, MariaDB/Redis sehat; pengguna melaporkan login ulang dan uji upload/download satu file berhasil. | Aktif. Akses ponsel/jaringan luar belum diverifikasi; share Samba belum disambungkan (ditunda). VM207 tidak dibuat. |
| Uptime Kuma | CT104 `:3001`, 13 monitor aktif pada audit terdahulu; container kini healthy. | Aktif. Immich belum dimonitor. Notifikasi Uptime Kuma → Gotify belum dikonfigurasi. |
| Prometheus + PVE exporter | Berjalan di CT104; target scrape Prometheus dan PVE pernah terverifikasi `up`; Prometheus hanya localhost CT104. | Aktif. Retensi dan akses terbatas sesuai catatan konfigurasi. |
| Grafana | Berjalan di CT104 `:3000`; datasource Prometheus dan dashboard `Home Server Overview` delapan panel telah dibuat. | Aktif; login selesai menurut pengguna. |
| Gotify | CT104 `:8070`, container sehat. Target PVE `gotify-proxmox` telah diuji oleh pengguna; matcher `gotify-all` mengirim semua notifikasi PVE ke Gotify. | Konfigurasi target/matcher aktif. Event PVE nyata yang tampil di ponsel belum diverifikasi. Matcher email bawaan tetap dipertahankan. |
| Beszel | Hub CT104 `:8090`; agent Proxmox dan CT104 terhubung; ada monitor Beszel di Kuma. | Aktif. Log pembacaan SMART pernah menunjukkan kegagalan pada NVMe dan `/dev/sda`; data SMART belum terverifikasi. |
| Home Assistant | VM202 `haos` berjalan di `.21`; wizard selesai menurut pengguna. | OS aktif. Integrasi perangkat rumah dan pemantauan dari luar belum dicatat tuntas. |
| PBS | VM212 `.30`; datastore `store1` dan storage PVE `pbs-store1` aktif. Job harian pukul 00.00 WIB untuk CT101–104 dan VM202, enkripsi sisi klien, retensi 7; uji restore CT101 ke CT109 lulus. | PBS aktif. Backup harian pertama masih perlu diverifikasi; bind mount data aplikasi `backup=0` tidak ikut backup guest. Datastore 100 GiB berada di NVMe yang sama dengan PVE, jadi belum menjadi salinan fisik terpisah. Backup media Immich belum dibuat. |

## Rencana lama yang belum dipasang

| Aplikasi / VM target lama | Status sekarang |
|---|---|
| Caddy + sertifikat lokal | Belum dipasang; layanan saat ini diakses dengan IP/port masing-masing. |
| Homepage | Belum dipasang. |
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

1. Setelah upload Immich selesai, buat backup terpisah untuk file media dan dump database, lalu verifikasi hasilnya di PBS.
2. Periksa hasil job PBS harian pertama dan event notifikasinya di Gotify.
3. Tambahkan monitor Immich di Uptime Kuma dan atur notifikasi Kuma → Gotify dengan aplikasi/token Gotify khusus.
4. Uji akses Immich dari ponsel melalui Tailscale; biarkan salinan foto asli di ponsel sampai backup diverifikasi.
5. Uji akses share Samba dari Windows. Integrasi Samba–Nextcloud dan akses Samba dari ponsel tetap ditunda sampai pengguna meminta dilanjutkan.
6. Pilih urutan aplikasi lanjutan dari daftar yang belum dipasang; jangan menghidupkan semua VM sekaligus pada CPU 4 thread.

Sumber utama status: `STATUS.md`, `data/guest.yaml`, `docs/04-board.md`, dan `catatan/hasil-uji.md`. Bila status matriks ini berbeda dari audit server terbaru, audit terbaru menjadi acuan dan matriks harus diperbarui.
