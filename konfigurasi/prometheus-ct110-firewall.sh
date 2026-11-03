#!/bin/sh
set -eu

PORTAINER_IP='192.168.88.105'
GRAFANA_CT_IP='192.168.88.20'
GRAFANA_NEXT_CT_IP='192.168.88.108'
AGENT_PORT='9001'
PROMETHEUS_PORT='9090'

tries=0
until iptables -nL DOCKER-USER >/dev/null 2>&1; do
  tries=$((tries + 1))
  if [ "$tries" -ge 30 ]; then
    echo 'DOCKER-USER chain not ready' >&2
    exit 1
  fi
  sleep 1
done

# Agent: allow Portainer CT105 and reject all other sources.
iptables -C DOCKER-USER -p tcp -s "$PORTAINER_IP" --dport "$AGENT_PORT" -j RETURN 2>/dev/null || iptables -I DOCKER-USER 1 -p tcp -s "$PORTAINER_IP" --dport "$AGENT_PORT" -j RETURN
iptables -C DOCKER-USER -p tcp --dport "$AGENT_PORT" -j DROP 2>/dev/null || iptables -I DOCKER-USER 2 -p tcp --dport "$AGENT_PORT" -j DROP

# Prometheus API: allow only the old CT104 rollback instance and current Grafana CT111.
iptables -C DOCKER-USER -p tcp -s "$GRAFANA_CT_IP" --dport "$PROMETHEUS_PORT" -j RETURN 2>/dev/null || iptables -I DOCKER-USER 1 -p tcp -s "$GRAFANA_CT_IP" --dport "$PROMETHEUS_PORT" -j RETURN
iptables -C DOCKER-USER -p tcp -s "$GRAFANA_NEXT_CT_IP" --dport "$PROMETHEUS_PORT" -j RETURN 2>/dev/null || iptables -I DOCKER-USER 1 -p tcp -s "$GRAFANA_NEXT_CT_IP" --dport "$PROMETHEUS_PORT" -j RETURN
iptables -C DOCKER-USER -p tcp --dport "$PROMETHEUS_PORT" -j DROP 2>/dev/null || iptables -I DOCKER-USER 2 -p tcp --dport "$PROMETHEUS_PORT" -j DROP

# Also filter host-proxy traffic to the Agent, including IPv6 listener traffic.
iptables -C INPUT -p tcp -s "$PORTAINER_IP" --dport "$AGENT_PORT" -j ACCEPT 2>/dev/null || iptables -I INPUT 1 -p tcp -s "$PORTAINER_IP" --dport "$AGENT_PORT" -j ACCEPT
iptables -C INPUT -p tcp --dport "$AGENT_PORT" -j DROP 2>/dev/null || iptables -I INPUT 2 -p tcp --dport "$AGENT_PORT" -j DROP
ip6tables -C INPUT -p tcp --dport "$AGENT_PORT" -j DROP 2>/dev/null || ip6tables -I INPUT 1 -p tcp --dport "$AGENT_PORT" -j DROP

echo 'Portainer Agent and Prometheus firewall rules applied.'
