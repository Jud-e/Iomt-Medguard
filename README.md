# MedGuard — IoMT & Health Data Pipeline Anomaly Detection

Real-time monitoring pipeline for IoMT (Internet of Medical Things) endpoints. Ingests
synthetic health data (Synthea) and network traffic, runs it through a zero-trust
gateway, scores it for anomalies with unsupervised ML, and surfaces alerts in a
dashboard.

## Prerequisites

- [Docker](https://docs.docker.com/get-docker/) + Docker Compose (bundled with Docker Desktop)
- ~4GB free RAM for the containers (Kafka + Zookeeper are the heaviest)
- Python 3.12+ if you want to run scripts locally outside the containers

## Project structure

```
iomt-medguard/
├── docker-compose.yml     # orchestrates every service below
├── gateway/                # FastAPI zero-trust API gateway
│   ├── Dockerfile
│   ├── requirements.txt
│   └── main.py
├── ingestion/               # Synthea configs, dataset loaders (WIP)
├── stream/                  # Kafka producer/consumer scripts (WIP)
├── ml/                       # Isolation Forest / Autoencoder models (WIP)
└── app/                      # MedGuard frontend dashboard (WIP)
```

## First-time setup

1. Clone the repo and `cd` into the project root:
   ```bash
   cd iomt-medguard
   ```
2. Build and start everything:
   ```bash
   docker compose up -d --build
   ```
   This pulls the Kafka/Zookeeper/Postgres/Kafka-UI images and builds the gateway
   image from `gateway/Dockerfile`. First run takes a few minutes; later runs are fast.
3. Confirm everything is healthy:
   ```bash
   docker compose ps
   ```
   You should see `zookeeper`, `kafka`, `kafka-ui`, `gateway`, and `iomt-db` all `Up`.

## Verifying it's working

- Gateway health check: open `http://localhost:8000/health` → should return
  `{"status": "gateway is up"}`
- Kafka UI: open `http://localhost:8085` → should show the local cluster with any
  topics that have been created
- Postgres: connect with any client to `localhost:5432`, user `medguard`, password
  `medguard_dev`, database `medguard`

## Everyday commands

| Command | What it does |
|---|---|
| `docker compose up -d` | Start everything in the background |
| `docker compose up -d --build` | Rebuild images first (use after Dockerfile/requirements changes) |
| `docker compose ps` | List running services and their health |
| `docker compose logs -f <service>` | Tail logs, e.g. `docker compose logs -f gateway` |
| `docker compose restart <service>` | Restart one service without touching the rest |
| `docker compose down` | Stop and remove all containers |
| `docker compose down -v` | Same, plus wipe volumes (fresh Postgres/Kafka data) |

## Editing the gateway

The `gateway/` folder is mounted into the container as a live volume, and the
service runs `uvicorn --reload`. That means editing `gateway/main.py` on your
machine updates the running container automatically — no rebuild needed for plain
code changes. You only need `--build` again if you change
`gateway/requirements.txt` or the `Dockerfile`.

## Troubleshooting

- **Gateway container exits immediately** → `docker compose logs gateway` almost
  always shows the Python traceback causing it.
- **Kafka won't come up / gateway can't connect** → give Zookeeper a few extra
  seconds to start before Kafka; check `docker compose logs kafka`.
- **Port already in use** → something else on your machine is using 8000, 8085,
  5432, 2181, or 29092. Either stop that process or change the left-hand side of
  the port mapping in `docker-compose.yml` (e.g. `"8001:8000"`).
- **Changes to `main.py` not showing up** → confirm the container is actually
  running with `--reload` (it is, by default, via the `command:` override in
  `docker-compose.yml`) and that you're editing the file in `gateway/` on your host.

## Team

Jude & David — Douglas College, Emerging Technology (CIS)
Always check the latest branch before pulling changes
