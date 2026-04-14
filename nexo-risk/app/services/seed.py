"""
Generador de datos sintéticos para NEXO Risk
=============================================
Crea cuentas y transacciones que incluyen patrones
de riesgo reales documentados por FATF/FinCEN.
"""

import random
from datetime import datetime, timedelta

from faker import Faker
from sqlalchemy.orm import Session

from app.models.db import Account, Transaction

fake = Faker("es_MX")
random.seed(42)

COUNTRIES = ["CR", "CR", "CR", "MX", "PA", "CO", "US"]
CHANNELS  = ["transfer", "transfer", "cash", "mobile"]


def _rand_ts(days_back: int = 30) -> datetime:
    delta = timedelta(
        days=random.randint(0, days_back),
        hours=random.randint(0, 23),
        minutes=random.randint(0, 59),
    )
    return datetime.utcnow() - delta


def _night_ts() -> datetime:
    """Timestamp entre 22:00 y 05:00."""
    base = datetime.utcnow().replace(minute=random.randint(0, 59), second=0)
    base = base.replace(hour=random.choice([22, 23, 0, 1, 2, 3, 4]))
    return base - timedelta(days=random.randint(0, 14))


def seed_database(db: Session, n_normal: int = 20, n_risky: int = 8) -> dict:
    """
    Puebla la BD con cuentas normales y cuentas de riesgo.
    Devuelve resumen de lo insertado.
    """
    accounts = []
    txn_counter = [1]

    def _new_account(code: str) -> Account:
        acc = Account(
            code=code,
            name=fake.name(),
            country=random.choice(COUNTRIES),
        )
        db.add(acc)
        db.flush()
        accounts.append(acc)
        return acc

    def _txn(sender: Account, receiver: Account, amount: float, ts: datetime):
        ref = f"TXN-{txn_counter[0]:06d}"
        txn_counter[0] += 1
        t = Transaction(
            ref=ref,
            sender_id=sender.id,
            receiver_id=receiver.id,
            amount=round(amount, 2),
            currency="USD",
            timestamp=ts,
            channel=random.choice(CHANNELS),
        )
        db.add(t)

    # ── Cuentas normales ───────────────────────────────────────────────────────
    normal_accs = [_new_account(f"ACC-{i:04d}") for i in range(1, n_normal + 1)]

    for acc in normal_accs:
        # 1-3 transacciones aleatorias, montos variados
        for _ in range(random.randint(1, 3)):
            other = random.choice([a for a in normal_accs if a.id != acc.id])
            _txn(acc, other, random.uniform(100, 5000), _rand_ts(30))

    # ── Cuentas de riesgo (con patrones FATF) ─────────────────────────────────
    risky_accs = [_new_account(f"RISK-{i:04d}") for i in range(1, n_risky + 1)]

    for i, risky in enumerate(risky_accs):
        # S1: múltiples depósitos pequeños desde cuentas normales
        senders = random.sample(normal_accs, min(7, len(normal_accs)))
        window  = datetime.utcnow() - timedelta(hours=18)
        for s in senders:
            _txn(s, risky, random.uniform(50, 490), window + timedelta(minutes=random.randint(1, 1000)))

        # S2: remitentes múltiples en 7 días
        for _ in range(random.randint(2, 5)):
            s = random.choice(normal_accs)
            _txn(s, risky, random.uniform(200, 800), _rand_ts(7))

        # S3: dispersión rápida (sale casi todo lo que entró)
        out_targets = random.sample(normal_accs, min(4, len(normal_accs)))
        dispersal_ts = datetime.utcnow() - timedelta(hours=random.randint(2, 30))
        for ot in out_targets:
            _txn(risky, ot, random.uniform(300, 1200), dispersal_ts)

        # S4: varias transacciones nocturnas
        night_peers = random.sample(normal_accs, 3)
        for np_ in night_peers:
            _txn(risky, np_, random.uniform(100, 500), _night_ts())
            _txn(np_, risky, random.uniform(50, 300), _night_ts())

    # ── Algunas transacciones cruzadas entre riesgosas (S5) ───────────────────
    for _ in range(12):
        a, b = random.sample(risky_accs, 2)
        _txn(a, b, random.uniform(100, 2000), _rand_ts(20))

    db.commit()

    return {
        "accounts_normal": n_normal,
        "accounts_risky":  n_risky,
        "transactions":    txn_counter[0] - 1,
    }
