# 08 - Catatan keputusan

| # | Keputusan | Alasan | Alternatif yang ditolak |
|---|---|---|---|
| 1 | Lab dulu (Model A), baru mesin asli | Nol biaya, bisa dihapus | Menunggu mesin datang |
| 2 | Yang kritis di luar Proxmox (MikroTik, AdGuard utama, Tailscale) | Internet dan akses jauh tidak boleh ikut mati | Semua di satu mesin |
| 3 | AdGuard Home, bukan Pi-hole | Ringan, DoH/DoT bawaan, aturan per klien | Pi-hole (tetap valid) |
| 4 | Dua DNS di DHCP (Opsi 1), bukan dnsdist | Tanpa titik gagal tunggal baru | Balancer sebagai satu-satunya DNS |
| 5 | Debian 13 untuk semua VM, perintah tanpa sudo | Konsisten; sudo tidak terpasang bila root diberi password | Ubuntu, sudo |
| 6 | Docker di VM, bukan LXC | Lebih stabil; saran dokumentasi Proxmox | Docker di LXC, image OCI (tech preview) |
| 7 | Akses luar hanya lewat Tailscale | Privasi; tanpa port forwarding | Port forwarding, VPN lain |
| 8 | Tailscale subnet router di LXC CT103 (nanti STB 2); STB 1 khusus AdGuard | Stabilitas DNS rumah | Tailscale di STB 1 atau di VM Docker |
| 9 | Caddy dengan CA lokal (Jalur 1) untuk layanan privat | Gratis, tanpa domain | Domain berbayar (Jalur 2, opsional) |
| 10 | Tailscale Serve untuk layanan yang aplikasi HP-nya menolak CA lokal | Sertifikat tepercaya | Pasang CA di tiap aplikasi |
| 11 | Satu VM per layanan, kecuali kelompok ringan | Batasi dampak kebobolan, backup per layanan | Semua di satu VM Docker |
| 12 | Mode hemat: n8n, web, AFFiNE, musik di VM 206 `apps` | Hemat RAM | Terpisah penuh |
| 13 | PBS di VM terpisah, datastore di disk fisik berbeda, enkripsi aktif | Backup terpisah dari yang dicadangkan | PBS di host |
| 14 | Disk foto Immich **ikut** backup | Foto tidak bisa dibuat ulang | `backup=0` dan hanya backup bawaan Immich |
| 15 | Disk musik `backup=0` | Bisa dibuat ulang dari sumber asli | Ikut backup |
| 16 | Hanya situs statis yang dipublikasikan (Cloudflare Tunnel, VM 210) | Permukaan serangan kecil | WordPress, n8n publik |
| 17 | OnlyOffice untuk office, AFFiNE untuk catatan, Pocket ID untuk SSO | Pilihan pengguna dan ringan | Authentik, Authelia |
| 18 | Profil RAM untuk mesin 16 GB | Semua VM tidak muat bersamaan | Memaksa semua menyala |
| 19 | Memigrasi satu layanan per langkah, uji, baru lanjut | Hindari kesalahan berantai | Pindah massal |
| 20 | Mesin asli: Lenovo ThinkCentre M710q; Proxmox dipasang langsung dari USB | Mesin sudah ada | Lab nested VMware, instal ke disk dulu |
| 21 | Hapus Model A (VMware) dan Model C dari buku (Revisi 3) | Tidak diperlukan lagi; mengurangi kebingungan | Menyimpannya sebagai opsi |
| 22 | RAM saat ini dilaporkan 16+8 GB (24 GB); verifikasi BIOS/MemTest86. 32 GB dapat dipertimbangkan nanti setelah kebutuhan dan kompatibilitas dipastikan | Modul 8 GB pertama diganti dengan 16 GB; konfigurasi 24 GB sekarang tersedia secara fisik | Menganggap jumlah terpasang sudah dikenali atau langsung menyalakan semua VM |
| 23 | NVMe 500 GB untuk sistem dan VM; HDD 2 TB untuk datastore PBS | Backup harus di perangkat fisik berbeda dari data | Semua di NVMe |
| 24 | Disk data besar (foto, musik) dikecilkan awal agar muat di NVMe | NVMe hanya 500 GB | Ukuran contoh 200/300 GiB |
| 25 | Gunakan baseline profil 16 GB sampai konfigurasi aktual diverifikasi. RAM yang dilaporkan sekarang 24 GB; Bab 56.8 menambah batas konservatif sementara. Opsi 32 GB tetap bersyarat pengukuran | Menjaga ruang bagi host dan mencegah OOM | Menganggap alokasi VM teoritis sama dengan RAM aman untuk VM |
| 26 | Repo GitHub private sebagai basis pengetahuan; rahasia tidak pernah masuk | Pemulihan konteks lintas AI | Hanya PDF |

