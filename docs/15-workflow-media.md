# Rancangan workflow otomasi media Jellyfin

**Status: client torrent dasar sudah terpasang; workflow belum menjadi operasional.** Pengguna mengusulkan tiga pintu masuk: tautan unduhan langsung, tautan torrent, serta folder pengumpulan. CT108 khusus qBittorrent telah dibuat dan diverifikasi; proses unduh legal/end-to-end belum diuji.

## Alur yang disarankan

1. **Intake:** form n8n menerima link langsung yang memenuhi batas protokol/host; client torrent menerima magnet atau file torrent melalui guest tersendiri; file yang dimiliki pengguna dapat diletakkan di `\\192.168.88.12\Media\Inbox`.
2. **Staging:** link langsung, torrent selesai, dan file SMB diarahkan ke antrean yang terpisah. File torrent yang masih diunduh tidak boleh masuk antrean pemrosesan.
3. **Stabilitas dan validasi:** tunggu ukuran/mtime stabil; cek ekstensi dan metadata teknis memakai `ffprobe`/MediaInfo. Helper organizer saat ini hanya menerima file reguler video di child langsung `Inbox`; ia tidak membaca isi audio/video.
4. **Pengenalan:** parsing judul/tahun/season/episode dari nama lalu cocokkan katalog metadata eksternal bila pengguna menyetujui sumber dan kredensialnya. AI dapat mengusulkan hasil, bukan memilih lokasi tanpa guardrail.
5. **Pengelompokan:** Movie → `Movies/Judul (Tahun)/Judul (Tahun).ext`; series → `Shows/Nama Series/Season 01/Nama Series - S01E01 - Judul Episode.ext`. Berkas ambigu/duplikat/tidak dikenal masuk Review dan tidak otomatis dipindahkan.
6. **Perpindahan:** same-filesystem move/rename setelah validasi; jangan overwrite tujuan. Simpan log ringkas status/error tanpa credential.
7. **Pustaka:** Jellyfin realtime monitoring menjemput hasil di Movies/Shows.

## Keamanan dan batasan

- Jangan pernah mount folder Immich ke n8n/client download.
- Torrent client ditempatkan pada CT108 tersendiri, bukan diberi hak menjalankan shell dari n8n. CT108 `.114` (DHCP static menurut pengguna) hanya me-mount Inbox dan staging HDD; Movies/Shows dan Immich tidak dapat diakses. Agent firewall hanya menerima CT105; Portainer CT108 Up 2/2 dan Kuma ID 15 Up/HTTP 200.
- Link langsung dibatasi ke HTTP(S), verifikasi redirect/ukuran/tipe file dan host untuk mengurangi SSRF dan unduhan tak sengaja. Tautan autentikasi tidak disimpan di workflow atau log; kredensial dikelola melalui n8n Credentials.
- n8n belum diberi kredensial AI/katalog; jangan kirim file video utuh ke model. Tahap awal dapat mengandalkan nama + metadata teknis + katalog, dengan Review manual saat confidence rendah.
- Prototipe `Media — Inbox ke Movies dan Shows` yang hanya parsing nama sudah diuji dan kemudian di-unpublish pada 5 Nov 2026 sesuai arahan pengguna; jangan aktifkan kembali sebagai solusi akhir.
- qBittorrent 5.3.0 di CT108 menggunakan default `/inbox` → Inbox Jellyfin dan temp `/downloads/incomplete` → staging HDD. WebUI `.114:8080` HTTP 200; Agent `.114:9001` memberi HTTP 204 dari CT105 dan timeout dari CT104. Homepage card aktif. Password admin awal belum diganti, belum ada uji unduhan legal end-to-end. Backup terenkripsi CT108 `ct/108/2026-11-04T19:05:33Z` sukses dan VMID masuk job PBS harian; bind mount unduhan `backup=0` tidak ada di backup guest.
- Integrasi yang selesai 5 Nov: Portainer `CT108-qBittorrent` Up (2/2 container); Kuma HTTP monitor ID 15 Up/200 ke WebUI. Password awal image LinuxServer harus dibaca langsung di Portainer → CT108 → container `qbittorrent` → Logs, lalu segera diganti di qBittorrent WebUI; jangan bagikan log atau password di chat. Sesudah itu, hasilkan API key qBittorrent dari WebUI dan simpan sebagai credential di n8n, bukan teks workflow.

### Rujukan resmi

- [LinuxServer.io qBittorrent container documentation](https://docs.linuxserver.io/images/docker-qbittorrent/)
- [qBittorrent upstream session settings](https://github.com/qbittorrent/qBittorrent/blob/master/src/base/bittorrent/sessionimpl.cpp)
- [qBittorrent API key authentication (v5.2+)](https://github.com/qbittorrent/qBittorrent/wiki/API-Key-Authentication-%28%E2%89%A5v5.2.0%29)

## Kondisi implementasi awal 5 Nov 2026

- CT119 `.113`: n8n 2.46.6/PostgreSQL sehat; helper `media-organizer` internal Docker, health healthy, tidak menerbitkan port di LAN.
- Helper mengembalikan daftar file Inbox, memvalidasi child path dan ekstensi, membatasi destination ke Movies/Shows, menolak path traversal/symlink dan destination yang telah ada, serta memindahkan tanpa menyalin video. Uji dummy kecil berhasil dan bersih.
- Prototipe workflow di-unpublish. Workflow aktif: 0. Portainer environment CT119, monitor Kuma, direct download dan torrent belum dibuat.
- Backup PBS terenkripsi CT119 `ct/119/2026-11-04T17:41:16Z` berhasil; PBS berada pada NVMe fisik yang sama dengan Proxmox.

## Audit lanjutan — helper Inbox dan Review (5 November 2026)

- Kondisi live diperiksa ulang: CT119 n8n 2.46.6 dan PostgreSQL 18 berjalan, `n8n-media-organizer` healthy, HTTP `192.168.88.113:5678` menjawab 200. CT108 qBittorrent juga berjalan, tetapi password admin awal belum dipastikan telah diganti dan belum ada unduhan legal end-to-end.
- Helper kini menunggu file dengan ukuran dan `mtime` yang tidak berubah selama 10 menit pengamatan sebelum mendaftarkannya di `/inbox`. Sesudah restart helper, masa stabilitas dihitung ulang. Destinasi diizinkan `Movies`, `Shows`, atau `Review`; pemindahan tetap same-filesystem, menolak overwrite, symlink, path traversal, dan ekstensi di luar daftar video.
- Workflow yang sudah ada diperbarui dengan ID yang sama dan diimpor kembali sebagai inactive: `Media — Inbox ke Movies, Shows, atau Review`. Klasifikasi nama yang jelas mengarah ke struktur Movies/Shows; pola yang tak dikenali masuk Review dengan nama asli. Uji parser lokal untuk Dune (2021), The Bear S02E03, dan judul tak dikenal lulus. Smoke test endpoint `/move` dengan satu file dummy menghasilkan `moved: true` ke Review; file dummy dipastikan sudah dihapus. Workflow aktif tetap 0 dan scheduler belum diuji end-to-end.
- Pembatasan: alur ini hanya memeriksa ekstensi, ukuran, waktu stabil, dan pola nama. Belum memeriksa codec/isi dengan ffprobe atau mencocokkan metadata katalog; tidak ada AI yang membaca video. Direct download belum ada. Torrent API belum disambungkan; credential qBittorrent harus dibuat/disimpan privat setelah password awal diganti.
- Backup sebelum implementasi: PBS terenkripsi `ct/119/2026-11-05T03:51:16Z` sukses, snapshot sementara dibersihkan. PBS berada pada NVMe host PVE yang sama. Storage PBS setelah backup 42.89% terpakai; thin-pool data 38.95%, dengan warning autoextend/overcommit yang sudah diketahui.
- Error/deviasi persis pada sesi ini: quoting probe PowerShell menghasilkan `The module 'Session' could not be loaded. For more information, run 'Import-Module Session'.`; tangkapan layar browser gagal dua kali dengan `encode latest capture frame failed: window crop is outside captured monitor.`; Python lokal tidak tersedia: `Python was not found; run without arguments to install from the Microsoft Store, or disable this shortcut from Settings > Apps > Advanced app settings > App execution aliases.`; probe parser Node pertama gagal `SyntaxError: Illegal return statement`, percobaan wrapper kedua gagal `ReferenceError: $input is not defined`, lalu runner konteks diperbaiki dan semua contoh lulus; impor workflow awal dengan `--activeState=fromJson` gagal `The "--activeState=fromJson" flag can only be used when n8n is running in queue or multi-main mode. In regular deployment mode, workflow activation is not supported.`; opsi dihapus dan workflow berhasil diimpor inactive. Percobaan SSH backup dengan opsi salah gagal `command-line: line 0: Bad configuration option: nnecttimeout`; percobaan ulang memakai `-o ConnectTimeout=8` sukses. Probe HTTP yang terbungkus keliru sempat menghasilkan `000`; probe langsung dari PVE kemudian menjawab `200`.
- Tambahan error probe awal sesi (pemulihan: jalankan probe terpisah dengan nama container dan quoting yang benar): `Error response from daemon: No such container: media-organizer`; `File "<string>", line 1 ... SyntaxError: unexpected character after line continuation character`; serta PowerShell `The term '*' is not recognized as a name of a cmdlet, function, script file, or executable program.`. Probe status akhir yang dipisah menunjukkan helper sehat dan n8n HTTP 200.

## qBittorrent — konfirmasi pengguna dan backup setelah perubahan (5 Nov 2026)

- Pengguna membalas “done” setelah diminta mengganti password awal qBittorrent dan menguji unduhan legal kecil. Dicatat sebagai laporan pengguna bahwa kedua tindakan selesai; password tidak dibaca/dicatat dan unduhan belum diverifikasi langsung melalui daftar WebUI.
- Live: CT108 `qbittorrent` dan Portainer Agent Up; WebUI `.114:8080` HTTP 200.
- Backup terenkripsi pascakonfirmasi `ct/108/2026-11-05T05:02:52Z` sukses; snapshot dibersihkan. Bind mount media/torrent `backup=0` tidak termasuk backup guest. PBS satu NVMe bersama PVE; kapasitas sekitar 42.91% terpakai; thin-pool data 38.95%, peringatan autoextend/overcommit tetap muncul.
- Langkah berikut: pengguna membuat API key di qBittorrent 5.3 Preferences → Web UI → API Key dan menyimpannya sendiri pada n8n sebagai HTTP Header Auth (`Authorization`, nilai `Bearer <API key>`). Key jangan dibagikan lewat chat. Setelah credential tersedia, saya lanjut mengikat workflow.

## Persiapan qBittorrent API → n8n — 5 November 2026

- Audit ulang repo bersih sebelum kerja; live CT108 running, container qBittorrent dan Agent Up, WebUI HTTP 200. Pengguna melaporkan password awal sudah diganti serta uji unduhan legal kecil selesai; laporan dicatat tanpa membaca rahasia dan tanpa klaim verifikasi file unduhan.
- Backup pascakonfirmasi CT108 `ct/108/2026-11-05T05:02:52Z` sukses terenkripsi. PVE mengonfirmasi mount media/torrent (`mp0`, `mp1`) dikecualikan dari backup guest; snapshot dibersihkan. Storage PBS aktif 42.91%; thin-pool data 38.95%. PBS satu NVMe dengan PVE.
- Rujukan upstream qBittorrent menyatakan API key tersedia pada versi 5.2+; qBittorrent 5.3.0 dapat memakai header `Authorization: Bearer …`. API key dibuat di Preferences → Web UI → API Key; hanya satu key aktif pada satu waktu dan rotasi membatalkan key sebelumnya. Belum ada key/credential yang dibuat atau dimasukkan ke chat/repo.
