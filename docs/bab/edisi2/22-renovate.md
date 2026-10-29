# Bab 22. Renovate: Pembaruan Otomatis

Renovate memindai repository, menemukan versi lama (image Docker, chart, dependensi), lalu membuat  
pull request pembaruan otomatis. Dengan GitOps, menerima PR (merge) cukup untuk memperbarui  
aplikasi.  

## 22.1 Menyiapkan akun bot

1. Di Forgejo buat user renovate-bot (Site Administration &gt; User Accounts &gt; Create).  
> Penjelasan: Akun terpisah agar PR dari bot mudah dikenali.
2. Tambahkan bot sebagai Collaborator dengan izin Write pada repo homelab.  
> Penjelasan: Agar bot boleh membuat cabang dan PR.
3. Login sebagai bot &gt; Settings &gt; Applications: buat access token dengan izin repository (read dan  
write), user (read), dan issue (read dan write). Simpan tokennya.  
4. Buat token GitHub read-only tanpa izin (untuk membaca catatan rilis tanpa batas laju).  
> Penjelasan: Opsional tetapi disarankan.

## 22.2 Menjalankan Renovate

**BERKAS: /opt/renovate/env** | VM Debian 13; pada Renovate lama gunakan RENOVATE_PLATFORM=gitea

```
RENOVATE_PLATFORM=forgejo
RENOVATE_ENDPOINT=http://192.168.88.20:3000/api/v1/
RENOVATE_TOKEN=TOKEN_BOT_FORGEJO
RENOVATE_GIT_AUTHOR=Renovate Bot <renovate@lab.local>
RENOVATE_AUTODISCOVER=true
RENOVATE_GITHUB_COM_TOKEN=TOKEN_GITHUB_READONLY
LOG_LEVEL=info
```

**TERMINAL (login sebagai root)** | VM Debian 13 (root)

```
mkdir -p /opt/renovate && chmod 700 /opt/renovate
```
> Penjelasan: Membuat folder dan membatasi aksesnya.
```
nano /opt/renovate/env
```
> Penjelasan: Isi berkas variabel (di atas) lalu simpan.
```
chmod 600 /opt/renovate/env
```
> Penjelasan: Hanya root yang boleh membaca token.
```
docker run --rm --env-file /opt/renovate/env renovate/renovate:<VERSI>
```
> Penjelasan: Menjalankan Renovate satu kali (ganti &lt;VERSI&gt; dengan versi terbaru). Baca log di layar.

**TERMINAL (login sebagai root)** | VM Debian 13 (root)

```
crontab -e
```
> Penjelasan: Menjadwalkan agar berjalan berkala. Tambahkan baris di bawah.

**BERKAS: crontab** | Setiap 6 jam

```
0 */6 * * * docker run --rm --env-file /opt/renovate/env renovate/renovate:<VERSI>
```

## 22.3 Berkas renovate.json di repository

**BERKAS: renovate.json** | Di akar repository

```
{
"$schema": "https://docs.renovatebot.com/renovate-schema.json",
"extends": ["config:recommended"],
"schedule": ["before 6am on saturday"],
"prConcurrentLimit": 5
}
```

Setelah Renovate berjalan, repository akan mendapat PR Configure Renovate (jika perlu), lalu PR  
pembaruan seperti Update nginx to v1.28. Tinjau, merge, dan Flux menerapkannya ke cluster.  
TIPS  
Pin versi image (jangan latest) pada compose dan manifest. Renovate hanya bisa mengusulkan pembaruan  
bila versi tertulis eksplisit. Berkas compose.yaml Docker juga dipindai otomatis.  
KASUS NYATA - Renovate tidak membuat PR sama sekali  
Gejala: Log berakhir tanpa PR, atau tidak ada repository ditemukan.  
Penyebab: Bot belum jadi collaborator, token kurang izin, atau tidak ada dependensi dikenali.  
Solusi: Periksa log: cari repositories dan No repositories found; tambahkan bot ke repo, periksa izin  
token, dan pastikan versi image tertulis.
