# Memory Project: Home Server Lab

Ekspor memory Claude untuk project "Home Server Lab Project".
Diekspor: 2026-10-30. Isi disalin apa adanya dari file memory (format `[stated]` = disebutkan langsung oleh pengguna).
Catatan: file `/areas/home-server.md` level akun (di luar project) tidak diekspor; versi project-nya ada di bagian 3.

## Daftar isi

1. index
2. preferences
3. areas/home-server
4. areas/proxmox-lab
5. areas/buku-panduan-suplemen
6. areas/rencana-lanjutan
7. areas/home-server-roadmap

---

## 1. index

- name: Home Server Lab Project
- description: Home Server Lab Project
- updated: 2026-10-09

---

## 2. preferences

- description: Preferensi cara kerja untuk Home Server Lab Project (pembaruan buku panduan PDF bertahap).
- aliases: preferensi
- updated: 2026-10-20

- [stated] for updates to the Home Server Lab guide PDF (Edisi 2 onward): deliver in several phases, not all at once and not a total rewrite (2026-10-18)
- [stated] in Edisi 3 chapters, explain setup more completely: both the server side and the client side that connects to it (e.g. Tailscale on the server and on the phone and laptop used for access) (2026-10-18)
- [stated] working rules for guide supplements (2026-10-18): each chapter covers the server side and the client side (Windows, Android, iPhone); commands without sudo (SSH in, then su -); same page style as earlier supplements (use the source zip); check official documentation before writing and mark anything uncertain
- [stated] new rule for the guide (2026-10-20): every app/container/docker should be separated into its own Proxmox VM or container, and every installation chapter must open with an explanation of whether to create a new VM/container or combine into an existing one

---

## 3. areas/home-server

- description: Proyek home server pemula: AdGuard Home di STB HG680 (Armbian), perangkat jaringan rumah (IndiHome, MikroTik RB750GL, TP-Link).
- aliases: adguard, home server, homelab
- updated: 2026-10-13

- [stated] starting a home server project from scratch, from the most basic step; first project is AdGuard Home (ad blocker) for the home network
- [stated] plan: flash STB IndiHome HG680 with Armbian and run AdGuard on it
- [stated] owns: IndiHome router, TP-Link TL-WR826N, STB IndiHome HG680, MikroTik RB951Ui-2nD (but will use MikroTik RB750GL instead from now on), TP-Link LiteWave LS1005 (switch; corrected from TL-LS1008)
- [stated] connection plan: IndiHome router reached via WiFi by TL-WR826N, which then connects to MikroTik and the rest of the home network (not a wired link from IndiHome)
- [stated] wants phones, laptop and computer on the separate network to stay on WiFi; considering getting a 2nd STB to run OpenWrt as an internet gateway with a portable USB modem
- [stated] has done a fresh install of Armbian v25.05.0 for Aml S905x (Linux 6.1.137-ophub) on the STB and connects to it via PuTTY; STB currently gets a 192.168.1.x address while a router was set to 192.168.2.100
- [stated] TL-WR826N routing table shows default route via 192.168.1.1 on WAN, LAN/WLAN subnet 192.168.2.0/24 with gateway 192.168.2.1, and WAN on 192.168.1.0/24 (WAN IP appears to be 192.168.1.7); STB is plugged into WR826N LAN 1 but still gets 192.168.1.100 with the IndiHome router as gateway
- [stated] http://192.168.1.1 (from the PC) shows a TP-Link TL-WR820N login page, same model as the page at http://192.168.2.1, but the admin password set on the 192.168.2.1 router does not work on it; STB traceroute shows hops 192.168.1.1 -> 192.168.2.1 -> 192.168.1.1 (IndiHome) -> ISP
- [stated] the black device labeled IndiHome/FiberHome in the photo is the STB itself (not a modem); a short white cable runs from the white TL-WR820N on the desk (label MAC A8-6E-84-E1-E7-5C) to the STB
- [stated] the router page at 192.168.2.1 (also TL-WR820N) shows WAN 192.168.1.7 (Dynamic IP, gateway 192.168.1.1), LAN MAC 48-22-54-39-93-90, LAN 192.168.2.1, DHCP pool 192.168.2.100-199; its clients are all wireless 2.4G and include the desk router at 192.168.2.100 (MAC A8-6E-84-E1-E7-5D)
- [stated] previously installed Armbian onto the STB's built-in eMMC; currently boots a fresh Armbian from an external "SSD" and is unsure whether the running system uses the eMMC or the SSD
- [stated] believes owning only one TL-WR820N router
- [stated] corrections: the desk TL-WR820N was reaching IndiHome through another router's WAN (192.168.2.100 was that router's IP); it is now connected directly to IndiHome and still not configured
- [stated] MikroTik has arrived but is not yet configured or installed; also bought a fresh TP-Link TL-WR840N ver 6.20 (not yet powered on or configured)
- [stated] wants to compare TL-WR840N vs TL-WR820N for WAN receiver (from IndiHome) vs access point roles
- [stated] too many separate TP-Link power cables; asked GPT to design a central multi-output DC power supply PCB (12 V in, 5/12/24 V outputs, barrel jacks) and is unsure it is correct, so asked for a review
- [stated] IndiHome has no LAN cable available, uplink is WiFi only; has set up the TL-WR840N in WISP mode as the receiver (confirmed done), next step is connecting it to the MikroTik RB750GL ether1
- [stated] connected to the MikroTik RB750GL in WinBox (via cable on ether2); WAN check passed (ether1 gets an address from the TL-WR840N and internet pings work); next: switch + STB behind MikroTik, AdGuard Home install, DHCP DNS to the STB
- [stated] TL-WR820N has been switched to Access Point mode; asked for a complete detailed manual covering cabling and setup of the receiver router, MikroTik, AP router, switch and STB (HG680)
- [stated] MikroTik RB750GL runs RouterOS 6.49.23 (up to date on stable); ether1-gateway is bound to 192.168.0.100 from the WR840N with working internet and DNS; DHCP pool set to 192.168.88.100-254; telnet/ftp/api/api-ssl disabled and winbox/ssh limited to 192.168.88.0/24; backup awal-ok and export config-awal-ok saved on the router
- [stated] listed more network devices alongside the MikroTik project question: Ubiquiti UniFi U6 Lite, Nokia G-2425G-A, FortiGate 60F, Cisco IP1101, TP-Link TL-POE160S
- [stated] STB HG680 now plugged into MikroTik RB750GL ether4 (2026-10-13); asked what to do next
- [stated] suspects the STB has two Armbian installs, one on eMMC and one on SD card (2026-10-13); wants this sorted before installing AdGuard
- [stated] STB (Armbian v25.05.0) now at 192.168.88.253 behind MikroTik; internet and DNS pings OK. Running system is on the SD card (mmcblk1, 29G, fresh install); eMMC (mmcblk2, 7.3G) holds an older unused Armbian install (BOOT_EMMC/ROOTFS_EMMC); still deciding whether to move to eMMC before installing AdGuard
- [stated] STB 192.168.88.253 now set as static lease on the MikroTik; agrees to move to eMMC, but in other projects Armbian on eMMC sometimes failed to boot (blank screen) after the STB was powered off or restarted
- [stated] /boot/uEnv.txt on the SD card system uses FDT=/dtb/amlogic/meson-gxl-s905x-p212.dtb with rootflags=data=writeback and fsck.fix/repair=yes
- [stated] moved the STB to eMMC and said it is now safe (booting OK); next: install AdGuard Home
- [stated] AdGuard Home installed on the STB (192.168.88.253) and the setup wizard finished (port 53 freed from systemd-resolved first); next: test nslookup, then set MikroTik DHCP DNS to the STB
- [stated] nslookup tests from the PC against 192.168.88.253 passed (google.com resolves, doubleclick.net returns 0.0.0.0); next: set the MikroTik DHCP DNS to 192.168.88.253
- [stated] MikroTik DHCP DNS now 192.168.88.253; PC wired (192.168.88.252) shows DNS 192.168.88.253. The PC's WiFi was on 192.168.2.107 with gateway 192.168.2.1 (not the MikroTik network) before ipconfig /release left it disconnected
- [stated] wants to start with the next steps (AdGuard config backup, MikroTik hardening, Tailscale); considering a second STB for Tailscale and other services so the AdGuard STB stays dedicated
- [stated] AdGuard config backup (AdGuardHome.yaml) copied to the PC; starting MikroTik hardening next
- [stated] MikroTik RB750GL on RouterOS 6.49.23 (stable): IP services api/api-ssl/ftp/telnet/www-ssl disabled, ssh and winbox limited to 192.168.88.0/24; deliberately kept www (port 80) enabled so it can be configured remotely once Tailscale is set up
- [stated] MikroTik hardening steps all done (admin password, services, MAC server/neighbors, firewall check); next: Tailscale
- [stated] Tailscale on hold until the second STB arrives; going with Tailscale on STB 2 (subnet router) and keeping STB 1 for AdGuard only
- [stated] access point (TL-WR820N) setup done and working behind the MikroTik (said "sudah aman")
- [stated] while waiting for STB 2, wants to learn MikroTik and find what can be learned and put to use (2026-10-14)

---

## 4. areas/proxmox-lab

- description: Lab latihan Proxmox VE (nested di VMware Workstation Pro, laptop + HDD 2 TB) sebelum mesin server utama datang; rencana install ulang + restore backup.
- aliases: proxmox, lab virtual, nested virtualization, proxmox lab
- updated: 2026-10-28

- [stated] part of [[home-server]]: main server machine has not arrived yet, so building a practice lab instead of waiting (2026-10-16)
- [stated] lab setup: Proxmox VE installed inside a VM on VMware Workstation Pro on the laptop (nested virtualization); the VM files are stored on an existing 2 TB HDD to save laptop storage; VM uses bridged networking so Proxmox gets its own home-network IP and is opened from the laptop browser at https://IP-proxmox:8006
- [stated] goals of the lab: learn the Proxmox UI/menus, storage and network setup, create containers (LXC) and light VMs, practice backup and restore, practice updates and configuration without risking the real machine; zero extra cost
- [stated] known limits accepted: slower (two virtualization layers + HDD), hardware-dependent features like GPU passthrough can't be tried, and the lab install can't be moved directly to the real machine
- [stated] plan: when the real machine arrives, do a clean Proxmox install and restore VM/container backups made in this lab
- [stated] Proxmox lab VM allocation: 2 CPU cores and 200 GB disk; VMware Workstation itself is also installed on the 2 TB HDD (2026-10-16)
- [stated] Proxmox lab VM has 8 GB RAM allocated; the laptop has 20 GB RAM (2026-10-16)
- [stated] VM settings done in VMware (2026-10-16): VM files at G:\VM\Proxmox (G: is the 2 TB HDD), 200 GB disk not preallocated and single file, VT-x/EPT enabled, bridged (Automatic) network, ISO proxmox-ve_9.2-1.iso attached; Proxmox not yet installed, asked to be guided through the install
- [stated] Proxmox installed with IP 192.168.100.2 but the laptop browser cannot connect to https://192.168.100.2:8006; laptop was not connected to the MikroTik network during install (2026-10-16)
- [stated] fixed the IP mismatch by editing /etc/network/interfaces and /etc/hosts; Proxmox web UI is now reachable from the laptop (2026-10-16)
- [stated] apt repositories fixed (enterprise disabled, no-subscription on) and DNS fixed, apt update works; plans to install on Proxmox: 1) TrueNAS / Nextcloud as NAS, 2) three Pi-hole/AdGuard instances, two as ad blockers and one as a balancer between the two, 3) Portainer (2026-10-16)
- [stated] extended app plan for the Proxmox server (2026-10-16): also wants Docker, Kubernetes, GitOps, a personal GitHub, Renovate bots, and more apps to be listed later (in addition to TrueNAS/Nextcloud, the Pi-hole/AdGuard trio and Portainer)
- [stated] the "personal GitHub" means a self-hosted Git server for storing code and projects; also listed the TP-Link receiver router, TP-Link access point, MikroTik, Home Assistant and Tailscale as items and asked whether everything can run on one machine or should be split (2026-10-16)
- [stated] clarified: the MikroTik and TP-Link items are meant only as website shortcuts to open their admin pages without typing IPs; asked for a sensible split assuming one Proxmox machine and one STB (2026-10-16)
- [stated] asked for a complete, very detailed PDF tutorial book split into chapters (from zero to the end, with solutions for problems already encountered in the chats); delivered as Buku_Panduan_Home_Server_Lab.pdf (2026-10-16)
- [stated] requested a revised book (Edisi 2, 2026-10-17): code in visible boxes with each command line separated, three Proxmox install models (in a VM, on the real machine, or onto an SSD/HDD first then moved), a tutorial while connected to the MikroTik home network, a more complete install walkthrough, Debian GNU/Linux 13 as the VM OS, download links (Debian 13.7.0 netinst ISO https://cdimage.debian.org/debian-cd/current/amd64/iso-cd/debian-13.7.0-amd64-netinst.iso, Proxmox, etc.), commands without sudo, Tailscale install/config in the STB steps, an explanation for every step, separate detailed chapters per app (system and MikroTik configuration), a comparison of AdGuard vs Pi-hole and an assessment of the 3-ad-blocker idea (2 working + 1 balancer), a dashboard of shortcuts for everything installed, and images where possible; delivered as Buku_Panduan_Home_Server_Lab_Edisi2.pdf
- [stated] will install Proxmox on a used computer (real machine) for now, while waiting for funds to buy a mini PC (2026-10-18)
- [stated] pengujian dari nol (2026-10-23): memakai Model A (Proxmox di VM VMware); punya SSD NVMe 500 GB yang akan jadi tempat instalasi Proxmox dan HDD 2 TB untuk penyimpanan; VM VMware "Proxmox_project_1" dibuat dengan 16 GB RAM, 2 prosesor, disk 400 GB, bridged (Automatic), file di F:\02-Proxmox Mechine\Proxmox_project_1\
- [stated] drive F: = SSD NVMe 500 GB lewat adaptor disk eksternal (USB); HDD 2 TB belum dipasang; laptop RAM 20 GB; tahap ini hanya menyiapkan Proxmox lab, lalu backup dan dipindah ke mesin asli saat sudah datang dan siap
- [stated] catatan untuk ditambahkan ke buku (kasus nyata dari pengujian 2026-10-23): (1) installer VMware Workstation muncul "invalid drive G:" karena folder instal lama ada di drive portabel yang sudah tidak ada; solusi: Command Prompt sebagai Administrator, jalankan subst G: C:\ lalu pasang VMware, setelah selesai subst G: /d. (2) VMnet0 tidak muncul di Virtual Network Editor walau sudah instal ulang dan perbaikan lewat Device Manager; menambah jaringan manual tetap gagal memilih Bridged dengan pesan "Cannot change network to bridged: There are no un-bridged host network adapters"; hasil uji cara-cara pemulihan: menyusul
- [stated] hasil uji: hash ISO proxmox-ve_9.2-1.iso cocok dengan SHA256 resmi; Virtualization di Task Manager Enabled; laptop sudah di jaringan MikroTik (gateway aman); VM diubah ke 8192 MB
- [stated] hasil uji VMnet0: VMware Bridge Protocol sudah terpasang dan tercentang di adapter Wi-Fi Realtek RTL8723DE (bukan penyebab); Restore Defaults di Virtual Network Editor tidak memunculkan VMnet0 (hanya VMnet1 dan VMnet8); VMnet0 ditambah manual tetap gagal Bridged dengan "no un-bridged host network adapters"; Npcap terpasang di laptop
- [stated] 2026-10-23: sc query vmnetbridge = error 1060 (layanan tidak terdaftar) setelah instal ulang VMware di laptop, sc query vmnetadapter STOPPED (1077), VMnet0 tidak bisa jadi Bridged; pengguna menghentikan perbaikan dan memutuskan memasang di PC lama saja (bukan laptop)
- [stated] garis besar (2026-10-23): VM VMware di laptop tidak bisa bridged, nanti akan dicoba instal ulang VMware sebagai percobaan terpisah; jika memakai komputer lama hanya bisa memakai HDD karena adaptor M.2 ke SATA yang dimiliki tidak cocok untuk NVMe M.2 (NVMe 500 GB hanya jalan lewat adaptor USB)
- [stated] komputer lama = HP prebuilt tanpa slot NVMe M.2 (2026-10-24): RAM 2 GB, HDD 2 TB, CPU Pentium (ditulis "62020T", kemungkinan G2020T, belum dikonfirmasi), Intel VT-x supported, Intel HT dan Intel SMX tidak supported
- [stated] hasil uji lanjutan di laptop (2026-10-24): layanan Windows VMware yang terdaftar hanya VMnetDHCP dan VMware NAT Service (ditambah driver VMnetAdapter dan VMnetUserif); VMnetBridge dan VMAuthdService (error 1060) tidak ada; kunci registry InstallPath VMware Workstation tidak ditemukan; indikasi instalasi VMware rusak sebagian, rencana: uninstall bersih lalu pasang ulang ke C: dengan folder VM tetap di F: (SSD NVMe via USB)
- [stated] Settings > Apps > Installed apps: pencarian "vmware" tidak menemukan apa pun (tidak ada entri uninstall VMware Workstation), padahal aplikasi VMware Workstation 25H2 bisa dibuka; lokasi program belum diketahui
- [stated] vmware.exe yang berjalan berada di G:\VM\VMware Workstation Pro\vmware.exe, padahal drive data pengguna adalah F: (NVMe via USB); G: ternyata drive nyata (HDD 2 TB, sekitar 1,8 TB, sudah terpasang; perintah subst kosong), jadi VMware berjalan dari HDD; drive lain di laptop: C: (625 GB kosong), D:, E:, F: (NVMe 477 GB kosong)
- [stated] peta drive laptop: F: = SSD NVMe 500 GB eksternal (file VM Proxmox_project_1); G: = HDD 2 TB (belum dipindah ke mesin server; tidak selalu tersambung); VMware Workstation terpasang hanya di G:\VM\VMware Workstation Pro (C:\VM dan C:\Program Files (x86)\VMware tidak ada); G:\VM\Proxmox ada (isi belum diperiksa, jangan dihapus)
- [stated] hasil uji lanjutan (2026-10-24): layanan VMnetDHCP dan VMware NAT Service menunjuk ke C:\Windows\system32\vmnetdhcp.exe dan vmnat.exe (bukan ke G:), jadi teori jalur G: tidak terbukti; G:\VM\Proxmox berisi VM lama yang pernah dijalankan (Proxmox.vmdk sekitar 22,3 GB, log vmware.log) dan jangan dihapus; penyebab layanan Authorization/Bridge hilang belum diketahui, berikutnya periksa log pemasang VMware di %TEMP%
- [stated] bukti dari log VMware UI (vmware-ui-20164.log, 2026-10-24): VMware tidak bisa menghubungi authd (CnxAuthdConnectPipe failed, "Failed to read vmware-authd port number: Cannot connect to VMX" untuk VM Proxmox_project_1, VIX_E_HOST_TCP_SOCKET_ERROR); pesan lain di log (CDS softwareupdate.broadcom.com error, config.ini/vsphereFeatures tidak ada, parallel ports) bukan penyebab; rencana: pasang ulang VMware lewat pemasang ke C:\Program Files (x86) dengan G: tersambung, folder VM tetap di F:
- [stated] setelah pasang ulang VMware ke C:\Program Files\VMware\VMware Workstation (2026-10-24, pemasang tidak meminta restart, tanpa error): VMAuthdService RUNNING dan vmware.exe berjalan dari C:\Program Files; sc query vmnetbridge masih error 1060; langkah berikut: restart Windows lalu uji lagi Virtual Network Editor / Bridged
- [stated] setelah pasang ulang VMware ke C: dan restart: Virtual Network Editor awalnya kosong, Restore Defaults hanya membuat VMnet1 (Custom) dan VMnet8 (NAT), VMnet0 (Bridged) masih tidak ada; berikutnya periksa berkas netbridge.inf di folder instalasi dan pasang manual lewat properti adapter
- [stated] berkas bridge ada di C:\Program Files\VMware\VMware Workstation (netbridge.inf, vmnetBridge.sys/.dll/.cat); VMware Bridge Protocol sudah ada di properti Wi-Fi sejak awal tetapi VMnet0 tetap tidak bisa dipilih dan layanan vmnetbridge tidak terdaftar; dugaan: binding sisa instalasi lama (belum terbukti), rencana uji: uninstall protokol dari properti adapter lalu pasang ulang dari netbridge.inf di C:
- [stated] 2026-10-25: Windows laptop diinstal ulang bersih, VMware Workstation dipasang ulang, dan pengguna melaporkan VMnet0 sekarang ada dan terhubung ke bridge (belum diverifikasi dengan tangkapan layar/perintah); sebelumnya bridged gagal walau VMware dipasang ulang beberapa kali tanpa instal ulang Windows
- [stated] 2026-10-26: setelah instal ulang Windows, Virtual Network Editor menampilkan VMnet0 Bridged ke "ASIX USB to Gigabit Ethernet Family Adapter" (adapter LAN USB), VMnet1 Host-only 192.168.40.0, VMnet8 NAT 192.168.96.0; daftar VM di Library masih kosong (VM Proxmox_project_1 belum dibuka ulang)
- [stated] 2026-10-26: ipconfig laptop: adapter Ethernet (kabel via USB LAN) 192.168.88.252/24 gateway 192.168.88.1 (jaringan MikroTik OK), Wi-Fi terputus; Windows build 10.0.26300.9711 setelah instal ulang; adapter vEthernet (WSL (Hyper-V firewall)) 172.30.208.1 ada, sehingga komponen WSL/Hyper-V mungkin aktif dan perlu dicek terhadap VT-x di VMware
- [stated] 2026-10-27: laptop CPU AMD Ryzen 3 4300U (4 core, 4 thread), RAM 19,4 GB, Virtualization Enabled di Task Manager; VM baru "Proxmox" di F:\Proxmox\Proxmox.vmx (8 GB RAM, 2 prosesor, disk 200 GB, ISO di E:\93-..., Bridged Automatic); menyalakan VM gagal dengan "Virtualized AMD-V/RVI is not supported on this platform" dan "Feature 'hv.capable' was 0, but must be at least 0x1. Module 'FeatureCompatLate' power on failed"; Windows Features: Hyper-V, Virtual Machine Platform, dan Windows Hypervisor Platform tercentang (penyebab yang dicurigai, sesuai Bab 5.4); WSL dan Windows Sandbox tidak tercentang
- [stated] 2026-10-27: Memory integrity Off; Hyper-V, Virtual Machine Platform, dan Windows Hypervisor Platform sudah dihilangkan centangnya dan Windows di-restart; systeminfo | findstr hypervisor tidak menampilkan apa pun (tidak ada hypervisor Windows terdeteksi); VM Proxmox belum dinyalakan setelah perbaikan
- [stated] 2026-10-28: now owns the real server machine: Lenovo ThinkCentre M710q, Core i5-6500T, 16 GB RAM installed, spare RAM sticks 16 GB and 8 GB not installed, NVMe M.2 500 GB SSD; decided to remove everything about VMware (Model A) and installing to a disk first (Model C) from the book, keeping only direct install on the real machine (Model B)

---

## 5. areas/buku-panduan-suplemen

- description: Status Buku Panduan Home Server Lab: Edisi 2 + Suplemen 1-9 selesai (Bab 25-56), belum diuji; pengujian dari nol dimulai, lalu revisi.
- aliases: suplemen, buku panduan, pdf suplemen, edisi 2
- updated: 2026-10-29

- [stated] guide updates for [[home-server]] / [[proxmox-lab]] are delivered as separate supplement PDFs on top of Edisi 2; next chapters start at Bab 39 (2026-10-18)
- [stated] supplements already made (2026-10-18): Suplemen 1 = security and Tailscale (Bab 25-26); 2 = Proxmox on a used computer (Bab 27-30); 3 = Uptime Kuma, Gotify, Beszel (Bab 31-34); 4 = Caddy and local SSL with the home.arpa name (Bab 35-38)
- [stated] none of the supplements has been tested yet; will report results per chapter
- [stated] uploaded the PDF-builder source zip (sumber_suplemen_1-4.zip) so new supplements keep the same page style
- [stated] planned supplements: 5 = web hosting and n8n (Cloudflare Tunnel only optional, for web); 6 = AFFiNE, Nextcloud calendar, Vaultwarden; 7 = Proxmox Backup Server and security audit; 8 = SSO and Immich; 9 = optional AMP + playit.gg, Ollama, and a small catalog; 10 = main machine (OnlyOffice, Tailscale moved to STB 2)
- [stated] Suplemen 5 (hosting web and n8n, Bab 39-43) was requested as the next step; next supplement chapters start at Bab 44 (2026-10-19)
- [stated] asked to continue (2026-10-19) after Suplemen 5, so Suplemen 6 (Vaultwarden, AFFiNE, Nextcloud calendar, Bab 44-47) was written; next supplement chapters start at Bab 48; still no supplement tested yet
- [stated] asked to continue to Suplemen 7 (2026-10-20): done as Bab 48-52 (guest placement map, VM template, Proxmox Backup Server, Proxmox firewall, security audit); Suplemen 1-6 reissued as Revisi 2 with a placement box at the start of each install chapter; next chapters start at Bab 53 (Suplemen 8: SSO and Immich)
- [stated] asked (2026-10-20) to add one more docker, a self-hosted Spotify-like music app, then to merge all PDFs into one complete book: Navidrome added as Bab 53 (Suplemen 8, VM 127 music); complete book Buku_Panduan_Home_Server_Lab_Edisi3_Lengkap.pdf (Suplemen 1-8 merged, 154 pages) made; Edisi 2 PDF was not in the upload so Bab 1-24 are not included; next chapters start at Bab 54
- [stated] continuing (2026-10-21) from sumber_buku_lengkap_serah_terima.zip (sumber Suplemen 1-8 + buku gabungan) with Edisi 2 PDF uploaded; wants renumbering to VM 201 docker-core, 204 git, 205-211 services, 212 pbs, template 9100, IPs .20-.31; final merge = Edisi 2 as-is on pages 1-122, my part from page 123, plus a "Peta isi Edisi 2" page and PDF outline; must grep afterwards: no VM 120-130 or template 9000 of mine left, no duplicate IP vs Lampiran B Edisi 2; three decisions awaiting approval: Forgejo+Renovate to VM 204, skip Edisi 2 Bab 16 for Suplemen 6 Bab 47, Homepage port 80 to 3001 before Caddy
- [stated] approved all three decisions (Forgejo+Renovate to VM 204, skip Edisi 2 Bab 16 for Suplemen 6 Bab 47, Homepage port change before Caddy) and said: follow the source book as the newest plan (VM 201 = 2048 MB, backup job 201-211)
- [stated] approved next supplement (2026-10-22): SSO with Pocket ID (VM 213 sso .32) and Immich (VM 214 immich .33, 6144 MB, separate photo disk); main machine RAM is currently 16 (GB assumed), to be upgraded later
- [stated] (2026-10-22) said that after Suplemen 9 (Bab 54-56) the next step is running the guide from zero; the new plan and testing prompt are in [[rencana-lanjutan]]; next supplement chapters would start at Bab 57 (Suplemen 10, optional), after testing and revision
- [stated] asked (2026-10-24) to update the book first, before continuing the tests: done as a 3-page addendum "Lampiran E. Lembar Revisi 1" (halaman 301-303) appended to the end of the 300-page PDF, file Buku_Panduan_Home_Server_Lab_Edisi2_plus_Suplemen_1-9_Rev1.pdf (pages 1-300 unchanged); contains errata E1-E6, Kasus Nyata (VMware "invalid drive", VMnet0/bridged), NVMe/M.2 adapter note, interim test results; PDF bookmarks for Bagian 4-8 test sections corrected; full rebuild was not done because the source zip lacks Suplemen 9 and the renumbering was unfinished
- [stated] wants a dedicated GitHub repo for this project (2026-10-28); connector "GitHub Integration" is installed but gave no write tools in chat, so a home-server-lab.zip skeleton (README, .gitignore, docs, catatan, konfigurasi) was chosen, to be pushed manually with git
- [stated] wants the GitHub repo to be complete enough that Claude, Gemini or ChatGPT can read it and understand everything if chat or memory is lost (2026-10-28); repo home-server-lab.zip rebuilt with AGENTS.md, STATUS.md, data/*.yaml, docs/00-11, chapters Bab 1-56 as Markdown (Revisi 3: no VMware, no install-to-disk-first, machine = ThinkCentre M710q) and configs in konfigurasi/; still to push to GitHub manually

---

## 6. areas/rencana-lanjutan

- description: Rencana lanjutan Home Server Lab setelah pengujian dari nol dan revisi buku (Suplemen 1-9): fase A-E, urutan uji, Suplemen 10-11, roadmap lanjutan.
- aliases: rencana lanjutan, plan baru, plan setelah pengujian, fase pengujian
- updated: 2026-10-22

- [stated] (2026-10-22) next step: starts running the whole guide from zero (Edisi 2 + Suplemen 1-9), then testing and verification, then revisions; after that continues the project; asked to remember a new plan for this, see [[buku-panduan-suplemen]], [[home-server-roadmap]], [[proxmox-lab]]
- [stated] asked to remember: Fase A = execution and testing from zero, one chapter at a time, in book order (Edisi 2 network Bab 3, Proxmox, LXC/VM and template, STB AdGuard + Tailscale, DNS failover, Docker/Portainer; then Suplemen 1 security, 3 monitoring, 4 Caddy, Edisi 2 Git, Suplemen 5, 6, 7 PBS and firewall, 8 Navidrome, 9 SSO and Immich); each chapter gets a result (lulus / gagal / perlu revisi), exact error text, and the [BELUM PASTI] items checked
- [stated] asked to remember: Fase B = revision from the test log: errata list, answers for every [BELUM PASTI] item, then Revisi 3 PDFs (supplements and merged book on top of Edisi 2) in phases, not a total rewrite
- [stated] asked to remember: Fase C = Suplemen 10 (optional): CubeCoders AMP + playit.gg, Ollama (needs more RAM, wait for upgrade), Wake-on-LAN on the STB for the Proxmox machine, a small catalog of extra services; every service in its own VM/LXC with a placement box
- [stated] asked to remember: Fase D = main machine (Suplemen 11): RAM upgrade from the current 16 (GB assumed), clean Proxmox install and restore of lab backups, OnlyOffice, Tailscale subnet router moved to a second STB, update of the RAM profiles in Bab 56
- [stated] asked to remember: Fase E = roadmap projects from [[home-server-roadmap]]: NAS with TrueNAS/Nextcloud, printing from anywhere with TP-Link MR3020, backup server, browser code studio, LLM server (only if needed), second internet connection as failover, home electricity monitoring, solar panels, and the Home Assistant device book
- [stated] asked to remember: working rules for the testing sessions: one step at a time, confirm the result before the next step, record every deviation, never assume RAM / ID / IP values without checking Appendix B of Edisi 2 and Bab 48.3, commands without sudo (SSH then su -), server side and client side (Windows, Android, iPhone)
- [stated] asked to remember: the starter prompt for new testing sessions is the file PROMPT_SESI_PENGUJIAN.md (made 2026-10-22) with a test-log template; results go to a file CATATAN_PENGUJIAN.md kept by the user

---

## 7. areas/home-server-roadmap

- description: Daftar proyek home server ke depan: Home Assistant, NAS Nextcloud, hosting, print TP-Link MR3020, backup, code studio, LLM, internet failover, monitor listrik, panel surya
- aliases: catatan project kedepan, future projects, roadmap
- updated: 2026-10-25

- [stated] asked to remember: future project list for [[home-server]], in this order: 1) Home Assistant, 2) NAS with Nextcloud, 3) server hosting, 4) printing from anywhere using a TP-Link MR3020, 5) backup server, 6) a virtual code studio for coding from anywhere (corrected: not a VPS, something like VS Code in the browser), 7) LLM server (still only a possibility, depends on future needs), 8) a second internet connection besides IndiHome (maybe a modem) as failover so the network keeps running when IndiHome is down, 9) home electricity monitoring, 10) solar panels
- [stated] asked for a complete PDF book (categorized, with photos where available, with uses, pros and cons) of all devices that can connect to and be used with Home Assistant (2026-10-14)
- [stated] wants to add new installable features to the home server (2026-10-18): 1) web hosting, 2) n8n hosting, 3) Grafana & Prometheus / Uptime Kuma to monitor CPU temperature, RAM usage, SSD capacity and uptime of all home server services, 4) a personal Notion-like app for note-taking
- [stated] uploaded own analysis PDFs of three homelab YouTubers (Techno Tim, Hardware Haven, DB Tech) and asked to study them plus their videos to find more things to add to the home server (2026-10-18)
- [stated] also wants a personal calendar (Google Calendar replacement) and a personal doc/Microsoft Office-style suite running and storing data on the server, and wants all added features reachable from anywhere outside the home network (2026-10-18)
- [stated] decisions (2026-10-18): remote access only through Tailscale (for privacy), OnlyOffice as the office suite, AFFiNE as the Notion-like notes app
- [stated] Cloudflare Tunnel is wanted only as an additional option for web hosting (Tailscale stays the main remote access for all private services); wants Edisi 3 to make server security stronger and more assured; wants a complete conclusion and a detailed update plan before any writing starts (2026-10-18)
- [stated] apps/docker items of interest to install (2026-10-18): 1) CubeCoders AMP + playit.gg, 2) DNS service (Pi-hole + AdGuard Home), 3) local reverse proxy server with SSL certificates, 4) Homepage lab dashboard, 5) Proxmox Backup Server, 6) monitoring with Uptime Kuma / Beszel, 7) authentication (SSO), 8) Immich as Google Photos replacement, 9) Ollama, 10) Wake-on-LAN, possibly installed on the STB to power on the Proxmox machine
- [stated] wants the book to fully explain all three Proxmox install models (A in VM, B on real machine, C onto a disk first); Edisi 2 only explained the VM install fully, so B and C need detailed chapters (2026-10-18)
- [stated] phone is Android, but wants setup steps for both Android and iPhone in the book (2026-10-18)
- [stated] asked (2026-10-25) whether the real server can also host a VM that works as a gaming PC (GPU passthrough); idea only, no decision yet

## 8. Snapshot perangkat saat tiba, sebelum instalasi — 2026-10-31

Catatan pada bagian ini menggambarkan kondisi sebelum Proxmox dipasang. Progres terbaru ada di bagian 9.

- [stated] Mini PC Lenovo ThinkCentre M710q sudah tiba/tersedia. RAM awalnya 16 GB sebagai 2×8 GB; modul pertama diganti dengan 16 GB, sehingga total fisik yang diharapkan sekarang 24 GB (16+8). Kapasitas yang dikenali BIOS/OS dan hasil MemTest86 belum dikonfirmasi.
- [stated] SSD NVMe M.2 500 GB sudah dipasang di slot M.2 1. Proxmox belum diinstal; periksa isi dan partisi disk sebelum memilihnya sebagai target instalasi.


## 9. Progres server fisik setelah Proxmox dipasang — 2026-10-31

- [stated] Proxmox sudah berjalan pada Lenovo ThinkCentre M710q dan pembaruan melalui menu Proxmox selesai (2026-10-31). Setelah reboot, `uname -r` menunjukkan `7.0.14-26-pve`; `systemctl --failed` menunjukkan `0 loaded units listed`.
- [stated] RAM fisik terpasang adalah 16 GB + 8 GB; `free -h` pada Proxmox melaporkan 23 GiB total. BIOS dan MemTest86 belum diperiksa, jadi tes memori masih terbuka.
- [stated] `lsblk` menunjukkan NVMe `nvme0n1`, model Samsung MZALQ512HALU-000L2, 476.9G. Storage `local` dan `local-lvm` aktif; belum ada VM/container dibuat dan local-lvm masih kosong.
- [stated] Saat pembaruan pertama, host sementara memakai `192.168.0.200/24`, gateway `192.168.0.1`, sedangkan DNS lama menunjuk ke `192.168.88.253`. IP publik dapat diping tetapi DNS gagal. Setelah DNS host disesuaikan ke `192.168.0.1`, `getent hosts deb.debian.org` berhasil dan `apt-get -o Acquire::ForceIPv4=true update` sukses. Pengguna menegaskan jaringan `192.168.0.0/24` hanya sementara sampai server kembali ke MikroTik.
- [stated] Pengguna menemukan enclosure HDD single-bay lama, tetapi belum menguji fungsinya. Enclosure dan kedua HDD Seagate Surveillance 2 TB berada di rumah; pengguna akan mengujinya setelah tiba di rumah. Belum ada HDD terlihat pada Proxmox, belum ada backup, dan format disk belum boleh dilakukan sebelum identifikasi.
- [stated] Rencana selanjutnya: setelah kembali ke rumah, sambungkan server ke MikroTik dan pastikan alamat manajemen stabil; uji enclosure dan satu HDD; tentukan storage/backup; lalu buat VM/LXC dengan disk guest di local-lvm bila sesuai.
