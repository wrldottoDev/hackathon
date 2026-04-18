from decimal import Decimal
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from app.database import SessionLocal, init_db
from app.schemas.transaction import TransferRequest
from app.schemas.user import UserCreate
from app.services.account_service import create_account
from app.services.auth_service import register_user
from app.services.transaction_service import create_internal_transfer
from app.settings import BANK_CODE, BANK_NAME, DATABASE_PATH


DEFAULT_PASSWORD = "DemoPass123"
USERS = [
    {
        "full_name": "Demo Cliente Banco C",
        "email": "demo@bancoc.com",
        "balances": [80_000, 25_000],
    },
    {"full_name": "Roberto Campos", "email": "roberto@bancoc.com", "balances": [18_000]},
    {"full_name": "Elena Vega", "email": "elena@bancoc.com", "balances": [22_500]},
    {"full_name": "Miguel Torres", "email": "miguel@bancoc.com", "balances": [14_000]},
    {"full_name": "Valeria Rios", "email": "valeria@bancoc.com", "balances": [11_500]},
    {"full_name": "Diego Herrera", "email": "diego@bancoc.com", "balances": [9_800]},
]


def reset_database():
    if DATABASE_PATH.exists():
        DATABASE_PATH.unlink()
    init_db()


def build_transfer(
    *,
    source_account_number: str,
    destination_account_number: str,
    amount: Decimal | int | str,
    channel: str,
    location: str,
    description: str,
) -> TransferRequest:
    return TransferRequest(
        source_account_number=source_account_number,
        destination_account_number=destination_account_number,
        amount=amount,
        channel=channel,
        location=location,
        description=description,
    )


def seed_bank():
    reset_database()
    with SessionLocal() as db:
        created_users: dict[str, tuple[object, list[object]]] = {}

        for user_data in USERS:
            user = register_user(
                db,
                UserCreate(
                    full_name=user_data["full_name"],
                    email=user_data["email"],
                    password=DEFAULT_PASSWORD,
                ),
            )
            accounts = [
                create_account(db, user, initial_balance=balance)
                for balance in user_data["balances"]
            ]
            created_users[user_data["email"]] = (user, accounts)

        demo_user, demo_accounts = created_users["demo@bancoc.com"]
        roberto_user, roberto_accounts = created_users["roberto@bancoc.com"]
        elena_user, elena_accounts = created_users["elena@bancoc.com"]
        miguel_user, miguel_accounts = created_users["miguel@bancoc.com"]
        valeria_user, valeria_accounts = created_users["valeria@bancoc.com"]
        diego_user, diego_accounts = created_users["diego@bancoc.com"]

        # Concentración: múltiples cuentas enviando a cuenta hub
        for source_user, source_account in [
            (roberto_user, roberto_accounts[0]),
            (elena_user, elena_accounts[0]),
            (miguel_user, miguel_accounts[0]),
            (valeria_user, valeria_accounts[0]),
        ]:
            create_internal_transfer(
                db,
                build_transfer(
                    source_account_number=source_account.account_number,
                    destination_account_number=demo_accounts[1].account_number,
                    amount=1_800,
                    channel="web",
                    location="San Jose, CR",
                    description="Concentración a cuenta hub BKC",
                ),
                source_user,
            )

        # Transferencia de alto monto
        create_internal_transfer(
            db,
            build_transfer(
                source_account_number=demo_accounts[0].account_number,
                destination_account_number=roberto_accounts[0].account_number,
                amount=18_000,
                channel="api",
                location="Remote API",
                description="Transferencia interna alto monto BKC",
            ),
            demo_user,
        )

        # Ráfaga de pequeños pagos
        for amount in [190, 200, 215, 225, 235]:
            create_internal_transfer(
                db,
                build_transfer(
                    source_account_number=demo_accounts[0].account_number,
                    destination_account_number=diego_accounts[0].account_number,
                    amount=amount,
                    channel="mobile",
                    location="Alajuela, CR",
                    description="Ráfaga de pagos pequeños BKC",
                ),
                demo_user,
            )

        # Salida rápida de fondos
        create_internal_transfer(
            db,
            build_transfer(
                source_account_number=demo_accounts[1].account_number,
                destination_account_number=elena_accounts[0].account_number,
                amount=5_500,
                channel="web",
                location="Cartago, CR",
                description="Salida rápida de fondos BKC",
            ),
            demo_user,
        )

        print(f"{BANK_NAME} seed completado")
        print(f"Banco: {BANK_CODE}")
        print(f"Password demo: {DEFAULT_PASSWORD}")
        for email, (_, accounts) in created_users.items():
            print(email, [account.account_number for account in accounts])


if __name__ == "__main__":
    seed_bank()
