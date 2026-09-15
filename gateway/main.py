from fastapi import FastAPI

app = FastAPI(title="MedGuard Zero-Trust Gateway")


@app.get("/health")
def health():
    return {"status": "gateway is up"}


# TODO Week 1-2:
# - POST /ingest endpoint that accepts device telemetry
# - Token auth dependency (require Authorization header)
# - JSON schema validation (pydantic model) before publishing to Kafka