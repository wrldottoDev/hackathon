import os


BANK_INSTANCES = {
    "banco1": {
        "id": "banco1",
        "name": "Banco 1",
        "db_path": "backend/bank.db",
        "api_port": 8000,
        "frontend_port": 5173,
        "secret_key": "banco1-dev-secret-key-change-me-2026",
    },
    "banco2": {
        "id": "banco2",
        "name": "Banco 2",
        "db_path": "backend/banco2.db",
        "api_port": 8001,
        "frontend_port": 5175,
        "secret_key": "banco2-dev-secret-key-change-me-2026",
    },
    "banco3": {
        "id": "banco3",
        "name": "Banco 3",
        "db_path": "backend/banco3.db",
        "api_port": 8002,
        "frontend_port": 5176,
        "secret_key": "banco3-dev-secret-key-change-me-2026",
    },
}


def configure_bank_environment(bank_id: str):
    bank = BANK_INSTANCES[bank_id]
    os.environ.setdefault("BANK_ID", bank["id"])
    os.environ.setdefault("BANK_NAME", bank["name"])
    os.environ.setdefault("BANK_DB_PATH", bank["db_path"])
    os.environ.setdefault("BANK_SECRET_KEY", bank["secret_key"])
    return bank
