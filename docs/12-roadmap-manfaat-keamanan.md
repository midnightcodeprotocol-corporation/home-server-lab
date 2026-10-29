# Roadmap manfaat dan keamanan Home Server Lab

**Status:** usulan bertahap, belum diterapkan di server.  
**Kondisi saat ini:** jaringan rumah berjalan; Proxmox belum dipasang; ThinkCentre M710q memiliki RAM 16 GB dan NVMe 500 GB; dua HDD 3,5 inci belum dipasang. Karena enclosure yang tersedia single-bay, rencana awal memakai satu HDD dahulu.

## Prinsip pelaksanaan

1. Amankan akses dan buktikan pemulihan sebelum menambah banyak layanan.
2. Terapkan satu perubahan, uji dari sisi klien, catat hasilnya, lalu lanjut.
3. Jangan membuka port administrasi ke internet. Pertahankan akses jarak jauh melalui Tailscale dengan kebijakan admin terbatas.
4. Jangan menganggap RAID, snapshot, atau dua partisi pada mesin yang sama sebagai backup independen.
5. Pilih layanan karena ada kebutuhan nyata; jangan menyalakan semua VM sekaligus pada CPU 4 thread dan RAM 16 GB.

## Urutan prioritas

| Prioritas | Pekerjaan | Manfaat | Syarat lulus |
|---|---|---|---|
| **P0 — sekarang** | Aktifkan MFA/passkey pada akun GitHub dan Tailscale; simpan kode pemulihan secara offline. Tinjau pengguna yang diundang ke tailnet dan aturan port-forward/UPnP pada router. | Mengurangi risiko akun diambil alih dan akses internet tidak sengaja terbuka. | MFA aktif, pemulihan akun tersedia, tidak ada akses publik yang tidak disengaja. |
| **P0 — sekarang** | Cadangkan konfigurasi MikroTik secara terenkripsi di tempat aman, simpan versi RouterOS dan prosedur restore. Jangan commit backup router ke GitHub. | Mempercepat pemulihan jika konfigurasi rusak atau router diganti. | File backup berada di luar router, dienkripsi, dan lokasinya tercatat tanpa menyimpan kata sandi di repo. |
| **P1 — sebelum layanan** | Pasang RAM 16 GB cadangan hanya setelah cocok, jalankan MemTest86, cek BIOS dan kondisi NVMe. Instal Proxmox langsung di M710q setelah memastikan target disk dengan benar. | Fondasi yang stabil dan kapasitas lebih baik untuk VM. | MemTest lulus, backup data penting PC aman, Proxmox bisa diakses hanya dari jaringan admin. |
| **P1 — setelah Proxmox** | Buat akun admin bernama sendiri dengan MFA; batasi SSH dan UI Proxmox melalui firewall untuk perangkat admin. Aktifkan notifikasi tugas backup dan kegagalan storage. | Mengurangi penggunaan root sehari-hari dan mempercepat deteksi masalah. | Akses admin diuji dari laptop; port administrasi tidak dapat dijangkau dari internet atau guest biasa. |
| **P2 — storage dan backup** | Mulai dengan satu HDD melalui enclosure yang tersedia. Catat model/serial secara lokal, periksa kesehatan SMART jika enclosure mendukungnya, lalu putuskan apakah disk untuk data atau datastore PBS. Jangan format sebelum disk dan targetnya teridentifikasi. | Memakai kapasitas yang sudah dimiliki tanpa membeli enclosure kedua dulu. | Model/health dicatat, disk terpasang stabil, peruntukan dan sistem berkas dipilih, data yang ada dipastikan aman. |
| **P2 — storage dan backup** | Siapkan backup VM, enkripsi sisi klien, jadwal verifikasi, dan uji restore VM/file. Simpan satu salinan tambahan di media terpisah; gunakan HDD kedua sebagai media terpisah/offline setelah enclosure tersedia. | Melindungi dari salah hapus, kerusakan disk, dan kegagalan host. | Restore sampel berhasil; salinan tambahan tidak selalu terhubung dan kunci enkripsi punya salinan pemulihan aman. |
| **P3 — DNS dan akses** | Setelah Proxmox stabil, siapkan AdGuard kedua di CT101 dan sinkronkan konfigurasi. Uji resolusi ketika STB utama mati dan pastikan kedua resolver memakai kebijakan filter yang sama. | Mengurangi satu titik kegagalan DNS. | Klien tetap bisa membuka internet dan nama lokal saat salah satu resolver dimatikan. |
| **P3 — akses jarak jauh** | Terapkan kebijakan Tailscale yang hanya memberi akses LAN kepada grup admin. Uji dari jaringan seluler; periksa juga jalur IPv6 dan pastikan tidak ada port-forward yang melewati kebijakan ini. | Akses luar rumah tetap privat dan terbatas. | Hanya perangkat admin yang bisa mencapai LAN; layanan privat hanya bisa diakses oleh identitas yang diizinkan. |
| **P4 — layanan yang terasa manfaatnya** | Tambahkan layanan satu per satu sesuai kebutuhan: Samba untuk berbagi file lokal; Home Assistant jika perangkat rumah pintar sudah dipilih; Nextcloud untuk sinkronisasi dokumen; Immich untuk foto setelah backup foto siap. | Layanan punya tujuan nyata dan mudah dipelihara. | Setiap layanan punya pemilik/data, jalur akses, backup, dan prosedur restore yang terdokumentasi. |
| **P5 — pemantauan dan daya** | Gunakan Uptime Kuma untuk pemeriksaan layanan/DNS/internet, Beszel untuk host/VM, dan Gotify untuk notifikasi penting. Setelah konsumsi daya diketahui, pertimbangkan UPS yang mendukung shutdown teratur. | Masalah diketahui lebih awal dan server tidak mati mendadak saat listrik padam. | Alarm kegagalan benar-benar diterima; shutdown saat UPS lemah diuji saat aman. |
| **P6 — segmentasi jaringan** | Rencanakan VLAN terpisah untuk admin/server, IoT, dan tamu; batasi komunikasi antarsegmen. Tunda penerapan sampai kemampuan MikroTik, access point, dan switch diverifikasi. LS1005 yang tercatat adalah switch unmanaged; AP TL-WR820N juga perlu diverifikasi dukungan VLAN/SSID sebelum dijadikan bagian desain. | Membatasi dampak jika perangkat IoT atau tamu terkompromi. | Diagram port/VLAN, aturan firewall, dan jalur pemulihan sudah diuji sebelum perangkat dipindah. |

## Pilihan layanan dengan kapasitas sekarang

Pada 16 GB RAM, jalankan hanya layanan inti dan satu kebutuhan utama. Setelah RAM 32 GB, tambah layanan dengan memantau CPU, RAM, disk, dan suhu. Kubernetes/k3s, Immich machine learning, dan beberapa VM sekaligus sebaiknya menunggu sampai ada kebutuhan yang jelas serta hasil pemantauan menunjukkan kapasitas cukup.

Urutan awal yang masuk akal:

1. Proxmox, firewall, DNS, backup/restore.
2. Monitoring dan notifikasi dasar.
3. Samba atau Home Assistant — pilih yang paling dibutuhkan lebih dahulu.
4. Caddy dan layanan web privat setelah sertifikat serta akses klien diuji.
5. Nextcloud, Immich, Navidrome, AFFiNE, atau layanan lain satu per satu.
6. Kubernetes dan publikasi situs hanya jika manfaatnya jelas dan isolasinya sudah diuji.

## Pemeriksaan keamanan berkala

- **Setiap bulan:** periksa kegagalan backup, jalankan verifikasi backup, pulihkan satu file/VM contoh, lihat status SMART/suhu, dan tinjau pembaruan keamanan.
- **Setiap perubahan firewall/Tailscale:** simpan konfigurasi sebelumnya, uji akses yang harus diizinkan dan ditolak, lalu catat hasilnya.
- **Setiap tiga bulan:** tinjau pengguna/tokens/API keys, aturan port-forward, akun admin, ruang storage, dan langkah pemulihan.
- **Setelah perubahan besar:** perbarui diagram jaringan, inventaris, `STATUS.md`, dan `catatan/hasil-uji.md`.

## Rujukan resmi

- [Tailscale: syntax kebijakan akses](https://tailscale.com/docs/reference/syntax/policy-file)
- [Proxmox Backup Server: enkripsi dan sinkronisasi datastore](https://pbs.proxmox.com/docs/faq.html)
- [Proxmox Backup Server: penyimpanan datastore](https://pbs.proxmox.com/docs/storage.html)
- [MikroTik RouterOS: backup dan restore](https://help.mikrotik.com/docs/spaces/ROS/pages/40992852/Backup)
- [MikroTik RouterOS: ekspor konfigurasi](https://help.mikrotik.com/docs/spaces/ROS/pages/328155/Configuration%2BManagement)
