import os
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parents[2]


def _load_env_file(path: Path) -> None:
    if not path.exists():
        return

    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue

        if line.startswith("export "):
            line = line.removeprefix("export ").strip()

        if "=" not in line:
            continue

        key, value = line.split("=", 1)
        key = key.strip()
        if not key or key in os.environ:
            continue

        value = value.strip()
        if len(value) >= 2 and value[0] == value[-1] and value[0] in {'"', "'"}:
            value = value[1:-1]
        os.environ[key] = value


_load_env_file(ROOT_DIR / "analytics" / ".env")
_load_env_file(ROOT_DIR / ".env")


def _resolve_database_url() -> str:
    explicit_url = os.getenv("DATABASE_URL")
    if explicit_url:
        return explicit_url
    raw_path = os.getenv("ANALYTICS_DB_PATH", "analytics/app/analytics.db")
    return f"sqlite:///{_resolve_file_path(raw_path)}"


def _resolve_file_path(raw_path: str) -> Path:
    path = Path(raw_path)
    if not path.is_absolute():
        path = ROOT_DIR / path
    return path.resolve()


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


def _parse_csv_list(env_name: str, *, default: list[str]) -> list[str]:
    raw_value = os.getenv(env_name)
    if not raw_value:
        return default
    return [value.strip() for value in raw_value.split(",") if value.strip()]


DATABASE_URL = _resolve_database_url()
ANALYTICS_API_KEY = os.getenv("FLOWLENS_ANALYTICS_API_KEY", "flowlens-analytics-key-dev")
SERVICE_TOKEN = os.getenv("FLOWLENS_SERVICE_TOKEN", "flowlens-service-token-dev")
FETCH_TIMEOUT_SECONDS = float(os.getenv("ANALYTICS_FETCH_TIMEOUT_SECONDS", "5"))
ALLOWED_ORIGINS = _parse_allowed_origins()
SECURE_ALERTS_SGT_TAG = os.getenv("SECURE_ALERTS_SGT_TAG", "CONATT-SECURE-ENTRY")
SECURE_ALERTS_ALLOWED_IPS = _parse_csv_list(
    "SECURE_ALERTS_ALLOWED_IPS",
    default=["127.0.0.1", "::1", "::ffff:127.0.0.1", "10.0.2.2"],
)
SECURE_ALERTS_PRIVATE_KEY_PATH = _resolve_file_path(
    os.getenv(
        "SECURE_ALERTS_PRIVATE_KEY_PATH",
        "analytics/app/keys/dev_alerts_private.pem",
    )
)
SECURE_ALERTS_PUBLIC_KEY_PATH = _resolve_file_path(
    os.getenv(
        "SECURE_ALERTS_PUBLIC_KEY_PATH",
        "analytics/app/keys/dev_alerts_public.pem",
    )
)
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-pro")
GEMINI_CORRELATION_WINDOW_HOURS = int(
    os.getenv("GEMINI_CORRELATION_WINDOW_HOURS", "24")
)
GEMINI_CORRELATION_ALERT_LIMIT = int(
    os.getenv("GEMINI_CORRELATION_ALERT_LIMIT", "20")
)
GEMINI_CORRELATION_TRANSACTION_LIMIT = int(
    os.getenv("GEMINI_CORRELATION_TRANSACTION_LIMIT", "200")
)
PII_TOKENIZATION_SALT = os.getenv(
    "PII_TOKENIZATION_SALT",
    "flowlens-dev-tokenization-salt",
)
