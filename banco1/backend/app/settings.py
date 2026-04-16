import os
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parents[2]
BACKEND_DIR = Path(__file__).resolve().parents[1]


def _resolve_database_path() -> Path:
    raw_path = os.getenv("BANK_DB_PATH", "backend/bank.db")
    path = Path(raw_path)
    if not path.is_absolute():
        path = ROOT_DIR / path
    return path.resolve()


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


BANK_ID = os.getenv("BANK_ID", "banco1")
BANK_NAME = os.getenv("BANK_NAME", "Banco 1")
DATABASE_PATH = _resolve_database_path()
DATABASE_URL = f"sqlite:///{DATABASE_PATH}"
SECRET_KEY = os.getenv(
    "BANK_SECRET_KEY",
    os.getenv("BANCO1_SECRET_KEY", "banco1-dev-secret-key-change-me-2026"),
)
ALLOWED_ORIGINS = _parse_allowed_origins()
