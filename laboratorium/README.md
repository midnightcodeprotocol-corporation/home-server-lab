# Indeks catatan laboratorium

Folder ini menampung pengetahuan kerja yang berkembang dari ide sampai hasil, kendala, dan evaluasi. Setiap catatan sebaiknya berdiri sendiri, bertanggal, mudah ditautkan dari STATUS/papan kerja, dan tidak memuat rahasia.

## Alur pengetahuan

```text
IDE → EVALUASI KELAYAKAN → RENCANA → PERCOBAAN → HASIL / KENDALA
                      ↑                              │
                      └──────── OPTIMASI ←───────────┘
```

Alur ini tidak wajib lurus. Percobaan boleh membatalkan rencana; kendala boleh melahirkan ide baru. Catat perubahan keputusan di `docs/08-keputusan.md` bila memang sudah disepakati.

## Lokasi catatan

| Topik | Lokasi | Panduan |
|---|---|---|
| Ide | `laboratorium/ide/` | Satu file per ide; salin [template ide](ide/TEMPLATE.md). |
| Rencana | `perencanaan-arsitektur/`, `docs/`, `rencana-pemasangan/` | Tandai target, dependensi, risiko, kriteria lulus, dan rollback. |
| Data | `data/` dan snapshot bertanggal di `docs/` | Pertahankan sumber, tanggal pengamatan, dan tingkat keyakinan. Jangan menyimpan rahasia. |
| Hasil percobaan | `laboratorium/percobaan/` | Laporan lengkap memakai [template percobaan](percobaan/TEMPLATE.md); ringkasan juga dicatat di `catatan/hasil-uji.md`. |
| Kendala | `laboratorium/kendala/` | Satu file per kendala dengan [template kendala](kendala/TEMPLATE.md); indekskan juga di `catatan/belum-pasti.md` atau `catatan/kasus-nyata-lab.md` sesuai jenisnya. |
| Kelayakan | `laboratorium/evaluasi/` | Salin [template kelayakan](evaluasi/TEMPLATE-kelayakan.md); evaluasi opsi, resource, biaya, keamanan, dan pemulihan. |
| Optimasi | `laboratorium/evaluasi/` | Salin [template optimasi](evaluasi/TEMPLATE-optimasi.md); bandingkan baseline dan hasil sesudah perubahan. |
| Keputusan | `docs/08-keputusan.md` | Rekam keputusan final, alasan, tanggal, dan alternatif. |

## Aturan kualitas

- Gunakan nama file `YYYY-MM-DD-topik-singkat.md` untuk catatan bertanggal.
- Tandai fakta sebagai **live terverifikasi**, **dilaporkan**, **historis**, **rencana**, atau **belum diverifikasi**.
- Untuk angka/resource, tulis unit, metode/sumber pengukuran, dan waktu pengukuran.
- Untuk pengujian, nyatakan prasyarat, perangkat/guest terdampak, perubahan yang dilakukan, backup/rollback, hasil yang diharapkan, hasil aktual, dan keterbatasan.
- Jangan menyamakan `stopped` dengan belum dibuat atau kosong. Audit file/data sebelum mengubah atau menghapus guest.
- Jangan menyimpan atau menampilkan password, token, private key, kunci backup/enkripsi, isi `.env`, data keluarga, atau credential dalam log.
- Jangan jalankan percobaan pada server produksi tanpa instruksi pengguna, audit awal, batas risiko, dan pemulihan yang sesuai.

## Template

- [Ide](ide/TEMPLATE.md)
- [Percobaan](percobaan/TEMPLATE.md)
- [Kendala](kendala/TEMPLATE.md)
- [Kelayakan](evaluasi/TEMPLATE-kelayakan.md)
- [Optimasi](evaluasi/TEMPLATE-optimasi.md)
