# 09 - Mulai di ThinkCentre M710q

Urutan hari pertama. Rujukan bab ada di kolom kanan.

| Urut | Tindakan | Bab |
|---|---|---|
| 1 | Cadangkan data penting dari NVMe (bila ada isinya). Lepas HDD 2 TB selama instalasi | 6.1 |
| 2 | Periksa di BIOS bahwa dua modul RAM terbaca (diharapkan total 24 GB dari 16+8); catat slot/kapasitas dan jalankan MemTest86 | 27.1, 27.3 |
| 3 | Jalankan MemTest86 dari USB sampai 1-2 putaran tanpa error | 27.3 |
| 4 | Perbarui BIOS Lenovo (opsional), atur BIOS: VT-x wajib; VT-d opsional untuk passthrough; UEFI, Secure Boot mati, AHCI, Wake on LAN, After Power Loss, Enhanced Power Saving mati | 27.5 |
| 5 | Unduh ISO Proxmox VE, cek SHA256 | 28.3 |
| 6 | Buat USB bootable (Rufus mode DD atau Etcher) | 6.3 |
| 7 | Siapkan data instalasi: IP 192.168.88.10/24, gateway .1, DNS .253, hostname pve.lab.local | 28.2 |
| 8 | Boot dari USB (F12), instal ke NVMe, sistem berkas ext4 | 8, 28 |
| 9 | Cabut USB, boot pertama, buka https://192.168.88.10:8006 | 28.7 |
| 10 | Pengaturan awal: DNS, repository no-subscription, update | 9.4-9.6 |
| 11 | Setelah update: buat template VM 9100 dan template CT 9200 sebagai sumber guest berulang | 49.2-49.4, 49.6 |
| 12 | Sensor dan Wake-on-LAN dari STB | 30.4-30.5 |
| 13 | Saat enclosure tersedia: uji satu HDD 3,5 inci, identifikasi disk, lalu tentukan storage; jangan format sebelum verifikasi | 27.4, 9.9 |
| 14 | Keamanan dasar dan Tailscale | 25, 26 |
| 15 | Buat guest aplikasi dengan clone template; atur nama, IP, RAM/CPU, lalu pasang aplikasi | 49.4, 49.6 dan bab aplikasi |

> Template disiapkan sekali setelah host diperbarui. Gunakan VM 9100 untuk guest berbasis VM/Docker dan CT 9200 untuk layanan Linux ringan tanpa Docker. Setiap clone harus memiliki nama, alamat jaringan, identitas SSH, dan resource sendiri. Jika host masih berada di jaringan sementara, gunakan DHCP; tetapkan IP akhir setelah tersambung ke MikroTik.

Catat hasil tiap baris di `catatan/hasil-uji.md`. Berhenti dan laporkan pesan error persis bila ada yang gagal.

## Yang perlu dicatat dari mesin

| Data | Cara | Hasil Anda |
|---|---|---|
| Nama kartu LAN | `ip -br link` | |
| MAC kartu LAN (untuk WoL dan reservasi) | `ip -br link` | |
| Nama disk NVMe | `lsblk -o NAME,SIZE,MODEL` | |
| Total RAM terbaca | `free -m` | |
| Suhu CPU diam | `sensors` | |
| Kesehatan NVMe | `smartctl -H /dev/nvme0` | |

