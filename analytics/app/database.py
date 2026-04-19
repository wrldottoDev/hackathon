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
    inspector = inspect(engine)
    table_names = inspector.get_table_names()
    statements: list[str] = []

    if "observed_transactions" in table_names:
        observed_columns = {
            column["name"]
            for column in inspector.get_columns("observed_transactions")
        }
        if "beneficiary" not in observed_columns:
            statements.append(
                "ALTER TABLE observed_transactions ADD COLUMN beneficiary VARCHAR(255)"
            )
        if "concept" not in observed_columns:
            statements.append(
                "ALTER TABLE observed_transactions ADD COLUMN concept TEXT"
            )
        if "source_balance_before" not in observed_columns:
            statements.append(
                "ALTER TABLE observed_transactions ADD COLUMN source_balance_before NUMERIC(14, 2)"
            )
        if "source_balance_after" not in observed_columns:
            statements.append(
                "ALTER TABLE observed_transactions ADD COLUMN source_balance_after NUMERIC(14, 2)"
            )

    if "risk_alerts" in table_names:
        alert_columns = {
            column["name"]
            for column in inspector.get_columns("risk_alerts")
        }
        if "category" not in alert_columns:
            statements.append(
                "ALTER TABLE risk_alerts ADD COLUMN category VARCHAR(30)"
            )
        if "data_protection_applied" not in alert_columns:
            statements.append(
                "ALTER TABLE risk_alerts ADD COLUMN data_protection_applied BOOLEAN DEFAULT 0"
            )

    if "observed_accounts" in table_names:
        account_columns = {
            column["name"]
            for column in inspector.get_columns("observed_accounts")
        }
        if "reported" not in account_columns:
            statements.append(
                "ALTER TABLE observed_accounts ADD COLUMN reported BOOLEAN DEFAULT 0"
            )

    if "alertas" in table_names:
        secure_alert_columns = {
            column["name"]
            for column in inspector.get_columns("alertas")
        }
        if "latitude" not in secure_alert_columns:
            statements.append("ALTER TABLE alertas ADD COLUMN latitude FLOAT")
        if "longitude" not in secure_alert_columns:
            statements.append("ALTER TABLE alertas ADD COLUMN longitude FLOAT")

    if not statements:
        return

    with engine.begin() as connection:
        for statement in statements:
            connection.execute(text(statement))
        if "risk_alerts" in table_names:
            connection.execute(
                text("UPDATE risk_alerts SET category = COALESCE(category, 'aml')")
            )
            connection.execute(
                text(
                    "UPDATE risk_alerts SET data_protection_applied = "
                    "COALESCE(data_protection_applied, 0)"
                )
            )
        if "observed_accounts" in table_names:
            connection.execute(
                text("UPDATE observed_accounts SET reported = COALESCE(reported, 0)")
            )
