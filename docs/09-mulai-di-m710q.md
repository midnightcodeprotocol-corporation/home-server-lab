# 09 - Mulai di ThinkCentre M710q

Urutan hari pertama. Rujukan bab ada di kolom kanan.

| Urut | Tindakan | Bab |
|---|---|---|
| 1 | Cadangkan data penting dari NVMe (bila ada isinya). Lepas HDD 2 TB selama instalasi | 6.1 |
| 2 | Pasang RAM 16 GB cadangan di slot kedua (total 32 GB). Simpan 8 GB sebagai suku cadang | 27.1 |
| 3 | Jalankan MemTest86 dari USB sampai 1-2 putaran tanpa error | 27.3 |
| 4 | Perbarui BIOS Lenovo (opsional), atur BIOS: VT-x, VT-d, UEFI, Secure Boot mati, AHCI, Wake on LAN, After Power Loss, Enhanced Power Saving mati | 27.5 |
| 5 | Unduh ISO Proxmox VE, cek SHA256 | 28.3 |
| 6 | Buat USB bootable (Rufus mode DD atau Etcher) | 6.3 |
| 7 | Siapkan data instalasi: IP 192.168.88.10/24, gateway .1, DNS .253, hostname pve.lab.local | 28.2 |
| 8 | Boot dari USB (F12), instal ke NVMe, sistem berkas ext4 | 8, 28 |
| 9 | Cabut USB, boot pertama, buka https://192.168.88.10:8006 | 28.7 |
| 10 | Pengaturan awal: DNS, repository no-subscription, update | 9.4-9.6 |
| 11 | Sensor, SMART, Wake-on-LAN dari STB | 30.4-30.5 |
| 12 | Pasang HDD 2 TB (bay 2,5" atau USB), buat Directory | 27.4, 9.9 |
| 13 | Keamanan dan Tailscale | 25, 26 |
| 14 | Templat VM 9100 dan VM pertama | 49 |

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
