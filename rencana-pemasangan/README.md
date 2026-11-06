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
