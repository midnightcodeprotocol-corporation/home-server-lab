# Revisi 5: Proxmox, KVM/VT-x tanpa layar, dan template guest

**Tanggal:** 31 Oktober 2026
**Cakupan:** pembaruan buku berdasarkan hasil uji Proxmox pada ThinkCentre M710q dan keputusan membuat template VM serta CT segera setelah update host.

## Ringkasan kasus nyata: VT-x/KVM

Setelah Proxmox diperbarui, VM gagal dinyalakan dengan:

```text
TASK ERROR: KVM virtualisation configured, but not available. Either disable in VM configuration or enable in BIOS.
```

Pemeriksaan awal tidak menunjukkan `Virtualization` pada `lscpu`, dan `/dev/kvm` belum ada. Pengguna tidak memiliki monitor untuk masuk BIOS. Karena host menyediakan driver Lenovo `thinklmi`, Intel Virtualization Technology diaktifkan dari Linux, lalu host direboot. Pemeriksaan ulang menunjukkan `Virtualization: VT-x` dan `/dev/kvm` tersedia. Perubahan yang dicatat hanya VT-x; VT-d tetap `Disabled` karena passthrough PCI belum dibutuhkan.

**Catatan keselamatan:** metode thinklmi tidak tersedia pada semua model/versi BIOS. Ikuti hanya jika atributnya benar-benar ada dan pilihan `Enabled` dicantumkan. Jangan menulis password BIOS di chat. `save_settings` belum dipastikan perlu; langkah ini tidak menyuruh mengubahnya.

## Ringkasan kasus nyata: jaringan sementara dan DNS APT

Percakapan Gemini yang diberikan pengguna membahas akses Proxmox tanpa monitor dan perubahan nama interface setelah sistem dipindahkan. Saran di sana dibandingkan dengan keluaran host yang dikirim pengguna; hanya fakta yang sudah cocok yang dicatat di sini. Pemeriksaan aktual menunjukkan `enp0s31f6` dan `eno1`, `vmbr0` beralamat `192.168.0.200/24`, serta default gateway `192.168.0.1`. Konfigurasi host memakai kedua port sebagai anggota `vmbr0`. Alamat `192.168.88.10` dan DNS `192.168.88.253` adalah alamat jaringan rumah, tetapi host saat itu belum tersambung ke subnet MikroTik `192.168.88.0/24`.

Host bisa menjangkau alamat IP internet, tetapi pencarian nama gagal karena DNS menunjuk ke `192.168.88.253` yang tidak dapat dijangkau dari jaringan sementara. Setelah DNS disesuaikan ke `192.168.0.1`, `getent hosts deb.debian.org` berhasil dan `apt-get -o Acquire::ForceIPv4=true update` selesai. Karena itu, gejala DNS tersebut tidak memerlukan instalasi ulang Proxmox.

**Pelajaran pemulihan:** sebelum mengedit jaringan, simpan keluaran `ip -br link`, `ip -br address`, `ip route`, `cat /etc/resolv.conf`, dan `/etc/network/interfaces`. Cocokkan nama port Ethernet yang nyata, IP, gateway, dan DNS dengan subnet tempat kabel server sedang terhubung. Alamat `.88.x` dipakai setelah host tersambung ke MikroTik; di jaringan sementara gunakan alamat layanan jaringan sementara. Jangan menyalin contoh `bridge-ports all`, konfigurasi interface hasil tebakan, atau file Auto-Installer dari percakapan tanpa verifikasi. Contoh Auto-Installer pada PDF berisi password root langsung di berkas konfigurasi; jangan memakai pola tersebut atau menyimpan rahasia di repo/chat.

## Perubahan buku

| Lokasi | Perubahan |
|---|---|
| Bab 9.1, 9.3-9.4 | Menambahkan diagnosis jaringan sementara: cocokkan bridge/interface, IP, gateway, dan DNS dengan subnet aktif sebelum mengubah jaringan. |
| Bab 9.6 | Setelah update/reboot, cek `lscpu` dan `/dev/kvm` sebelum template atau guest dibuat. Catatan DNS menegaskan cocokkan nameserver dengan jaringan host yang sedang aktif. |
| Bab 11 | Kasus nyata KVM merujuk ke metode BIOS tanpa layar Bab 27.5 dan meminta pemeriksaan VT-x serta `/dev/kvm`. |
| Bab 24 | Baris diagnosis KVM dan jaringan mencantumkan pemeriksaan sesuai hasil aktual. |
| Bab 27.5 | Menambahkan prosedur thinklmi berbatas jelas, pemeriksaan nilai yang tersedia, reboot, verifikasi, dan catatan VT-d opsional. |
| Bab 49 | Template VM 9100 dan CT 9200 ditempatkan segera setelah update Proxmox. Prasyaratnya KVM sehat. Panduan membedakan VM Docker dan CT Linux ringan, lalu mengklon dengan identitas, IP, resource, serta nama sendiri. |
| `docs/09-mulai-di-m710q.md` | Urutan awal diperbarui agar template dibuat setelah update dan sebelum guest layanan. |

## Hasil uji yang dicatat pada 31 Oktober 2026

- `uname -r`: `7.0.14-26-pve`; `systemctl --failed`: tidak ada unit gagal.
- `free -h`: RAM terdeteksi 23 GiB; BIOS dan MemTest86 masih perlu diuji.
- NVMe Samsung MZALQ512HALU-000L2 terdeteksi pada 476,9 GB.
- DNS update awal gagal karena nameserver `192.168.88.253` tidak berada di jaringan sementara `192.168.0.0/24`. Setelah DNS host disetel ke `192.168.0.1`, resolusi DNS dan `apt-get -o Acquire::ForceIPv4=true update` berhasil.
- `ip -br link`/`interfaces` yang dikirim pengguna mengidentifikasi port `enp0s31f6` dan `eno1` pada `vmbr0`; gateway aktif `192.168.0.1`. Nama interface, subnet, dan DNS harus diperiksa bersama, bukan menyalin contoh dari percakapan lain.
- Windows `192.168.0.100` dapat menjangkau SSH TCP 22 pada host `192.168.0.200`. Fingerprint host diverifikasi; autentikasi Codex belum disiapkan.
- Template dan layanan belum dibuat. Enclosure single-bay ditemukan tetapi belum diuji.

## Batas

Hasil uji hanya menggambarkan satu M710q dan konfigurasi firmware yang dilaporkan. Bab layanan, clone template, firewall, penyimpanan HDD, dan pemulihan belum diuji. Catat hasil aktual di `catatan/hasil-uji.md` sebelum menandai fase selesai.
