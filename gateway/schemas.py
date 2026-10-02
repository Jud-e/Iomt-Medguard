"""
Zero-trust schema definitions for incoming IoMT telemetry.

Design decision: `extra="forbid"` (inherited by every subclass from
TelemetryCommon) means any field not explicitly declared here gets rejected
with a 422 before it ever reaches the ingest() function body. This is what
actually enforces "strict JSON schema payload validation" from the project
brief — an injected/unexpected field (e.g. a payload-tampering attack) is
caught structurally, at the schema layer, before it can reach Kafka.

Clinically/behaviorally anomalous-but-well-formed values (e.g. an
impossible heart rate) are intentionally allowed through by the numeric
bounds below — catching those is the ML model's job downstream, not the
gateway's. The gateway's job is structural validity, not behavioral
judgment.
"""
from datetime import datetime
from typing import Annotated, Literal, Optional, Union

from pydantic import BaseModel, ConfigDict, Field


class DeviceConfig(BaseModel):
    """Reported device configuration state, used for vulnerability checks
    (see vulnerability_rules.py) — separate from behavioral anomaly detection."""
    model_config = ConfigDict(extra="forbid")

    auto_lock_enabled: bool
    default_credentials_changed: bool
    firmware_up_to_date: bool
    tls_enabled: bool


class TelemetryCommon(BaseModel):
    model_config = ConfigDict(extra="forbid")

    message_id: str
    device_id: str
    unit: str
    timestamp: datetime
    packet_size_bytes: int = Field(ge=0, le=65535)
    request_rate_per_min: float = Field(ge=0)
    config: Optional[DeviceConfig] = None


class InfusionPumpTelemetry(TelemetryCommon):
    device_type: Literal["infusion_pump"]
    infusion_rate_ml_per_hr: float = Field(ge=0, le=5000)
    occlusion_pressure_mmHg: float = Field(ge=0, le=500)
    battery_pct: int = Field(ge=0, le=100)


class CardiacMonitorTelemetry(TelemetryCommon):
    device_type: Literal["cardiac_monitor"]
    heart_rate_bpm: int = Field(ge=0, le=400)
    spo2_pct: int = Field(ge=0, le=100)
    systolic_bp_mmHg: int = Field(ge=0, le=300)
    diastolic_bp_mmHg: int = Field(ge=0, le=200)


class PulseOximeterTelemetry(TelemetryCommon):
    device_type: Literal["pulse_oximeter"]
    spo2_pct: int = Field(ge=0, le=100)
    pulse_bpm: int = Field(ge=0, le=400)


TelemetryPayload = Annotated[
    Union[InfusionPumpTelemetry, CardiacMonitorTelemetry, PulseOximeterTelemetry],
    Field(discriminator="device_type"),
]