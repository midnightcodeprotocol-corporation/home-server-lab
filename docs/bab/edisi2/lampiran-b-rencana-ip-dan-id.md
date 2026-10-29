# Lampiran B. Rencana IP dan ID

Perangkat / layanan ID IP Port / akses Catatan  
MikroTik RB750GL - 192.168.88.1 80 (WebFig), WinBox  
TL-WR820N (AP) - 192.168.88.2 80  
TL-WR840N (penerima) - 192.168.0.1 80 Jaringan di atas MikroTik  
Proxmox - 192.168.88.10 8006 IP statis  
AdGuard #2 (LXC) 101 192.168.88.11 80, 53 Static lease  
Samba (LXC) 102 192.168.88.12 445 Static lease  
Tailscale cadangan (LXC) 103 - Opsional  
dnsdist (LXC) 104 192.168.88.13 53 Opsional (latihan)  
Pi-hole (LXC) 105 192.168.88.14 80, 53 Opsional  
VM Debian 13 201 192.168.88.20 80, 3000, 2222, 8080,  
9443  
Dashboard, Forgejo,  
Nextcloud, Portainer  
VM Home Assistant 202 192.168.88.21 8123 Static lease  
VM k3s 203 192.168.88.22 6443 Static lease  
Template Debian 9000 - -  
STB (AdGuard + Tailscale) - 192.168.88.253 80, 53 Static lease
