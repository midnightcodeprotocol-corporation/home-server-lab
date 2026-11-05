# Port dan akses layanan

**Snapshot live: 6 November 2026.** DHCP lease bisa berubah; reservasi RouterOS belum diverifikasi langsung. Port pada tabel adalah hasil konfigurasi/observasi LAN, bukan instruksi membuka akses internet.

| Guest | Layanan | IP:port | Hasil |
|---|---|---|---|
| PVE | Web UI / SSH | .10:8006 HTTPS / 22 | HTTPS 200; SSH audit berhasil |
| VM212 | PBS Web UI | .30:8007 HTTPS | 200 |
| CT101 | AdGuard DNS / UI | .11:53 TCP+UDP / 80 | service konfigurasi teramati |
| CT102 | Samba | .12:445 TCP | share Media, Immich, Files |
| CT104 | Immich / Beszel / Portainer lama | .20:2283 / 8090 / 9443 | Immich dan Beszel 200 |
| CT105 | Portainer | .105:9443 HTTPS | 200 |
| CT106 | Jellyfin / Agent | .111:8096 / 9001 | API 200; Agent dibatasi CT105 |
| CT107 | Nextcloud / Agent | .112:8080 / 9001 | status.php 200; Agent dibatasi CT105 |
| CT108 | qBittorrent / BitTorrent / Agent | .114:8080 / 6881 TCP+UDP / 9001 | Web 200; Agent dibatasi CT105 |
| CT109 | Kuma / Agent | .106:3001 / 9001 | 302 login; Agent dibatasi CT105 |
| CT110 | Prometheus / exporter / Agent | .107:9090 / 9221 internal / 9001 | Prometheus dibatasi; Agent CT105 |
| CT111 | Grafana / Agent | .108:3000 / 9001 | health 200; Agent CT105 |
| CT112 | Gotify / Agent | .109:8070 / 9001 | health 200; Agent CT105 |
| CT115 | Homepage / Agent | .110:3000 / 9001 | 200; Agent CT105 |
| CT119 | n8n / PostgreSQL / helper / Agent | .113:5678 / internal / 9001 | healthz 200; DB/helper internal; Agent CT105 |
| CT121 | Speedtest Tracker / Agent | .115:8765 / 9001 | 302 login; DHCP dinamis, Agent tanpa filter |
| VM202 | Home Assistant / Observer | .21:80 / 4357 | 200 / 200 |

## Samba Windows

- \\\\192.168.88.12\\Media → Jellyfin Movies/Shows/Inbox/Review.
- \\\\192.168.88.12\\Immich → dataset Immich terpisah.
- \\\\192.168.88.12\\Files → folder umum.
- Share writable untuk akun Samba labshare; kredensial tidak dicatat di repo.

## Pembatasan akses

- Agent TCP 9001 menerima sumber CT105 .105 pada CT106–112, CT115, CT119. CT121 tidak mempunyai pembatasan sumber yang sama dan menjadi pekerjaan terbuka.
- Prometheus 9090 menerima Grafana .108 dan legacy CT104 .20; akses laptop gagal sesuai aturan.
- PVE firewall service berjalan, tetapi firewall global PVE disabled.
- Router DHCP pool/reservations, firewall/NAT dan port-forward tidak diperiksa 6 Nov. Jangan anggap semua port-forward kosong.
- HTTP 200/302 bukan bukti login atau pengujian fitur penuh. Detail koneksi/storage ada di [inventaris live](16-inventaris-live-2026-11-06.md).
