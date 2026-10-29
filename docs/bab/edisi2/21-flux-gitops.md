# Bab 21. GitOps dengan Flux

GitOps berarti Git adalah sumber kebenaran: kondisi cluster dideskripsikan dalam berkas YAML di  
repository, dan agen di cluster (Flux) menyamakan cluster dengan isi repository. Mengubah aplikasi cukup  
dengan commit.  
Langkah Pelaku  
1. Tulis atau ubah YAML, commit, push ke Forgejo Anda  
2. Memantau repository tiap beberapa menit Flux (di k3s)  
3. Menerapkan perbedaan ke cluster Flux  
4. Mengusulkan versi image baru lewat pull request Renovate (Bab 22)  

## 21.1 Struktur repository

Pakai repository homelab di Forgejo (Bab 15.4). Strukturnya:  
BERKAS: struktur folder repository homelab  
 1 homelab/  
 2 clusters/  
 3 home/  
 4 apps.yaml &lt;- memberi tahu Flux folder apps/ harus diterapkan  
 5 flux-system/ &lt;- dibuat otomatis oleh flux bootstrap  
 6 apps/  
 7 web/  
 8 namespace.yaml  
 9 deployment.yaml  
10 service.yaml  
11 kustomization.yaml  
12 renovate.json  

## 21.2 Memasang Flux (bootstrap)

**TERMINAL (login sebagai root)** | VM 203 (root)

```
curl -s https://fluxcd.io/install.sh | bash
```
> Penjelasan: Memasang perintah flux di VM 203.
```
export KUBECONFIG=/etc/rancher/k3s/k3s.yaml
```
> Penjelasan: Memberi tahu flux dan kubectl letak berkas akses cluster k3s.
```
flux check --pre
```
> Penjelasan: Memeriksa prasyarat cluster. Harus berakhir "prerequisites checks passed".
```
flux bootstrap git --url=ssh://git@192.168.88.20:2222/USERNAME/homelab.git \
  --branch=main --path=clusters/home
```
> Penjelasan: Memasang Flux di cluster dan menyimpan konfigurasinya di repository. Ganti USERNAME.
1. Perintah bootstrap menampilkan kunci publik. Tambahkan di repository: Settings &gt; Deploy  
Keys &gt; Add, centang Enable Write Access.  
> Penjelasan: Flux perlu menulis ke repository untuk menyimpan konfigurasinya sendiri.
2. Kembali ke terminal, tekan y untuk melanjutkan.  
> Penjelasan: Flux memasang komponennya di namespace flux-system.
3. Periksa dengan flux get all dan kubectl -n flux-system get pods.  
> Penjelasan: Semua pod harus Running.

## 21.3 Aplikasi pertama (contoh web)

BERKAS: apps/web/namespace.yaml  
 1 apiVersion: v1  
 2 kind: Namespace  
 3 metadata:  
 4 name: web  
BERKAS: apps/web/deployment.yaml  
 1 apiVersion: apps/v1  
 2 kind: Deployment  
 3 metadata:  
 4 name: web  
 5 namespace: web  
 6 spec:  
 7 replicas: 2  
 8 selector:  
 9 matchLabels:  
10 app: web  
11 template:  
12 metadata:  
13 labels:  
14 app: web  
15 spec:  
16 containers:  
17 - name: nginx  
18 image: nginx:1.27  
19 ports:  
20 - containerPort: 80  
BERKAS: apps/web/service.yaml  
 1 apiVersion: v1  
 2 kind: Service  
 3 metadata:  
 4 name: web  
 5 namespace: web  
 6 spec:  
 7 type: NodePort  
 8 selector:  
 9 app: web  
10 ports:  
11 - port: 80  
12 targetPort: 80  
13 nodePort: 30080  
BERKAS: apps/web/kustomization.yaml  
 1 apiVersion: kustomize.config.k8s.io/v1beta1  
 2 kind: Kustomization  
 3 resources:  
 4 - namespace.yaml  
 5 - deployment.yaml  
 6 - service.yaml  

**BERKAS: clusters/home/apps.yaml** | Memberi tahu Flux untuk menerapkan apps/web setiap 5 menit

```
apiVersion: kustomize.toolkit.fluxcd.io/v1
kind: Kustomization
metadata:
name: apps
namespace: flux-system
spec:
interval: 5m
path: ./apps/web
prune: true
sourceRef:
kind: GitRepository
name: flux-system
```

**TERMINAL (user biasa)** | Laptop / VM 203

```
git add . && git commit -m "tambah aplikasi web" && git push
```
> Penjelasan: Mengirim perubahan ke Forgejo (dari laptop atau VM).
```
flux reconcile source git flux-system
```
> Penjelasan: Memaksa Flux menarik perubahan sekarang (tanpa menunggu 5 menit).
```
flux get kustomizations
```
> Penjelasan: Status penerapan; kolom READY harus True.
```
kubectl -n web get pods
```
> Penjelasan: Memastikan 2 pod nginx berjalan.
Ubah replicas: 2 menjadi 3, commit dan push: jumlah pod menjadi tiga. Jika Anda mengubah lewat  
kubectl scale, Flux mengembalikannya sesuai isi Git.  

## 21.4 Rahasia di Git dengan SOPS dan age

Jangan menyimpan password atau token apa adanya di repository. Pakai SOPS dengan kunci age agar  
berkas rahasia terenkripsi di Git dan hanya didekripsi di dalam cluster.  

**TERMINAL (login sebagai root)** | VM 203 (root)

```
age-keygen -o age.agekey
```
> Penjelasan: Membuat kunci age. Salin kunci publik (age1...) dari keluarannya.
2  
# kubectl create secret generic sops-age --namespace=flux-system \  
 --from-file=age.agekey=age.agekey  
> Penjelasan: Menyimpan kunci privat di cluster. Jangan masukkan age.agekey ke Git.

**BERKAS: .sops.yaml** | Di akar repository

```
creation_rules:
- path_regex: .*\.secret\.yaml$
encrypted_regex: ^(data|stringData)$
age: <KUNCI-PUBLIK-AGE>
```

**BERKAS: tambahan pada Kustomization Flux** | Untuk Kustomization yang berisi rahasia

```
spec:
decryption:
provider: sops
secretRef:
name: sops-age
```

Enkripsi berkas dengan sops --encrypt --in-place nama.secret.yaml sebelum commit. Cadangkan  
age.agekey di password manager; bila hilang, rahasia tidak bisa dibuka.  
KASUS NYATA - Flux bootstrap gagal: permission denied (publickey)  
Gejala: Bootstrap berhenti dengan error SSH.  
Penyebab: Deploy key belum ditambahkan atau tidak punya izin tulis.  
Solusi: Tambahkan kunci publik di Settings &gt; Deploy Keys repo homelab dengan Write Access, lalu ulangi  
bootstrap.  
KASUS NYATA - Perubahan di Git tidak muncul di cluster  
Gejala: Setelah push, pod tidak berubah.  
Penyebab: Flux belum menarik, path salah, atau YAML tidak valid.  
Solusi: Jalankan flux reconcile source git flux-system dan flux get kustomizations; baca  
kolom Message; kubectl -n flux-system logs deploy/kustomize-controller.
