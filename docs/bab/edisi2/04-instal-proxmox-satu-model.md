# Bab 4. Instal Proxmox di Mesin Asli (Satu Model)

## 4.1 Keputusan: satu model saja

Proxmox VE dipasang **langsung di mesin asli** (Lenovo ThinkCentre M710q). Hasil akhirnya server Proxmox dengan web di port 8006, disk sistem di NVMe 500 GB.

| Pada Edisi 2/3 | Pada Revisi 3 | Alasan |
|---|---|---|
| Model A: Proxmox di VM VMware | **Dihapus** | Mesin asli sudah ada; lab nested lambat dan tidak bisa dipindah ke mesin asli |
| Model B: mesin asli | **Satu-satunya model** | Performa penuh, fitur perangkat keras (passthrough, sensor, Wake-on-LAN) tersedia |
| Model C: instal ke disk dulu, lalu dipindah | **Dihapus** | Mesin asli bisa boot dari USB; tidak perlu memindah disk dan memperbaiki nama kartu jaringan |

Bab 5 dan Bab 7 (serta Bab 29) tetap ada sebagai penanda singkat agar nomor bab dan rujukan silang tidak bergeser.

## 4.2 Urutan kerja

| Langkah | Bab |
|---|---|
| Kenali mesin: spesifikasi, RAM, disk, BIOS | Bab 27 |
| Siapkan perangkat dan USB bootable, boot dari USB | Bab 6 |
| Instal layar demi layar | Bab 8 (dan Bab 28 untuk nilai khusus M710q) |
| Konfigurasi awal: jaringan, DNS, repository, update | Bab 9 |
| Pasca-instalasi: sensor, SMART, Wake-on-LAN | Bab 30 |
