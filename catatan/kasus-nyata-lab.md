# Kasus nyata (arsip)

Masalah yang benar-benar terjadi. **Bagian lab VMware sudah tidak relevan** karena Proxmox dipasang langsung di mesin asli, tetapi disimpan sebagai pelajaran.

## Jaringan awal (Oktober 2026), masih relevan
| Gejala | Penyebab | Solusi |
|---|---|---|
| Router TL-WR820N di belakang router lain; IP 192.168.1.x | Double NAT, urutan perangkat salah | Urutan: WISP -> MikroTik -> AP |
| Password admin ditolak pada halaman router yang tampak sama | Dua router berbeda dengan halaman serupa | Beri label fisik, catat alamat |
| WiFi laptop putus setelah `ipconfig /release` | IP dilepas tanpa diminta lagi | `ipconfig /renew` |
| STB tidak jelas berjalan dari eMMC atau SD | Dua instalasi Armbian | `lsblk`, `findmnt /`; pilih satu, lalu pindah ke eMMC |
| AdGuard gagal start | Port 53 dipakai systemd-resolved | `DNSStubListener=no` |

## Instalasi Proxmox pertama (16 Okt), relevan sebagian
| Gejala | Penyebab / hasil | Status |
|---|---|---|
| Web Proxmox tidak terbuka dari laptop | IP Proxmox 192.168.100.x beda jaringan dengan laptop | Selesai: ubah `interfaces` dan `hosts` (Bab 9.3) |
| `apt update` gagal | Repo enterprise aktif, DNS kosong | Selesai (Bab 9.4, 9.5) |

## Lab VMware di laptop (23-27 Okt), **arsip: dihentikan**
| Tanggal | Gejala | Penyebab / hasil uji | Status |
|---|---|---|---|
| 23 Okt | Pemasang VMware: "invalid drive G:" | Folder instal lama di drive portabel hilang | Solusi: `subst G: C:\` lalu `subst G: /d` |
| 23-24 Okt | VMnet0 tidak muncul; Bridged gagal "no un-bridged host network adapters" | Layanan `vmnetbridge` tidak terdaftar (error 1060); `VMAuthdService` tidak berjalan; instal ulang VMware tidak memperbaiki | Diselesaikan dengan **instal ulang Windows** |
| 24 Okt | Log VMware: gagal menghubungi authd | Instalasi VMware rusak sebagian | Dipasang ulang ke C: |
| 25-26 Okt | Setelah instal ulang Windows | VMnet0 Bridged ke adaptor USB-LAN (ASIX); laptop 192.168.88.252 | Berhasil |
| 27 Okt | VM tidak menyala: "Virtualized AMD-V/RVI is not supported on this platform"; `hv.capable was 0` | Hyper-V, Virtual Machine Platform, Windows Hypervisor Platform tercentang | Dimatikan, restart; VM belum dinyalakan lagi |
| 28 Okt | Mesin asli tiba | Lab dihentikan | Model A dan C dihapus dari buku |

Pelajaran umum: Windows dengan Hyper-V/WSL2 bentrok dengan VMware; adaptor WiFi sering menolak MAC tambahan untuk bridged; adaptor USB-LAN lebih stabil.

## Catatan dari Lembar Revisi 1 (24 Okt)
Lembar Revisi 1 (errata E1-E6, kasus nyata VMware, catatan adaptor NVMe M.2, hasil uji sementara) ada di PDF terpisah milik pengguna dan **tidak ada di repo**. Bila diperlukan, minta pengguna menyalin isinya ke berkas ini.

## Catatan perangkat keras lama
- PC HP lama tanpa slot NVMe M.2 (RAM 2 GB, Pentium, VT-x ada, HT tidak): tidak dipakai.
- NVMe 500 GB sebelumnya dipakai lewat adaptor USB (drive F:); kini dipasang di M.2 M710q.
