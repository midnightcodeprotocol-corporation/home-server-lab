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
