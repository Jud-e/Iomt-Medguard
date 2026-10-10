"""
Checks a device reading against the assigned patient's actual prescription
— a smarter signal than a generic "is this value in range" check, since a
rate can be perfectly plausible in general and still be wrong for this
specific patient.

Currently only infusion rate is checked, since that's the one vital with a
clear prescribed value in the sample patient data. Deliberately narrow in
scope, matching the project's Option 2 decision (patient context informing
checks already in the pipeline, not a full second FHIR ingestion system).
"""
from typing import Optional

# How far a reading can drift from the prescribed rate before it's flagged.
# A real clinical system would tune this per-drug/per-patient; a flat
# tolerance is an intentional simplification for this project's scope.
INFUSION_RATE_TOLERANCE_ML_PER_HR = 15


def check_prescription_mismatch(patient: Optional[dict], device_type: str, message: dict) -> list[str]:
    if patient is None:
        return []

    flags = []

    if device_type == "infusion_pump":
        prescribed = patient.get("prescribed_infusion_rate_ml_per_hr")
        actual = message.get("infusion_rate_ml_per_hr")
        if prescribed is not None and actual is not None:
            if abs(actual - prescribed) > INFUSION_RATE_TOLERANCE_ML_PER_HR:
                flags.append("infusion_rate_mismatch")

    return flags


PRESCRIPTION_REMEDIATION_TIPS = {
    "infusion_rate_mismatch": "This device's infusion rate does not match the patient's prescribed rate — verify the pump settings against the current order before continuing.",
}