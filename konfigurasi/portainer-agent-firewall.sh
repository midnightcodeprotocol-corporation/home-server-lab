#!/bin/sh
set -eu

PORTAINER_IP='192.168.88.105'
AGENT_PORT='9001'

tries=0
until iptables -nL DOCKER-USER >/dev/null 2>&1; do
  tries=$((tries + 1))
  if [ "$tries" -ge 30 ]; then
    echo 'DOCKER-USER chain not ready' >&2
    exit 1
  fi
  sleep 1
done

# Published IPv4 Docker traffic traverses DOCKER-USER; allow CT105 then drop others.
iptables -C DOCKER-USER -p tcp -s "$PORTAINER_IP" --dport "$AGENT_PORT" -j RETURN 2>/dev/null || iptables -I DOCKER-USER 1 -p tcp -s "$PORTAINER_IP" --dport "$AGENT_PORT" -j RETURN
iptables -C DOCKER-USER -p tcp --dport "$AGENT_PORT" -j DROP 2>/dev/null || iptables -I DOCKER-USER 2 -p tcp --dport "$AGENT_PORT" -j DROP

# Also filter host-proxy traffic in INPUT, including IPv6 listener traffic.
iptables -C INPUT -p tcp -s "$PORTAINER_IP" --dport "$AGENT_PORT" -j ACCEPT 2>/dev/null || iptables -I INPUT 1 -p tcp -s "$PORTAINER_IP" --dport "$AGENT_PORT" -j ACCEPT
iptables -C INPUT -p tcp --dport "$AGENT_PORT" -j DROP 2>/dev/null || iptables -I INPUT 2 -p tcp --dport "$AGENT_PORT" -j DROP
ip6tables -C INPUT -p tcp --dport "$AGENT_PORT" -j DROP 2>/dev/null || ip6tables -I INPUT 1 -p tcp --dport "$AGENT_PORT" -j DROP

echo 'Portainer Agent firewall rules applied.'
