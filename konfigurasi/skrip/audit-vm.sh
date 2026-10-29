#!/bin/bash
# Audit baca-saja untuk VM (Bab 52.2). Mencetak temuan, tidak mengubah apa pun.
echo "== Host: $(hostname) | $(date '+%F %T')"
echo "== Port mendengarkan selain loopback"
ss -tulnH | awk '$5 !~ /^127\.|^\[::1\]/ {print $1, $5}'
if command -v docker >/dev/null; then
  echo "== Port Docker yang dipublikasikan"
  docker ps --format '{{.Names}}: {{.Ports}}' | grep -- '->'
  echo "== Kontainer privileged (idealnya kosong)"
  docker ps -q | xargs -r docker inspect \
    --format '{{.Name}} {{.HostConfig.Privileged}}' | grep true
  echo "== Kontainer yang memasang docker.sock"
  docker ps -q | xargs -r docker inspect \
    --format '{{.Name}} {{range .Mounts}}{{.Source}} {{end}}' | grep docker.sock
fi
echo "== Berkas .env terbaca orang lain (idealnya kosong)"
find /opt/stacks -maxdepth 2 -name .env -perm /077 2>/dev/null
echo "== Pengaturan SSH"
sshd -T 2>/dev/null | grep -E '^(permitrootlogin|passwordauthentication) '
echo "== Pembaruan otomatis"
systemctl is-enabled unattended-upgrades 2>/dev/null || echo "tidak aktif"
echo "== Jumlah paket menunggu pembaruan"
apt list --upgradable 2>/dev/null | grep -vc '^Listing'
