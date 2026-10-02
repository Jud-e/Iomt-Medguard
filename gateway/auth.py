"""
Zero-trust token authentication.

Every /ingest call must carry `Authorization: Bearer <token>` matching
GATEWAY_API_TOKEN. This is deliberately a simple shared-secret scheme, not
full OAuth — appropriate for the scope of this project (devices are
simulated, not real hardware with their own identity provider), while still
demonstrating the "API token authentication" requirement from the project
brief.
"""
import os

from fastapi import Header, HTTPException, status

GATEWAY_API_TOKEN = os.getenv("GATEWAY_API_TOKEN", "dev-shared-secret-change-me")


async def verify_token(authorization: str = Header(default=None)) -> bool:
    if authorization is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing Authorization header",
        )

    scheme, _, token = authorization.partition(" ")
    if scheme.lower() != "bearer" or token != GATEWAY_API_TOKEN:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing bearer token",
        )

    return True