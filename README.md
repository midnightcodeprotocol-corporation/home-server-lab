# Home Server Lab

Panduan dan catatan proyek home server pribadi berbasis **Lenovo ThinkCentre M710q**. Repo ini menggabungkan rancangan jaringan, panduan Proxmox, konfigurasi layanan, catatan pengujian, dan keputusan proyek dalam satu tempat.

> [!IMPORTANT]
> Repo ini **private dan tidak boleh berisi rahasia**. Jangan commit kata sandi, token, private key SSH/age, `ENCRYPTION_KEY`, kunci backup, dump database, atau arsip konfigurasi host. Nilai asli disimpan di Vaultwarden; repo hanya menyimpan contoh seperti `*.example`.

## Status proyek

Pembaruan terakhir **2 November 2026**: Proxmox `.10` terhubung internet; AdGuard kedua di `.11` selesai dikonfigurasi dan tes DNS A/AAAA dari Proxmox dan laptop lulus; upstream Quad9 independen dari STB untuk domain internet; pengguna melaporkan DHCP kini membagikan `.3` dan `.11`; lease klien belum diverifikasi; Jellyfin sehat dan Portainer 2.45.3 setup selesai menurut pengguna di CT104 `.101`; VM202 Home Assistant OS berjalan di `.21` dengan onboarding selesai menurut pengguna. HDD 2 TB sengaja dilepas. Lihat [STATUS.md](STATUS.md) untuk rincian dan batas verifikasi.

- **Jaringan rumah sudah berjalan:** IndiHome melalui WiFi ke TL-WR840N mode WISP, lalu ke MikroTik RB750GL. Access point dan STB AdGuard juga sudah berfungsi.
- **Server utama:** ThinkCentre M710q, Intel Core i5-6500T (4 core/4 thread), Proxmox sudah berjalan. RAM terpasang 16+8 GB; Linux melaporkan 23 GiB, tetapi BIOS/MemTest86 belum diperiksa. NVMe Samsung terdeteksi sebagai `nvme0n1`, 476,9 GB. Kernel aktif `7.0.14-26-pve`; tidak ada unit systemd gagal.
- **Penyimpanan:** HDD pertama saat ini tidak terpasang (konfirmasi pengguna 2 Nov); ketika terlihat pada 1 Nov, disk berisi partisi NTFS 2 TB dan S.M.A.R.T. PASSED. Periksa ulang isi sebelum menetapkan storage; jangan format. HDD kedua menunggu enclosure.
- **Layanan terpasang:** CT101 `adguard2` memakai statis `.11`, `onboot=1`, dan service AdGuard Home aktif; port 53 listen dan tes DNS A/AAAA dari Proxmox lulus. Tes laptop lulus; pengguna melaporkan DNS DHCP diperbarui; verifikasi lease klien masih pending. CT104 `docker-services` aktif di `.101`; Portainer 2.45.3 UI/API merespons dan setup selesai menurut pengguna; Jellyfin healthy pada TCP 8096, `/srv/media` masih kosong/read-only. Reservasi DHCP CT104 belum diaudit. VM201 `docker-core` berhenti/onboot=0. VM202 HAOS 18.4 aktif di `.21`, UEFI, 2 vCPU/2 GiB, disk 32 GiB; checksum image resmi cocok dan onboarding selesai menurut pengguna.
- Buku panduan lengkap Bab 1–56, lampiran, fase, dan roadmap tersedia dalam edisi terpadu. Revisi 7 mencatat audit identitas template dan hasil clone; guest layanan, backup, dan pemulihan **belum diuji**. Sumber buku ada di [panduan-lengkap-home-server-lab.md](docs/panduan-lengkap-home-server-lab.md); build PDF ada di [tools/book_builder/README.md](tools/book_builder/README.md) dan [tools/build_handbook.py](tools/build_handbook.py). Riwayat pengujian ada di [catatan/hasil-uji.md](catatan/hasil-uji.md).
- Tailscale subnet router belum dipasang; rancangan tetap CT103 sementara dan STB2 setelah tersedia. Login/persetujuan tailnet perlu dilakukan pengguna.

Repo pernah memuat rencana lab VMware. Rencana tersebut sudah dihentikan dan dihapus dari alur instalasi pada Revisi 3. Lihat [catatan Revisi 3](docs/bab/REVISI-3.md).

## Gambaran jaringan

Diagram berikut menggabungkan jaringan rumah yang sudah berjalan dengan server dan layanan yang **masih menjadi target**, bukan klaim bahwa semuanya sudah dipasang.

```mermaid
flowchart TB
  Internet["Internet: IndiHome<br/>uplink WiFi"] -. WiFi .-> WISP["TP-Link TL-WR840N<br/>mode WISP"]
  WISP -->|"Ethernet"| MT["MikroTik RB750GL<br/>WAN 192.168.0.100<br/>LAN 192.168.88.1/24"]
  MT -->|"ether5"| Admin["Laptop admin .252"]
  AP -. WiFi rumah .-> Clients["Laptop Windows, HP,<br/>perangkat rumah"]
  MT -->|"ether4 -> port 1"| Switch["Switch LiteWave LS1005<br/>port 1 uplink, port 2 AP, port 3 Proxmox, port 4-5 kosong"]
  MT -->|"ether3"| STB1["STB HG680 .3<br/>Armbian + AdGuard Home<br/>DNS utama"]
  MT -.->|"ether2 kosong; rencana WAN2"| Modem2["Modem cadangan (rencana)"]
  Switch -->|"port 2"| AP["TP-Link TL-WR820N<br/>Access Point .2"]
  Switch -->|"port 3"| PVE

  subgraph PVE["Target: Proxmox di ThinkCentre M710q — 192.168.88.10"]
    direction TB
    Core["VM 201 .20 — docker-core<br/>Caddy, Portainer, monitoring,<br/>notifikasi, dashboard"]
    Apps["VM layanan terpisah<br/>Forgejo, Vaultwarden, AFFiNE,<br/>Nextcloud, n8n, web, musik"]
    Special["VM khusus<br/>Home Assistant, k3s/Flux,<br/>PBS, Pocket ID, Immich"]
    LXC["LXC<br/>AdGuard kedua .11,<br/>Samba .12, Tailscale router"]
    Core -. proxy HTTPS .-> Apps
    Core -. proxy HTTPS .-> Special
  end

  Clients -->|"DNS *.home.arpa"| STB1
  Clients -->|"HTTPS 443"| Core
  Remote["Laptop / HP di luar rumah<br/>Tailscale aktif"] <-->|"tailnet / HTTPS Serve"| TS["Tailscale<br/>CT103 sementara;<br/>STB 2 direncanakan"]
  TS --> PVE
  Remote <-->|"HTTPS *.ts.net"| Private["Vaultwarden, Navidrome,<br/>Pocket ID, Immich"]
  Internet -. "opsional: situs statis saja" .-> CF["Cloudflare Tunnel keluar<br/>VM 210 web-public"]
```

### Cara membaca diagram

- **Jaringan rumah:** MikroTik menjadi gateway, DHCP, firewall, dan NAT. Pool DHCP direncanakan pada `192.168.88.100–254`; alamat server menggunakan rentang statis di luar pool.
- **DNS:** AdGuard Home utama berada di STB HG680 `192.168.88.3` (dipindah dari `.253`, kueri langsung berhasil). MikroTik membagikan `.3`; laptop menerima `.3` dan `.11`, tetapi `.11` belum diverifikasi aktif dan jangan digunakan sebagai cadangan sebelum diuji. Nama `*.home.arpa` diarahkan ke Caddy di VM 201.
- **Akses privat lokal:** klien membuka layanan melalui Caddy pada HTTPS 443; firewall Proxmox membatasi port aplikasi agar hanya dapat dijangkau dari gerbang yang diperlukan.
- **Akses dari luar rumah:** memakai Tailscale. Rancangan tidak membuka port admin Proxmox atau router ke internet dan tidak memakai Tailscale Funnel.
- **Situs publik opsional:** hanya situs statis di VM 210 melalui koneksi keluar Cloudflare Tunnel; VM ini dirancang terisolasi dari LAN.
- Detail kabel, DNS, akses jauh, GitOps, monitoring, dan backup ada di [diagram alur koneksi](docs/02-rangkaian-koneksi.md).

## Arsitektur layanan target

Host Proxmox dibuat sesederhana mungkin: **tanpa Docker dan tanpa aplikasi**. Sesuai keputusan proyek, Docker ditempatkan di CT104 Debian 13 unprivileged dengan nesting; ini menghemat VM namun isolasinya lebih rendah daripada Docker di VM. Aplikasi yang memang memerlukan OS terpisah memakai VM.

| Guest | Alamat | Peran target |
|---|---:|---|
| Host Proxmox | `192.168.88.10` | Hypervisor M710q |
| CT101 / CT102 | `.11 / .12` | AdGuard kedua (CT101 statis aktif; DNS A/AAAA lulus dari Proxmox) / Samba (rencana) |
| CT103 | Belum ditetapkan | Tailscale subnet router (rencana; autentikasi pengguna diperlukan) |
| CT104 | Lease `.101` sementara | Docker/Portainer + Jellyfin; Jellyfin healthy, media dan wizard admin belum selesai |
| VM 201 | Target `.20` | docker-core (stopped/onboot=0); Caddy/layanan pada tabel adalah rencana lama |
| VM 202 / 203 | `.21` aktif / `.22` target | Home Assistant OS (running, onboarding selesai menurut pengguna) / k3s + Flux (rencana) |
| VM 204 / 205 | `.23 / .24` | Forgejo + Renovate / Vaultwarden |
| VM 206 / 207 | `.25 / .26` | AFFiNE / Nextcloud |
| VM 208 / 209 | `.27 / .28` | n8n / situs privat + WordPress |
| VM 210 | `.29` | Situs statis publik opsional; akses melalui tunnel keluar |
| VM 212 / 211 | `.30 / .31` | Proxmox Backup Server / Navidrome |
| VM 213 / 214 | `.32 / .33` | Pocket ID / Immich |
| VM 200 | — | Template Debian 13 bersih; 1 vCPU/2 GiB/32 GiB, QEMU Agent aktif pada konfigurasi |
| CT 100 | — | Template Debian 13 bersih; 1 vCPU/512 MiB RAM dan swap/8 GiB, unprivileged, nesting, DHCP |

Rancangan layanan tetap bertahap. Layanan yang sudah berjalan dan status IP aktual dibedakan dari target di [data/guest.yaml](data/guest.yaml); uji DNS AdGuard dari laptop, DNS cadangan DHCP MikroTik, reservasi MikroTik, serta media Jellyfin masih perlu diselesaikan. Tabel port dan aturan akses ada di [docs/07-port-dan-akses.md](docs/07-port-dan-akses.md).

Linux melaporkan 23 GiB dari konfigurasi RAM 16+8 GB. BIOS/MemTest86 belum diperiksa; gunakan profil konservatif dan pantau penggunaan sebelum menyalakan banyak VM. Mode hemat tetap perlu memantau batas CPU 4 thread.

## Penyimpanan dan backup

Rancangan penyimpanan memakai NVMe 500 GB untuk sistem/VM. HDD pertama sedang dilepas; sebelumnya terdeteksi sebagai Seagate ST2000VX008-2E3164, `/dev/sda`, 2 TB NTFS, S.M.A.R.T. PASSED. Isi/fungsi belum ditetapkan; periksa read-only setelah dipasang kembali dan jangan format sebelum data dikonfirmasi. PBS direncanakan mencadangkan VM setiap hari, dengan enkripsi sisi klien, salinan USB offline, dan arsip konfigurasi host.

**Keadaan saat ini:** HDD unit 1 sedang tidak terpasang; saat terpasang terakhir kali terlihat berpartisi NTFS dan belum menjadi Proxmox storage. HDD kedua menunggu enclosure; PBS belum dipasang; belum ada backup atau uji pemulihan. Karena itu backup belum boleh dianggap tersedia. Prosedur backup baru dianggap terbukti setelah pemulihan berhasil diuji. Lihat [Bab 50](docs/bab/suplemen/50-proxmox-backup-server.md) dan catatan uji.

## Mulai menjelajahi repo

Buku utama terbaru: [Panduan Lengkap Home Server Lab - Edisi Lengkap 2026](docs/panduan-lengkap-home-server-lab.md). PDF edisi terpadu 2026.11 berisi 258 halaman. Sumber Markdown ada di repo; PDF hasil build disimpan lokal pada `06-Book`. Build dapat diulang lewat [tools/book_builder/README.md](tools/book_builder/README.md).

1. Baca [tujuan awal](docs/00-ide-awal.md) dan [arsitektur target](docs/01-ide-akhir.md).
2. Lihat [status dan langkah berikutnya](STATUS.md), lalu [urutan hari pertama di M710q](docs/09-mulai-di-m710q.md).
3. Gunakan [board proyek](docs/04-board.md) untuk melihat fase dan backlog.
4. Baca [Edisi 2: Bab 1–24](docs/bab/edisi2/README.md) dan [Suplemen: Bab 25–56](docs/bab/suplemen/README.md).
5. Cek [butir yang belum pasti](catatan/belum-pasti.md) dan [hasil uji](catatan/hasil-uji.md).

### Peta dokumentasi

| Lokasi | Isi |
|---|---|
| `docs/00-ide-awal.md` – `docs/10-konteks-proyek.md` | Tujuan, arsitektur, diagram jaringan, perangkat, konsep, port, keputusan, status awal, dan preferensi kerja |
| `docs/11-rencana-kerja-ai-ssh.md` | Koordinasi Codex dan Claude saat mengakses Proxmox lewat SSH |
| [docs/12-roadmap-manfaat-keamanan.md](docs/12-roadmap-manfaat-keamanan.md) | Prioritas peningkatan kegunaan, keamanan, backup, pemantauan, dan segmentasi jaringan |
| [docs/panduan-lengkap-home-server-lab.md](docs/panduan-lengkap-home-server-lab.md) | Sumber buku pemula terpadu, langkah kerja, diagram, checklist, perintah, serta syarat lulus tiap fase |
| `docs/bab/edisi2/` | Instalasi Proxmox, jaringan, VM/LXC, Docker, Git, Home Assistant, dan dasar layanan |
| `docs/bab/suplemen/` | Keamanan, Tailscale, M710q, monitoring, Caddy, web, aplikasi, penempatan, PBS, firewall, audit, foto, dan profil RAM |
| `konfigurasi/` | Contoh konfigurasi server, GitOps, Caddy, firewall, skrip, dan contoh environment |
| `data/` | Data terstruktur perangkat dan guest |
| `catatan/` | Hasil uji, hal belum pasti, dan pelajaran dari lab terdahulu |
| `docs/arsip/` | Materi lama sebelum Revisi 3 untuk riwayat |

> [!WARNING]
> Teks bab hasil ekstraksi dan arsip dapat kehilangan indentasi YAML. Untuk Compose dan YAML, gunakan berkas di `konfigurasi/` sebagai sumber format yang benar. Konfigurasi tersebut belum dijalankan di server.

## Aturan kerja dan keamanan

- Jawab dan tulis panduan dalam **Bahasa Indonesia**; pengguna belajar dari dasar dan menggunakan Windows serta Android. Panduan klien juga mencakup iPhone bila relevan.
- Berikan satu langkah per giliran untuk sesi pengujian; tunggu hasil dan catat pesan error persis sebelum lanjut.
- Gunakan IP, VMID, dan RAM dari `data/guest.yaml`; jangan menebak bila data berbeda atau belum diperiksa.
- Perintah panduan memakai alur tanpa `sudo` (akun biasa lalu `su -`, atau root di host Proxmox).
- Tandai asumsi yang belum diverifikasi dengan **[BELUM PASTI]**. Periksa dokumentasi resmi saat menulis instruksi teknis baru.
- Sebelum perubahan berisiko—misalnya disk, firewall, jaringan, SSH, atau penghapusan VM—jelaskan dampak dan jalur pemulihan.
- Untuk akses melalui SSH oleh lebih dari satu asisten, hanya satu operator yang boleh mengubah server pada satu waktu. Lakukan audit baca-saja dahulu dan tulis catatan serah-terima. Lihat [rencana kerja AI melalui SSH](docs/11-rencana-kerja-ai-ssh.md).
- Jangan menaruh rahasia di chat maupun repo; gunakan Vaultwarden untuk nilai asli.

## Riwayat revisi

- **Revisi 3 (28 Oktober 2026):** menghapus rencana lab VMware dan instal-ke-disk-dulu setelah M710q tersedia. Mesin asli menjadi target instal Proxmox langsung dari USB.
- **Revisi 4 (30 Oktober 2026):** memperbaiki kebijakan akses Tailscale, direktori penyimpanan PostgreSQL 18 pada n8n, dan nilai awal pendaftaran Vaultwarden. Lihat [catatan Revisi 4](docs/bab/REVISI-4.md).
- **Revisi 6 (1 November 2026):** mencatat template Debian 13 VM/CT dan persiapan jaringan MikroTik.
- **Revisi 7 (1 November 2026):** mencatat identitas yang ikut tersalin, perbaikan template CT 100/VM 200, hasil clone, dan pembersihan guest uji.
- **Revisi 8 (1 November 2026):** membuat CT 101 `adguard2` dan VM 201 `docker-core` dari template. Keduanya berjalan dengan DHCP router sementara; IP akhir dan pemasangan aplikasi menunggu MikroTik. Lihat [catatan Revisi 8](docs/bab/REVISI-8.md).
- **Revisi 9 (1 November 2026):** memasang AdGuard Home pada CT101 (service ditahan sampai jaringan final) dan Docker CE/Compose pada VM201. Lihat [catatan Revisi 9](docs/bab/REVISI-9.md).
- **Revisi 10 (1 November 2026):** menangani pesan `systemd-ssh-generator` AF_VSOCK pada VM201; SSH TCP dan Docker tetap aktif. Lihat [catatan Revisi 10](docs/bab/REVISI-10.md).
