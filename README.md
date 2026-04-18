# Pi Homelab

A self-hosted monitoring and network DNS stack running on a Raspberry Pi 4, fully reachable over Tailscale. Metrics are scraped by Prometheus, visualized in Grafana, and Tailnet DNS is filtered through Blocky.

## Stack

| Service | Role | Port (Tailnet) |
|---|---|---|
| Blocky | DNS with ad-blocking, DoT upstream to Quad9 | 53 |
| Prometheus | Metrics storage and scraping | internal |
| Grafana | Dashboards | 3000 |
| node_exporter | Host metrics | internal |
| cAdvisor | Container metrics | internal |
| Tailscale | Zero-trust network overlay | (host) |

## Setup

1. Clone and configure:

```bash
   git clone https://github.com/jglunn/homelab.git
   cd homelab
   cp .env.example .env
   # edit .env: set TS_IP, GRAFANA_ADMIN_PASSWORD, TZ
```

2. Install Tailscale on the host:

```bash
   curl -fsSL https://tailscale.com/install.sh | sh
   sudo tailscale up --ssh
   tailscale ip -4   # copy this into .env as TS_IP
```

3. Install Docker:

```bash
   curl -fsSL https://get.docker.com | sh
   sudo usermod -aG docker $USER
   # log out and back in
```

4. Launch:

```bash
   docker compose up -d
```

5. In the Tailscale admin console → **DNS**, add the Pi's Tailscale IP as a global nameserver and toggle **Override local DNS**.

## Access

- Grafana: `http://<tailscale-ip>:3000`
- Blocky metrics: internal only, scraped by Prometheus at `blocky:4000/metrics`
- Prometheus: internal only; query via Grafana

## Dashboards

Import the following by ID in Grafana → Dashboards → New → Import:

- **1860** — Node Exporter Full
- **14282** — cAdvisor
- **13768** — Blocky

## Screenshots
<img width="1573" height="821" alt="image" src="https://github.com/user-attachments/assets/cb118d45-cd39-478c-bd4c-b5d3676f4fef" />
<img width="1586" height="824" alt="image" src="https://github.com/user-attachments/assets/4c806e48-4139-4db5-b26f-4d3120cad6bc" />
<img width="996" height="166" alt="image" src="https://github.com/user-attachments/assets/d0a6e673-9315-4c0e-8046-7518d10aadb9" />


## License

MIT
