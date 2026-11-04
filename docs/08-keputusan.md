# 08 - Catatan keputusan

| # | Keputusan | Alasan | Alternatif yang ditolak |
|---|---|---|---|
| 1 | Lab dulu (Model A), baru mesin asli | Nol biaya, bisa dihapus | Menunggu mesin datang |
| 2 | Yang kritis di luar Proxmox (MikroTik, AdGuard utama, Tailscale) | Internet dan akses jauh tidak boleh ikut mati | Semua di satu mesin |
| 3 | AdGuard Home, bukan Pi-hole | Ringan, DoH/DoT bawaan, aturan per klien | Pi-hole (tetap valid) |
| 4 | Dua DNS di DHCP (Opsi 1), bukan dnsdist | Tanpa titik gagal tunggal baru | Balancer sebagai satu-satunya DNS |
| 5 | Debian 13 untuk semua VM, perintah tanpa sudo | Konsisten; sudo tidak terpasang bila root diberi password | Ubuntu, sudo |
| 6 | Docker pada CT unprivileged 104 dengan nesting, sesuai persetujuan pengguna | Mengurangi jumlah VM dan memanfaatkan RAM/CPU; menerima isolasi lebih rendah dibanding VM | VM khusus untuk Docker |
| 7 | Akses luar hanya lewat Tailscale | Privasi; tanpa port forwarding | Port forwarding, VPN lain |
| 8 | Tailscale subnet router di LXC CT103 (nanti STB 2); STB 1 khusus AdGuard | Stabilitas DNS rumah | Tailscale di STB 1 atau di VM Docker |
| 9 | Caddy dengan CA lokal (Jalur 1) untuk layanan privat | Gratis, tanpa domain | Domain berbayar (Jalur 2, opsional) |
| 10 | Tailscale Serve untuk layanan yang aplikasi HP-nya menolak CA lokal | Sertifikat tepercaya | Pasang CA di tiap aplikasi |
| 11 | Kelompok layanan ringan pada CT104; gunakan VM hanya untuk aplikasi yang memang memerlukan VM | Hemat sumber daya; nesting disetujui dengan memahami trade-off isolasi | Satu VM per aplikasi |
| 12 | Mode hemat: n8n, web, AFFiNE, musik di VM 206 `apps` | Hemat RAM | Terpisah penuh |
| 13 | PBS di VM terpisah, datastore di disk fisik berbeda, enkripsi aktif | Backup terpisah dari yang dicadangkan | PBS di host |
| 14 | Disk foto Immich **ikut** backup | Foto tidak bisa dibuat ulang | `backup=0` dan hanya backup bawaan Immich |
| 15 | Disk musik `backup=0` | Bisa dibuat ulang dari sumber asli | Ikut backup |
| 16 | Hanya situs statis yang dipublikasikan (Cloudflare Tunnel, VM 210) | Permukaan serangan kecil | WordPress, n8n publik |
| 17 | OnlyOffice untuk office, AFFiNE untuk catatan, Pocket ID untuk SSO | Pilihan pengguna dan ringan | Authentik, Authelia |
| 18 | Profil RAM untuk mesin 16 GB | Semua VM tidak muat bersamaan | Memaksa semua menyala |
| 19 | Memigrasi satu layanan per langkah, uji, baru lanjut | Hindari kesalahan berantai | Pindah massal |
| 20 | Mesin asli: Lenovo ThinkCentre M710q; Proxmox dipasang langsung dari USB | Mesin sudah ada | Lab nested VMware, instal ke disk dulu |
| 21 | Hapus Model A (VMware) dan Model C dari buku (Revisi 3) | Tidak diperlukan lagi; mengurangi kebingungan | Menyimpannya sebagai opsi |
| 22 | RAM saat ini dilaporkan 16+8 GB (24 GB); verifikasi BIOS/MemTest86. 32 GB dapat dipertimbangkan nanti setelah kebutuhan dan kompatibilitas dipastikan | Modul 8 GB pertama diganti dengan 16 GB; konfigurasi 24 GB sekarang tersedia secara fisik | Menganggap jumlah terpasang sudah dikenali atau langsung menyalakan semua VM |
| 23 | NVMe 500 GB untuk sistem dan VM; HDD 2 TB untuk datastore PBS | Backup harus di perangkat fisik berbeda dari data | Semua di NVMe |
| 24 | Disk data besar (foto, musik) dikecilkan awal agar muat di NVMe | NVMe hanya 500 GB | Ukuran contoh 200/300 GiB |
| 25 | Gunakan baseline profil 16 GB sampai konfigurasi aktual diverifikasi. RAM yang dilaporkan sekarang 24 GB; Bab 56.8 menambah batas konservatif sementara. Opsi 32 GB tetap bersyarat pengukuran | Menjaga ruang bagi host dan mencegah OOM | Menganggap alokasi VM teoritis sama dengan RAM aman untuk VM |
| 26 | Repo GitHub private sebagai basis pengetahuan; rahasia tidak pernah masuk | Pemulihan konteks lintas AI | Hanya PDF |
| 27 | **Digantikan 3 Nov 2026 atas arahan terbaru pengguna:** gunakan Prometheus. Prometheus 3.15.1 + PVE exporter 3.11.0 berjalan di CT110 dan Grafana 13.3.0 di CT111 sejak 4 Nov. PVE API memakai akun/token terbatas `PVEAuditor`; retensi Prometheus 30 hari; API Prometheus 9090 dibatasi firewall CT110 hanya ke CT104 (rollback) dan CT111, exporter hanya jaringan Docker. | Pengguna membalik keputusan sebelumnya; kontrol akses minimal dan retensi terbatas | Menganggap keputusan lama “tanpa Prometheus” masih berlaku |

## Keputusan layanan media — 4 November 2026

Pisahkan data aplikasi Immich dan katalog video Jellyfin pada HDD: Samba share `Immich` menunjuk `/srv/media/immich`, sementara share `Media` menunjuk `/srv/media/jellyfin` dengan subfolder `Movies` dan `Shows`. CT106 Jellyfin hanya menerima bind mount read-only untuk folder `jellyfin`; upload dilakukan melalui SMB CT102, bukan langsung dari container Jellyfin. Pertahankan folder dan isi Immich di tempat. Tujuannya mencegah Jellyfin memindai atau menampilkan dataset Immich, sekaligus menyediakan lokasi upload yang sederhana. Backup CT mengecualikan bind mount, sehingga dataset media perlu backup file tersendiri; PBS saat ini masih pada NVMe host yang sama.

## Urutan pemasangan lanjutan — 4 November 2026

Atas arahan pengguna, selesaikan Nextcloud CT107 terlebih dahulu. Sesudah migrasi dan uji Nextcloud tuntas, jadikan otomasi download media Jellyfin prioritas sebelum layanan lain pada backlog. Alur awal berfokus pada Inbox, file/link yang dapat diakses, identifikasi dan penamaan, lalu penempatan Movies/Shows. n8n menjadi orchestrator yang direncanakan; torrent client baru ditambahkan pada tahap berikutnya setelah alur dasar lulus. Akses otomasi harus dibatasi ke Inbox dan direktori Jellyfin yang diperlukan; tidak boleh ada mount atau kredensial Immich.
