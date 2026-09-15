# David's setup — Stream + ML side

Jude has the shared infra (Docker Compose: Kafka, Zookeeper, Postgres, gateway)
already running and pushed to the repo. You don't need to touch
`docker-compose.yml` or `gateway/` — your work happens in `stream/` and `ml/`.

## 1. Get the repo and shared infra running

```bash
git clone <repo-url>
cd iomt-medguard
cp .env.example .env          # fill in any values if needed, defaults are fine for local dev
docker compose up -d --build  # starts Kafka, Zookeeper, Postgres, the gateway
docker compose ps             # confirm everything shows "Up"
```

Check `http://localhost:8085` (Kafka UI) — you should see the same cluster Jude
sees. This is the shared message bus your consumer will read from.

## 2. Set up your local Python environment

Your scripts (`stream/consumer.py`, `ml/train_isolation_forest.py`) run directly
on your machine, not inside a container — that makes it easier to iterate on
model training without rebuilding an image every time.

```bash
python -m venv venv
venv\Scripts\activate          # Windows
pip install -r stream/requirements.txt
```

## 3. What's stubbed out for you

- **`stream/consumer.py`** — connects to Kafka, listens on the raw telemetry
  topic, has placeholders for preprocessing and scoring, publishes to the
  scored topic. Run it with:
  ```bash
  python stream/consumer.py
  ```
  It won't do anything useful yet because nothing is publishing to the raw
  topic — that's Jude's gateway `/ingest` endpoint, still being built. You can
  test independently by manually producing a fake message to
  `iomt.telemetry.raw` via Kafka UI's "Produce Message" button.

- **`ml/train_isolation_forest.py`** — skeleton for training Isolation Forest
  on the CICIDS2017/ECU IoMT dataset. Has a `score_to_risk()` function stubbed
  for turning the model's raw output into the 0-100 risk score the project
  spec calls for.

## 4. Your Week 1-5 tasks (per the project timeline)

- Week 1-3: get familiar with the CICIDS2017/ECU IoMT dataset structure,
  identify which columns/features are usable for anomaly detection
- Week 4: build the actual preprocessing logic in `consumer.py`
- Week 5: train Isolation Forest, then Autoencoder; wire up real risk scoring

## Questions / blockers

Kafka connection issues, topic naming, or anything about the gateway's output
format — ping Jude. Shared config (topic names, ports) lives in `.env.example`
so we don't drift out of sync.