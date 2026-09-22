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
