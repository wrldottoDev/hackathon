import os
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parents[2]


def _resolve_database_url() -> str:
    explicit_url = os.getenv("DATABASE_URL")
    if explicit_url:
        return explicit_url
    raw_path = os.getenv("ANALYTICS_DB_PATH", "analytics/app/analytics.db")
    path = Path(raw_path)
    if not path.is_absolute():
        path = ROOT_DIR / path
    return f"sqlite:///{path.resolve()}"


def _parse_allowed_origins() -> list[str]:
    raw_origins = os.getenv("ANALYTICS_ALLOWED_ORIGINS")
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


DATABASE_URL = _resolve_database_url()
ANALYTICS_API_KEY = os.getenv("FLOWLENS_ANALYTICS_API_KEY", "flowlens-analytics-key-dev")
SERVICE_TOKEN = os.getenv("FLOWLENS_SERVICE_TOKEN", "flowlens-service-token-dev")
FETCH_TIMEOUT_SECONDS = float(os.getenv("ANALYTICS_FETCH_TIMEOUT_SECONDS", "5"))
ALLOWED_ORIGINS = _parse_allowed_origins()

