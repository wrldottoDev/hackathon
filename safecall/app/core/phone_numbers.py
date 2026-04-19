from __future__ import annotations

import hashlib
import re

SERVICE_PROVIDERS = (
    "AuroraNet",
    "Cima Mobile",
    "PuraLinea",
)


def normalize_cr_phone_number(value: str) -> str:
    digits = re.sub(r"\D", "", value or "")
    if not digits:
        return ""

    if digits.startswith("506") and len(digits) == 11:
        return f"+{digits}"

    if len(digits) == 8 and digits.startswith("8"):
        return f"+506{digits}"

    return f"+{digits}" if value.strip().startswith("+") else digits


def pick_service_provider(number: str) -> str:
    normalized = normalize_cr_phone_number(number)
    if not normalized:
        return SERVICE_PROVIDERS[0]

    digest = hashlib.sha256(normalized.encode()).digest()
    return SERVICE_PROVIDERS[digest[0] % len(SERVICE_PROVIDERS)]
