# 03 - Pohon (tree)

Tiga pohon: perangkat, guest dan ketergantungan, lalu struktur folder.

## 1. Pohon perangkat (jaringan)

```
IndiHome (WiFi)
└── TL-WR840N (WISP)  192.168.0.1
    └── MikroTik RB750GL  ether1=192.168.0.100 | LAN 192.168.88.1/24
        ├── ether2   Kosong (calon WAN modem cadangan; belum dikonfigurasi)
        ├── ether3   STB HG680 .3 (AdGuard Home utama; sebelumnya .253)
        ├── ether4   Switch LiteWave LS1005 port 1 (uplink)
        │   ├── port 2: AP TL-WR820N .2
        │   ├── port 3: Proxmox .10 (ThinkCentre M710q)
        │   │   ├── CT101 adguard2 .11 (rencana IP)
        │   │   ├── CT102 files .12 (Samba; rencana IP)
        │   │   ├── CT103 ts-router (IP belum ditetapkan)
        │   │   ├── CT104 docker-services (IP final belum ditetapkan)
        │   │   ├── VM 201 docker-core .20 (target IP)
        │   │   └── VM 202-214 (rencana; lihat data/guest.yaml)
        │   └── port 4-5: kosong
        └── ether5   Laptop admin .252
            └── STB 2 .250 (usulan, belum tiba): Tailscale subnet router
```

## 2. Pohon ketergantungan (apa butuh apa)

Baca dari atas ke bawah: yang di bawah butuh yang di atasnya. **Uji dari atas.**

```
Internet (IndiHome)
└── TL-WR840N WISP
    └── MikroTik (DHCP, NAT, firewall)
        ├── DNS: AdGuard STB 1 (+ CT101 sebagai failover)
        │   └── DNS rewrite *.home.arpa -> 192.168.88.20
        ├── Proxmox host (Bab 8-9, 25)
        │   ├── Templat VM 200 (Bab 49)
        │   │   └── semua VM layanan
        │   ├── Firewall antar-guest (Bab 51)  <- IPSet admin, MikroTik reservasi laptop
        │   └── PBS VM 212 (Bab 50)  <- disk fisik kedua
        ├── Tailscale (Bab 26)  <- CT103 / STB 2, tailnet, HTTPS Certificates aktif
        │   ├── Split DNS home.arpa
        │   └── Tailscale Serve di lab-vault / lab-music / lab-sso / lab-immich
        │       └── grants tcp:443 (Bab 44.3)
        └── VM 201 docker-core
            ├── Docker + jaringan proxy
            ├── Gotify  <- notifikasi dari Kuma, Beszel, PBS, n8n, Proxmox
            ├── Uptime Kuma, Beszel
            └── Caddy (Bab 36)  <- DNS rewrite, sertifikat akar di perangkat (Bab 37)
                ├── web, wp, n8n, affine, nextcloud, git
                └── (Cloudflare Tunnel: VM 210, tidak lewat Caddy)

Pocket ID (VM 213) -> Immich SSO (VM 214), perlu extra_hosts ke IP Tailscale VM sso
Vaultwarden (VM 205) -> menyimpan semua kunci/kata sandi layanan lain
Forgejo (VM 204) -> Flux (VM 203) dan Renovate
```

Urutan uji yang disarankan: Jaringan (Bab 3) -> Proxmox -> STB AdGuard -> DNS failover -> Docker
-> Suplemen 1 (keamanan, Tailscale) -> 3 (monitoring) -> 4 (Caddy) -> Git -> 5 -> 6 -> 7 -> 8 -> 9.

## 3. Pohon folder di server

```
/opt/stacks/                     (di setiap VM Docker; satu folder per aplikasi)
├── caddy/        compose.yaml  Caddyfile  data/ (kunci CA!)  config/
├── gotify/       compose.yaml  .env  data/
├── uptime-kuma/  compose.yaml  data/
├── beszel/       compose.yaml  beszel_data/
├── beszel-agent/ compose.yaml
├── homepage/     compose.yaml  config/ (settings, widgets, services .yaml)
├── adguard-sync/ compose.yaml
├── forgejo/      compose.yaml  forgejo/
├── vaultwarden/  compose.yaml  .env  data/  backup/
├── affine/       compose.yaml  .env  config/ storage/ db/ backup/
├── nextcloud/    compose.yaml  .env  html/ data/ db/ backup/
├── n8n/          compose.yaml  .env  data/ db/ backup/
├── web/          compose.yaml  Caddyfile  sites/
├── wordpress/    compose.yaml  .env  html/ db/ backup/
├── tunnel-web/   compose.yaml  .env  Caddyfile  public/
├── music/        compose.yaml  .env  data/    (musik di /srv/music)
├── sso/          compose.yaml  .env  data/
└── immich/       docker-compose.yml  docker-compose.override.yml  .env  postgres/   (foto di /srv/foto/library)
```

## 4. Pohon repo

```
home-server-lab/
├── README.md                 ringkasan, arsitektur, dan navigasi
├── AGENTS.md                 panduan kerja untuk asisten
├── STATUS.md                 posisi proyek dan langkah berikutnya
├── data/                     data perangkat dan guest (YAML)
├── docs/
│   ├── 00-10-*.md            konteks, arsitektur, jaringan, keputusan, status awal
│   ├── 11-rencana-kerja-ai-ssh.md
│   ├── bab/
│   │   ├── edisi2/            Bab 1-24 dan lampiran
│   │   ├── suplemen/          Bab 25-56 dan pengantar/penutup
│   │   ├── REVISI-3.md
│   │   └── arsip/             bila tersedia, materi historis
│   └── arsip/                 dokumen lama
├── catatan/                   hasil uji, belum pasti, kasus nyata
└── konfigurasi/
    ├── server/                konfigurasi layanan
    ├── gitops/                Flux, Kustomize, SOPS, Renovate
    ├── caddy/                 reverse proxy
    ├── firewall/              aturan jaringan
    ├── skrip/                 otomasi host/layanan
    └── contoh-env/            contoh variabel lingkungan
```

Pohon ini menjelaskan **pengelompokan dokumentasi**, bukan bukti bahwa semua layanan sudah berjalan. Untuk kondisi aktual, rujuk `STATUS.md`; untuk daftar guest terstruktur, rujuk `data/guest.yaml`.
