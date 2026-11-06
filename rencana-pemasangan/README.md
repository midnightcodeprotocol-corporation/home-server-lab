# Rencana pemasangan dan migrasi Home Server Lab

Panduan ini memisahkan **keadaan live** dari **pekerjaan yang direncanakan**. Dibuat 6 November 2026. Tidak ada perubahan server yang dilakukan untuk dokumen ini. Sebelum menjalankan langkah, cocokkan keadaan aktual di Proxmox dan baca [inventaris live](../docs/16-inventaris-live-2026-11-06.md).

## Kondisi awal yang perlu diingat

- CT104 masih menjalankan Immich, Beszel, PVE exporter, Portainer lama, serta MariaDB/Redis Nextcloud untuk rollback.
- Backup CT104 terenkripsi berhasil pada 6 Nov, tetapi Proxmox mengecualikan bind mount HDD `/srv/media` dan `/srv/appdata`. Pengguna mengonfirmasi sudah membuat backup media Immich; pastikan arsip dan database dapat dibaca/dipulihkan sebelum mematikan sumber.
- PBS VM212 berada pada NVMe fisik yang sama dengan Proxmox. Salinan di PBS tidak melindungi dari kegagalan fisik host/NVMe.
- User meminta tidak mengerjakan DHCP static dan mendaftarkan Agent ke Portainer. Isi tabel di akhir setelah guest baru memperoleh IP.
- Jangan hapus CT104 atau folder sumber sampai guest pengganti lulus pemeriksaan dan masa observasi selesai.

## Urutan kerja yang disarankan

Kerjakan **berurutan, satu migrasi selesai dan diverifikasi sebelum berikutnya**. Ini mencegah layanan yang saling bergantung berubah serentak dan memudahkan rollback.

### Fase 0 — persiapan

1. Masuk Proxmox `https://192.168.88.10:8006`; pastikan CT104, storage `backup-disk`, `local-lvm`, dan PBS aktif.
2. Pastikan file backup media Immich benar-benar ada, ukuran masuk akal, checksum/arsip lolos pemeriksaan, dan backup database Immich terbaru tersedia. Simpan lokasi dan tanggal di tabel pekerjaan; jangan masukkan kredensial.
3. Catat backup CT104: `ct/104/2026-11-06T03:32:23Z`. Backup ini berisi rootfs, bukan bind mount HDD.
4. Cek ID kosong di Proxmox setiap kali membuat guest. Pada audit 6 Nov, `nextid` adalah 113; 113, 114, 123, 124 terlihat kosong saat itu. Kondisi dapat berubah.
5. Catat IP DHCP dan MAC baru dari guest, lalu buat reservation di MikroTik. Jangan memakai alamat contoh atau IP rencana yang belum diuji konflik.

### Fase 1 — CT121 Speedtest Tracker: lengkapi operasi

CT121 sudah ada pada `.115` saat audit, tetapi lease masih DHCP dinamis; RAM 512 MiB, `onboot` belum diset, belum ada backup PBS, dan Portainer Agent `latest` membuka TCP 9001 di semua interface.

1. Periksa lease/MAC live di MikroTik (`BC:24:11:05:BE:F7`) dan buat static lease untuk IP yang benar-benar sedang dipakai.
2. Putuskan `onboot` sesuai kebutuhan, lalu verifikasi reboot terjadwal hanya jika aman.
3. Batasi Agent 9001 supaya hanya Portainer CT105 (`192.168.88.105`) dapat mengaksesnya; gunakan versi Agent yang dipin dan sama dengan standar lab.
4. Tambahkan CT121 ke job PBS dan buat backup terenkripsi; cek hasil di PBS.
5. Uji Homepage/Kuma/Portainer setelah alamat final disepakati.

### Fase 2 — pisahkan Immich dari CT104 ke guest khusus

**Usulan sementara: CT124**, Debian 13 unprivileged + nesting, 2–4 vCPU sesuai beban, RAM awal 4–6 GiB bila kapasitas host memungkinkan. Alamat IP belum ditentukan. Pastikan ID kosong dan kapasitas sebelum membuat.

1. Siapkan guest baru dan Docker Compose Immich berdasarkan versi/konfigurasi sumber; simpan rahasia hanya dalam `.env` root-only dan jangan commit.
2. Pasang dataset media Immich ke guest baru dengan hak tulis minimum yang diperlukan. Jangan mount folder Jellyfin.
3. Buat salinan konsisten database terbaru dan media Immich sesuai prosedur backup yang Anda konfirmasi. Validasi arsip, checksum, permission/UID, ruang, dan kompatibilitas versi.
4. Untuk cutover, hentikan penulisan/upload Immich sementara, buat dump DB final, sinkronkan delta file terakhir, pulihkan DB, jalankan stack baru, dan verifikasi login, jumlah aset, thumbnail, unduh, unggah uji, serta log.
5. Perbarui link Homepage, monitor Kuma, klien ponsel/PC, dan integrasi yang mengarah ke alamat lama.
6. Pertahankan stack CT104 dalam keadaan berhenti sebagai rollback. Jangan hapus sumber/backup sebelum masa observasi dan uji pemulihan selesai.

### Fase 3 — pindahkan Beszel hub dari CT104

**Usulan lama: CT113**, belum dibuat pada audit. Cek ID kosong, siapkan guest Docker, pindahkan konfigurasi/data hub secara konsisten, lalu daftarkan ulang agent host/guest. Uji semua host terlihat, grafik berlanjut, Homepage/Kuma, dan backup sebelum menghentikan Beszel di CT104.

### Fase 4 — rapikan sisa CT104

- **PVE exporter CT104:** CT110 sudah memiliki exporter 3.11.0. Periksa konfigurasi scrape dan target Prometheus; setelah exporter CT104 terbukti tidak dipakai, hentikan duplikat.
- **Portainer lama CT104:** Portainer Server utama berada di CT105. Pertahankan lama sampai semua environment baru berhasil didaftarkan manual oleh pengguna dan rollback tidak dibutuhkan; baru hentikan duplikat.
- **Nextcloud MariaDB/Redis lama:** ini sisa rollback setelah cutover ke CT107. Pertahankan sampai validasi backup dan masa rollback disetujui; jangan pindahkan/hapus tergesa-gesa.
- Setelah layanan lama dipensiunkan, verifikasi alasan operasional jika CT104 masih harus memiliki satu container. Jangan mempertahankan container tanpa fungsi hanya demi mencapai angka satu; putuskan berdasarkan dependensi aktual.

### Fase 5 — pemasangan rencana lainnya

ID berikut adalah **usulan lama**, bukan alokasi yang dijamin. Tetapkan satu per satu setelah kapasitas, alamat, storage, backup, dependensi, dan pemulihan disetujui.

| Guest target usulan | Aplikasi | Status / prasyarat |
|---|---|---|
| CT114 | Caddy + CA lokal | Belum dipasang; DNS lokal, TLS, dan fallback akses langsung perlu dirancang. |
| CT116 | Forgejo | Belum dipasang; tetapkan backup repository dan akses Git/SSH. |
| CT117 | Renovate | Belum dipasang; bergantung pada Forgejo/repo dan token disimpan sebagai secret. |
| CT118 | AFFiNE | Belum dipasang; tentukan persistensi DB/file dan backup. |
| CT120 | WordPress | Belum dipasang; tetapkan publik/privat, database, dan backup. |
| CT122 | OnlyOffice | Opsional; uji kebutuhan RAM/CPU dan integrasi Nextcloud lebih dulu. |
| Belum ditetapkan | Navidrome | Target CT121 lama dibatalkan karena CT121 menjalankan Speedtest Tracker. VM211/.31 adalah rencana legacy, belum disetujui. |
| VM203 | k3s + Flux | Opsional; beban tinggi untuk host 4 thread, kerjakan setelah layanan inti stabil. |
| VM205 | Vaultwarden | Belum dipasang; layanan sensitif, prioritaskan backup terisolasi dan akses privat. |
| VM210 | situs statis + Cloudflare Tunnel | Opsional; isolasi LAN harus dirancang sebelum publikasi. |
| VM213 | Pocket ID | Belum dipasang; rancang dampak SSO bila guest gagal. |
| Belum ditetapkan | AMP/game server, Ollama, TrueNAS, server cetak/monitor listrik | Wishlist; jangan buat guest kosong sebelum perangkat dan kebutuhan disepakati. |

## Rencana tambahan: STB sebagai control plane rumah

**Belum dijalankan.** Ini rencana arsitektur, bukan keadaan live dan bukan instruksi untuk langsung mereset STB.

### Homeio dan OS

Homeio bukan OS yang menggantikan sistem STB. Installer resminya dipasang pada OS 64-bit Debian, Ubuntu, atau Raspberry Pi OS yang didukung; skrip memasang Docker jika belum ada, menyiapkan Homeio sebagai service, dan memakai Nginx pada port 80. Jalur Docker Compose memakai port 12026. Homeio juga dapat mengelola Docker lewat Docker socket, tetapi ini tidak otomatis memindahkan atau menggantikan Portainer. Periksa dukungan SoC/OS image spesifik STB HG680 sebelum memilih media/OS. Rujukan: [install Homeio](https://homeio.app/install), [dokumentasi Homeio](https://homeio.app/docs).

Perintah yang diusulkan pengguna (`curl -fsSL https://get.homeio.app | sudo bash`) menjalankan skrip jarak jauh dengan hak root. Sebelum dipakai, unduh/tinjau isi skrip atau jalankan dry-run resmi; pastikan backup konfigurasi STB dan jalur akses lokal tersedia. Reset pabrik menghapus data/konfigurasi sehingga jangan dilakukan tanpa console/recovery image dan hasil backup yang bisa dipulihkan.

### Susunan target yang diusulkan

| Komponen | Target | Catatan/dependensi |
|---|---|---|
| OS STB HG680 | Install ulang OS 64-bit yang didukung perangkat | Validasi image/boot/recovery HG680; jangan menganggap Homeio adalah OS. Buat backup konfigurasi Tailscale, AdGuard, hostname, jaringan, dan key yang aman sebelum reset. |
| AdGuard Home | STB | Pertahankan IP/DNS dan blocklist/config; siapkan backup config dan uji DNS lokal sebelum menjadikan resolver utama. |
| Tailscale subnet router | STB | Login ulang dan iklankan route LAN; uji akses dari luar. Pastikan ada jalur administrasi alternatif ketika STB mati. |
| Homeio dashboard | STB | UI install script default port 80. Periksa konflik dengan AdGuard UI/layanan HTTP dan akses admin; pilih port/hostname yang konsisten. |
| Portainer Server | Tetap CT105 sampai rencana cutover diuji | Portainer Server perlu host Linux dengan Docker atau Kubernetes yang didukung. Rekomendasi: jangan pindah ke STB bersamaan dengan reset/AdGuard/Tailscale; siapkan cadangan/restore Portainer dan uji endpoint satu per satu. Homeio Docker manager dan Portainer adalah pilihan yang bisa berdampingan, tetapi satu control plane utama perlu dipilih. |
| Homepage | STB hanya jika disepakati | Homepage sudah berjalan di CT115. Jika dipindah, salin config, tes port, backup, dan pertahankan CT115 rollback. Bisa juga tetap di CT115 dan ditautkan dari Homeio. |
| Wake-on-LAN | STB mengirim magic packet ke mini PC | Aktifkan WoL di BIOS/NIC mini PC dan konfigurasi paket jaringan di STB. Uji saat berada di LAN; pastikan STB selalu mendapat daya. Tidak bergantung pada Portainer/Homepage. |
| Reset “old PC” | Belum ditetapkan | Klarifikasi perangkat yang dimaksud. Jika yang dimaksud ThinkCentre Proxmox, factory reset akan menghapus host/guest; jangan reset sebelum backup terpisah semua data, rencana reinstall, dan restore teruji. |

### Tahapan cutover control plane

1. Inventaris model/revisi HG680, bootloader, OS saat ini, storage, IP/MAC, AdGuard config, Tailscale state/routes, dan cara recovery.
2. Simpan backup konfigurasi AdGuard dan daftar layanan/route Tailscale secara privat; jangan commit key/token. Siapkan akses admin dari laptop lewat jalur LAN alternatif.
3. Uji OS image yang tepat dan boot/recovery terlebih dahulu. Jangan reset Proxmox mini PC sebagai bagian dari reset STB.
4. Pasang OS STB dan validasi jaringan/IP serta akses shell.
5. Pasang Homeio secara terpisah; verifikasi port 80/12026 dan konflik dengan AdGuard UI.
6. Kembalikan AdGuard, uji kueri DNS dari klien, baru arahkan resolver utama bila berhasil.
7. Kembalikan Tailscale, approve subnet route, lalu uji akses dari perangkat luar. Pertahankan jalur lokal/admin cadangan.
8. Migrasikan Portainer setelah backup/restore server dan daftar environment diuji; pindahkan Homepage hanya jika ada alasan, lalu uji reverse links/monitoring.
9. Siapkan WoL BIOS/NIC, konfigurasi magic packet di STB, dan uji cold start mini PC. Catat hasil dan rollback.

### Portainer dan Debian/LXC

Portainer tidak berjalan “tanpa OS” di CT. LXC CT adalah lingkungan Linux guest dan tetap memerlukan distribusi dasar seperti Debian. Pasang Docker Engine di CT Debian, kemudian jalankan Portainer Server sebagai container; untuk mengelola Docker pada CT lain, pasang Portainer Agent di masing-masing Docker guest dan batasi akses Agent TCP 9001 ke alamat Portainer. Rujukan: [Portainer Docker Standalone](https://docs.portainer.io/start/install-ce/server/docker/linux) dan [prasyarat Portainer](https://docs.portainer.io/start/requirements-and-prerequisites). Alternatif VM juga memerlukan OS guest. Jangan memasang Docker/Portainer langsung pada host Proxmox.

Homeio Docker mode juga membutuhkan Docker host/OS. Install script Homeio langsung pada STB memerlukan OS yang didukung; perintah tersebut bukan firmware flash dan tidak mengubah STB menjadi OS Homeio.

### Tabel alamat dan cutover control plane

| Perangkat/service | MAC/IP live sebelum reset | IP reservation sesudah reset | Port/URL | Backup/config dipulihkan | Uji lulus/tanggal |
|---|---|---|---|---|---|
| STB HG680 | | | | | |
| AdGuard Home | | | DNS 53, UI: | | |
| Tailscale subnet router | | | subnet 192.168.88.0/24 | | |
| Homeio | | | 80 atau 12026 | | |
| Portainer (jika dipindah) | | | 9443; Agent 9001 | | |
| Homepage (jika dipindah) | | | 3000 | | |
| WoL target mini PC | MAC NIC: | n/a | magic packet | | |

## Checklist per guest

- [ ] ID bebas diverifikasi langsung sebelum pembuatan.
- [ ] CPU/RAM/root disk dan storage dicatat; kapasitas host diperiksa.
- [ ] MAC/IP live dicatat; DHCP static dibuat pengguna di MikroTik.
- [ ] Port host dan sumber jaringan yang boleh mengakses dicatat; tidak ada publikasi port tanpa rencana.
- [ ] Bind mount minimum; folder Immich/Jellyfin/Nextcloud terpisah.
- [ ] Rahasia disimpan di file lokal yang dikecualikan Git; tidak disalin ke chat.
- [ ] Backup terenkripsi berhasil dan cakupan bind mount dipahami.
- [ ] Aplikasi sehat, login/fitur klien diuji, monitoring dan Homepage diperbarui.
- [ ] Rollback diuji/ditulis sebelum menghentikan sumber.

## Tabel DHCP dan Portainer — diisi setelah pembuatan guest

Alamat di bawah sengaja kosong. Masukkan hasil aktual dari guest dan MikroTik; jangan gunakan rencana IP lama sebagai alamat final.

| Guest | MAC live | IP live | IP static MikroTik | Agent URL untuk Portainer CT105 | Nama environment / status |
|---|---|---|---|---|---|
| CT121 Speedtest Tracker | BC:24:11:05:BE:F7 | 192.168.88.115 saat audit | | http://192.168.88.115:9001 (setelah reservation diverifikasi) | |
| CT124 Immich (usulan) | | | | | |
| CT113 Beszel (usulan) | | | | | |
| CT114 Caddy (usulan) | | | | | |
| CT116 Forgejo (usulan) | | | | | |
| CT117 Renovate (usulan) | | | | | |
| CT118 AFFiNE (usulan) | | | | | |
| CT120 WordPress (usulan) | | | | | |
| CT122 OnlyOffice (usulan) | | | | | |
| Navidrome (guest belum ditetapkan) | | | | | |

Agent URL hanya diisikan saat Agent aktif, IP telah dicadangkan, dan firewall guest membatasi sumber ke CT105. Jangan menambahkan Agent URL yang belum diamankan.

## Catatan pelaksanaan

Catat setiap perubahan, verifikasi, error persis, backup, endpoint baru, dan rollback pada `STATUS.md` serta `catatan/hasil-uji.md`. Setelah diperbarui, commit/push dokumentasi sesuai `AGENTS.md` tanpa memasukkan rahasia.
