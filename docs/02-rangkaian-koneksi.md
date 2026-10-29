# 02 - Rangkaian koneksi

Dari kabel fisik sampai alur data. Diagram memakai Mermaid (tampil otomatis di GitHub).

## 1. Rangkaian fisik (kabel dan radio)

```mermaid
flowchart LR
  ISP["IndiHome<br/>(WiFi saja, tidak ada LAN)"] -. "WiFi" .-> WR840["TL-WR840N<br/>WISP, LAN 192.168.0.1"]
  WR840 -- "kabel LAN" --> E1["MikroTik ether1<br/>192.168.0.100 (DHCP client)"]
  subgraph MT["MikroTik RB750GL, LAN 192.168.88.1/24"]
    E1
    E2["ether2: kabel admin / laptop"]
    E4["ether4: STB 1"]
    EX["port lain: switch, AP, server"]
  end
  E4 --- STB1["STB HG680<br/>192.168.88.253"]
  EX --- AP["TL-WR820N (AP)<br/>192.168.88.2<br/>colok ke port LAN, bukan WAN"]
  EX --- SW["Switch LS1005"]
  SW --- PVE["Proxmox 192.168.88.10"]
  AP -. "WiFi rumah" .-> CL["HP, laptop, perangkat lain"]
```

Catatan kabel:
- AP dicolok ke port **LAN** AP (bukan WAN/Internet), DHCP AP dimatikan.
- Saat setup MikroTik, laptop di **ether2** (bukan ether1 yang ke WAN).
- Laptop admin: kabel via adaptor USB-LAN ke jaringan MikroTik (`192.168.88.252`). Server Proxmox: kabel LAN dari port Ethernet M710q ke MikroTik/switch.

## 2. Rangkaian logis (alamat)

| Lapisan | Alamat | Fungsi |
|---|---|---|
| Jaringan atas | `192.168.0.0/24` | LAN TL-WR840N; MikroTik ether1 = .100 |
| LAN rumah | `192.168.88.0/24` | MikroTik .1 (gateway, DHCP, NAT) |
| Pool DHCP | `.100 - .254` | Klien biasa |
| Server (di luar pool) | `.2 - .99` | Static lease / IP statis |
| Tailnet | `100.x.y.z` | Tailscale |

NAT berlapis: perangkat -> MikroTik (masquerade di ether1) -> TL-WR840N (WISP) -> IndiHome.

## 3. Alur DNS (nama menjadi alamat)

```mermaid
sequenceDiagram
  participant K as Klien (HP/laptop)
  participant M as MikroTik DHCP
  participant A as AdGuard STB 1 (.253)
  participant B as AdGuard CT101 (.11)
  participant U as Upstream (Quad9 / 1.1.1.1)
  K->>M: minta IP (DHCP)
  M-->>K: IP + DNS .253 dan .11
  K->>A: kuma.home.arpa ?
  A-->>K: 192.168.88.20 (DNS rewrite *.home.arpa)
  K->>A: google.com ?
  A->>U: teruskan
  U-->>A: jawaban
  A-->>K: jawaban
  K->>A: doubleclick.net ?
  A-->>K: 0.0.0.0 (diblokir)
  Note over K,B: Bila .253 mati, klien memakai .11
```

Aturan: jangan menaruh DNS publik (8.8.8.8) sebagai DNS kedua di DHCP; sebagian klien lolos dari pemblokiran.

## 4. Alur akses layanan privat

```mermaid
flowchart LR
  C["Klien"] -->|"nama *.home.arpa"| DNS["AdGuard .253"]
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

STB 1 (`.253`) menjalankan `nyalakan-proxmox` (magic packet ke MAC Proxmox). Dari luar rumah:
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
