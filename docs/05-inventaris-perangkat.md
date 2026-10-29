# 05 - Inventaris perangkat

  Perangkat   Peran | Alamat / catatan |
|---|---|---|
| IndiHome | Sumber internet | Tidak ada kabel LAN yang bisa dipakai; uplink WiFi |
| TP-Link TL-WR840N v6.20 | Penerima (mode WISP) | LAN 192.168.0.1 |
| MikroTik RB750GL | Router utama | 192.168.88.1; RouterOS 6.49.23 (stable); ether1 = WAN |
| TP-Link TL-WR820N | Access Point | 192.168.88.2; DHCP mati; kabel ke port LAN |
| TP-Link LiteWave LS1005 | Switch | Opsional, memperbanyak port |
| STB HG680 (Amlogic S905x) | AdGuard Home utama | 192.168.88.253; Armbian v25.05.0 (ophub, Linux 6.1) di eMMC |
| STB 2 | Tailscale subnet router (rencana) | Belum tiba; usulan 192.168.88.250 |
| **Lenovo ThinkCentre M710q** | **Server Proxmox** | **192.168.88.10; Core i5-6500T (4 core/4 thread); RAM 16 GB terpasang; NVMe M.2 500 GB** |
| RAM cadangan 16 GB dan 8 GB | Suku cadang / penambah RAM | Rencana: 16+16 = 32 GB; 8 GB disimpan (slot hanya dua) |
| 2 × HDD Seagate Surveillance 2 TB | Calon disk data / backup; belum dialokasikan | Belum dipasang; model tiap unit belum dicatat; setidaknya satu belum diformat. Verifikasi ukuran fisik dan kebutuhan daya sebelum menentukan penempatan. |
| Laptop (AMD Ryzen 3 4300U, RAM 19,4 GB) | Laptop admin | 192.168.88.252 via adaptor USB-LAN (ASIX); WinBox, browser, SSH |

## Perangkat lain yang dimiliki (belum berperan)
Ubiquiti UniFi U6 Lite, Nokia G-2425G-A, FortiGate 60F, Cisco IP1101, TP-Link TL-POE160S.

## Tidak dipakai lagi
PC HP lama (RAM 2 GB, Pentium, tanpa slot M.2), TL-WR826N, MikroTik RB951Ui-2nD, lab VMware di laptop.

## Perangkat yang direncanakan
Modem kedua untuk failover internet, TP-Link MR3020 (cetak dari mana saja), UPS kecil, sensor monitor listrik, panel surya.

## Catatan kelistrikan
Banyak adaptor TP-Link terpisah; ada ide catu daya DC terpusat (12 V masuk; keluaran 5/12/24 V) yang rancangannya masih perlu ditinjau sebelum dibuat.
