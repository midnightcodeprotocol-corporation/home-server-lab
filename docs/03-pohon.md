# 03 - Pohon (tree)

Tiga pohon: perangkat, guest dan ketergantungan, lalu struktur folder.

## 1. Pohon perangkat (jaringan)

```
IndiHome (WiFi)
└── TL-WR840N (WISP)  192.168.0.1
    └── MikroTik RB750GL  ether1=192.168.0.100 | LAN 192.168.88.1/24
        ├── ether2   laptop admin (WinBox)
        ├── ether4   STB 1 HG680  .253  AdGuard Home utama
        ├── TL-WR820N (AP)  .2  -> WiFi rumah -> HP, laptop, TV, dll.
        └── Switch LiteWave LS1005
            ├── Proxmox  .10  (ThinkCentre M710q)  (ThinkCentre M710q)
            │   ├── CT101 adguard2   .11
            │   ├── CT102 files      .12  (Samba)
            │   ├── CT103 ts-router
            │   ├── VM 201 docker-core .20
            │   ├── VM 202 haos        .21
            │   ├── VM 203 k3s         .22
            │   ├── VM 204 git         .23
            │   ├── VM 205 vault       .24
            │   ├── VM 206 affine      .25
            │   ├── VM 207 nextcloud   .26
            │   ├── VM 208 n8n         .27
            │   ├── VM 209 web         .28
            │   ├── VM 210 web-public  .29
            │   ├── VM 212 pbs         .30
            │   ├── VM 211 music       .31
            │   ├── VM 213 sso         .32
            │   ├── VM 214 immich      .33
            │   └── VM 9100 tpl-debian-docker (templat) | 9000 templat cloud-init (k3s)
            └── STB 2 .250 (usulan, belum tiba)  Tailscale subnet router
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
        │   ├── Templat VM 9100 (Bab 49)
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

## 4. Pohon repo ini

```
home-server-lab/
├── README.md
├── .gitignore
├── docs/
│   ├── 00-ide-awal.md            01-ide-akhir.md
│   ├── 02-rangkaian-koneksi.md   03-pohon.md
│   ├── 04-board.md               05-inventaris-perangkat.md
│   ├── 06-dasar-konsep.md        07-port-dan-akses.md
│   ├── 08-keputusan.md
│   └── buku/   PDF Edisi 2 + Suplemen 1-9
├── catatan/
│   ├── belum-pasti.md   hasil-uji.md   kasus-nyata-lab.md
└── konfigurasi/
    ├── caddy/  firewall/  skrip/  contoh-env/
```
