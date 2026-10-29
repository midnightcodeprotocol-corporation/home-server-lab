# Lampiran A. Ringkasan Perintah

A.1 Proxmox (Shell, root)  
Tujuan Perintah  
Versi Proxmox pveversion  
Daftar VM / CT qm list / pct list  
Start / stop VM qm start 201 / qm shutdown 201  
Start / stop CT pct start 101 / pct shutdown 101  
Konfigurasi VM qm config 201  
Terapkan jaringan ifreload -a  
Backup vzdump 201 --storage local --mode snapshot  
Restore VM / CT qmrestore berkas 201 / pct restore 101 berkas  
Update apt update && apt full-upgrade  
Status web systemctl status pveproxy  
A.2 MikroTik (terminal)  
Tujuan Perintah  
Backup konfigurasi /system backup save name=NAMA dan /export file=NAMA  
Daftar lease DHCP /ip dhcp-server lease print  
Reservasi IP /ip dhcp-server lease add address=IP mac-address=MAC  
comment=NAMA  
DNS untuk klien /ip dhcp-server network set 0 dns-server=A,B  
DNS router /ip dns set servers=A,B allow-remote-requests=no  
Ping dari router /ping 192.168.88.10 count=3  
Lihat layanan /ip service print  
Tabel ARP /ip arp print  
A.3 Docker, Kubernetes, Flux  
Tujuan Perintah  
Container berjalan / log docker ps / docker logs -f NAMA  
Naik / turun stack docker compose up -d / docker compose down  
Perbarui image docker compose pull && docker compose up -d  
Node / pod / service kubectl get nodes / kubectl get pods -A / kubectl get svc  
-A  
Tujuan Perintah  
Status Flux flux get all  
Paksa sinkron Flux flux reconcile source git flux-system  
A.4 Windows dan jaringan  
Tujuan Perintah  
Lihat IP ipconfig /all  
Perbarui lease DHCP ipconfig /renew  
Tes DNS nslookup domain alamat-dns  
Cek hash ISO certutil -hashfile berkas.iso SHA256  
SSH ssh root@192.168.88.10
