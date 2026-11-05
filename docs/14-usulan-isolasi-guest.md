# Usulan susunan guest per aplikasi

**Status: rencana disetujui dan pelaksanaan bertahap dimulai 3 November 2026.** CT106 Jellyfin, CT107 Nextcloud, CT109–112, Homepage CT115, dan n8n CT119 aktif. Pengguna mengonfirmasi login/unduh Nextcloud pascamigrasi selesai. CT119 menjalankan n8n/PostgreSQL dan helper media internal. Workflow prototipe unpublished setelah pengguna menetapkan tiga sumber intake; integrasi Portainer dan Kuma masih perlu diselesaikan.

## Dasar rancangan

- Host adalah Lenovo ThinkCentre M710q dengan 4 CPU thread dan 23 GiB RAM yang dikenali Linux. Snapshot host terbaru menunjukkan load average `25.88, 20.81, 12.64`; `docker stats` pada saat itu menampilkan `immich_server` 145.05%, `immich_machine_learning` 199.55%, dan `immich_postgres` 12.07% CPU.
- CT104 sekarang `cores=4`, tanpa `cpulimit`. Pada snapshot tersebut, dua container Immich utama memakai CPU setara kira-kira 3.45 core, sebelum menghitung komponen lain. Ini satu cuplikan saat upload/pemrosesan aktif, bukan rata-rata jangka panjang.
- Rancangan memakai satu **guest per aplikasi stack**. Komponen internal yang saling bergantung (misalnya Immich + PostgreSQL + Redis + ML) tetap bersama dalam guest yang sama. Ini menghindari pemecahan database menjadi titik ketergantungan jaringan baru.
- Gunakan CT unprivileged untuk aplikasi Linux ringan sebagai pilihan awal. VM disediakan bagi appliance/OS khusus atau aplikasi yang memang memerlukan batas isolasi tambahan. LXC berbagi kernel host; VM KVM menjalankan OS guest tersendiri. Proxmox menyediakan `cores`, `cpulimit`, dan `cpuunits`; `cores` menentukan CPU yang terlihat, sedangkan `cpulimit` memberi batas konsumsi waktu CPU.
- Portainer dapat tetap menjadi satu server pengelola di CT khusus. Setiap Docker guest lain perlu didaftarkan sebagai environment, misalnya dengan Portainer Agent; port agent hanya diizinkan dari guest Portainer.
- Pemisahan guest tidak menambah kapasitas host. Tetapkan batas CPU per guest setelah pengukuran supaya Immich atau transcode Jellyfin tidak mengambil seluruh empat thread.

## Guest yang sudah ada dan dipertahankan

| Guest | Peran | Rencana |
|---|---|---|
| CT100 | Template Debian 13 | Pertahankan untuk membuat CT baru. |
| CT101 | AdGuard Home kedua | Pertahankan; layanan sudah mandiri. |
| CT102 | Samba | Pertahankan; layanan sudah mandiri. |
| CT103 | Tailscale subnet router | Pertahankan sementara; lease `.104` dinamis, jangan dicatat sebagai IP final. |
| CT104 | Docker-services, masih menampung beberapa aplikasi | Sumber migrasi/rollback. Nextcloud app lama berhenti setelah cutover ke CT107; DB/Redis lama tetap hidup untuk rollback. Immich, Beszel, dan Portainer lama tetap di sini. Stack Gotify, Jellyfin, Kuma, Prometheus, dan Grafana lama berhenti. Pertahankan CT104 sampai klien Nextcloud teruji dan rollback tidak lagi diperlukan. |
| CT105 | Portainer Server khusus, dibuat 3 Nov 2026 | Docker/Compose aktif dan UI HTTPS `:9443` merespons. Admin setup selesai; pengguna melaporkan menambahkan CT104 dan CT109. Lease `.105` dilaporkan static dan aktif di guest. Agent di guest lain dibatasi ke source `.105`. |
| VM200 | Template Debian 13 | Pertahankan untuk VM baru. |
| VM201 | docker-core | Tetap stopped. Tidak perlu menyalakannya untuk arsitektur baru. |
| VM202 | Home Assistant OS | Pertahankan sebagai VM mandiri. |
| VM212 | Proxmox Backup Server | Pertahankan sebagai VM mandiri. Datastore 100 GiB saat ini masih pada NVMe host yang sama; perluasan backup fisik dibahas terpisah. |
| CT115 | Homepage | CT khusus Docker aktif di `.110:3000`; Homepage 2.7.0 healthy dan HTTP 200. Portainer menampilkan environment `CT115-Homepage` Up, Agent 2.45.3, 2/2 container. Backup PBS pasca-setup sukses. |
| CT108 | qBittorrent | Guest Debian 13 unprivileged khusus dibuat 5 Nov 2026 di `.114` (DHCP static menurut laporan pengguna), 1 vCPU/1 GiB/8 GiB. qBittorrent 5.3.0 dan Agent 2.45.3 Up. Default download `/inbox`; incomplete `/downloads/incomplete`. Hanya bind mount Inbox Jellyfin dan staging HDD, tanpa akses ke Movies/Shows maupun Immich. Agent firewall hanya CT105; tes CT105 204, CT104 timeout. Homepage card aktif; Portainer environment Up 2/2; Kuma ID15 Up/HTTP 200; backup PBS terenkripsi dan job harian sudah mencakup CT108. Password awal dan unduhan E2E masih perlu diselesaikan. |

## Aplikasi yang saat ini ada di CT104

| Aplikasi | Guest target usulan | Stack yang tetap bersama | Urutan / catatan migrasi |
|---|---|---|---|
| Portainer | CT105 (sudah dibuat) | Server Portainer saja; tambahkan Agent pada setiap guest Docker yang dikelola. | Setup admin selesai. Screenshot mengonfirmasi environment CT104 `Up` dan 16/16 container. DHCP static lease `.105` dilaporkan pengguna. Firewall persisten CT104 membatasi akses TCP 9001 ke source `.105`; status environment tetap `Up` setelah aturan aktif menurut pengguna 4 Nov; pertahankan instance lama selama transisi. Berkas firewall ada di `konfigurasi/portainer-agent-firewall.*`. |
| Jellyfin | CT106 (aktif) | Jellyfin dan konfigurasi/library-nya. | `.111:8096` healthy; mount read-only hanya folder Jellyfin; SMB `Media` dipisah dari `Immich`; subfolder `Movies` dan `Shows` siap menerima upload. Pengguna mengonfirmasi library `/media/Movies` dan `/media/Shows`, pemantauan realtime, uji salin dan playback Windows, environment Portainer, serta akses klien selesai. CT104 dipertahankan sebagai rollback. Transcode dapat memakai CPU tinggi. |
| Nextcloud | CT107 (aktif, cutover selesai) | Nextcloud + MariaDB + Redis. | `.112` static lease pengguna konfirmasi, cocok dengan MAC di WebFig. Nextcloud 35.0.2.2, OCC installed/maintenance false/DB upgrade false; HTTP `status.php` 200. Data di HDD bind mount owner www-data mode 750 (`backup=0`). Portainer CT107 Up (4 running, 2 healthy); Homepage/Kuma mengarah ke `.112`. Backup final CT104 dan pasca-cutover CT107 terenkripsi PBS sukses. CT104 app stopped sebagai rollback, DB/Redis tetap hidup. Minta pengguna uji klien Windows/Android/iPhone pada endpoint baru sebelum rollback dihentikan. |
| Immich | CT108 (baru) | Immich server + machine learning + PostgreSQL + Redis. | **Pindahkan terakhir** setelah upload ponsel selesai dan backup file + dump database sudah diuji. Pemrosesan awal foto dapat menghabiskan CPU; atur job concurrency/CPU limit. |
| Uptime Kuma | CT109 (sudah dibuat dan dipakai) | Kuma dan database/file persistennya. | Versi 2.5.9 berjalan di `.106:3001`; 14 monitor tersalin, SQLite integrity `ok`, HTTP UI merespons dan container healthy. Rootfs 16 GiB. Backup PBS terenkripsi CT109 berhasil. CT104 lama stopped untuk rollback. Target monitor self-check telah diperbarui ke `.106:3001` dan monitor Grafana ke `.108:3000` (database Kuma terverifikasi). |
| Prometheus + PVE exporter | CT110 (sudah dibuat dan dipakai) | Prometheus dan exporter sebagai komponen pengambilan metrik Proxmox. | Prometheus 3.15.1 dan exporter 3.11.0 berjalan di `.107`; dari CT111 kedua target `up`. API 9090 dibatasi ke Grafana CT104 `.20` dan CT111 `.108`. Agent 2.45.3 aktif, hanya source `.105` boleh; backup PBS terenkripsi lulus. Pengguna melaporkan static lease `.107`; alamat aktif terverifikasi dari CT110, RouterOS belum diaudit langsung. Environment Portainer dilaporkan terdaftar; Agent dari CT105 merespons. Container CT104 stopped untuk rollback. |
| Grafana | CT111 (sudah dibuat dan dipakai) | Grafana, datasource, dan dashboard. | Grafana 13.3.0 aktif di `.108:3000`; API health HTTP 200; `Home Server Overview` dan datasource `Prometheus` `.107:9090` diverifikasi; SQLite integrity `ok`. Rootfs 12 GiB; backup PBS terenkripsi berhasil. Agent 2.45.3 dibatasi ke `.105`. Pengguna melaporkan static lease `.108`; alamat aktif terverifikasi dari CT111, RouterOS belum diaudit langsung. Environment Portainer dilaporkan terdaftar; monitor Kuma ke `.108:3000` diverifikasi. CT104 lama stopped untuk rollback. |
| Gotify | CT112 (aktif, cutover selesai) | Gotify dan data aplikasinya. | Gotify 3.1.1 healthy di `.109:8070`; data final disalin dari CT104 saat berhenti, hash cocok, DB integrity `ok`. PVE target dan Uptime Kuma mengarah ke CT112 dan pengiriman uji sukses; monitor health HTTP 200. Pengguna mengonfirmasi URL Android/iPhone sudah diperbarui dan notifikasi uji diterima. Portainer environment CT112-Gotify 2/2 container berjalan. Backup PBS terenkripsi pascamigrasi sukses. CT104 Gotify tetap berhenti sebagai rollback. |
| Beszel hub | CT113 (baru) | Hub Beszel; agent tetap pada host/guest masing-masing. | Daftarkan ulang alamat hub pada agent bila alamat berubah; uji agent. |

CT106 menjadi host Jellyfin; CT107 Nextcloud; CT109 menjadi host Docker khusus Uptime Kuma; CT110 Prometheus/PVE exporter; CT111 Grafana; CT112 Gotify; CT115 Homepage. Lease `.112` static dikonfirmasi pengguna dan kecocokan lease/IP/MAC terlihat di WebFig. CT104 `.20` tetap berjalan untuk aplikasi lain; Nextcloud app lama serta stack Gotify/Jellyfin/Kuma/Prometheus/Grafana lama berhenti sebagai rollback. CT108, CT113, dan CT114 masih rencana. CT115 static lease `.110` dilaporkan pengguna.

## Aplikasi rencana yang belum dipasang

| Aplikasi / rencana | Guest target usulan | Status dan keputusan |
|---|---|---|
| Caddy + CA lokal | CT114 (baru) | Belum dipasang. Guest terpisah; jika Caddy berhenti, hostname proxy terdampak, sedangkan layanan langsung tetap berjalan. |
| Homepage | CT115 (aktif) | Terpasang di `.110:3000`; Homepage 2.7.0 healthy, HTTP 200, konfigurasi tautan layanan dimuat. Environment Portainer `CT115-Homepage` Up, Agent 2.45.3, 2/2 container. Backup PBS pasca-setup sukses. |
| Forgejo | CT116 (baru) | Belum dipasang; satu guest khusus. |
| Renovate | CT117 (baru) | Belum dipasang; worker terpisah dari Forgejo. |
| k3s + Flux | VM203 (rencana lama) | Belum dipasang. Anggap sebagai satu lingkungan Kubernetes/automation untuk latihan; fase lanjut karena menambah beban pada CPU 4 thread. |
| Vaultwarden | VM205 (rencana lama) | Belum dipasang. Guest khusus untuk password manager; akses privat Tailscale. Belum ada instalasi/konfigurasi. |
| AFFiNE | CT118 (baru) | Belum dipasang; satu guest khusus. |
| n8n | CT119 (aktif) | Orchestrator otomasi umum; fase pertama media Jellyfin. | CT119 `.113`, lease static dilaporkan pengguna, MAC `BC:24:11:7F:73:F6`. Docker CE 29.9.3, Compose 5.7.0, n8n 2.46.6, PostgreSQL 18 healthy; UI HTTP 200. HDD hanya subtree Jellyfin; Inbox/Movies/Shows ada dan Immich tidak terlihat. Agent 2.45.3/firewall hanya CT105; helper media internal healthy dan tidak menerbitkan port host. Backup PBS terbaru `ct/119/2026-11-04T17:41:16Z` sukses. Workflow prototipe di-unpublish setelah kebutuhan intake link/torrent/folder; tidak ada workflow aktif. Portainer environment dan monitor Kuma belum diverifikasi. |
| WordPress | CT120 (baru) | Belum dipasang; terpisah dari situs statis. |
| Situs statis publik + Cloudflare Tunnel | VM210 (rencana lama, opsional) | Belum dipasang. Pertahankan isolasi dari LAN; jangan publikasikan layanan admin. |
| Navidrome | CT121 (baru) | Belum dipasang; satu guest khusus. |
| Pocket ID | VM213 (rencana lama) | Belum dipasang; guest khusus untuk identitas/SSO. |
| OnlyOffice | CT122 (baru) | Belum dipasang; fase opsional karena penggunaan memori/CPU bisa besar. |
| AMP + playit.gg | Belum ditetapkan | Wishlist opsional; baru rancang guest jika server game benar-benar dipilih. |
| Ollama | Belum ditetapkan | Belum direkomendasikan untuk M710q ini: hanya 4 CPU thread dan RAM 23 GiB, kecuali model sangat kecil dan ekspektasi rendah. |
| TrueNAS | Tidak dibuat saat ini | Wishlist. Samba sudah menyediakan share; desain disk sekarang memakai HDD untuk data aplikasi. Evaluasi lagi setelah layout disk/backup baru disepakati. |
| Server cetak / pemantauan listrik / panel surya | Belum ditetapkan | Menunggu perangkat dan aplikasi yang akan dipakai; jangan membuat guest kosong dulu. |

CT108 kini telah dibuat untuk client torrent. Guest usulan lain CT114–122 belum dibuat dan alamatnya belum dialokasikan. VM203/205/210/213 berasal dari slot rencana lama; status tersebut bukan bukti guest pernah dibuat.

## Keputusan layanan file dan NAS

Pengguna menyetujui pembagian peran berikut pada 3 November 2026:

| Komponen | Peran yang dipilih | Status |
|---|---|---|
| Nextcloud | Layanan file utama yang digunakan anggota keluarga melalui aplikasi ponsel, klien sinkronisasi PC/laptop, dan web. Akun per orang; grup dan kuota ditata sesuai kebutuhan. | Cutover ke CT107 selesai; pengguna mengonfirmasi login dan unduh/pengujian klien pascamigrasi berhasil. CT104 tetap rollback sementara. Integrasi Samba ditunda. |
| Samba di CT102 | Pelengkap untuk share jaringan yang dibuka langsung dari PC/laptop, misalnya folder bersama atau transfer file di LAN. Gunakan akun dan izin per pengguna/grup. | Sudah berjalan; uji akses Windows masih tercatat pending. Akses ponsel dan integrasi SMB ke Nextcloud ditunda. |
| TrueNAS | Bukan layanan file utama pengguna saat ini. Opsi masa depan sebagai lapisan pengelola NAS/storage, setelah rancangan disk dan akses aplikasi disepakati. | Belum dipasang; jangan buat VM atau ubah layout disk sebelum tahap evaluasi storage. |

> Setiap folder sebaiknya memiliki satu jalur utama untuk perubahan agar penulisan bersamaan melalui SMB dan Nextcloud tidak menimbulkan kebingungan izin atau sinkronisasi. Jangan mengekspos dataset aplikasi langsung sebagai share umum. TrueNAS, bila kelak dipakai sebagai storage pusat, menjadi dependensi bagi layanan yang membaca dataset tersebut; pemisahan aplikasi ke guest sendiri tidak menghilangkan dependensi storage bersama.

## Tahap migrasi

1. Upload Immich dilaporkan selesai. Dump DB baru lolos `gzip -t`; folder media berhasil dicadangkan terenkripsi ke PBS pada `host/immich-data/2026-11-03T15:00:28Z`. Pemulihan penuh arsip berhasil dan SHA-256 dump hasil restore cocok dengan sumber. Sebelum migrasi Immich, rekonsiliasi jumlah akhir (query database 10.638 asset vs catatan ponsel sebelumnya 12.923); backup ini bukan salinan fisik terpisah karena PBS masih berada di NVMe host yang sama.
2. Tetapkan pola Docker per guest, jaringan/port, IP yang tidak bertabrakan, mount data, dan batas CPU/RAM. Catat backup serta langkah rollback sebelum memindahkan tiap stack.
3. Uji Portainer Server CT105 mengelola satu guest Docker percobaan menggunakan Agent dengan akses jaringan terbatas.
4. **Selesai untuk Uptime Kuma, Prometheus, dan Grafana:** migrasi data/config masing-masing; SQLite Kuma/Grafana integrity `ok`, Kuma menyimpan 14 monitor, kedua target scrape Prometheus `up`, Grafana health/API/dashboard/datasource terverifikasi. Container lama CT104 stopped untuk rollback.
5. **Selesai 4 Nov:** monitor Kuma Gotify diarahkan ke `.109:8070/health` dan HTTP 200; notifikasi default Gotify diarahkan ke `.109` dan tombol Test memberi sukses tanpa mengubah token. Monitor Immich telah ada; heartbeat terakhir `Up / 200 - OK`.
6. Pengguna melaporkan static lease DHCP `.107/.108` dan environment `CT110-prometheus`/`CT111-grafana` sudah selesai. HTTP 403 dari Agent tanpa signature mengonfirmasi jalur jaringan dari CT105; status dashboard Portainer/router belum diperiksa langsung.
7. **Gotify CT112, Homepage CT115, dan pemantauan Immich selesai diverifikasi** (4 Nov): pengguna mengonfirmasi notifikasi Gotify Android/iPhone; environment Portainer Homepage Up 2/2; monitor Immich Kuma heartbeat Up / HTTP 200. Lanjutkan migrasi aplikasi dengan backup/rollback per tahap; Immich tetap terakhir setelah rekonsiliasi aset.
8. Setelah tiap layanan lulus, stop hanya stack lamanya. Pertahankan CT104 sebagai rollback sampai semua layanan dan backup terverifikasi.
9. **Prioritas pengguna, 4–5 Nov 2026:** setelah pengguna mengonfirmasi login dan pengujian klien Nextcloud, prioritaskan otomasi Jellyfin lebih dulu. CT119 n8n dibuat dengan Docker/PostgreSQL dan helper terbatas ke Jellyfin. Pengguna menetapkan tiga intake: link download, link torrent, dan folder kumpulan. CT108 qBittorrent kini terpasang terpisah; unduhan selesai diarahkan ke `\\192.168.88.12\Media\Inbox`, file parsial ke staging HDD. Agent dibatasi firewall ke Portainer CT105. qBittorrent, Portainer environment, dan monitor Kuma telah diverifikasi pada 5 Nov. Form magnet n8n kini dipublikasikan dengan login n8n + execute permission; URL `http://192.168.88.113:5678/form/media-torrent-intake` memberi HTTP 302 ke autentikasi tanpa sesi dan path production terdaftar setelah restart. Pengguna mengirim satu magnet tetapi eksekusi berhenti di validator sebelum mencapai qBittorrent. Parser kini diperbarui tanpa global `URL` yang tidak diekspos daftar native task runner; ini dugaan penyebab, perlu pengiriman ulang untuk memastikan. E2E qB menunggu verifikasi. Pengelompokan series, rename, review, dan perpindahan aman diuji bertahap; akses otomasi tidak mencakup Immich.
10. Sesudah observasi beban, terapkan `cpulimit`/`cpuunits`. Untuk mengurangi CPU Immich saat pemrosesan awal, gunakan concurrency rendah sesuai pengaturan resmi Immich; jangan menganggap penambahan guest akan menurunkan kebutuhan CPU total.

### Rujukan resmi

- [Proxmox VE `pct` — CPU, container, dan limit](https://github.com/proxmox/pve-docs/blob/master/pct.adoc)
- [Docker `stats` — arti angka CPU](https://docs.docker.com/reference/cli/docker/container/stats/)
- [Immich FAQ — beban CPU dan cara menguranginya](https://immich.app/docs/FAQ)
- [Portainer — menambahkan Docker Standalone environment](https://docs.portainer.io/admin/environments/add/docker)
