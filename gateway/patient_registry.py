"""
Loads patient context (currently hand-authored sample data standing in for
real Synthea output — see data/patients.json) and exposes a lookup by
patient_id, so the gateway can cross-reference a device reading against
what that patient is actually prescribed.

This is intentionally a small, static JSON file read once at startup, not a
database — appropriate for the project's current scope. If this grows
beyond a handful of patients, move it into Postgres instead.
"""
import json
import os
from functools import lru_cache
from typing import Optional

REGISTRY_PATH = os.getenv("PATIENT_REGISTRY_PATH", "/app/data/patients.json")


@lru_cache
def _load_registry() -> dict:
    with open(REGISTRY_PATH) as f:
        data = json.load(f)
    return {p["patient_id"]: p for p in data["patients"]}


def get_patient(patient_id: str) -> Optional[dict]:
    registry = _load_registry()
    return registry.get(patient_id)