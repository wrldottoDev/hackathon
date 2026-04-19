from __future__ import annotations

import httpx

from ..settings import ANALYTICS_API_URL, ANALYTICS_API_KEY


async def forward_phone_alert(payload: dict) -> bool:
    url = f"{ANALYTICS_API_URL}/api/external-intel/phone-alert"
    headers = {"X-API-Key": ANALYTICS_API_KEY, "Content-Type": "application/json"}
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.post(url, json=payload, headers=headers)
            return resp.status_code < 400
    except httpx.HTTPError:
        return False
