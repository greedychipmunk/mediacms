# Tailscale Serve configuration

`serve.json` is consumed by the `tailscale` service in `docker-compose.yaml`
(`TS_SERVE_CONFIG=/config/serve.json`, with this directory mounted at
`/config`). It makes MediaCMS available at
`https://mediacms.<your-tailnet>.ts.net`:

- `TCP 443 -> HTTPS: true` — Tailscale terminates TLS on port 443 with a
  certificate it provisions and renews automatically for the MagicDNS name.
- `Web / -> Proxy http://127.0.0.1:80` — decrypted traffic is proxied to
  nginx inside the shared network namespace of the `tailscale` service.
- `AllowFunnel: false` — the portal stays private to the tailnet; it is
  never exposed to the public internet.

`${TS_CERT_DOMAIN}` is substituted by the Tailscale container at startup
with this node's full MagicDNS name, so the file never needs editing.
Because it is a plain JSON file (not inlined in the compose file), a single
`$` is correct — Docker Compose never performs variable substitution here.

The directory is mounted as a whole (not the individual file) so the
container detects configuration changes.
