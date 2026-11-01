# 05 - Inventaris perangkat

| Perangkat | Peran | Alamat / catatan |
|---|---|---|
| IndiHome | Sumber internet | Tidak ada kabel LAN yang bisa dipakai; uplink WiFi |
| TP-Link TL-WR840N v6.20 | Penerima (mode WISP) | LAN 192.168.0.1 |
| MikroTik RB750GL | Router utama | 192.168.88.1; RouterOS 6.49.23 (stable); ether1 = WAN utama, ether2 kosong (calon WAN2), ether3 = STB, ether4 = switch, ether5 = laptop admin |
| TP-Link TL-WR820N | Access Point | 192.168.88.2; DHCP mati; kabel ke port LAN |
| TP-Link LiteWave LS1005 | Switch | Port 1 ke MikroTik ether4; port 2 ke AP; port 3 ke Proxmox; port 4-5 kosong |
| STB HG680 (Amlogic S905x) | AdGuard Home utama | `192.168.88.3` (static DHCP lease; sebelumnya `.253`); Armbian v25.05.0 (ophub, Linux 6.1) di eMMC; DNS langsung diuji berhasil 1 Nov 2026 |
| STB 2 | Tailscale subnet router (rencana) | Belum tiba; usulan 192.168.88.250 |
| **Lenovo ThinkCentre M710q** | **Server Proxmox** | **Konfigurasi host diarahkan ke `192.168.88.10/24`, gateway `192.168.88.1`, DNS diarahkan ke `192.168.88.3` melalui NIC `enp0s31f6`; MikroTik ping 16/16 berhasil; panel WebUI terbuka. Kabel Proxmox ke switch port 3, switch port 1 ke MikroTik ether4; `getent hosts` dan `getent ahostsv4 deb.debian.org` berhasil untuk IPv6 dan IPv4; akses repository belum diuji. Sebelumnya sementara `192.168.0.200`; Core i5-6500T (4 core/4 thread); Linux melaporkan 23 GiB RAM (BIOS/MemTest belum dicatat); NVMe Samsung MZALQ512HALU-000L2 terdeteksi 476,9 GB; kernel `7.0.14-26-pve`; VT-x/KVM aktif** |
| RAM M710q | Konfigurasi fisik dilaporkan 1×16 GB + 1×8 GB | Total yang diharapkan 24 GB; pastikan kapasitas terbaca dan lulus MemTest86 |
| 2 × HDD Seagate Surveillance 2 TB, 3,5 inci | Unit 1 terdeteksi; fungsi storage belum diputuskan | Unit 1: Seagate ST2000VX008-2E3164, `/dev/sda`, partisi NTFS, SMART PASSED; belum mounted/dikonfigurasi. Unit 2 menunggu enclosure. Jangan format sebelum data dan peran dikonfirmasi. |
| Laptop (AMD Ryzen 3 4300U, RAM 19,4 GB) | Laptop admin | 192.168.88.252 via adaptor USB-LAN (ASIX); WinBox, browser, SSH |

## Perangkat lain yang dimiliki (belum berperan)
Ubiquiti UniFi U6 Lite, Nokia G-2425G-A, FortiGate 60F, Cisco IP1101, TP-Link TL-POE160S.

## Tidak dipakai lagi
PC HP lama (RAM 2 GB, Pentium, tanpa slot M.2), TL-WR826N, MikroTik RB951Ui-2nD, lab VMware di laptop.

## Perangkat yang direncanakan
Modem kedua untuk failover internet, TP-Link MR3020 (cetak dari mana saja), UPS kecil, sensor monitor listrik, panel surya.

## Catatan kelistrikan
Banyak adaptor TP-Link terpisah; ada ide catu daya DC terpusat (12 V masuk; keluaran 5/12/24 V) yang rancangannya masih perlu ditinjau sebelum dibuat.

