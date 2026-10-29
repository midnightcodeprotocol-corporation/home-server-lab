# 06 - Dasar dan konsep

Dari yang paling dasar. Rujukan: Bab 1.5 dan Lampiran D buku.

## Jaringan
| Istilah | Arti sederhana | Di proyek ini |
|---|---|---|
| IP address | Alamat perangkat, seperti nomor rumah | 192.168.88.10 = Proxmox |
| CIDR /24 | Tiga angka pertama sama untuk semua perangkat | 192.168.88.0/24 |
| Gateway | Pintu ke luar jaringan | MikroTik 192.168.88.1 |
| DNS | Penerjemah nama ke IP | AdGuard 192.168.88.253 |
| DNS sinkhole | DNS yang menjawab 0.0.0.0 untuk domain iklan | AdGuard Home |
| DHCP | Pembagi IP otomatis | MikroTik, pool .100-.254 |
| Static lease | IP tetap berdasarkan MAC | semua VM, LXC, STB |
| MAC address | Nomor unik kartu jaringan | Lihat di Hardware VM |
| NAT / masquerade | Banyak perangkat berbagi satu alamat | MikroTik di ether1 |
| WISP | Router menerima internet lewat WiFi | TL-WR840N |
| Double NAT | Router di belakang router lain | Terjadi pada setup awal; urutan dibenahi |
| Bridge (vmbr0) | Saklar virtual Proxmox | Menghubungkan VM ke kabel LAN |
| Bridged (VMware) | VM mendapat IP sendiri di LAN | Mode lab VMware |

## Virtualisasi
| Istilah | Arti |
|---|---|
| VM | Komputer virtual penuh dengan kernel sendiri |
| LXC | Container ringan berbagi kernel host |
| Nested | VM di dalam VM (Proxmox di VMware) |
| VT-x / AMD-V | Fitur CPU untuk virtualisasi (wajib di BIOS) |
| Hyper-V | Hypervisor Windows; bentrok dengan VMware bila aktif |
| ISO | Salinan DVD instalasi |
| Templat | VM sumber untuk diklon (9100 untuk layanan, 9000 cloud-init untuk k3s) |
| Snapshot | Titik simpan kondisi VM, **bukan backup** |
| vzdump / PBS | Backup bawaan Proxmox / server backup terdeduplikasi |

## Tiga model instal Proxmox
| Model | Di mana | Kapan |
|---|---|---|
| A | Di dalam VM (VMware) | Latihan saat mesin belum ada |
| B | Langsung di mesin asli (USB bootable) | Cara standar, paling bersih |
| C | Instal ke disk di komputer lain, lalu dipindah | Mesin tujuan tanpa layar/USB berfungsi |

Model A tidak bisa dipindah ke mesin asli: instal ulang bersih lalu restore backup.

## Keamanan
| Istilah | Arti |
|---|---|
| Kunci SSH | Pasangan privat (di laptop) dan publik (di server), pengganti password |
| 2FA / TOTP | Kode 6 digit dari aplikasi autentikator |
| UFW | Firewall sederhana Linux (**tidak** mengatur port yang dibuka Docker) |
| Firewall Proxmox | Bekerja di bridge, di luar guest; tidak bisa ditembus port Docker |
| Safe Mode (MikroTik) | Membatalkan perubahan otomatis bila koneksi putus |
| Tailnet / subnet router | Jaringan privat Tailscale / perangkat pintu ke LAN |
| Tailscale Serve vs Funnel | Serve: hanya anggota tailnet. Funnel: terbuka ke internet (**tidak dipakai**) |
| Reverse proxy (Caddy) | Satu pintu HTTPS yang meneruskan ke layanan |
| CA lokal | Otoritas sertifikat buatan sendiri; akarnya dipasang di perangkat |
| SSO / OIDC / passkey | Satu login untuk banyak aplikasi / standarnya / login tanpa kata sandi |

## Aturan 3-2-1
Tiga salinan, dua media, satu di luar lokasi. Satu mesin saja belum memenuhi; salinan USB offline dan arsip konfigurasi host menutup celah itu.

## Kebiasaan baik
- Matikan server dengan benar, jangan cabut HDD saat VM jalan.
- Penomoran: LXC 100-199, VM 200-299, templat 9000+.
- Snapshot sebelum eksperimen besar; jangan menumpuk banyak snapshot.
- Pin versi image Docker (bukan `latest`) dan biarkan Renovate mengusulkan pembaruan.
- Rahasia di `.env` berizin 600; tidak pernah di Git.
