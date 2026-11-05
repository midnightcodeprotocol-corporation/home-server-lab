# 02 - Rangkaian koneksi

> Audit terkini 6 Nov 2026: inventaris live, guest, alamat, port, keterhubungan, dan ketidakpastian RouterOS ada di [docs/16](16-inventaris-live-2026-11-06.md). Diagram kabel/rencana di dokumen ini sebagian besar catatan historis dan belum diverifikasi ulang. Jangan menganggap proxy Caddy, VM 201–211, port forwarding, DNS DHCP, atau firewall di bawah sudah diterapkan.

Dari kabel fisik sampai alur data. Diagram memakai Mermaid (tampil otomatis di GitHub).

## 1. Rangkaian fisik (kabel dan radio)

```mermaid
flowchart LR
  ISP["IndiHome (WiFi saja)"] -. WiFi .-> WR840["TL-WR840N (WISP)<br/>LAN 192.168.0.1"]
  WR840 -- "kabel LAN" --> E1["MikroTik ether1<br/>WAN utama"]
  subgraph MT["MikroTik RB750GL, LAN 192.168.88.1/24"]
    E1
    E2["ether2: kosong; calon WAN2"]
    E3["ether3: STB AdGuard .3"]
    E4["ether4: uplink switch"]
    E5["ether5: laptop admin .252"]
  end
  E3 --- STB["STB HG680<br/>AdGuard Home"]
  E4 --> SW1
  subgraph SW["Switch LiteWave LS1005"]
    SW1["Port 1: uplink MikroTik"]
    SW2["Port 2: AP"]
    SW3["Port 3: Proxmox .10"]
    SW4["Port 4: kosong"]
    SW5["Port 5: kosong"]
  end
  SW2 --- AP["TL-WR820N<br/>192.168.88.2"]
  AP -. "WiFi rumah" .-> CL["HP dan perangkat rumah"]
  SW3 --- PVE["Proxmox<br/>192.168.88.10"]
  E5 --- LAP["Laptop admin<br/>192.168.88.252"]
```

Catatan kabel:
- Susunan kabel yang dilaporkan pengguna per 1 Nov 2026: ether1 WAN dari WR840N, ether2 kosong (rencana WAN2), ether3 STB AdGuard, ether4 switch, ether5 laptop admin. Switch port 1 menerima uplink dari ether4; port 2 ke AP; port 3 ke Proxmox; port 4-5 kosong.
- Rencana masa depan: ether2 akan dipakai untuk modem WAN cadangan saat IndiHome mati. Sebelum itu, rancang dan uji failover WAN; Proxmox saat ini sudah berada di switch port 3.
- Proxmox saat ini tersambung ke switch port 3; switch port 1 ke MikroTik ether4. MikroTik ether2 kosong; STB ke ether3.

## 2. Rangkaian logis (alamat)

| Lapisan | Alamat | Fungsi |
|---|---|---|
| Jaringan atas | `192.168.0.0/24` | LAN TL-WR840N; MikroTik ether1 = .100 |
| LAN rumah | `192.168.88.0/24` | MikroTik .1 (gateway, DHCP, NAT) |
| Pool DHCP | `.100 - .254` | Klien biasa |
| AdGuard STB 1 | `.3` | Static DHCP lease; sebelumnya `.253` |
| Server (di luar pool) | `.2 - .99` | Static lease / IP statis |
| Tailnet | `100.x.y.z` | Tailscale |

NAT berlapis: perangkat -> MikroTik (masquerade di ether1) -> TL-WR840N (WISP) -> IndiHome.

## 3. Alur DNS (nama menjadi alamat)

```mermaid
sequenceDiagram
  participant K as Klien (HP/laptop)
  participant M as MikroTik DHCP
  participant A as AdGuard STB 1 (.3)
  participant B as AdGuard CT101 (.11)
  participant U as Upstream (Quad9 / 1.1.1.1)
  K->>M: minta IP (DHCP)
  M-->>K: IP + DNS .3; .11 hanya setelah layanan cadangan diuji
  K->>A: kuma.home.arpa ?
  A-->>K: 192.168.88.20 (DNS rewrite *.home.arpa)
  K->>A: google.com ?
  A->>U: teruskan
  U-->>A: jawaban
  A-->>K: jawaban
  K->>A: doubleclick.net ?
  A-->>K: 0.0.0.0 (diblokir)
  Note over K,B: .11 belum aktif/terverifikasi; jangan dibagikan sebagai DNS cadangan dulu
```

Aturan: jangan menaruh DNS publik (8.8.8.8) sebagai DNS kedua di DHCP; sebagian klien lolos dari pemblokiran.

## 4. Alur akses layanan privat

```mermaid
flowchart LR
  C["Klien"] -->|"nama *.home.arpa"| DNS["AdGuard .3"]
  DNS -->|"192.168.88.20"| C
  C -->|"HTTPS 443"| CD["Caddy (VM 201)"]
  CD -->|"IP:port"| S1["VM 206 affine :3010"]
  CD --> S2["VM 207 nextcloud :8080"]
  CD --> S3["VM 208 n8n :5678"]
  CD --> S4["VM 209 web :8081 / :8082"]
  CD --> S5["VM 204 git :3000"]
  CD --> S6["VM 201 kuma, beszel, gotify"]
```

Firewall Proxmox: VM tujuan hanya menerima port itu dari `192.168.88.20`.

## 5. Alur akses jarak jauh (Tailscale)

```mermaid
flowchart LR
  HP["HP / laptop di luar rumah<br/>Tailscale aktif"] <-->|"WireGuard<br/>langsung atau relay DERP"| TS["CT103 ts-router<br/>(nanti STB 2)<br/>subnet 192.168.88.0/24"]
  TS --> LAN["Seluruh LAN rumah<br/>MikroTik, Proxmox, VM, STB"]
  HP <-->|"*.ts.net :443"| N1["lab-vault"]
  HP <--> N2["lab-music"]
  HP <--> N3["lab-sso"]
  HP <--> N4["lab-immich"]
```

- Tidak ada port yang dibuka di router.
- `tailscale funnel` **tidak pernah** dijalankan.
- Node `lab-*` menjalankan Tailscale Serve di VM sendiri (port 443), meneruskan ke `127.0.0.1:PORT`.

## 6. Alur publik opsional (Cloudflare Tunnel)

```mermaid
flowchart LR
  V["Pengunjung internet"] --> CF["Cloudflare (HTTPS publik)"]
  CF <-.->|"koneksi KELUAR dari VM"| CFD["cloudflared (VM 210)"]
  CFD --> WP["web-public (situs statis)"]
```

VM 210 tidak boleh menjangkau LAN (firewall `OUT DROP 192.168.88.0/24`, kecuali DNS).

## 7. Alur backup

```mermaid
flowchart LR
  G["VM 201-211, 213, 214"] -->|"snapshot 02:00, terenkripsi"| PBS["VM 212 pbs<br/>datastore store1 (disk fisik terpisah)"]
  PBS --> USB["Disk USB (offline, mingguan)"]
  HOST["Host: tar /etc/pve"] --> LAP["Laptop / HDD"]
  PBS -->|"prune, GC, verify"| PBS
  PBS -. "gagal" .-> GOT["Gotify -> HP"]
```

## 8. Alur peringatan dan monitoring

```mermaid
flowchart LR
  A["Proxmox, VM, STB, MikroTik"] --> UK["Uptime Kuma<br/>hidup atau mati"]
  A --> BZ["Beszel<br/>CPU, RAM, disk, suhu"]
  UK --> GT["Gotify"]
  BZ --> GT
  UK --> TG["Telegram (iPhone)"]
  GT --> P["HP"]
  TG --> P
```

Batas: bila IndiHome atau listrik rumah mati, tidak ada notifikasi yang sampai (butuh layanan luar seperti Healthchecks.io).

## 9. Alur Wake-on-LAN

STB 1 (`.3`) menjalankan `nyalakan-proxmox` (magic packet ke MAC Proxmox). Dari luar rumah:
HP -> Tailscale -> SSH ke STB -> perintah WoL. Wajib di BIOS: Wake on LAN aktif, ErP/Deep Sleep mati,
Restore on AC Power Loss = Power On.

## 10. Alur GitOps (Flux, Renovate)

```mermaid
flowchart LR
  L["Laptop: edit YAML, git push"] --> F["Forgejo (VM 204)"]
  R["Renovate (VM 204)"] -->|"pull request versi baru"| F
  F -->|"pantau tiap 5 menit"| FX["Flux di k3s (VM 203)"]
  FX --> K["Cluster k3s"]
```
