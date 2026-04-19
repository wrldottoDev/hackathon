import os
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parents[2]
BACKEND_DIR = Path(__file__).resolve().parents[1]
DEFAULT_BANK_REGISTRY = {
    "BKA": "http://127.0.0.1:8001",
    "BKB": "http://127.0.0.1:8002",
    "BKC": "http://127.0.0.1:8004",
}


def _resolve_database_url() -> str:
    explicit_url = os.getenv("DATABASE_URL")
    if explicit_url:
        return explicit_url
    raw_path = os.getenv("BANK_DB_PATH", "banco_a/app/banco_a.db")
    path = Path(raw_path)
    if not path.is_absolute():
        path = ROOT_DIR / path
    return f"sqlite:///{path.resolve()}"


def _parse_allowed_origins() -> list[str]:
    raw_origins = os.getenv("BANK_ALLOWED_ORIGINS")
    if raw_origins:
        return [origin.strip() for origin in raw_origins.split(",") if origin.strip()]

    return [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:5174",
        "http://127.0.0.1:5174",
        "http://localhost:5175",
        "http://127.0.0.1:5175",
        "http://localhost:5176",
        "http://127.0.0.1:5176",
        "http://localhost:4173",
        "http://127.0.0.1:4173",
        "http://localhost:4174",
        "http://127.0.0.1:4174",
        "http://localhost:4175",
        "http://127.0.0.1:4175",
        "http://localhost:4176",
        "http://127.0.0.1:4176",
    ]


def _parse_bank_registry() -> dict[str, str]:
    registry = DEFAULT_BANK_REGISTRY.copy()
    raw_registry = os.getenv("FLOWLENS_BANK_REGISTRY")
    if not raw_registry:
        return registry

    for item in raw_registry.split(","):
        entry = item.strip()
        if not entry or "=" not in entry:
            continue
        bank_code, api_url = entry.split("=", 1)
        bank_code = bank_code.strip().upper()
        api_url = api_url.strip().rstrip("/")
        if bank_code and api_url:
            registry[bank_code] = api_url

    return registry


BANK_ID = os.getenv("BANK_ID", "banco_a")
BANK_NAME = os.getenv("BANK_NAME", "Banco A")
BANK_CODE = os.getenv("BANK_CODE", "BKA")
DATABASE_URL = _resolve_database_url()
SECRET_KEY = os.getenv("BANK_SECRET_KEY", "banco-a-dev-secret-key-change-me-2026")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "720"))
ALLOWED_ORIGINS = _parse_allowed_origins()
BANK_REGISTRY = _parse_bank_registry()
PUBLIC_API_URL = os.getenv(
    "BANK_PUBLIC_API_URL",
    BANK_REGISTRY.get(BANK_CODE, "http://127.0.0.1:8001"),
).rstrip("/")
SERVICE_TOKEN = os.getenv("FLOWLENS_SERVICE_TOKEN", "flowlens-service-token-dev")
INTERBANK_TIMEOUT_SECONDS = float(os.getenv("INTERBANK_TIMEOUT_SECONDS", "5"))
TRANSACTION_EXPORT_LIMIT = int(os.getenv("TRANSACTION_EXPORT_LIMIT", "1000"))
