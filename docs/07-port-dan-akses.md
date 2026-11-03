# 07 - Port dan akses

## Alamat dan port per guest
| Guest | IP | Port | Akses | Lewat |
|---|---|---|---|---|
| MikroTik | .1 | 80 (WebFig), WinBox | LAN | langsung |
| TL-WR820N (AP) | .2 | 80 | LAN | langsung |
| TL-WR840N | 192.168.0.1 | 80 | jaringan atas | langsung |
| Proxmox host (M710q) | `192.168.88.10` (terverifikasi aktif; GUI dan SSH audit) | 8006, 22 | LAN + IPSet admin (rencana firewall) | `proxmox.home.arpa` |
| CT101 adguard2 | `192.168.88.11` statis; wizard selesai 2 Nov | 80 Admin UI HTTP; 53 DNS TCP/UDP (A/AAAA lulus dari Proxmox; tes klien pending) | LAN | `http://192.168.88.11` |
| CT102 files (Samba) | `192.168.88.12` statis; smbd/nmbd aktif; pengguna menyatakan password `labshare` sudah dibuat | 445 SMB | LAN | File Explorer: `\\192.168.88.12\Media`, `\\192.168.88.12\Files`; uji Windows belum dicatat. Samba tidak menyediakan web UI. |
| CT103 tailscale-router | DHCP sementara `.104`; IP final belum ditetapkan | Route `192.168.88.0/24` tampil sebagai primary pada node | Laptop berhasil menjangkau Immich `.20:2283`; uji aplikasi dari ponsel masih pending | Klien Tailscale dapat mengakses IP LAN melalui CT103 selama Tailscale aktif |
| CT104 docker-services | Statis `192.168.88.20/24` pada config CT; di luar pool DHCP, belum ada router reservation | 9443 Portainer HTTPS, 8096 Jellyfin HTTP, 2283 Immich HTTP, 8080 Nextcloud HTTP, 8070 Gotify HTTP, 8090 Beszel HTTP; monitoring lama dihentikan untuk rollback | LAN / tailnet melalui route CT103; akses `.20:2283` dari laptop lewat Tailscale telah lulus | `https://192.168.88.20:9443`, `http://192.168.88.20:8096`, `http://192.168.88.20:2283`, `http://192.168.88.20:8080`, `http://192.168.88.20:8070`, `http://192.168.88.20:8090` (Beszel akun dan kedua agent terhubung; target Gotify PVE diuji, matcher PVE aktif; notifikasi event nyata belum diverifikasi) |
| CT105 Portainer | DHCP `.105`, reservation dilaporkan pengguna | 9443 HTTPS; Agent clients hanya menerima koneksi dari CT105 | LAN | `https://192.168.88.105:9443` |
| CT109 Uptime Kuma | DHCP `.106`; reservation dilaporkan static pengguna | 3001 HTTP; Agent 9001 hanya dari CT105 | LAN / tailnet | `http://192.168.88.106:3001` |
| CT110 Prometheus | DHCP `.107` aktif; static lease MikroTik belum diverifikasi | 9090 HTTP hanya menerima CT104 rollback dan CT111 Grafana; Agent 9001 hanya dari CT105 | LAN terbatas | `http://192.168.88.107:9090` |
| CT111 Grafana | DHCP `.108` aktif; static lease MikroTik belum diverifikasi | 3000 HTTP; Agent 9001 hanya dari CT105 | LAN / tailnet | `http://192.168.88.108:3000` |
| VM 201 docker-core | Stopped, tanpa IP; `.20` dialihkan ke CT104 | 80, 443 (Caddy, rencana lama) | seluruh LAN | gerbang |
| | | 3001 Kuma, 8090 Beszel, 8070 Gotify, 9443 Portainer, 3002 Homepage | di balik Caddy; 8070 dibuka untuk host, n8n, PBS | |
| VM 202 haos | Lease DHCP aktif `192.168.88.21`; reservasi dilaporkan pengguna | 8123 | LAN + Tailscale (rencana) | `http://192.168.88.21` (wizard selesai menurut pengguna); `ha.lan` belum disiapkan |
| VM 203 k3s | .22 | 6443 | IPSet admin | langsung |
| VM 204 git | .23 | 3000 web, 2222 SSH Git | web dari .20; SSH dari admin dan .22 | `git.home.arpa` |
| VM 205 vault | .24 | 127.0.0.1:8081 | Tailscale Serve | `lab-vault.*.ts.net` |
| VM 206 affine | .25 | 3010 | dari .20 | `affine.home.arpa` |
| VM 207 (slot lama Nextcloud) | `.26` target lama; VM tidak dibuat | — | — | Nextcloud 35.0.2.2 berjalan di CT104, lihat baris CT104 |
| VM 208 n8n | .27 | 5678 | dari .20 | `n8n.home.arpa` |
| VM 209 web | .28 | 8081 WordPress, 8082 situs | dari .20 | `wp.home.arpa`, `web.home.arpa` |
| VM 210 web-public | .29 | (tidak ada masuk) | Cloudflare Tunnel keluar | domain Anda |
| VM 211 music | .31 | 127.0.0.1:4533 | Tailscale Serve | `lab-music.*.ts.net` |
| VM 212 pbs | `192.168.88.30`; datastore `store1` dan storage PVE `pbs-store1` aktif | 8007 HTTPS | admin LAN/tailnet | `https://192.168.88.30:8007`; jadwal harian terenkripsi aktif, backup uji CT101 berhasil dipulihkan; verifikasi job terjadwal pertama masih menunggu |
| VM 213 sso | .32 | 127.0.0.1:1411 | Tailscale Serve | `lab-sso.*.ts.net` |
| VM 214 (slot lama Immich) | .33 target lama, belum dibuat | — | — | Immich dialihkan ke CT104; lihat baris CT104 |
| STB 1 | .3 | 80 admin, 53 DNS | LAN | `adguard.home.arpa` |
| Agen Beszel | tiap mesin | 45876 | hanya dari .20 | |

Nama PBS diakses lewat **IP**, bukan nama: rewrite `*.home.arpa` mengarahkan nama ke docker-core.

## Matriks siapa boleh ke mana (Bab 51.2)
- Semua VM: SSH hanya dari IPSet `admin` (PC kabel 192.168.88.252, laptop, alamat CT103).
- VM di belakang Caddy: port layanan hanya dari `192.168.88.20`.
- VM 205, 211, 213, 214: slot target, belum ada port layanan aktif di LAN.
- VM 210: tidak boleh keluar ke LAN selain DNS.

## Nama domain
| Akhiran | Dipakai untuk | Catatan |
|---|---|---|
| `.home.arpa` | Layanan baru (Caddy) | Standar untuk jaringan rumah; hindari `.local` (bentrok mDNS) |
| `.lan` / `lab.local` | Nama lama Edisi 2 | Boleh berdampingan |
| `.ts.net` | Node Tailscale Serve | Hanya terjawab lewat Tailscale |

## Cara masuk dari luar rumah
Tailscale CT103 online dan route `192.168.88.0/24` tampil pada status node; koneksi dari klien HP/laptop belum diuji. Setelah klien Tailscale aktif: klien -> CT103 -> IP layanan LAN. Nextcloud memiliki web UI di `http://192.168.88.20:8080`; untuk akses di luar rumah gunakan route Tailscale, jangan buka port ke internet.
Jangan buka port 8006, 22, atau 80 MikroTik ke internet.
