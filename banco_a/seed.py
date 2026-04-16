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
        "full_name": "Demo Cliente Banco A",
        "email": "demo@bancoa.com",
        "balances": [50_000, 12_000],
    },
    {"full_name": "Ana Mora", "email": "ana@bancoa.com", "balances": [9_500]},
    {"full_name": "Carlos Solis", "email": "carlos@bancoa.com", "balances": [16_500]},
    {"full_name": "Luisa Vargas", "email": "luisa@bancoa.com", "balances": [8_200]},
    {"full_name": "Pablo Castro", "email": "pablo@bancoa.com", "balances": [7_900]},
    {"full_name": "Sofia Ramirez", "email": "sofia@bancoa.com", "balances": [7_800]},
]


def reset_database():
    if DATABASE_PATH.exists():
        DATABASE_PATH.unlink()
    init_db()


def build_transfer(
    *,
    source_account_number: str,
    destination_account_number: str,
    amount: float,
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

        demo_user, demo_accounts = created_users["demo@bancoa.com"]
        ana_user, ana_accounts = created_users["ana@bancoa.com"]
        carlos_user, carlos_accounts = created_users["carlos@bancoa.com"]
        luisa_user, luisa_accounts = created_users["luisa@bancoa.com"]
        pablo_user, pablo_accounts = created_users["pablo@bancoa.com"]
        sofia_user, sofia_accounts = created_users["sofia@bancoa.com"]

        for amount in [180, 190, 210, 220, 240]:
            create_internal_transfer(
                db,
                build_transfer(
                    source_account_number=demo_accounts[0].account_number,
                    destination_account_number=ana_accounts[0].account_number,
                    amount=amount,
                    channel="mobile",
                    location="San Jose, CR",
                    description="Ráfaga de pagos pequeños",
                ),
                demo_user,
            )

        for source_user, source_account in [
            (carlos_user, carlos_accounts[0]),
            (luisa_user, luisa_accounts[0]),
            (pablo_user, pablo_accounts[0]),
            (sofia_user, sofia_accounts[0]),
        ]:
            create_internal_transfer(
                db,
                build_transfer(
                    source_account_number=source_account.account_number,
                    destination_account_number=demo_accounts[1].account_number,
                    amount=1_250,
                    channel="web",
                    location="Heredia, CR",
                    description="Concentración hacia cuenta hub",
                ),
                source_user,
            )

        create_internal_transfer(
            db,
            build_transfer(
                source_account_number=demo_accounts[0].account_number,
                destination_account_number=carlos_accounts[0].account_number,
                amount=12_500,
                channel="api",
                location="Remote API",
                description="Transferencia interna de alto monto",
            ),
            demo_user,
        )
        create_internal_transfer(
            db,
            build_transfer(
                source_account_number=demo_accounts[1].account_number,
                destination_account_number=luisa_accounts[0].account_number,
                amount=4_200,
                channel="web",
                location="Cartago, CR",
                description="Salida rápida de fondos",
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
