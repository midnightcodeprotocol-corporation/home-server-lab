#!/bin/bash
# Ganti profil pemakaian di host Proxmox (Bab 56.3). Pakai: profil.sh harian|kerja|foto|backup|belajar
ALL="201 202 203 204 205 206 207 210 212 213 214"
case "${1:-}" in
  harian)  ON="201 202 205 207 213" ;;
  kerja)   ON="201 202 205 207 213 204 206" ;;
  foto)    ON="201 202 205 213 214" ;;
  backup)  ON="201 202 205 207 213 212" ;;
  belajar) ON="201 203 204 205 213" ;;
  *) echo "pakai: $0 harian|kerja|foto|backup|belajar"; exit 1 ;;
esac
if pgrep -f vzdump >/dev/null; then
  echo "vzdump masih berjalan; ditunda"; exit 1
fi
for id in $ALL; do
  case " $ON " in *" $id "*) continue ;; esac
  if qm status "$id" 2>/dev/null | grep -q running; then
    qm shutdown "$id" --timeout 120
  fi
done
for id in $ON; do
  if ! qm status "$id" 2>/dev/null | grep -q running; then
    qm start "$id"
  fi
done
qm list
