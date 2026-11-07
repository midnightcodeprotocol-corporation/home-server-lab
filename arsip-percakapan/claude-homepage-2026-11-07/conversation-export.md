# Homepage dashboard setup - conversation export

> Condensed, sanitized export of a chat between me and Claude (Anthropic) while
> building this dashboard. It is a structured summary, not a word-for-word
> transcript. Secrets (API keys, tokens, passwords) are deliberately left out.
> Widget parameters were partly verified against the official Homepage docs and
> partly written from memory, so double-check them at <https://gethomepage.dev/widgets/>
> if a widget misbehaves after an upgrade.

## Environment

| Item | Value |
|---|---|
| Dashboard | Homepage `ghcr.io/gethomepage/homepage:v2.7.0`, own CT (`192.168.88.110:3000`) |
| Compose location | `/opt/stacks/homepage` (config in `./config`) |
| Hypervisor | Proxmox VE (`192.168.88.10`), Proxmox Backup Server (`192.168.88.30`) |
| Router | MikroTik RB750GL, RouterOS **6.49.23** |
| Internet receiver | TP-Link TL-WR840N (`192.168.0.1`, IndiHome) |
| Access point | TP-Link TL-WR842N (`192.168.88.2`) |
| DNS | AdGuard Home on STB (`.3`) and CT101 (`.11`) |
| Media | Jellyfin **12.4.0** (`.111:8096`) |
| Every app | Runs in its own separate CT with its own IP |

## Timeline

### 1. Initial services.yaml
- Merged the new application table into the existing group structure.
- Rules used: spaces only (no tabs), lowercase `icon:` names from Dashboard Icons, groups Network / Management / Monitoring / Apps / Automation / Dashboard.
- Added: Portainer (legacy), Prometheus, Home Assistant Observer; MikroTik link changed to WebFig.

### 2. Enriching the dashboard
Four areas: status indicators (`siteMonitor`), per-service widgets, header widgets (`widgets.yaml`), and appearance (`settings.yaml`). Credentials go in `.env` as `HOMEPAGE_VAR_*` and are referenced as `"{{HOMEPAGE_VAR_NAME}}"`.

### 3. Finding the compose file
```bash
docker inspect homepage --format '{{ index .Config.Labels "com.docker.compose.project.working_dir" }}'
```
Result: `/opt/stacks/homepage`. Added `env_file: - .env` to the compose file.

### 4. Phase 1 and 2 rollout
- Phase 1: icons, new services, `siteMonitor`, `settings.yaml` layout. Found that `settings.yaml` listed a group (`Server`) that did not exist in `services.yaml`. Layout group names must match exactly.
- Phase 2: widgets one at a time, starting with AdGuard. `.env` was secured with `chmod 600` and the container recreated with `docker compose up -d`.
- All commands run inside the Homepage CT, not on the Proxmox host.

## Troubleshooting log (the useful part)

### Jellyfin widget errors
| Symptom | Cause | Fix |
|---|---|---|
| `Unexpected end of JSON input` | Jellyfin answered 401 with an empty body | Fix the API key |
| `401` with `X-Emby-Token` header, `200` with `Authorization: MediaBrowser Token="..."` | Jellyfin 12.x rejects the old header | Use a `customapi` widget with the new header |
| Log lines `404 calling /emby/Items/Counts?api_key=...` | Built-in `jellyfin` widget calls the removed `/emby` routes | Replace with `customapi` |
| `401` again after the key was recreated | `.env` had the new key but the container still held the old one (`restart` does not reread `.env`) | `docker compose up -d` |

Compare key in `.env` with key in the container without printing it:
```bash
grep '^HOMEPAGE_VAR_JELLYFIN_KEY=' .env | cut -d= -f2- | tr -d '\n' | sha256sum | cut -c1-8
docker exec homepage sh -c 'printf %s "$HOMEPAGE_VAR_JELLYFIN_KEY" | sha256sum | cut -c1-8'
```
Working widget:
```yaml
widget:
  type: customapi
  url: http://192.168.88.111:8096/Items/Counts
  method: GET
  headers:
    Authorization: 'MediaBrowser Token="{{HOMEPAGE_VAR_JELLYFIN_KEY}}"'
  mappings:
    - field: MovieCount
      label: Movies
```
Note: the built-in widget put the API key in the URL, so it ended up in the logs. That key had to be rotated. Always redact `api_key=` before sharing logs.

### Uptime Kuma widget errors
- Error was HTML (`Unexpected token '<'`) on both `status-page` endpoints.
- `curl` to `/api/status-page/homelab` returned valid JSON, so the server was healthy.
- Cause 1: `slug: /status/homelab`. The slug must be only `homelab`.
- Cause 2: the status page had no monitors (`heartbeatList` was empty). Add monitors and press Save.

### Speedtest Tracker widget error
- Error returned the Filament **login page** HTML.
- Speedtest Tracker 1.x needs `version: 2` and an API token (`key`). Create the token under the account menu -> API Tokens, then:
```bash
curl -s -H "Authorization: Bearer TOKEN" -H "Accept: application/json" http://192.168.88.115:8765/api/v1/results/latest | head -c 300
```

### MikroTik widget
- The Homepage MikroTik widget needs the **REST API (RouterOS v7)**.
- RB750GL runs RouterOS 6.49.23 (64 MB RAM), so no widget. Decision: do not upgrade to v7 just for a widget.
- Alternatives: ICMP ping monitor in Uptime Kuma, or SNMP via Prometheus `snmp_exporter` and Grafana.

### Self-signed certificates
Proxmox, PBS, Portainer use self-signed certificates. Widgets for them fail unless the container sets `NODE_TLS_REJECT_UNAUTHORIZED: "0"` (commented out in `compose.yaml`). Side effect: certificate verification is disabled for all outgoing connections of Homepage. LAN use only.

### Prometheus browser access (still open)
Diagnose from the Prometheus CT:
```bash
ss -tlnp | grep 9090          # 127.0.0.1 = localhost only, 0.0.0.0 = open
docker ps --format '{{.Names}} {{.Ports}}'
```
Then check Proxmox firewall, UFW, and MikroTik firewall rules. Prometheus has no built-in login, so allow only the PC, Grafana and Homepage IPs.

## Widget credentials cheat sheet

| Service | Where to create it | `.env` variable |
|---|---|---|
| Proxmox | Datacenter -> Permissions -> user + API token, role PVEAuditor on `/` | `HOMEPAGE_VAR_PVE_USER`, `HOMEPAGE_VAR_PVE_SECRET` |
| PBS | Access Control -> user + token, role Audit on `/` | `HOMEPAGE_VAR_PBS_USER`, `HOMEPAGE_VAR_PBS_SECRET` |
| Portainer | My account -> Access tokens | `HOMEPAGE_VAR_PORTAINER_KEY` |
| Immich | Account Settings -> API Keys | `HOMEPAGE_VAR_IMMICH_KEY` |
| Home Assistant | Profile -> Long-lived access tokens | `HOMEPAGE_VAR_HA_TOKEN` |
| Grafana | Dedicated Viewer user | `HOMEPAGE_VAR_GRAFANA_USER/PASS` |
| Gotify | Client token (not app token) | `HOMEPAGE_VAR_GOTIFY_KEY` |
| qBittorrent | WebUI login | `HOMEPAGE_VAR_QBIT_USER/PASS` |
| Speedtest Tracker | Account menu -> API Tokens | `HOMEPAGE_VAR_SPEEDTEST_KEY` |
| Beszel | Widget needs a superuser, so intentionally skipped | - |
| Nextcloud | Needs a server-side token via `occ`, skipped for now | - |

## Design decisions
- English labels everywhere; cyberpunk theme (neon cyan/magenta grid, scanlines, glow) in `custom.css`. Purely cosmetic, empty the file to revert.
- Group icons via `mdi-*` in `settings.yaml`. Group names in `services.yaml` and `settings.yaml` must stay identical.
- No inline secrets; every credential comes from `.env`.
- Widgets for services without credentials yet are written but commented out.

## Lessons learned
1. After any `.env` change use `docker compose up -d`; `restart` keeps the old environment.
2. Run diagnostics from the Homepage CT, because that is the network path the widgets use.
3. `siteMonitor` and widgets only fetch when the dashboard is open in a browser, so empty logs can just mean nobody was looking.
4. Compare secrets by hash, never paste them into chats or logs.
5. HTML in an API error nearly always means a wrong path/slug or missing authentication.

## Still open
- [ ] Open Prometheus access, then enable its `siteMonitor` and widget.
- [ ] Create the Speedtest Tracker API token and fill `HOMEPAGE_VAR_SPEEDTEST_KEY`.
- [ ] Enable Proxmox / PBS / Portainer / Immich / Home Assistant widgets one at a time.
- [ ] Rotate the Jellyfin API key that appeared in logs earlier.
- [ ] Optional: SNMP monitoring for the MikroTik via Prometheus.
