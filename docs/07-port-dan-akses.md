# 07 - Port dan akses

## Alamat dan port per guest
| Guest | IP | Port | Akses | Lewat |
|---|---|---|---|---|
| MikroTik | .1 | 80 (WebFig), WinBox | LAN | langsung |
| TL-WR820N (AP) | .2 | 80 | LAN | langsung |
| TL-WR840N | 192.168.0.1 | 80 | jaringan atas | langsung |
| Proxmox host (M710q) | .10 | 8006, 22 | LAN + IPSet admin | `proxmox.home.arpa` |
| CT101 adguard2 | .11 | 80, 53 | LAN | `adguard2.lan` |
| CT102 files (Samba) | .12 | 445 | LAN | `\\192.168.88.12\share` |
| VM 201 docker-core | .20 | 80, 443 (Caddy) | seluruh LAN | gerbang |
| | | 3001 Kuma, 8090 Beszel, 8070 Gotify, 9443 Portainer, 3002 Homepage | di balik Caddy; 8070 dibuka untuk host, n8n, PBS | |
| VM 202 haos | .21 | 8123 | LAN + Tailscale | `ha.lan` |
| VM 203 k3s | .22 | 6443 | IPSet admin | langsung |
| VM 204 git | .23 | 3000 web, 2222 SSH Git | web dari .20; SSH dari admin dan .22 | `git.home.arpa` |
| VM 205 vault | .24 | 127.0.0.1:8081 | Tailscale Serve | `lab-vault.*.ts.net` |
| VM 206 affine | .25 | 3010 | dari .20 | `affine.home.arpa` |
| VM 207 nextcloud | .26 | 8080 | dari .20 | `nextcloud.home.arpa` |
| VM 208 n8n | .27 | 5678 | dari .20 | `n8n.home.arpa` |
| VM 209 web | .28 | 8081 WordPress, 8082 situs | dari .20 | `wp.home.arpa`, `web.home.arpa` |
| VM 210 web-public | .29 | (tidak ada masuk) | Cloudflare Tunnel keluar | domain Anda |
| VM 211 music | .31 | 127.0.0.1:4533 | Tailscale Serve | `lab-music.*.ts.net` |
| VM 212 pbs | .30 | 8007 | host .10 dan admin | `https://192.168.88.30:8007` |
| VM 213 sso | .32 | 127.0.0.1:1411 | Tailscale Serve | `lab-sso.*.ts.net` |
| VM 214 immich | .33 | 127.0.0.1:2283 | Tailscale Serve | `lab-immich.*.ts.net` |
| STB 1 | .253 | 80 admin, 53 DNS | LAN | `adguard.home.arpa` |
| Agen Beszel | tiap mesin | 45876 | hanya dari .20 | |

Nama PBS diakses lewat **IP**, bukan nama: rewrite `*.home.arpa` mengarahkan nama ke docker-core.

## Matriks siapa boleh ke mana (Bab 51.2)
- Semua VM: SSH hanya dari IPSet `admin` (PC kabel 192.168.88.252, laptop, alamat CT103).
- VM di belakang Caddy: port layanan hanya dari `192.168.88.20`.
- VM 205, 211, 213, 214: tidak ada port layanan di LAN.
- VM 210: tidak boleh keluar ke LAN selain DNS.

## Nama domain
| Akhiran | Dipakai untuk | Catatan |
|---|---|---|
| `.home.arpa` | Layanan baru (Caddy) | Standar untuk jaringan rumah; hindari `.local` (bentrok mDNS) |
| `.lan` / `lab.local` | Nama lama Edisi 2 | Boleh berdampingan |
| `.ts.net` | Node Tailscale Serve | Hanya terjawab lewat Tailscale |

## Cara masuk dari luar rumah
Tailscale aktif di HP/laptop -> subnet router CT103 (nanti STB 2) -> LAN, atau langsung ke node `lab-*`.
Jangan buka port 8006, 22, atau 80 MikroTik ke internet.
