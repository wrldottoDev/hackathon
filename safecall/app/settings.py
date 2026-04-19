import os
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[2]


def _resolve_database_url() -> str:
    explicit_url = os.getenv("DATABASE_URL")
    if explicit_url:
        return explicit_url
    raw_path = os.getenv("SAFECALL_DB_PATH", "safecall/app/safecall.db")
    path = Path(raw_path)
    if not path.is_absolute():
        path = ROOT_DIR / path
    return f"sqlite:///{path.resolve()}"


def _parse_allowed_origins() -> list[str]:
    raw_origins = os.getenv("SAFECALL_ALLOWED_ORIGINS")
    if raw_origins:
        return [o.strip() for o in raw_origins.split(",") if o.strip()]
    return [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:5178",
        "http://127.0.0.1:5178",
    ]


DATABASE_URL = _resolve_database_url()
SAFECALL_API_KEY = os.getenv("FLOWLENS_SAFECALL_API_KEY", "flowlens-safecall-key-dev")
ANALYTICS_API_URL = os.getenv("ANALYTICS_API_URL", "http://127.0.0.1:8003")
ANALYTICS_API_KEY = os.getenv("FLOWLENS_ANALYTICS_API_KEY", "flowlens-analytics-key-dev")
ALLOWED_ORIGINS = _parse_allowed_origins()
