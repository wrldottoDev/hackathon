"""Seed script for SafeCall demo data."""
from __future__ import annotations

import random
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from safecall.app.core.phone_numbers import pick_service_provider
from safecall.app.database import SessionLocal, init_db
from safecall.app.models import PhoneNumber, PhoneReport, User

random.seed(42)

NOW = datetime.now(timezone.utc)

USERS = [
    ("Ana Lopez", "ana.lopez@demo.cr"),
    ("Carlos Mora", "carlos.mora@demo.cr"),
    ("Maria Jimenez", "maria.jimenez@demo.cr"),
    ("Roberto Vargas", "roberto.vargas@demo.cr"),
    ("Sofia Quesada", "sofia.quesada@demo.cr"),
    ("Diego Herrera", "diego.herrera@demo.cr"),
    ("Laura Castro", "laura.castro@demo.cr"),
    ("Fernando Solis", "fernando.solis@demo.cr"),
]

DANGEROUS_NUMBERS = [
    ("+50681234567", 3, 85),
    ("+50689876543", 1, 60),
    ("+50687771234", 7, 45),
]

SUSPICIOUS_NUMBERS = [
    ("+50684445678", 30, 20),
    ("+50686663210", 60, 10),
    ("+50688882222", 15, 35),
]

CLEAN_NUMBERS = [
    ("+50683331111", 180, 0),
    ("+50685559999", 365, 0),
]

HIGH_CATEGORIES = ["trata_personas", "sim_swapping", "extorsion", "secuestro_virtual"]
MEDIUM_CATEGORIES = ["estafa", "phishing", "vishing", "suplantacion"]

REPORT_TEMPLATES = [
    ("trata_personas", "Numero usado para contactar menores con ofertas de trabajo falsas en redes sociales"),
    ("extorsion", "Llamadas amenazantes exigiendo deposito inmediato bajo amenaza"),
    ("sim_swapping", "Victima reporta perdida de linea y acceso no autorizado a cuentas bancarias"),
    ("secuestro_virtual", "Llamada simulando secuestro de familiar, exigen rescate en colones"),
    ("estafa", "Oferta falsa de prestamo con solicitud de deposito previo"),
    ("phishing", "SMS con enlace falso de banco nacional solicitando credenciales"),
    ("vishing", "Llamada haciendose pasar por funcionario del BCR solicitando datos"),
    ("suplantacion", "Numero clonado utilizado para solicitar transferencias a contactos"),
    ("trata_personas", "Reclutamiento via WhatsApp para supuesto trabajo de modelaje en el extranjero"),
    ("extorsion", "Amenaza de publicar fotos intimas si no se realiza pago"),
]


def seed():
    init_db()
    db = SessionLocal()

    if db.query(User).count() > 0:
        print("Base de datos ya tiene datos. Limpiando...")
        db.query(PhoneReport).delete()
        db.query(PhoneNumber).delete()
        db.query(User).delete()
        db.commit()

    users = []
    for i, (name, email) in enumerate(USERS):
        u = User(
            full_name=name,
            email=email,
            assigned_simulated_number=f"+5068{100 + i}{1000 + i}",
            created_at=NOW - timedelta(days=random.randint(30, 180)),
        )
        db.add(u)
        users.append(u)
    db.flush()
    print(f"  {len(users)} usuarios creados")

    all_numbers = []
    for num, age_days, call_vol in DANGEROUS_NUMBERS + SUSPICIOUS_NUMBERS + CLEAN_NUMBERS:
        pn = PhoneNumber(
            number=num,
            carrier=pick_service_provider(num),
            created_at=NOW - timedelta(days=age_days),
            simulated_call_count_24h=call_vol,
        )
        db.add(pn)
        all_numbers.append(pn)
    db.flush()
    print(f"  {len(all_numbers)} numeros telefonicos creados")

    report_count = 0
    for pn_data, phone in zip(DANGEROUS_NUMBERS, all_numbers[:3]):
        num_reports = random.randint(8, 15)
        for j in range(num_reports):
            cat, desc = random.choice(REPORT_TEMPLATES[:4])
            r = PhoneReport(
                reporter_id=random.choice(users).id,
                phone_number_id=phone.id,
                reported_number=phone.number,
                category=cat,
                description=desc,
                risk_level="critical" if j < num_reports // 2 else "high",
                consent_data_processing=True,
                created_at=NOW - timedelta(days=random.randint(0, 14), hours=random.randint(0, 23)),
            )
            db.add(r)
            report_count += 1
        phone.total_reports = num_reports
        phone.last_reported_at = NOW - timedelta(hours=random.randint(1, 48))
        phone.is_blocked = True

    for pn_data, phone in zip(SUSPICIOUS_NUMBERS, all_numbers[3:6]):
        num_reports = random.randint(2, 5)
        for j in range(num_reports):
            cat, desc = random.choice(REPORT_TEMPLATES[4:])
            r = PhoneReport(
                reporter_id=random.choice(users).id,
                phone_number_id=phone.id,
                reported_number=phone.number,
                category=cat,
                description=desc,
                risk_level="medium",
                consent_data_processing=random.choice([True, False]),
                created_at=NOW - timedelta(days=random.randint(2, 30), hours=random.randint(0, 23)),
            )
            db.add(r)
            report_count += 1
        phone.total_reports = num_reports
        phone.last_reported_at = NOW - timedelta(days=random.randint(2, 10))

    db.commit()
    print(f"  {report_count} reportes creados")

    db.close()
    print("\nSeed SafeCall completado!")


if __name__ == "__main__":
    seed()
