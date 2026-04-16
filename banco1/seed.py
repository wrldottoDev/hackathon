import random

from backend.app import crud, models, schemas
from backend.app.database import DATABASE_PATH, SessionLocal, init_db
from backend.app.security import hash_password


random.seed(42)
DEFAULT_PASSWORD = "demo1234"
CHANNELS = ["web", "mobile", "atm", "api"]
LOCATIONS = [
    "San Jose, CR",
    "Heredia, CR",
    "Alajuela, CR",
    "Cartago, CR",
    "Limon, CR",
    "Remote API",
]
FIRST_NAMES = [
    "Ana",
    "Carlos",
    "Luisa",
    "Jorge",
    "Elena",
    "Mateo",
    "Sofia",
    "Valeria",
    "Daniel",
    "Camila",
    "Pablo",
    "Adriana",
]
LAST_NAMES = [
    "Rodriguez",
    "Gonzalez",
    "Mora",
    "Jimenez",
    "Solis",
    "Vargas",
    "Rojas",
    "Castro",
    "Lopez",
    "Ramirez",
]


def reset_database():
    if DATABASE_PATH.exists():
        DATABASE_PATH.unlink()
    init_db()


def create_user_with_account(db, full_name: str, email: str, initial_balance: float):
    user = crud.create_user(
        db,
        schemas.UserCreate(full_name=full_name, email=email, password=DEFAULT_PASSWORD),
        hashed_password=hash_password(DEFAULT_PASSWORD),
    )
    account = crud.create_account(db, user, initial_balance=initial_balance)
    return user, account


def perform_transfer(db, actor, source_account, destination_account, amount, channel=None, location=None):
    if source_account.id == destination_account.id:
        return False
    if source_account.balance < amount:
        return False

    payload = schemas.TransactionCreate(
        source_account_id=source_account.id,
        destination_account_id=destination_account.id,
        amount=round(amount, 2),
        channel=channel or random.choice(CHANNELS),
        location=location or random.choice(LOCATIONS),
    )
    try:
        crud.create_transaction(db, payload, actor=actor)
        db.refresh(source_account)
        db.refresh(destination_account)
        return True
    except (LookupError, PermissionError, ValueError):
        db.rollback()
        return False


def seed_users(db):
    actors = []

    demo_user, demo_account = create_user_with_account(
        db,
        full_name="Demo Analyst",
        email="demo@example.com",
        initial_balance=50_000,
    )
    actors.append((demo_user, demo_account))

    for index in range(1, 25):
        first_name = random.choice(FIRST_NAMES)
        last_name = random.choice(LAST_NAMES)
        user, account = create_user_with_account(
            db,
            full_name=f"{first_name} {last_name}",
            email=f"user{index}@example.com",
            initial_balance=random.randint(8_000, 35_000),
        )
        actors.append((user, account))

    return actors


def seed_normal_transactions(db, actors, target_count=150):
    created = 0
    attempts = 0
    while created < target_count and attempts < target_count * 8:
        attempts += 1
        source_user, source_account = random.choice(actors)
        destination_user, destination_account = random.choice(actors)
        del destination_user
        if source_account.id == destination_account.id:
            continue
        amount = random.randint(40, min(1_800, int(max(source_account.balance, 200))))
        if perform_transfer(db, source_user, source_account, destination_account, amount):
            created += 1
    return created


def seed_star_pattern(db, actors):
    hub_user, hub_account = actors[1]
    spokes = actors[2:8]
    created = 0

    for user, account in spokes:
        created += perform_transfer(db, user, account, hub_account, random.randint(600, 2_200), "mobile", "San Jose, CR")
        created += perform_transfer(db, hub_user, hub_account, account, random.randint(500, 1_600), "web", "Heredia, CR")

    return created


def seed_chain_pattern(db, actors):
    chain = actors[8:12]
    created = 0
    amount = 12_000

    for _, account in chain:
        if account.balance < 25_000:
            account.balance = 25_000
    db.commit()
    for _, account in chain:
        db.refresh(account)

    for index in range(len(chain) - 1):
        actor, source_account = chain[index]
        _, destination_account = chain[index + 1]
        created += perform_transfer(
            db,
            actor,
            source_account,
            destination_account,
            amount - index * 600,
            "api",
            "Remote API",
        )

    return created


def seed_structuring_pattern(db, actors):
    source_user, source_account = actors[12]
    destination_account = actors[13][1]
    created = 0

    if source_account.balance < 8_000:
        source_account.balance = 8_000
        db.commit()
        db.refresh(source_account)

    for _ in range(6):
        created += perform_transfer(
            db,
            source_user,
            source_account,
            destination_account,
            random.randint(180, 240),
            "atm",
            "Cartago, CR",
        )

    return created


def seed_high_value_pattern(db, actors):
    created = 0
    suspicious_pairs = [
        (actors[16], actors[17]),
        (actors[18], actors[19]),
        (actors[20], actors[21]),
        (actors[22], actors[23]),
    ]
    for (source_user, source_account), (_, destination_account) in suspicious_pairs:
        if source_account.balance < 20_000:
            source_account.balance = 20_000
            db.commit()
            db.refresh(source_account)
        created += perform_transfer(
            db,
            source_user,
            source_account,
            destination_account,
            random.randint(11_000, 16_000),
            "api",
            "Remote API",
        )
    return created


def print_summary(db):
    user_count = db.query(models.User).count()
    account_count = db.query(models.Account).count()
    transaction_count = db.query(models.Transaction).count()
    alert_count = db.query(models.RiskAlert).count()
    summary = crud.get_risk_summary(db)

    print("Banco 1 seed completado")
    print(f"Base recreada en: {DATABASE_PATH}")
    print(f"Usuarios: {user_count}")
    print(f"Cuentas: {account_count}")
    print(f"Transacciones: {transaction_count}")
    print(f"Alertas: {alert_count}")
    print(
        "Alertas por nivel: "
        f"low={summary.low}, medium={summary.medium}, high={summary.high}"
    )
    print("Credenciales demo: demo@example.com / demo1234")


def main():
    reset_database()
    db = SessionLocal()

    try:
        actors = seed_users(db)
        total_transactions = 0
        total_transactions += seed_normal_transactions(db, actors, target_count=160)
        total_transactions += seed_star_pattern(db, actors)
        total_transactions += seed_chain_pattern(db, actors)
        total_transactions += seed_structuring_pattern(db, actors)
        total_transactions += seed_high_value_pattern(db, actors)
        del total_transactions
        print_summary(db)
    finally:
        db.close()


if __name__ == "__main__":
    main()
