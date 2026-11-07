# Home Server Lab

Repo ini adalah **buku catatan kerja dan basis pengetahuan hidup** untuk merencanakan, membangun, menguji, memahami, dan mengoptimalkan home server keluarga. Fungsinya mengumpulkan ide, rencana, data, hasil percobaan, kendala, evaluasi kelayakan, keputusan, dan pelajaran pemulihan.

Buku panduan/PDF tetap tersedia sebagai salah satu cara menyajikan pengetahuan yang sudah terkumpul. Buku bukan lagi tujuan utama repo; catatan sumber, bukti, keputusan, dan status proyek lebih penting daripada menghasilkan bab atau PDF.

## Mulai di sini

1. Baca [status proyek](STATUS.md) untuk melihat posisi dan pekerjaan berikutnya.
2. Baca [indeks laboratorium](laboratorium/README.md) untuk mencatat ide, percobaan, kendala, kelayakan, dan optimasi dengan format konsisten.
3. Untuk kondisi server, gunakan [inventaris live terakhir](docs/16-inventaris-live-2026-11-06.md) dan [data guest](data/guest.yaml). Snapshot itu bertanggal 6 November 2026, bukan keadaan live hari ini.
4. Untuk arsitektur dan tahapan target, lihat [rencana menyeluruh](perencanaan-arsitektur/README.md), [matriks aktual vs rencana](docs/13-matriks-rencana-aktual.md), dan [papan kerja](docs/04-board.md).

## Apa yang dikumpulkan

| Jenis catatan | Tempat utama |
|---|---|
| Ide baru dan pertanyaan | `laboratorium/ide/` memakai [template ide](laboratorium/ide/TEMPLATE.md) |
| Rencana arsitektur dan rencana kerja | `perencanaan-arsitektur/`, `docs/`, dan `rencana-pemasangan/` |
| Data terstruktur perangkat/guest | `data/`; inventaris bertanggal di `docs/` |
| Hasil percobaan | `catatan/hasil-uji.md` untuk ringkasan; `laboratorium/percobaan/` untuk laporan rinci |
| Kendala, kegagalan, dan hal belum pasti | `catatan/belum-pasti.md`, `catatan/kasus-nyata-lab.md`, serta `laboratorium/kendala/` untuk laporan rinci |
| Kelayakan, pilihan, biaya, risiko, dan resource | `laboratorium/evaluasi/` memakai template evaluasi |
| Keputusan yang sudah disepakati | `docs/08-keputusan.md` |
| Buku panduan/PDF | `docs/bab/` dan `tools/book_builder/` sebagai keluaran turunan/opsional |

## Cara mencatat

- Pisahkan **terlihat live**, **dilaporkan pengguna**, **historis**, **rencana**, dan **belum diverifikasi**. Selalu cantumkan tanggal dan sumber untuk data yang dapat berubah.
- Ide bukan keputusan; rencana bukan implementasi; perintah yang tertulis bukan bukti berhasil; hasil uji harus menyertakan kondisi, langkah, hasil, dan keterbatasannya.
- Catat kegagalan dan jalan buntu juga. Sertakan pesan error yang tidak sensitif, dampak, dugaan penyebab, pemeriksaan yang sudah dilakukan, serta langkah berikutnya.
- Sebelum memilih solusi, catat kelayakan: kebutuhan, dependensi, resource, biaya, risiko, pilihan alternatif, pemulihan, dan kriteria berhasil.
- Jangan menjalankan perubahan server/router hanya karena sebuah rencana tercatat. Untuk setiap pekerjaan yang diminta, cocokkan dulu keadaan aktual dengan audit baca-saja.
- Jangan menyimpan password, token, private key, kunci enkripsi, isi `.env`, atau data pribadi keluarga. Repo ini harus tetap privat karena berisi detail jaringan rumah.

## Snapshot proyek

- **Audit live terakhir yang terdokumentasi:** 6 November 2026. Periksa [STATUS](STATUS.md) dan [inventaris](docs/16-inventaris-live-2026-11-06.md); semuanya perlu dicocokkan sebelum tindakan karena dapat berubah.
- **Fokus terbuka yang tercatat:** backup independen dan bind mount, kapasitas thin-pool, audit DHCP/firewall MikroTik, rekonsiliasi data Immich/rollback CT104, serta hardening CT121.
- **Rencana lokal AI:** Ollama dan 9Router dicatat sebagai kandidat, bukan layanan yang sudah terpasang. Lihat rencana menyeluruh untuk batas resource, akses, dan ketidakpastian integrasi.
- **Rencana ekspansi:** NAS tersendiri, node PVE kedua/cluster, dan unit AI/LLM khusus dicatat sebagai skenario masa depan; belum ada pembelian, alamat, migrasi, hardware, atau pilihan HA yang ditetapkan.

## Struktur repo

```text
laboratorium/          indeks, ide, laporan percobaan, kendala, evaluasi, template
perencanaan-arsitektur/ arsitektur target dan fase proyek
data/                  inventaris terstruktur perangkat dan guest
docs/                  konteks, keputusan, port, alur data, inventaris, handbook opsional
catatan/               hasil uji ringkas, kasus nyata, dan hal belum pasti
konfigurasi/            konfigurasi contoh yang sudah dirapikan; bukan kredensial
tools/                 utilitas dan pembangun handbook/PDF
```

Perubahan status pada perangkat, file, IP, atau layanan harus menyertakan tanggal/sumber. Untuk pertanyaan atau keputusan yang belum terjawab, tambahkan catatan lalu prioritaskan satu pertanyaan pada satu waktu.
