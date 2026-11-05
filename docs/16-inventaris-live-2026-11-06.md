# Inventaris live Home Server Lab — 6 November 2026

Audit baca-saja PVE/guest dan probe LAN. Nilai rahasia tidak dikumpulkan. Status adalah snapshot tanggal tersebut.

## Bukti dan batas audit

- SSH PVE 192.168.88.10 berhasil memakai HostKeyAlias 192.168.0.200.
- Alamat guest dan MAC dibaca dari Proxmox. Reservasi DHCP, pool, firewall/NAT, dan port-forward MikroTik tidak diperiksa langsung.
- Sebagian lease static adalah laporan pengguna dari sesi sebelumnya. CT121 .115 masih DHCP dinamis.
- PVE firewall service berjalan, tetapi firewall global PVE nonaktif.
- HTTP probe dari laptop mengukur keterjangkauan LAN, bukan login atau fungsi lengkap.
- Diagram kabel adalah catatan historis, tidak diverifikasi live pada tanggal ini.

## Host dan kapasitas

| Bagian | Kondisi |
|---|---|
| Server / PVE | Lenovo ThinkCentre M710q; PVE 9.2.24; kernel 7.0.14-26-pve |
| Uptime / load | sekitar 1 hari 16 jam; load 0.28–0.70 saat pemeriksaan |
| RAM | 23 GiB terlihat; 9.9 GiB terpakai, 13 GiB available; swap 1.7/8 GiB |
| Root PVE | 94 GiB total; 10 GiB used; 80 GiB free |
| HDD | /dev/sda1 ext4 di /mnt/pve/backup-disk; 1.8 TiB total, 124 GiB used, 1.6 TiB free |
| local | aktif, 10.59% used |
| local-lvm | aktif, 39.77% data, 1.75% metadata; peringatan autoextend/overcommit sebelumnya |
| PBS storage | pbs-store1 aktif, 43.76% used |
| PVE firewall | service berjalan; firewall global disabled |

## Guest live

Semua guest memakai vmbr0. DHCP tidak berarti alamat dijamin tetap.

| ID | Nama | IP, MAC | Resource | Peran |
|---|---|---|---|---|
| CT100 | Template-CT | — | Debian 13 | Template berhenti |
| CT101 | adguard2 | .11; BC:24:11:D5:DE:F2 | 1 CPU, 512 MiB, root 8 GiB | AdGuard; IP statis di config PVE |
| CT102 | files | .12; BC:24:11:97:FD:1D | 1 CPU, 512 MiB, root 8 GiB | Samba; bind mount HDD |
| CT103 | tailscale-router | .104 DHCP; BC:24:11:A9:16:BC; tailnet 100.119.135.10 | 1 CPU, 512 MiB | Tailscale subnet router |
| CT104 | docker-services | .20; BC:24:11:25:14:4B | 4 CPU, 8 GiB, swap 1 GiB, root 64 GiB | Immich, Beszel, Portainer lama, Nextcloud DB/Redis rollback |
| CT105 | portainer | .105 DHCP; BC:24:11:19:DA:40 | 1 CPU, 1 GiB, root 8 GiB | Portainer Server |
| CT106 | jellyfin | .111 DHCP; BC:24:11:9E:13:F4 | 1 CPU, 1 GiB, root 8 GiB | Jellyfin |
| CT107 | nextcloud | .112 DHCP; BC:24:11:0F:DA:1F | 2 CPU, 2 GiB, root 16 GiB | Nextcloud + MariaDB + Redis |
| CT108 | qbittorrent | .114 DHCP; BC:24:11:B9:6B:9D | 1 CPU, 1 GiB, root 8 GiB | qBittorrent |
| CT109 | uptime-kuma | .106 DHCP; BC:24:11:84:70:ED | 1 CPU, 1 GiB, root 16 GiB | Uptime Kuma |
| CT110 | prometheus | .107 DHCP; BC:24:11:A4:50:42 | 1 CPU, 1 GiB, root 8 GiB | Prometheus + PVE exporter |
| CT111 | grafana | .108 DHCP; BC:24:11:94:22:43 | 1 CPU, 1 GiB, root 12 GiB | Grafana |
| CT112 | gotify | .109 DHCP; BC:24:11:2F:EE:31 | 1 CPU, 512 MiB, root 8 GiB | Gotify |
| CT115 | homepage | .110 DHCP; BC:24:11:3C:42:DC | 1 CPU, 1 GiB, root 8 GiB | Homepage |
| CT119 | n8n | .113 DHCP; BC:24:11:7F:73:F6 | 2 CPU, 2 GiB, root 16 GiB | n8n + PostgreSQL + internal media helper |
| CT121 | Speedtest-tracker | .115 DHCP; BC:24:11:05:BE:F7 | 1 CPU, 512 MiB, swap 512 MiB, root 8 GiB | Speedtest Tracker; onboot unset; no bind mount; no PBS backup |
| VM200 | Template-VM | — | Debian | Template stopped |
| VM201 | docker-core | — | — | Legacy VM stopped |
| VM202 | haos | .21; BC:24:11:60:7C:42 | 2 CPU, 2 GiB, disk 32 GiB | Home Assistant OS |
| VM212 | pbs | .30; BC:24:11:09:FD:F1 | 2 CPU, 2 GiB, disks 32+100 GiB | PBS; data disk on same NVMe physical host |

Static lease .105/.106/.107/.108/.109/.110/.112/.113/.114 sebelumnya dilaporkan pengguna. Ini bukan audit RouterOS. CT104 .20 dan CT101/.11, CT102/.12 dikonfigurasi statis di PVE. CT103 .104 dan CT121 .115 dinamis.

## Aplikasi, port, dan keterhubungan

| Guest | Stack | Port LAN / hubungan |
|---|---|---|
| CT101 | AdGuard Home | DNS TCP/UDP 53; UI 80 di .11 |
| CT102 | Samba shares Media, Immich, Files | SMB TCP 445 di .12 |
| CT104 | Immich server v3 + PostgreSQL/ML/Redis; Beszel; Portainer lama; Nextcloud DB/Redis lama | .20:2283, :8090, :9443; exporter 9221 internal |
| CT105 | Portainer CE LTS | HTTPS .105:9443 |
| CT106 | Jellyfin; Agent 2.45.3 | .111:8096; Agent :9001 |
| CT107 | Nextcloud 35.0.2.2 + MariaDB + Redis; Agent 2.45.3 | .112:8080; Agent :9001 |
| CT108 | qBittorrent 5.3.0; Agent 2.45.3 | .114:8080; TCP/UDP 6881; Agent :9001 |
| CT109 | Uptime Kuma tag :2; Agent 2.45.3 | .106:3001; Agent :9001 |
| CT110 | Prometheus 3.15.1 + exporter 3.11.0; Agent 2.45.3 | .107:9090; exporter 9221 internal; Agent :9001 |
| CT111 | Grafana 13.3.0; Agent 2.45.3 | .108:3000; datasource Prometheus .107:9090; Agent :9001 |
| CT112 | Gotify gotify/server:latest; Agent 2.45.3 | .109:8070; Agent :9001 |
| CT115 | Homepage 2.7.0; Agent 2.45.3 | .110:3000; Agent :9001 |
| CT119 | n8n 2.46.6, PostgreSQL 18, media helper 1.0.0; Agent 2.45.3 | .113:5678; DB/helper internal; Agent :9001 |
| CT121 | Speedtest Tracker LinuxServer v1.15.1-ls179; Docker CE 29.9.3; Agent latest | port 8765→80 and Agent 9001 on all interfaces |

For CT106–112, CT115, CT119 guest firewall rules permit TCP 9001 only from CT105 .105 and drop other IPv4 sources. CT121 has no such restriction. Prometheus 9090 accepts Grafana .108 and legacy CT104 .20; laptop probe is denied. PVE global firewall remains off.

## HTTP probe LAN

| URL/path | Result |
|---|---|
| PVE .10:8006 HTTPS | 200 |
| PBS .30:8007 HTTPS | 200 |
| Portainer .105:9443 HTTPS | 200 |
| Immich .20:2283; Beszel .20:8090 | 200; 200 |
| Kuma .106:3001 | 302 login redirect |
| Prometheus .107:9090/-/healthy | 000; restricted |
| Grafana .108:3000/api/health | 200 |
| Gotify .109:8070/health | 200 |
| Homepage .110:3000 | 200 |
| Jellyfin .111:8096/System/Info/Public | 200 |
| Nextcloud .112:8080/status.php | 200 |
| n8n .113:5678/healthz | 200 |
| qBittorrent .114:8080 | 200 |
| Speedtest Tracker .115:8765 | 302 login redirect |
| HA .21 and Observer .21:4357 | 200; 200 |
| SMB, DNS, SSH, Agent | Configuration observed; not all TCP probes repeated |

## Media directories and connections

- HDD: /mnt/pve/backup-disk.
- CT102 share Media → /srv/media/jellyfin; Immich → /srv/media/immich; Files → /srv/files.
- Windows paths: \\192.168.88.12\Media, \\192.168.88.12\Immich, \\192.168.88.12\Files.
- CT106 sees only Jellyfin subtree read-only at /srv/jellyfin, published inside container as /media.
- CT108 sees Jellyfin Inbox at /srv/media-inbox→/inbox and torrent staging /srv/torrent→/downloads; it cannot access Movies, Shows, or Immich.
- CT119 sees the entire Jellyfin subtree read-write at /srv/media, including Inbox, Movies, Shows, Review. It cannot access Immich; this is broader write access than qBittorrent.
- CT104 Immich uses /srv/media/immich. CT107 Nextcloud data is a separate HDD bind mount.
- These HDD bind mounts use backup=0, so guest PBS archives exclude their data.

## Backup

- Job home-lab-daily: daily 00:00 WIB, snapshot, ZSTD, client-side encryption, keep-last 7.
- Actual VMID list: 101–112, 115, 119, 202. CT121 is missing.
- Latest visible entries CT108–119: 5 Nov 17:02–17:03 UTC (6 Nov 00:02–00:03 WIB). No CT121 backup entry.
- PBS VM212 virtual disk is on the same NVMe as PVE: no independent physical failure protection.
- Bind mounts marked backup=0 are excluded. Separate media/data backup and restore need independent verification.
- Capacity snapshot: PBS 43.76%; HDD 124 GiB used/1.8 TiB; local 10.59%; local-lvm 39.77% data/1.75% metadata; root 10/94 GiB.

## Pekerjaan terbuka dan perubahan keadaan

1. CT121: lease .115 DHCP dinamis; APP_URL mengarah ke .115:8765; onboot tidak diset; tidak tercakup PBS; Agent tag latest dipublish semua interface tanpa filter CT105. Belum ada perubahan live untuk menangani ini.
2. CT121 menggunakan 512 MiB, berbeda dari rencana setup 1 GiB. Schedule speed test tiap 30 menit; pertimbangkan dampak bandwidth.
3. RouterOS DHCP, firewall, NAT, port-forward dan pool belum diperiksa langsung.
4. Tinjau thin-pool autoextend/overcommit dan pastikan backup off-host untuk data penting.
5. n8n: verifikasi qBittorrent paused-state, form kategori terpadu, storage non-Jellyfin, rename/routing dan uji e2e masih terbuka. Hindari akses tulis Immich.
6. Rekonsiliasi aset Immich sebelum migrasi. CT104 tetap rollback.
7. Guest masa depan hanya tercatat sebagai rencana di matriks. Jangan menyimpulkan instalasi dari nomor ID atau bab buku.

## Sumber produk

Speedtest Tracker saat ini dijalankan sebagai Docker dalam LXC. Upstream menyebut Proxmox LXC tidak didukung sebagai metode instalasi: [panduan instalasi resmi](https://github.com/alexjustesen/speedtest-tracker-docs/blob/main/getting-started/installation/README.md). [Dokumentasi image LinuxServer](https://docs.linuxserver.io/images/docker-speedtest-tracker/).
