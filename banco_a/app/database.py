from sqlalchemy import create_engine, event, inspect, text
from sqlalchemy.engine import Engine
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.pool import NullPool

from .settings import DATABASE_URL

_is_sqlite = DATABASE_URL.startswith("sqlite")

_engine_kwargs = {
    "future": True,
    "poolclass": NullPool,
}
if _is_sqlite:
    _engine_kwargs["connect_args"] = {"check_same_thread": False}

engine = create_engine(DATABASE_URL, **_engine_kwargs)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)

Base = declarative_base()


if _is_sqlite:

    @event.listens_for(Engine, "connect")
    def set_sqlite_pragma(dbapi_connection, connection_record):
        del connection_record
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    from . import models  # noqa: F401

    Base.metadata.create_all(bind=engine)
    if _is_sqlite:
        _apply_sqlite_migrations()


def _apply_sqlite_migrations():
    statements: list[str] = []
    inspector = inspect(engine)
    table_names = inspector.get_table_names()

    if "accounts" in table_names:
        account_columns = {
            column["name"]
            for column in inspector.get_columns("accounts")
        }
        if "last_activity_at" not in account_columns:
            statements.append(
                "ALTER TABLE accounts ADD COLUMN last_activity_at DATETIME"
            )
        if "last_credentials_change_at" not in account_columns:
            statements.append(
                "ALTER TABLE accounts ADD COLUMN last_credentials_change_at DATETIME"
            )
        if "current_location" not in account_columns:
            statements.append(
                "ALTER TABLE accounts ADD COLUMN current_location VARCHAR(255)"
            )
        if "location_history" not in account_columns:
            statements.append(
                "ALTER TABLE accounts ADD COLUMN location_history JSON"
            )
        if "data_protected_by_investigation" not in account_columns:
            statements.append(
                "ALTER TABLE accounts ADD COLUMN data_protected_by_investigation BOOLEAN DEFAULT 0"
            )

    if "transactions" not in table_names:
        if not statements:
            return
        with engine.begin() as connection:
            for statement in statements:
                connection.execute(text(statement))
        return

    existing_columns = {
        column["name"]
        for column in inspector.get_columns("transactions")
    }

    if "external_reference" not in existing_columns:
        statements.append(
            "ALTER TABLE transactions ADD COLUMN external_reference VARCHAR(100)"
        )
    if "failure_reason" not in existing_columns:
        statements.append(
            "ALTER TABLE transactions ADD COLUMN failure_reason TEXT"
        )
    if "beneficiary" not in existing_columns:
        statements.append(
            "ALTER TABLE transactions ADD COLUMN beneficiary VARCHAR(255)"
        )
    if "concept" not in existing_columns:
        statements.append(
            "ALTER TABLE transactions ADD COLUMN concept TEXT"
        )
    if "source_balance_before" not in existing_columns:
        statements.append(
            "ALTER TABLE transactions ADD COLUMN source_balance_before NUMERIC(14, 2)"
        )
    if "source_balance_after" not in existing_columns:
        statements.append(
            "ALTER TABLE transactions ADD COLUMN source_balance_after NUMERIC(14, 2)"
        )

    if not statements:
        return

    with engine.begin() as connection:
        for statement in statements:
            connection.execute(text(statement))
        connection.execute(
            text(
                "CREATE INDEX IF NOT EXISTS "
                "ix_transactions_external_reference ON transactions (external_reference)"
            )
        )
        connection.execute(
            text(
                "UPDATE accounts SET last_activity_at = COALESCE(last_activity_at, created_at)"
            )
        )
        connection.execute(
            text(
                "UPDATE accounts SET last_credentials_change_at = "
                "COALESCE(last_credentials_change_at, created_at)"
            )
        )
        connection.execute(
            text(
                "UPDATE accounts SET current_location = COALESCE(current_location, '')"
            )
        )
        connection.execute(
            text(
                "UPDATE accounts SET location_history = COALESCE(location_history, '[]')"
            )
        )
        connection.execute(
            text(
                "UPDATE accounts SET data_protected_by_investigation = "
                "COALESCE(data_protected_by_investigation, 0)"
            )
        )
