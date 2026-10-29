# Bagian 9. SSO dengan Pocket ID dan Immich (pengantar)

Bagian 9. SSO dengan Pocket ID dan Immich  
Asal: Suplemen 9. Bab 54-56.  
Suplemen 9 menambah dua layanan dan satu panduan pengaturan. Pocket ID adalah satu pintu masuk (SSO)  
berbasis passkey, tanpa kata sandi. Immich adalah pengganti Google Photos yang menyimpan foto dan video di  
server Anda sendiri. Karena RAM mesin utama saat ini 16 GB, bab terakhir menyusun profil pemakaian agar  
tidak semua VM menyala bersamaan.  
Bab Isi Hasil akhir  
54. SSO dengan Pocket ID VM sso, Tailscale Serve, server, passkey di  
Windows/Android/iPhone, klien OIDC, backup dan firewall  
Satu akun passkey untuk  
layanan yang  
mendukung OIDC  
55. Immich VM immich dan disk foto, server, SSO, klien  
Windows/Android/iPhone, backup dan firewall  
Foto HP tercadangkan  
otomatis ke server sendiri  
56. Mesin 16 GB Anggaran RAM, lima profil, skrip pergantian profil, jadwal  
PBS, rencana saat RAM naik  
Semua layanan bisa  
dipakai bergantian tanpa  
kehabisan RAM  
Prasyarat  
• Templat VM 9100 (Suplemen 7 Bab 49) dan tailnet dengan HTTPS Certificates aktif serta entri grants tcp:443  
(Suplemen 6 Bab 44.3).  
• Vaultwarden (Suplemen 6) untuk menyimpan kunci dan kata sandi yang dibuat di sini.  
• Perintah server dijalankan sebagai root setelah su - (tanpa sudo), di guest yang ditunjuk Kotak Penempatan.  
PERINGATAN  
Urutan penting. Kerjakan Bab 54 sebelum Bab 55, dan tetapkan nama tailnet Anda dulu. Passkey terikat ke nama  
alamat Pocket ID; bila nama berubah setelah passkey terdaftar, semua passkey harus didaftar ulang. Hal yang belum  
bisa saya pastikan ditandai [BELUM PASTI].
