# Status Home Server Lab

**Fungsi repo:** buku catatan kerja/basis pengetahuan hidup untuk mengumpulkan ide, rencana, data, hasil percobaan, kendala, evaluasi kelayakan, keputusan, dan optimasi. Buku/PDF adalah keluaran turunan opsional. Arah ini dicatat 7 November 2026; tidak ada perubahan server yang dilakukan.

**Audit live terakhir: 6 November 2026.** Snapshot dan rincian: [inventaris live](docs/16-inventaris-live-2026-11-06.md).

Catatan perencanaan menyeluruh sesi 7 November 2026: [arsitektur, fase, backup, keamanan, dan keputusan terbuka](perencanaan-arsitektur/README.md). Catatan itu bukan audit live dan tidak menandai pekerjaan implementasi sebagai selesai.

Pembaruan rencana 7 November: ditambahkan opsi Ollama untuk inferensi lokal CPU dan 9Router sebagai gateway API pada guest khusus setelah audit. Integrasi chat 9Router dengan backend Ollama belum dikonfirmasi; akses direncanakan hanya melalui LAN/tailnet.

Pembaruan rencana 7 November: ditambahkan skenario migrasi storage ke NAS serta opsi menambah node PVE kedua. Keduanya masih evaluasi masa depan; tujuan NAS dan pilihan host standalone/cluster/HA belum diputuskan.

Pembaruan rencana 7 November: ditambahkan unit AI/LLM khusus sebagai opsi terpisah dari node PVE kedua, dengan evaluasi workload, GPU/VRAM, daya, isolasi jaringan, privasi, backup, dan fallback.

Ringkasan percakapan Claude terkait dashboard Homepage diarsipkan di [arsip percakapan](arsip-percakapan/claude-homepage-2026-11-07/README.md); detailnya historis dan belum diverifikasi terhadap kondisi live.

## Kondisi aktual

- Proxmox VE 9.2.24 di 192.168.88.10, kernel 7.0.14-26-pve; RAM 23 GiB terlihat. PVE firewall global nonaktif.
- LXC aktif: CT101–112, CT115, CT119, CT121 (tidak termasuk 113/114); VM aktif: VM202 HAOS dan VM212 PBS. CT100/VM200 template berhenti; VM201 legacy berhenti.
- CT104 .20 tetap menjalankan Immich, Beszel, Portainer lama, serta DB/Redis Nextcloud rollback. Rincian guest, MAC, port, mount, resource, dan hasil HTTP ada di inventaris.
- CT121 Speedtest Tracker aktif di .115:8765, MAC BC:24:11:05:BE:F7. IP masih DHCP dinamis; RAM 512 MiB; onboot belum diset; tidak tercakup backup harian; Agent latest dapat diakses semua interface. Belum ada perubahan pada CT121.
- Storage: root 10/94 GiB; HDD 124 GiB/1.8 TiB; local 10.59%; local-lvm 39.77% data, 1.75% metadata; PBS 43.76%.
- Job home-lab-daily: setiap hari 00:00 WIB, snapshot/ZSTD, client-side encryption, keep-last 7; VMID 101–112, 115, 119, 202. CT121 tidak masuk. PBS VM212 disk 100 GiB ada di NVMe fisik yang sama dengan PVE. Bind mount HDD backup=0 tidak tercakup guest backup.
- RouterOS DHCP pool/reservation, firewall/NAT, dan port forwarding tidak diperiksa live sesi ini. DHCP static untuk beberapa guest adalah laporan pengguna, bukan verifikasi router.

## Endpoint utama

| Layanan | Endpoint |
|---|---|
| Proxmox / PBS | https://192.168.88.10:8006 / https://192.168.88.30:8007 |
| Portainer | https://192.168.88.105:9443 |
| Immich / Beszel | http://192.168.88.20:2283 / :8090 |
| Samba | Share Media, Immich, Files pada 192.168.88.12 |
| Jellyfin / Nextcloud | http://192.168.88.111:8096 / http://192.168.88.112:8080 |
| qBittorrent | http://192.168.88.114:8080; TCP/UDP 6881 |
| Kuma / Prometheus / Grafana | .106:3001 / .107:9090 / .108:3000 |
| Gotify / Homepage / n8n | .109:8070 / .110:3000 / .113:5678 |
| Speedtest Tracker | http://192.168.88.115:8765 (DHCP dinamis) |
| Home Assistant | http://192.168.88.21/; Observer :4357 |

## Langkah berikutnya

1. CT121: verifikasi lease MAC/IP di MikroTik, tetapkan reservasi, putuskan onboot, batasi Agent 9001 untuk CT105, masukkan ke backup, lalu cek backup dan data volume.
2. Tangani thin-pool autoextend/overcommit dan siapkan backup fisik/off-host. PBS satu NVMe bukan salinan independen; data bind mount perlu backup tersendiri.
3. Audit RouterOS DHCP, firewall, NAT, port-forward.
4. Otomasi media n8n: periksa item torrent paused; desain form sumber/kategori terpadu; isolasi folder tujuan kategori selain Jellyfin; uji klasifikasi/rename/Review/perpindahan end-to-end.
5. Rekonsiliasi aset Immich sebelum migrasi. Pertahankan CT104 rollback.
6. Ikuti [matriks aktual dan rencana](docs/13-matriks-rencana-aktual.md) dan [rencana isolasi guest](docs/14-usulan-isolasi-guest.md).

Daftar plan per CT/VM yang bisa dibuka langsung dari README: [Daftar plan pemasangan guest](docs/13-matriks-rencana-aktual.md#daftar-plan-pemasangan-guest). Target Navidrome lama CT121 tidak berlaku karena CT121 kini Speedtest Tracker; target pengganti belum ditetapkan.

Tidak ada konfigurasi server/router yang diubah dalam audit dokumentasi ini. Perintah format docker ps gagal dengan error `failed to execute template: template: :1:20: executing "" at <.Config.Image>: can't evaluate field Config in type *formatter.ContainerContext`; docker inspect kemudian berhasil. Tidak ada rahasia dicatat.

Lihat [port dan akses](docs/07-port-dan-akses.md), [papan kerja](docs/04-board.md), dan [hasil uji](catatan/hasil-uji.md).
