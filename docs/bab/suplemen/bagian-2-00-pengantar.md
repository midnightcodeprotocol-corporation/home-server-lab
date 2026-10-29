# Bagian 2. Proxmox di Mesin Asli (ThinkCentre M710q) (pengantar)

Bagian ini memasang Proxmox VE di **Lenovo ThinkCentre M710q**. Model A (VMware) dan Model C (instal ke disk dulu) pada Edisi 3 sudah dihapus pada Revisi 3.

| Bab | Isi | Hasil akhir |
|---|---|---|
| 27. Mesin M710q | Spesifikasi, rencana RAM 16+16 GB, rencana disk NVMe + HDD, BIOS | Mesin siap diinstal |
| 28. Instal langsung | Unduh dan verifikasi ISO, USB bootable, boot, layar installer, masalah umum | Proxmox hidup di 192.168.88.10:8006 |
| 29. (dihapus) | Penanda | - |
| 30. Pasca-instalasi | BIOS, sensor, SMART, Wake-on-LAN, pemulihan backup, keamanan | Server stabil, bisa dinyalakan dari STB |

Urutan: Bab 27, Bab 6 (USB), Bab 8 dan 28 (instalasi), Bab 9 (konfigurasi awal), Bab 30. Lalu ulangi Bab 25 dan 26 di mesin ini.

**PERINGATAN.** Instalasi Proxmox menghapus seluruh isi disk yang dipilih. Salin dulu data penting dari NVMe (bila ada isinya) dan lepaskan HDD 2 TB berisi data selama instalasi.

| Alamat | Perangkat |
|---|---|
| 192.168.88.1 | MikroTik RB750GL |
| 192.168.88.10 | Proxmox (ThinkCentre M710q) |
| 192.168.88.20 | VM Debian 13 (docker-core) |
| 192.168.88.253 | STB HG680 (AdGuard); juga pengirim Wake-on-LAN (Bab 30.5) |
