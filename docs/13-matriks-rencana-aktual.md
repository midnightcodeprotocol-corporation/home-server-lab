# Matriks rencana vs aktual

**Audit live 6 November 2026.** RouterOS tidak diperiksa langsung; alamat DHCP static yang dilaporkan pengguna tetap ditandai sebagai laporan. Lengkapi rujukan di [inventaris live](16-inventaris-live-2026-11-06.md).

| ID | Layanan / guest | Kondisi aktual | Berikutnya |
|---|---|---|---|
| CT100 | Template Debian | Template berhenti | Pertahankan |
| CT101 | AdGuard kedua | Aktif .11 | Uji failover DNS |
| CT102 | Samba/files | Aktif .12, Media/Immich/Files | Verifikasi akses klien dan backup |
| CT103 | Tailscale router | Aktif .104 DHCP; tailnet .10 | Uji route/klien luar; IP LAN dinamis |
| CT104 | Docker services | Aktif .20; Immich, Beszel, Portainer lama, Nextcloud DB/Redis rollback | Pertahankan rollback; rekonsiliasi Immich |
| CT105 | Portainer | Aktif .105:9443 | Lease router belum diperiksa |
| CT106 | Jellyfin | Aktif .111:8096, media RO | Selesai menurut konfirmasi pengguna; simpan CT104 rollback |
| CT107 | Nextcloud | Aktif .112:8080; data HDD bind mount | Klien teruji menurut pengguna; backup bind mount sendiri |
| CT108 | qBittorrent | Aktif .114:8080, Inbox dan staging | Verifikasi item paused dan alur n8n |
| CT109 | Uptime Kuma | Aktif .106:3001 | Monitor berjalan; lease router belum diperiksa |
| CT110 | Prometheus | Aktif .107:9090 + exporter | Akses dibatasi; lease router belum diperiksa |
| CT111 | Grafana | Aktif .108:3000, Prometheus datasource | Aktif; lease router belum diperiksa |
| CT112 | Gotify | Aktif .109:8070 | Ponsel/notifikasi teruji menurut pengguna |
| CT115 | Homepage | Aktif .110:3000 | Aktif; lease router belum diperiksa |
| CT119 | n8n | Aktif .113:5678, PostgreSQL, helper | Form terpadu dan kategori lain belum selesai |
| CT121 | Speedtest Tracker | Aktif .115:8765; 512 MiB; DHCP dinamis; Agent exposed; onboot unset | DHCP, onboot, firewall Agent, backup perlu diselesaikan |
| VM200 | Template Debian | Stopped | Pertahankan |
| VM201 | Docker legacy | Stopped | Tidak dipakai arsitektur kini |
| VM202 | Home Assistant OS | Aktif .21 | UI dan Observer HTTP 200 |
| VM212 | PBS | Aktif .30; datastore disk di NVMe host | Backup fisik/off-host dibutuhkan; CT121 belum termasuk |
| CT114, CT116–118, CT120, CT122 | Caddy, Forgejo, Renovate, AFFiNE, WordPress, OnlyOffice | Tidak terlihat pada guest live | Rencana; jangan dipasang sebelum prioritas/kapasitas |
| VM203, VM205, VM210, VM213 | k3s, Vaultwarden, situs publik, SSO | Tidak terlihat aktif | Rencana lama/opsional |
| Immich | Migrasi dari CT104 | Masih aktif di CT104 | Rekonsiliasi aset + backup sebelum pindah |
| Otomasi media | n8n + qBittorrent | CT119 dan CT108 aktif | Form intake, routing aman dan end-to-end belum tuntas |
| Jaringan/backup | MikroTik, PBS, thin-pool | MikroTik tidak diaudit; PBS satu NVMe | Audit router, thin-pool dan salinan off-host |

Lease .105/.106/.107/.108/.109/.110/.112/.113/.114 pernah dilaporkan static oleh pengguna. Tidak ada pemeriksaan RouterOS live untuk memvalidasinya. CT121 .115 dinamis saat audit.
