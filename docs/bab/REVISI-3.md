# Revisi 3: apa yang berubah

**Alasan.** Mesin asli sudah ada: Lenovo ThinkCentre M710q (Core i5-6500T, RAM 16 GB terpasang, NVMe 500 GB), dengan RAM cadangan 16 GB dan 8 GB. Lab VMware dan instal-ke-disk-dulu tidak diperlukan.

## Dihapus
| Bab | Isi | Pengganti |
|---|---|---|
| 5 | Model A: Proxmox di VM VMware | Penanda singkat; BIOS di Bab 27.5 |
| 7 | Model C: instal ke disk dulu | Penanda singkat; gunakan Bab 6 dan 8 |
| 29 | Model C (Suplemen 2) | Penanda singkat; gunakan Bab 28 |
| 9.10 | open-vm-tools | - |
| 23.5 | Prosedur pindah ke mesin asli | Diganti prosedur instal ulang dan restore |
| 30.3 (lama) | Laptop: tutup layar tidak mematikan server | Diganti penempatan fisik dan suhu M710q |
| 30.6 (lama) | Memindahkan isi lab ke mesin asli | Diganti pemulihan backup setelah instal ulang |

## Ditulis ulang
| Bab | Perubahan |
|---|---|
| 4 | Hanya satu model instalasi |
| 6 | Khusus ThinkCentre M710q (6.3-6.5 dipertahankan) |
| 27 | Spesifikasi M710q, rencana RAM 16+16 GB, rencana disk NVMe + HDD, BIOS Lenovo |
| 28 | Instal langsung di M710q (nilai khusus: nvme0n1, enp0s31f6, F1/F12) |
| 30 | Pasca-instalasi M710q; sensor, SMART, Wake-on-LAN dipertahankan |
| 56 | Tambah 56.7: RAM 32 GB, mode hemat, CPU 4 thread |
| Lampiran C | Daftar periksa untuk mesin asli |

## Disesuaikan (pengeditan kecil)
Bab 1 (tujuan, perangkat, topologi, copy-paste), Bab 2 (VMware dihapus dari alat), Bab 8 (layar installer: NVMe, F12, tanpa Model A/C), Bab 9 (kebiasaan baik, disk data), Bab 11 (kasus KVM dan lambat), Bab 13 dan 18 (kata "nested"), Bab 24 (baris VMware dan Model C dihapus), Lampiran D (glosarium), Bab 25, 26 (jalur darurat, uji luar jaringan), Bagian 3, Bab 33, 48.6, 50.2, 53, 55.

## Yang masih perlu Anda putuskan atau periksa
- Tebal dan jenis HDD 2 TB (muat di bay 2,5" M710q atau pakai casing USB), Bab 27.4.
- Ukuran disk data contoh (musik, foto, datastore PBS) agar tidak memenuhi NVMe 500 GB, Bab 27.4.
- Nama menu BIOS Lenovo persisnya (cocokkan dengan layar Anda), Bab 27.5.
- Nama kartu LAN asli (`ip -br link`); contoh memakai `enp0s31f6`.
- Spesifikasi M710q di Bab 27.1 adalah patokan model; cek label RAM dan unit Anda.
