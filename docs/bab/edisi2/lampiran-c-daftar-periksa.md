# Lampiran C. Daftar Periksa

• RAM terpasang sesuai rencana dan lulus MemTest86 (Bab 27.1).  
• BIOS diatur: VT-x, VT-d, UEFI, Secure Boot mati, AHCI, WoL, After Power Loss (Bab 27.5).  
• ISO diverifikasi dan USB bootable dibuat (Bab 6.3).  
• Kabel LAN dari mesin ke MikroTik, monitor dan keyboard terpasang.  
• HDD 2 TB dilepas selama instalasi (hindari salah pilih disk).  
C.2 Setelah Proxmox hidup  
• Web terbuka di https://192.168.88.10:8006, login berhasil.  
• pveversion, /dev/kvm, dan jumlah vmx lebih dari 0.  
• Ping gateway, 8.8.8.8, dan deb.debian.org berhasil.  
• Repository enterprise mati, no-subscription aktif, upgrade selesai.  
• sensors dan smartctl -H /dev/nvme0 menampilkan data.  
C.3 Sebelum instal ulang atau perubahan besar  
• Semua VM/CT di-backup dan salinannya ada di luar Proxmox.  
• pve-host-config.tgz tersimpan.  
• Lampiran B terisi lengkap.  
• Password dan kunci (age.agekey, token, password) tersimpan di password manager.  
• Static lease MikroTik dan DNS rewrites AdGuard dicatat atau diekspor.
