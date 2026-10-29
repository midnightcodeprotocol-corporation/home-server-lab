# 11 - Prompt untuk memulai sesi dengan AI

Salin satu blok di bawah ke AI (Claude, Gemini, ChatGPT) sebagai pesan pertama. AI harus bisa membaca repo ini (beri tautan atau unggah berkas).

## Memulai sesi baru (lanjutkan proyek)

```
Kamu asisten untuk proyek Home Server Lab saya. Baca repo GitHub saya:
<TAUTAN-REPO>
Mulai dari AGENTS.md, lalu STATUS.md, lalu docs/10-konteks-proyek.md.
Setelah membaca, jawab singkat: (1) ringkasan proyek dan perangkat saya, (2) posisi terakhir, (3) langkah berikutnya.
Lalu pandu saya satu langkah dulu, tunggu hasil, baru lanjut. Jawab dalam Bahasa Indonesia, perintah tanpa sudo.
```

## Sesi pengujian satu bab

```
Baca repo (AGENTS.md dan STATUS.md). Hari ini saya menguji Bab <NOMOR> dari docs/bab/.
Pandu saya satu langkah setiap kali. Setelah selesai, buatkan baris untuk catatan/hasil-uji.md:
lulus / gagal / perlu revisi, pesan error persis, dan butir [BELUM PASTI] yang sudah terjawab.
```

## Memperbarui buku setelah uji

```
Baca repo. Dari catatan/hasil-uji.md, buat daftar errata (bab, kalimat salah, perbaikan).
Usulkan revisi bertahap, bukan tulis ulang total. Tandai yang tidak pasti dengan [BELUM PASTI].
```

## Bila sesuatu tidak jelas
Jangan mengarang nilai (IP, VMID, RAM, port). Cek `data/guest.yaml` dan `docs/07-port-dan-akses.md`; bila tidak ada, tanya saya.
