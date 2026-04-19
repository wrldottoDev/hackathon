import os
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parents[2]


def _resolve_database_url() -> str:
    explicit_url = os.getenv("DATABASE_URL")
    if explicit_url:
        return explicit_url
    raw_path = os.getenv("FINSTA_DB_PATH", "finsta/app/finsta.db")
    path = Path(raw_path)
    if not path.is_absolute():
        path = ROOT_DIR / path
    return f"sqlite:///{path.resolve()}"


def _parse_allowed_origins() -> list[str]:
    raw_origins = os.getenv("FINSTA_ALLOWED_ORIGINS")
    if raw_origins:
        return [origin.strip() for origin in raw_origins.split(",") if origin.strip()]
    return [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:5174",
        "http://127.0.0.1:5174",
        "http://localhost:5175",
        "http://127.0.0.1:5175",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ]


DATABASE_URL = _resolve_database_url()
FINSTA_API_KEY = os.getenv("FLOWLENS_FINSTA_API_KEY", "flowlens-finsta-key-dev")
ANALYTICS_API_URL = os.getenv("ANALYTICS_API_URL", "http://localhost:8004")
ANALYTICS_API_KEY = os.getenv("FLOWLENS_ANALYTICS_API_KEY", "flowlens-analytics-key-dev")
ALLOWED_ORIGINS = _parse_allowed_origins()
