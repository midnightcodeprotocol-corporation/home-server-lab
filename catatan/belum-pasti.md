# Butir [BELUM PASTI]

Dikumpulkan dari tabel penutup tiap bagian. Centang dan catat hasilnya setelah dipastikan.

## Bagian 5 (Bab 39-43)
- [ ] Tag `wordpress:6-apache` dan `mariadb:11` ada di Docker Hub
- [ ] Nomor versi n8n stabil terkini (contoh 2.29.10 belum dikonfirmasi)
- [ ] Perkiraan RAM WordPress dan n8n (ukur dengan Beszel)
- [ ] Aplikasi WordPress, HTTP Shortcuts, Pintasan menerima CA lokal
- [ ] Tag versi cloudflared yang didukung dan cara mematoknya di Compose; tag quick tunnel sementara
- [ ] Letak menu Cloudflare Tunnels dan batasan quick tunnel
- [ ] Biaya domain dan apakah Tunnel gratis untuk kebutuhan ini
- [ ] Cloudflare Access dan webhook sebagian jalur (tidak dikaji)
- [ ] IP publik IndiHome dinamis atau berbagi (tidak memengaruhi tunnel)

## Bagian 6 (Bab 44-47)
- [ ] Android Bitwarden dengan CA lokal (dihindari lewat Tailscale Serve)
- [ ] Sintaks grants `tcp:443` dan `autogroup:self`; serve dengan `--accept-dns=false`
- [ ] Nama image AFFiNE (`affine` vs `affine-graphql`) dan tata letak compose resmi
- [ ] Alamat halaman admin AFFiNE, opsi pendaftaran, login email tanpa SMTP
- [ ] AFFiNE Android/iPhone menerima CA lokal; langkah menu aplikasi
- [ ] Nomor mayor Nextcloud terkini untuk `NEXTCLOUD_TAG`
- [ ] DAVx5 menerima CA lokal, harga Play Store; Thunderbird; kode kalender bawaan `personal`
- [ ] Tag rilis Vaultwarden yang dipilih sebelum instalasi; pin versi image dan alur pembaruan
- [ ] Backup daring Vaultwarden dan titik pemeriksaan sehat
- [ ] Kebutuhan RAM gabungan

## Bagian 7 (Bab 48-52)
- [ ] RAM awal tiap VM dan total
- [ ] Instruksi pasang Docker untuk Debian 13 tidak berubah
- [ ] Lease DHCP statis di luar pool MikroTik diterima
- [ ] Nomor rilis ISO PBS; HDD sebagai datastore lambat
- [ ] Peran `DatastoreBackup` dan sintaks `proxmox-backup-manager`
- [ ] Masa tunggu GC dan nama menu notifikasi (PVE 9.2, PBS)
- [ ] Sintaks `+dc/admin`, opsi `dhcp: 1`, port keluar tunnel 7844
- [ ] Sumber IP perangkat Tailscale yang tiba di VM (CT103 sebagai subnet router)
- [ ] Versi `lynis` di Debian

## Bagian 8 (Bab 53)
- [ ] Sintaks `qm set --scsi1 STORAGE:UKURAN,backup=0`
- [ ] Letak menu pengguna dan tombol pindai Navidrome
- [ ] Perilaku klien musik (latar belakang, offline, harga Symfonium)
- [ ] Nomor versi Navidrome untuk dipin
- [ ] RAM/CPU saat transkoding

## Bagian 9 (Bab 54-56)
- [ ] Halaman `/setup` Pocket ID dan letak menu pengguna / klien OIDC
- [ ] Perintah token akses satu kali Pocket ID
- [ ] Callback `app.immich:///oauth-callback` diterima Pocket ID; bentuk Issuer URL
- [ ] `extra_hosts` ke alamat Tailscale VM sso dari dalam container
- [ ] Jalur Tailscale antar-VM saat firewall Proxmox aktif (langsung atau DERP)
- [ ] Backup bawaan Immich: hanya database atau lebih
- [ ] Nomor versi tetap Immich dan Pocket ID
- [ ] RAM/CPU sebenarnya (Immich impor, Pocket ID, host)
- [ ] Cadangan latar belakang Android/iOS
- [ ] Sumber aplikasi Immich di Android
- [ ] Batas ZFS ARC pada instalasi
