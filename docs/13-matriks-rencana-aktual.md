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

## Daftar plan pemasangan guest

Baris berikut adalah rencana, bukan guest yang sudah dibuat. ID/IP hanya target lama yang masih dipertahankan bila belum bertentangan dengan keadaan live. IP target tidak dialokasikan dan wajib diperiksa konflik DHCP sebelum membuat guest.

| Tahap | Guest target | Layanan/isi | Ketergantungan dan catatan |
|---|---|---|---|
| Prioritas operasional | CT121 sudah ada | Speedtest Tracker | Bukan pemasangan baru. Tetapkan lease, onboot, firewall Agent dan backup sebelum menganggap siap produksi. |
| Prioritas operasional | CT119 + CT108 sudah ada | n8n + qBittorrent media automation | Selesaikan status paused, intake/kategori terpadu, tujuan folder terisolasi, dan uji end-to-end. |
| Migrasi lanjutan | Guest belum ditetapkan | Immich khusus | Saat ini masih CT104. Rekonsiliasi jumlah aset serta uji backup/restore sebelum menetapkan guest dan jadwal pindah. |
| Rencana | CT113 (usulan lama) | Beszel hub | Saat ini hub Beszel ada di CT104; belum dipindah. Verifikasi agent dan kebutuhan resource. |
| Rencana | CT114 (usulan) | Caddy + CA lokal | Belum dipasang. IP belum ditetapkan; layanan langsung tetap jadi akses pemulihan jika proxy mati. |
| Rencana | CT116 (usulan) | Forgejo | Belum dipasang; perlu putuskan akses SSH/Git dan backup repository. |
| Rencana | CT117 (usulan) | Renovate | Belum dipasang; bergantung pada Forgejo/repository yang dikelola. |
| Rencana | CT118 (usulan) | AFFiNE | Belum dipasang; evaluasi resource dan penyimpanan. |
| Rencana lama | VM203 | k3s + Flux | Belum dipasang; latihan opsional, CPU host hanya 4 thread. |
| Rencana lama | VM205 | Vaultwarden | Belum dipasang; layanan sensitif memerlukan backup dan akses privat yang dirancang dulu. |
| Rencana lama | VM210 | Situs statis publik + Cloudflare Tunnel | Belum dipasang; isolasi jaringan dari LAN wajib dirancang. |
| Rencana lama | VM213 | Pocket ID / SSO | Belum dipasang; evaluasi kebutuhan identity dan dampak bila layanan mati. |
| Rencana | CT120 (usulan) | WordPress | Belum dipasang; terpisah dari situs statis. |
| Rencana opsional | CT122 (usulan) | OnlyOffice | Belum dipasang; uji kebutuhan CPU/RAM terlebih dahulu. |
| Rencana belum dipetakan | Belum ditetapkan | Navidrome / musik | Target lama CT121 bentrok karena CT121 kini menjalankan Speedtest Tracker; VM211 dan alamat .31 muncul di data rencana legacy, tetapi belum disetujui sebagai target pengganti. |
| Wishlist | Belum ditetapkan | AMP/game server, Ollama, TrueNAS, server cetak, pemantauan listrik/panel surya | Jangan membuat guest sebelum ada kebutuhan, perangkat, kapasitas, dan rancangan backup yang jelas. |

### Urutan kerja yang sudah disepakati

1. Tuntaskan risiko backup/storage dan konfigurasi produksi CT121.
2. Selesaikan otomasi media CT119/CT108 tanpa akses tulis ke Immich.
3. Rekonsiliasi dan migrasikan Immich setelah backup serta pemulihannya teruji.
4. Setelah tahap tersebut, pilih satu rencana aplikasi berikutnya dari tabel. Urutan CT113/114/116+ belum dikonfirmasi ulang; jangan menganggap semuanya harus dipasang.

Tidak ada alamat IP yang ditetapkan untuk guest rencana pada tabel ini. Nomor ID usulan tidak berarti slot Proxmox sudah kosong atau aman dipakai; periksa keadaan live saat implementasi.

Lease .105/.106/.107/.108/.109/.110/.112/.113/.114 pernah dilaporkan static oleh pengguna. Tidak ada pemeriksaan RouterOS live untuk memvalidasinya. CT121 .115 dinamis saat audit.
