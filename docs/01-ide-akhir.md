# 01 - Ide akhir (target arsitektur)

Gambaran setelah seluruh buku (Edisi 2 + Suplemen 1-9) dikerjakan dan lulus uji.

## Ringkasan dalam satu kalimat
Satu host Proxmox polos (tanpa Docker) berisi VM/LXC terpisah per layanan; satu gerbang HTTPS (Caddy)
untuk layanan privat; layanan paling sensitif hanya lewat Tailscale Serve; backup harian ke PBS di
disk terpisah dengan salinan kedua; firewall Proxmox antar-guest; akses luar hanya Tailscale.

## Diagram target

```mermaid
flowchart TB
  NET["Internet / IndiHome (WiFi)"] --> WR840["TL-WR840N<br/>mode WISP"]
  WR840 --> MT["MikroTik RB750GL<br/>192.168.88.1<br/>DHCP, firewall, NAT"]
  MT --> AP["TL-WR820N (AP)<br/>192.168.88.2"]
  MT --> SW["Switch LiteWave LS1005"]
  MT --> STB1["STB 1 .253<br/>AdGuard Home utama"]
  MT --> STB2["STB 2 .250 (nanti)<br/>Tailscale subnet router"]
  SW --> PVE

  subgraph PVE["Host Proxmox 192.168.88.10 (ThinkCentre M710q, tanpa Docker)"]
    direction TB
    V201["201 docker-core .20<br/>Caddy, Portainer, Gotify,<br/>Uptime Kuma, Beszel, Homepage"]
    V202["202 haos .21"]
    V203["203 k3s .22"]
    V204["204 git .23<br/>Forgejo, Renovate"]
    V205["205 vault .24<br/>Vaultwarden"]
    V206["206 affine .25"]
    V207["207 nextcloud .26"]
    V208["208 n8n .27"]
    V209["209 web .28"]
    V210["210 web-public .29"]
    V211["211 music .31"]
    V212["212 pbs .30"]
    V213["213 sso .32"]
    V214["214 immich .33"]
    C101["CT101 adguard2 .11"]
    C102["CT102 files .12"]
    C103["CT103 ts-router"]
  end
```

## Aturan penempatan (Bab 48.2)
| Pertanyaan | Jika ya |
|---|---|
| Memakai Docker? | VM (bukan LXC) |
| Layanan Linux ringan tanpa Docker? | Boleh LXC |
| Menyimpan rahasia? | VM sendiri |
| Menghadap internet? | VM sendiri, paling terisolasi |
| Data besar / siklus update berbeda? | VM sendiri |
| Ringan dan saling bergantung? | Gabung di docker-core |

## Tiga jalur akses
| Jalur | Dipakai oleh | Sertifikat |
|---|---|---|
| A. Caddy `*.home.arpa` | web, WordPress, n8n, AFFiNE, Nextcloud, Forgejo, Kuma, Beszel, Gotify | CA lokal Caddy (akar dipasang di perangkat) |
| B. Tailscale Serve `*.ts.net` | Vaultwarden, Navidrome, Pocket ID, Immich | Sertifikat tepercaya (tanpa domain) |
| C. Cloudflare Tunnel (opsional) | Hanya situs statis publik (VM 210) | Sertifikat Cloudflare |

## Pertahanan berlapis (Bab 25.1)
1. Internet: tidak ada port dibuka dari rumah.
2. WISP + IndiHome: NAT berlapis, tanpa port forwarding.
3. MikroTik: firewall input dan forward, layanan admin dibatasi LAN.
4. Tailscale: satu-satunya jalan masuk dari luar, dengan kebijakan akses.
5. Proxmox dan VM: firewall antar-guest, akun admin terpisah, 2FA, SSH hanya kunci.
6. Aplikasi dan data: update otomatis, backup 3-2-1, uji pemulihan.

## Backup (Bab 50)
- PBS di VM 212, datastore di disk fisik terpisah, enkripsi sisi klien (kunci wajib disimpan di dua tempat).
- Job harian 02:00 (snapshot), prune/GC/verify di PBS.
- Salinan kedua di luar mesin (USB offline), arsip konfigurasi host (`/etc/pve`).
- **Belum dianggap ada sebelum satu uji pulih berhasil.**

## Mesin: Lenovo ThinkCentre M710q (Bab 27 dan 56)
Core i5-6500T (4 core/4 thread), NVMe 500 GB, HDD 2 TB untuk backup. RAM 16 GB terpasang; dengan RAM cadangan menjadi **32 GB (16+16)**.
- Dengan 16 GB: lima profil pemakaian (harian, kerja, foto, backup, belajar) memakai `konfigurasi/skrip/profil.sh`.
- Dengan 32 GB: mode hemat, semua VM menyala bersamaan (Bab 56.7). Batas berikutnya adalah CPU 4 thread.

## Yang belum masuk target
Suplemen 10-11: AMP + playit.gg, Ollama, OnlyOffice, TrueNAS, STB 2, update profil RAM saat RAM naik.
Lihat `04-board.md`.
