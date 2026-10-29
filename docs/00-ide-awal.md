# 00 - Ide awal

Titik mulai proyek, dari yang paling dasar. Semua keputusan berikutnya berasal dari sini.

## Masalah yang ingin diselesaikan
- Belajar mengelola server **tanpa takut merusak mesin asli**.
- Memakai perangkat yang sudah ada lebih dulu (laptop, HDD 2 TB, STB bekas, router), **tanpa biaya tambahan**.
- Server utama (mini PC) awalnya belum ada, sehingga direncanakan lab latihan dulu. **Sekarang mesin asli sudah ada** (ThinkCentre M710q), lihat Revisi 3 di bawah.

## Ide pertama (Oktober 2026)
1. Proyek home server dimulai dari nol, dari langkah paling dasar.
2. Proyek pertama: **AdGuard Home** (pemblokir iklan) untuk seluruh jaringan rumah.
3. Tempat: **STB IndiHome HG680** yang di-flash dengan **Armbian**.
4. Jaringan: IndiHome tidak punya kabel LAN yang bisa dipakai, jadi uplink lewat WiFi
   (TL-WR840N mode WISP) lalu kabel ke **MikroTik RB750GL**.
5. Server: **Proxmox VE** (awalnya direncanakan di VMware di laptop; sekarang langsung di mesin asli).

## Prinsip dasar (Bab 1.3)
| Selalu hidup, di luar Proxmox | Boleh diutak-atik, di dalam Proxmox |
|---|---|
| MikroTik, TP-Link penerima, TP-Link AP | VM Debian 13 (Docker, Portainer, Git, dll.) |
| AdGuard Home utama di STB | LXC AdGuard kedua (failover) |
| Tailscale subnet router (STB 2 nanti) | VM Home Assistant, VM k3s, PBS, dll. |

Yang menjaga **internet dan akses jarak jauh** tidak boleh ikut mati saat Proxmox di-reboot, di-update, atau rusak karena eksperimen.

## Lima prinsip keamanan (Bab 25.1)
1. Kecilkan pintu masuk: hanya buka yang perlu.
2. Akses dari luar hanya lewat Tailscale (tidak ada port forwarding).
3. Login dengan kunci dan 2FA, bukan password saja.
4. Perbarui rutin.
5. Cadangkan dan **uji pemulihan**.

## Daftar keinginan awal (urutan dari pengguna)
1. Home Assistant
2. NAS dengan Nextcloud
3. Server hosting
4. Cetak dari mana saja (TP-Link MR3020)
5. Server backup
6. "Code studio" virtual (seperti VS Code di browser)
7. Server LLM (baru kemungkinan)
8. Internet kedua sebagai failover selain IndiHome
9. Monitor listrik rumah
10. Panel surya

Tambahan 18 Oktober: hosting web dan n8n, monitoring (Uptime Kuma, Beszel), aplikasi catatan ala Notion,
kalender pribadi, suite office, dan semua fitur bisa diakses dari luar rumah. Keputusan: akses luar
**hanya lewat Tailscale**, OnlyOffice untuk office, AFFiNE untuk catatan, Cloudflare Tunnel hanya opsi
tambahan untuk situs statis publik.

Gagasan lain yang belum diputuskan: VM sebagai gaming PC (GPU passthrough), server game (AMP + playit.gg), Ollama.

## Revisi 3 (28 Oktober 2026)
Mesin asli sudah ada (Lenovo ThinkCentre M710q). Rencana "lab dulu di VMware, lalu pindah" **sudah selesai peran**nya dan dihentikan: model instalasi A (VMware) dan C (instal ke disk dulu) dihapus dari buku. Pengalaman lab dicatat di `catatan/kasus-nyata-lab.md`.

## Revisi 3 (28 Oktober 2026)
Mesin asli sudah ada (Lenovo ThinkCentre M710q). Rencana "lab dulu di VMware, lalu pindah" **sudah selesai perannya** dan dihentikan: Model A (VMware) dan Model C (instal ke disk terlebih dahulu) dihapus dari alur panduan. Pengalaman lab lama disimpan sebagai catatan di `catatan/kasus-nyata-lab.md`.
