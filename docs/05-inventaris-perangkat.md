# 05 - Inventaris perangkat

> Snapshot perangkat/lab ini memuat catatan historis. Untuk keadaan live guest, IP, MAC, versi, port, mount, dan backup per 6 Nov 2026, gunakan [inventaris aktual](16-inventaris-live-2026-11-06.md). Jalur kabel/router di sini belum diverifikasi ulang.

| Perangkat | Peran | Alamat / catatan |
|---|---|---|
| IndiHome | Sumber internet | Tidak ada kabel LAN yang bisa dipakai; uplink WiFi |
| TP-Link TL-WR840N v6.20 | Penerima (mode WISP) | LAN 192.168.0.1 |
| MikroTik RB750GL | Router utama | 192.168.88.1; RouterOS 6.49.23 (stable); ether1 = WAN utama, ether2 kosong (calon WAN2), ether3 = STB, ether4 = switch, ether5 = laptop admin |
| TP-Link TL-WR820N | Access Point | 192.168.88.2; DHCP mati; kabel ke port LAN |
| TP-Link LiteWave LS1005 | Switch | Port 1 ke MikroTik ether4; port 2 ke AP; port 3 ke Proxmox; port 4-5 kosong |
| STB HG680 (Amlogic S905x) | AdGuard Home utama | `192.168.88.3` (static DHCP lease; sebelumnya `.253`); Armbian v25.05.0 (ophub, Linux 6.1) di eMMC; DNS langsung diuji berhasil 1 Nov 2026 |
| STB 2 | Tailscale subnet router (rencana) | Belum tiba; usulan 192.168.88.250 |
| **Lenovo ThinkCentre M710q** | **Server Proxmox** | **PVE 9.2.24 pada `192.168.88.10/24`, gateway `.1`, DNS `.3`; SSH audit berhasil. Kabel ke switch port 3; switch port 1 ke MikroTik ether4. NVMe Samsung 476,9 GB; kernel `7.0.14-26-pve`; VT-x/KVM aktif. Audit live 3 Nov: CT101–104 dan VM202/212 berjalan; CT100/VM200 template serta VM201 stopped.** |
| RAM M710q | Konfigurasi fisik dilaporkan 1×16 GB + 1×8 GB | Total yang diharapkan 24 GB; pastikan kapasitas terbaca dan lulus MemTest86 |
| 2 × HDD Seagate Surveillance 2 TB, 3,5 inci | Unit 1 menjadi data aplikasi; unit 2 menunggu enclosure | HDD unit 1 pernah diverifikasi sebagai ST2000VX008-2E3164, SMART PASSED melalui USB bridge, lalu GPT/ext4 dan storage `backup-disk` dibuat. Audit PVE terbaru menunjukkan storage `backup-disk` aktif; CT102/CT104 memakai bind mount dari direktori aplikasi di HDD. PBS sementara 100 GiB ada pada NVMe. Keputusan pengguna: kedua HDD untuk aplikasi, backup tambahan menyusul. Unit 2 belum terpasang. |
| Laptop (AMD Ryzen 3 4300U, RAM 19,4 GB) | Laptop admin | 192.168.88.252 via adaptor USB-LAN (ASIX); WinBox, browser, SSH |

## Perangkat lain yang dimiliki (belum berperan)
Ubiquiti UniFi U6 Lite, Nokia G-2425G-A, FortiGate 60F, Cisco IP1101, TP-Link TL-POE160S.

## Tidak dipakai lagi
PC HP lama (RAM 2 GB, Pentium, tanpa slot M.2), TL-WR826N, MikroTik RB951Ui-2nD, lab VMware di laptop.

## Perangkat yang direncanakan
Modem kedua untuk failover internet, TP-Link MR3020 (cetak dari mana saja), UPS kecil, sensor monitor listrik, panel surya.

## Catatan kelistrikan
Banyak adaptor TP-Link terpisah; ada ide catu daya DC terpusat (12 V masuk; keluaran 5/12/24 V) yang rancangannya masih perlu ditinjau sebelum dibuat.

