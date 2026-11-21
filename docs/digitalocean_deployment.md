# Deploying MediaCMS to a DigitalOcean Droplet

This guide deploys **this repository's** Docker Compose stack to a
DigitalOcean Droplet. The stack ships with a Tailscale sidecar (see
`docker-compose.yaml` and `deploy/docker/tailscale-serve/`), so the portal
is served over your tailnet at
`https://mediacms.<your-tailnet>.ts.net` with automatic HTTPS — and the
droplet exposes **no public web ports at all**. Only SSH is reachable from
the internet.

> If you want a classic public deployment (ports 80/443, Let's Encrypt),
> see [Alternative: public deployment](#alternative-public-deployment)
> at the end.

## 1. Overview

```text
tailnet device ──HTTPS──> Tailscale Serve (TLS termination, auto certs)
                              │
                              ▼ 127.0.0.1:80 (shared network namespace)
                          nginx + gunicorn (web container)
                              │
        ┌─────────────────────┼────────────────────┐
        ▼                     ▼                    ▼
   db (postgres)         redis             celery_worker / celery_beat
```

- The `tailscale` container joins your tailnet and terminates TLS on 443
  with a certificate it provisions and renews for the MagicDNS name.
- The `web` container shares the tailscale container's network namespace;
  nginx is reachable **only** through Tailscale Serve.
- Userspace networking (the image default) means there is no plain-HTTP
  path from the tailnet to the portal.

## 2. Prerequisites

- A DigitalOcean account with SSH keys configured
  ([docs](https://docs.digitalocean.com/products/droplets/how-to/add-ssh-keys/)).
- A Tailscale account. Enable **HTTPS certificates** for the tailnet if you
  haven't already ([docs](https://tailscale.com/kb/1153/enabling-https)) —
  Serve needs this to provision the certificate.
- A Tailscale **auth key**: create one at
  <https://login.tailscale.com/admin/settings/keys> as **reusable** and
  **non-ephemeral**, so the droplet keeps the same device identity across
  restarts.
- At least one device on your tailnet (laptop/phone) to browse the portal.

## 3. Provision the droplet

1. **Create → Droplets**. Under *OS → Marketplace tab*, choose the **Docker**
   image (Docker preinstalled on Ubuntu LTS). Alternatively install Docker
   yourself on a plain Ubuntu 24.04 image:
   `curl -fsSL https://get.docker.com | sh`
2. **Size**: transcoding video is CPU-bound. 2 vCPU / 4 GB RAM is a workable
   minimum for a personal portal; 4 vCPU / 8 GB is comfortable. Disk should
   be sized for your media library (uploads land in `media_files/` inside
   the repository checkout) — 80 GB is a reasonable start.
3. **Region**: pick one close to where you'll watch from; tailnet traffic
   goes device → droplet directly.
4. Add your SSH key, create the droplet, and note its public IP.

## 4. Lock down the droplet

Create a **Cloud Firewall** (Networking → Firewalls) and attach the droplet:

| Inbound | Protocol | Port | Sources |
|---|---|---|---|
| SSH | TCP | 22 | your IP (or `localhost` only — see below) |

That's the entire inbound ruleset. **Do not open 80 or 443** — all web
traffic rides the tailnet via the sidecar container, and SSH is the only
publicly reachable service.

Optional hardening: install Tailscale on the droplet host itself and use
Tailscale SSH for administration, then remove even the public SSH rule
(the DigitalOcean web console remains as break-glass access):

```sh
curl -fsSL https://tailscale.com/install.sh | sh
sudo tailscale up --ssh
```

## 5. Clone and configure

```sh
ssh root@<droplet-ip>
git clone https://github.com/greedychipmunk/mediacms.git ~/mediacms
cd ~/mediacms
cp .env.example .env
```

Edit `.env`:

```sh
TS_AUTHKEY=tskey-auth-...        # from step 2
FRONTEND_HOST=https://mediacms.YOUR-TAILNET.ts.net
```

Your tailnet's name is shown in the Tailscale admin console. The host name
`mediacms` matches the `hostname:` of the `tailscale` service in
`docker-compose.yaml` — change both together if you rename it.

Finally, set the initial admin password: in `docker-compose.yaml`, under
the `migrations` service, uncomment and set:

```yaml
      ADMIN_PASSWORD: 'choose-a-strong-password'
```

(If you skip this, `deploy/docker/prestart.sh` generates a random password
and prints it once in the migrations logs.)

## 6. Launch and verify

```sh
docker compose up -d
```

Check each layer:

```sh
docker compose ps                 # all services Up; tailscale shows (healthy)
docker compose logs tailscale     # joined the tailnet, serve config applied
docker compose exec tailscale tailscale serve status
```

Then open `https://mediacms.YOUR-TAILNET.ts.net` from any tailnet device.
Log in as the admin user (`admin` unless you changed `ADMIN_USER`) with the
password from step 5 — or recover the generated one:

```sh
docker compose logs migrations | grep "Created admin"
```

## 7. Where data lives

| What | Path | Notes |
|---|---|---|
| Uploaded media | `~/mediacms/media_files/` | `original/` + `encoded/`; grows with use |
| PostgreSQL data | `~/postgres_data/` | one level **above** the checkout (compose mounts `../postgres_data`) |
| Tailscale device identity | `tailscale-state` volume | keeps the same device across restarts |

`docker compose down` does **not** delete any of these.

## 8. Upgrades

Back up first (next section), then:

```sh
cd ~/mediacms
git pull
docker compose pull
docker compose down && docker compose up -d
```

**PostgreSQL caveat:** `docker compose pull` will happily move you to a new
PostgreSQL *major* version, and the data directory does not auto-upgrade
between majors. Check the `db` service image tag in `docker-compose.yaml`
before pulling; if the major version changes, dump and restore into a fresh
data directory and expect downtime.

## 9. Backups

```sh
# database
docker compose exec db pg_dump -U mediacms mediacms > mediacms-$(date +%F).sql

# media files (run from your workstation, or to attached storage)
rsync -a root@<droplet-ip>:mediacms/media_files/ /your/backup/dir/media_files/
```

DigitalOcean's droplet **Backups** feature (weekly full-droplet snapshots)
is a convenient safety net, but restores roll back *everything* at once —
keep the dump + rsync approach for granular recovery.

## 10. Troubleshooting

| Symptom | Check | Likely cause / fix |
|---|---|---|
| `tailscale` service unhealthy, portal unreachable | `docker compose logs tailscale` | Auth key expired, single-use, or ephemeral — mint a new reusable key, update `.env`, `docker compose up -d tailscale` |
| Portal loads but every form submission fails (CSRF errors) | `FRONTEND_HOST` in `.env` | Must be the exact `https://mediacms.<tailnet>.ts.net` URL — it drives `CSRF_TRUSTED_ORIGINS` |
| Certificate warnings | Tailscale admin console | HTTPS certificates not enabled for the tailnet (step 2) |
| Container keeps restarting | `docker compose logs <service>` | Check the service-specific log; `web` shares the tailscale netns, so nginx failures surface in `web` logs |

## Alternative: public deployment

This repository's compose stack is tailored to tailnet-private serving. If
you ever need a public deployment instead (ports 80/443 with Let's
Encrypt), compose variants for that ship in the [`docker-compose/`](../docker-compose/)
directory of this repository (`docker-compose-letsencrypt.yaml`,
`docker-compose-http-proxy.yaml`, `docker-compose-https-proxy.yaml`),
documented in [admins_docs.md §4](admins_docs.md). You would need to
restore the `web` service's `ports` publishing (removed in this fork in
favor of the Tailscale sidecar).
