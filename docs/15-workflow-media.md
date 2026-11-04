# Rancangan workflow otomasi media Jellyfin

**Status: rancangan untuk ditinjau; belum menjadi workflow operasional.** Pengguna mengusulkan tiga pintu masuk: tautan unduhan langsung, tautan torrent, serta folder pengumpulan.

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
- Torrent client sebaiknya guest/container Proxmox tersendiri, bukan diberi hak menjalankan shell dari n8n. Penempatan guest, VMID, RAM, IP, firewall, serta mount harus ditetapkan lewat plan dan diverifikasi live sebelum pemasangan.
- Link langsung dibatasi ke HTTP(S), verifikasi redirect/ukuran/tipe file dan host untuk mengurangi SSRF dan unduhan tak sengaja. Tautan autentikasi tidak disimpan di workflow atau log; kredensial dikelola melalui n8n Credentials.
- n8n belum diberi kredensial AI/katalog; jangan kirim file video utuh ke model. Tahap awal dapat mengandalkan nama + metadata teknis + katalog, dengan Review manual saat confidence rendah.
- Prototipe `Media — Inbox ke Movies dan Shows` yang hanya parsing nama sudah diuji dan kemudian di-unpublish pada 5 Nov 2026 sesuai arahan pengguna; jangan aktifkan kembali sebagai solusi akhir.

## Kondisi implementasi awal 5 Nov 2026

- CT119 `.113`: n8n 2.46.6/PostgreSQL sehat; helper `media-organizer` internal Docker, health healthy, tidak menerbitkan port di LAN.
- Helper mengembalikan daftar file Inbox, memvalidasi child path dan ekstensi, membatasi destination ke Movies/Shows, menolak path traversal/symlink dan destination yang telah ada, serta memindahkan tanpa menyalin video. Uji dummy kecil berhasil dan bersih.
- Prototipe workflow di-unpublish. Workflow aktif: 0. Portainer environment CT119, monitor Kuma, direct download dan torrent belum dibuat.
- Backup PBS terenkripsi CT119 `ct/119/2026-11-04T17:41:16Z` berhasil; PBS berada pada NVMe fisik yang sama dengan Proxmox.
