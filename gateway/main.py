"""
MedGuard Zero-Trust API Gateway.

Two layers of defense before anything reaches Kafka:
1. verify_token (auth.py)  — rejects requests without a valid bearer token (401)
2. TelemetryPayload (schemas.py) — rejects structurally invalid/tampered
   payloads via Pydantic, enforced automatically by FastAPI (422)

Only messages that pass both reach publish() -> Kafka.
"""
import os
from datetime import datetime, timezone

from fastapi import Depends, FastAPI, status

from auth import verify_token
from kafka_producer import publish
from schemas import TelemetryPayload
from vulnerability_rules import REMEDIATION_TIPS, check_config_vulnerabilities

app = FastAPI(title="MedGuard Zero-Trust Gateway")

TOPIC_RAW = os.getenv("TOPIC_TELEMETRY_RAW", "iomt.telemetry.raw")


@app.get("/health")
def health():
    return {"status": "gateway is up"}


@app.post("/ingest", status_code=status.HTTP_201_CREATED)
def ingest(payload: TelemetryPayload, _authorized: bool = Depends(verify_token)):
    message = payload.model_dump(mode="json")

    vulnerability_flags = check_config_vulnerabilities(payload.config)
    if vulnerability_flags:
        message["vulnerability_flags"] = vulnerability_flags
        message["remediation_tips"] = [REMEDIATION_TIPS[f] for f in vulnerability_flags]

    message["ingested_at"] = datetime.now(timezone.utc).isoformat()

    publish(TOPIC_RAW, key=payload.device_id, value=message)

    return {
        "message_id": payload.message_id,
        "status": "accepted",
        "vulnerability_flags": vulnerability_flags,
    }