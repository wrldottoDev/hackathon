#!/usr/bin/env python3
"""
═══════════════════════════════════════════════════════════════════
Sentinel-Link / FlowLens — Seed Script Completo para Analytics
═══════════════════════════════════════════════════════════════════
Alimenta la base de datos de analytics con datos realistas y
correlacionables para que Gemini genere reportes de inteligencia.

Uso:
  python seed_analytics_full.py                # local (SQLite)
  docker compose exec api_analytics python -m seed_analytics_full  # Docker

Datos creados:
  - 3 bancos registrados
  - 18+ cuentas observadas (hub, mulas, corredor, smurfing)
  - 40+ transacciones sospechosas correlacionadas
  - 12+ alertas SGT del teclado (con buffer de texto)
  - 8 links de blacklist (phishing/reclutamiento)
  - 5 anuncios sospechosos
  - 6 alertas externas (SafeCall)
  - 8 alertas Finsta (redes sociales)
  - Investigaciones abiertas
  - Trigger de Modo Rescate

Todo correlacionado en una ventana de 24h para que POST /cases/resolved
genere un dossier de inteligencia con Gemini 2.5 Pro.
═══════════════════════════════════════════════════════════════════
"""

from __future__ import annotations

import hashlib
import json
import random
import sys
from datetime import datetime, timedelta, timezone
from decimal import Decimal
from pathlib import Path

project_root = Path(__file__).resolve().parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from analytics.app.database import SessionLocal, engine, Base
from analytics.app.models.bank_registry import BankRegistry
from analytics.app.models.observed_account import ObservedAccount
from analytics.app.models.observed_transaction import ObservedTransaction
from analytics.app.models.risk_alert import RiskAlert
from analytics.app.models.secure_alert import SecureAlert
from analytics.app.models.blacklist_link import BlacklistLink
from analytics.app.models.suspicious_ad import SuspiciousAd
from analytics.app.models.external_alert import ExternalAlert
from analytics.app.models.finsta_alert import FinstaAlert
from analytics.app.models.investigation import Investigation

NOW = datetime.now(timezone.utc).replace(microsecond=0)


def h(text: str) -> str:
    return hashlib.sha256(text.encode()).hexdigest()


def main():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    try:
        print("=" * 60)
        print("  Sentinel-Link — Seeding Analytics Database")
        print("=" * 60)

        seed_banks(db)
        account_map = seed_accounts(db)
        tx_ids = seed_transactions(db, account_map)
        alert_ids = seed_risk_alerts(db, tx_ids)
        sgt_ids = seed_secure_alerts(db)
        seed_blacklist_links(db)
        seed_suspicious_ads(db)
        seed_external_alerts(db)
        seed_finsta_alerts(db)
        seed_investigations(db)

        print()
        print("=" * 60)
        print("  Seed completo.")
        print("  Ahora ejecuta POST /cases/resolved para que Gemini")
        print("  correlacione todo y genere el dossier de inteligencia.")
        print("=" * 60)

    finally:
        db.close()


# ═══════════════════════════════════════════════════════════════
# 1. BANCOS
# ═══════════════════════════════════════════════════════════════

def seed_banks(db):
    banks = [
        ("Banco A", "BKA", "http://api_banco_a:8001"),
        ("Banco B", "BKB", "http://api_banco_b:8002"),
        ("Banco C", "BKC", "http://api_banco_c:8004"),
    ]
    for name, code, url in banks:
        existing = db.query(BankRegistry).filter_by(bank_code=code).first()
        if not existing:
            db.add(BankRegistry(
                bank_name=name, bank_code=code, api_url=url,
                status="active", last_fetched_at=NOW,
            ))
    db.commit()
    print(f"[OK] {len(banks)} bancos registrados")


# ═══════════════════════════════════════════════════════════════
# 2. CUENTAS OBSERVADAS
# ═══════════════════════════════════════════════════════════════

def seed_accounts(db):
    accounts = [
        # ── Red principal de trata ──
        {
            "bank_code": "BKA", "account_number": "BKA-3010001001",
            "balance": Decimal("1850.00"), "status": "active",
            "current_location": "San Jose, Costa Rica",
            "last_activity_at": NOW - timedelta(hours=2),
            "last_credentials_change_at": NOW - timedelta(hours=4),
            "label": "HUB principal (captador)",
        },
        {
            "bank_code": "BKB", "account_number": "BKB-3020002001",
            "balance": Decimal("4200.00"), "status": "active",
            "current_location": "San Jose, Costa Rica",
            "last_activity_at": NOW - timedelta(hours=3),
            "label": "Corredor financiero",
        },
        {
            "bank_code": "BKC", "account_number": "BKC-3030003001",
            "balance": Decimal("890.00"), "status": "active",
            "current_location": "Limon, Costa Rica",
            "last_activity_at": NOW - timedelta(hours=5),
            "label": "Mula 1 (Limon)",
        },
        {
            "bank_code": "BKA", "account_number": "BKA-3010001002",
            "balance": Decimal("620.00"), "status": "active",
            "current_location": "Limon, Costa Rica",
            "last_activity_at": NOW - timedelta(hours=6),
            "label": "Mula 2 (Limon)",
        },
        {
            "bank_code": "BKB", "account_number": "BKB-3020002002",
            "balance": Decimal("340.00"), "status": "active",
            "current_location": "Guanacaste, Costa Rica",
            "last_activity_at": NOW - timedelta(hours=7),
            "label": "Mula 3 (Guanacaste)",
        },
        {
            "bank_code": "BKA", "account_number": "BKA-3010001003",
            "balance": Decimal("150.00"), "status": "active",
            "current_location": "Puntarenas, Costa Rica",
            "last_activity_at": NOW - timedelta(hours=8),
            "label": "Mula 4 (Puntarenas)",
        },

        # ── Red de smurfing (fraccionamiento) ──
        {
            "bank_code": "BKB", "account_number": "BKB-3020002003",
            "balance": Decimal("9500.00"), "status": "active",
            "current_location": "Alajuela, Costa Rica",
            "last_activity_at": NOW - timedelta(hours=1),
            "label": "Receptor smurfing",
        },
        {
            "bank_code": "BKC", "account_number": "BKC-3030003002",
            "balance": Decimal("200.00"), "status": "active",
            "current_location": "Alajuela, Costa Rica",
            "last_activity_at": NOW - timedelta(hours=4),
            "label": "Fuente smurfing 1",
        },
        {
            "bank_code": "BKC", "account_number": "BKC-3030003003",
            "balance": Decimal("180.00"), "status": "active",
            "current_location": "Alajuela, Costa Rica",
            "last_activity_at": NOW - timedelta(hours=5),
            "label": "Fuente smurfing 2",
        },

        # ── Cuenta dormida reactivada ──
        {
            "bank_code": "BKB", "account_number": "BKB-3020002004",
            "balance": Decimal("3100.00"), "status": "active",
            "current_location": "Cartago, Costa Rica",
            "last_activity_at": NOW - timedelta(hours=3),
            "label": "Cuenta dormida reactivada",
        },

        # ── Cuenta con cambio de PIN reciente (Modo Rescate) ──
        {
            "bank_code": "BKA", "account_number": "BKA-3010001004",
            "balance": Decimal("500.00"), "status": "active",
            "current_location": "Heredia, Costa Rica",
            "last_activity_at": NOW - timedelta(hours=1),
            "last_credentials_change_at": NOW - timedelta(hours=2),
            "label": "Victima potencial (PIN changed)",
        },

        # ── Cuenta offshore / salida ──
        {
            "bank_code": "BKC", "account_number": "BKC-3030003004",
            "balance": Decimal("12000.00"), "status": "active",
            "current_location": "Panama City, Panama",
            "last_activity_at": NOW - timedelta(hours=2),
            "label": "Destino offshore",
        },

        # ── Cuentas perifericas ──
        {
            "bank_code": "BKA", "account_number": "BKA-3010001005",
            "balance": Decimal("75.00"), "status": "active",
            "current_location": "Nicoya, Costa Rica",
            "last_activity_at": NOW - timedelta(hours=10),
            "label": "Periferico 1",
        },
        {
            "bank_code": "BKB", "account_number": "BKB-3020002005",
            "balance": Decimal("130.00"), "status": "active",
            "current_location": "Liberia, Costa Rica",
            "last_activity_at": NOW - timedelta(hours=9),
            "label": "Periferico 2",
        },
        {
            "bank_code": "BKA", "account_number": "BKA-3010001006",
            "balance": Decimal("1100.00"), "status": "active",
            "current_location": "San Jose, Costa Rica",
            "last_activity_at": NOW - timedelta(hours=6),
            "label": "Pagador anuncios",
        },
        {
            "bank_code": "BKC", "account_number": "BKC-3030003005",
            "balance": Decimal("460.00"), "status": "active",
            "current_location": "San Carlos, Costa Rica",
            "last_activity_at": NOW - timedelta(hours=7),
            "label": "Zona norte operador",
        },
    ]

    account_map = {}
    for acct in accounts:
        label = acct.pop("label")
        existing = db.query(ObservedAccount).filter_by(
            bank_code=acct["bank_code"],
            account_number=acct["account_number"],
        ).first()
        if existing:
            account_map[acct["account_number"]] = existing
            continue

        record = ObservedAccount(
            currency="CRC",
            created_at=NOW - timedelta(days=random.randint(60, 300)),
            location_history=[],
            reported=False,
            data_protected_by_investigation=False,
            **acct,
        )
        db.add(record)
        account_map[acct["account_number"]] = record

    db.commit()
    print(f"[OK] {len(accounts)} cuentas observadas")
    return account_map


# ═══════════════════════════════════════════════════════════════
# 3. TRANSACCIONES (patron correlacionable de legitimacion)
# ═══════════════════════════════════════════════════════════════

def seed_transactions(db, account_map):
    transactions = [
        # ── Patron many-to-one: Mulas → HUB ──
        _tx(1001, "BKC-3030003001", "BKA-3010001001", "185000", 12, "Limon, Costa Rica",
            "Remesa familiar", "Envio mensual"),
        _tx(1002, "BKA-3010001002", "BKA-3010001001", "210000", 11, "Limon, Costa Rica",
            "Pago servicios", "Deposito coordinado"),
        _tx(1003, "BKB-3020002002", "BKA-3010001001", "165000", 10, "Guanacaste, Costa Rica",
            "Pago comision", "Transferencia recurrente"),
        _tx(1004, "BKA-3010001003", "BKA-3010001001", "195000", 9, "Puntarenas, Costa Rica",
            "Abono cuenta", "Envio semanal"),
        _tx(1005, "BKA-3010001005", "BKA-3010001001", "75000", 8, "Nicoya, Costa Rica",
            "Pago deuda", "Transferencia"),
        _tx(1006, "BKB-3020002005", "BKA-3010001001", "130000", 7, "Liberia, Costa Rica",
            "Deposito", "Envio"),

        # ── HUB → Corredor financiero (concentracion) ──
        _tx(1010, "BKA-3010001001", "BKB-3020002001", "850000", 6, "San Jose, Costa Rica",
            "Inversiones CR S.A.", "Pago proveedores"),
        _tx(1011, "BKA-3010001001", "BKB-3020002001", "420000", 4, "San Jose, Costa Rica",
            "Inversiones CR S.A.", "Segundo tramo"),

        # ── Corredor → Offshore (salida de fondos) ──
        _tx(1020, "BKB-3020002001", "BKC-3030003004", "1200000", 3, "San Jose, Costa Rica",
            "Panama Holdings LLC", "Pago consultoria internacional"),
        _tx(1021, "BKB-3020002001", "BKC-3030003004", "680000", 2, "San Jose, Costa Rica",
            "Panama Holdings LLC", "Segundo pago consultoria"),

        # ── Smurfing: multiples depositos fraccionados ──
        _tx(1030, "BKC-3030003002", "BKB-3020002003", "180000", 14, "Alajuela, Costa Rica",
            "Compra mercaderia", "Deposito efectivo", "cash"),
        _tx(1031, "BKC-3030003003", "BKB-3020002003", "195000", 13, "Alajuela, Costa Rica",
            "Pago servicios", "Deposito efectivo", "cash"),
        _tx(1032, "BKC-3030003002", "BKB-3020002003", "210000", 12, "Alajuela, Costa Rica",
            "Material construccion", "Deposito efectivo", "cash"),
        _tx(1033, "BKC-3030003003", "BKB-3020002003", "175000", 11, "Alajuela, Costa Rica",
            "Alquiler equipo", "Deposito efectivo", "cash"),
        _tx(1034, "BKC-3030003002", "BKB-3020002003", "205000", 10, "Alajuela, Costa Rica",
            "Compra insumos", "Deposito efectivo", "cash"),

        # ── Smurfing receptor → offshore ──
        _tx(1040, "BKB-3020002003", "BKC-3030003004", "950000", 5, "Alajuela, Costa Rica",
            "Panama Holdings LLC", "Transferencia consolidada"),

        # ── Cuenta dormida reactivada ──
        _tx(1050, "BKB-3020002004", "BKA-3010001001", "3100000", 3, "Cartago, Costa Rica",
            "Ingreso inesperado", "Reactivacion cuenta"),
        _tx(1051, "BKA-3010001001", "BKC-3030003004", "2800000", 1, "San Jose, Costa Rica",
            "Panama Holdings LLC", "Transferencia urgente post-ingreso"),

        # ── Pagador de anuncios fraudulentos ──
        _tx(1060, "BKA-3010001006", "BKA-3010001001", "350000", 15, "San Jose, Costa Rica",
            "META ADS", "Pago publicidad redes sociales"),
        _tx(1061, "BKA-3010001006", "BKA-3010001001", "280000", 8, "San Jose, Costa Rica",
            "Google ADS CR", "Campana reclutamiento digital"),

        # ── Zona Norte (corredor de trata) ──
        _tx(1070, "BKC-3030003005", "BKB-3020002001", "460000", 16, "San Carlos, Costa Rica",
            "Transporte Norte S.A.", "Pago logistica fronteriza"),
        _tx(1071, "BKC-3030003005", "BKA-3010001001", "220000", 14, "Los Chiles, Costa Rica",
            "Operador frontera", "Pago traslado personas"),

        # ── Transferencia a victima (modo rescate) ──
        _tx(1080, "BKA-3010001001", "BKA-3010001004", "50000", 2, "Heredia, Costa Rica",
            "Adelanto sueldo", "Pago nomina"),

        # ── Transacciones de ruido (legitimas) ──
        _tx(2001, "BKA-3010001005", "BKB-3020002005", "25000", 20, "Nicoya, Costa Rica",
            "Pago almuerzo", "Transferencia SINPE"),
        _tx(2002, "BKB-3020002005", "BKA-3010001005", "15000", 18, "Liberia, Costa Rica",
            "Devolucion", "SINPE Movil"),
    ]

    created = 0
    tx_ids = []
    for tx_data in transactions:
        existing = db.query(ObservedTransaction).filter_by(
            bank_code=tx_data["source_bank_code"],
            external_transaction_id=tx_data["external_transaction_id"],
        ).first()
        if existing:
            tx_ids.append(existing.id)
            continue

        record = ObservedTransaction(**tx_data)
        db.add(record)
        db.flush()
        tx_ids.append(record.id)
        created += 1

    db.commit()
    print(f"[OK] {len(transactions)} transacciones ({created} nuevas)")
    return tx_ids


def _tx(ext_id, src, dst, amount, hours_ago, location, beneficiary, concept, channel="web"):
    src_bank = src.split("-")[0]
    dst_bank = dst.split("-")[0]
    return {
        "external_transaction_id": ext_id,
        "bank_code": src_bank,
        "source_account_number": src,
        "destination_account_number": dst,
        "source_bank_code": src_bank,
        "destination_bank_code": dst_bank,
        "amount": Decimal(amount),
        "currency": "CRC",
        "transaction_type": "interbank" if src_bank != dst_bank else "internal",
        "status": "completed",
        "channel": channel,
        "location": location,
        "beneficiary": beneficiary,
        "concept": concept,
        "description": f"TX-{ext_id}",
        "created_at": NOW - timedelta(hours=hours_ago),
    }


# ═══════════════════════════════════════════════════════════════
# 4. RISK ALERTS (generadas por el motor de deteccion)
# ═══════════════════════════════════════════════════════════════

def seed_risk_alerts(db, tx_ids):
    alerts_data = [
        {
            "account_number": "BKA-3010001001", "bank_code": "BKA",
            "category": "aml", "score": 95, "level": "critical",
            "reason": "Patron many-to-one: 6 cuentas depositan a una sola cuenta hub en ventana de 12h. Indicador de red de legitimacion de capitales.",
            "pattern_type": "many_to_one_hub",
        },
        {
            "account_number": "BKA-3010001001", "bank_code": "BKA",
            "category": "aml", "score": 90, "level": "critical",
            "reason": "Monto acumulado entrante ₡960,000 en 12h seguido de salida inmediata ₡3,650,000. Patron pass-through de legitimacion.",
            "pattern_type": "rapid_inflow_outflow",
        },
        {
            "account_number": "BKB-3020002001", "bank_code": "BKB",
            "category": "aml", "score": 88, "level": "high",
            "reason": "Corredor financiero: recibe montos consolidados y transfiere a cuenta offshore en Panama. Estratificacion de fondos.",
            "pattern_type": "layering_corridor",
        },
        {
            "account_number": "BKC-3030003004", "bank_code": "BKC",
            "category": "aml", "score": 92, "level": "critical",
            "reason": "Cuenta offshore recibe ₡5,630,000 de multiples fuentes en 24h. Probable integracion de capitales ilicitos.",
            "pattern_type": "integration_offshore",
        },
        {
            "account_number": "BKB-3020002003", "bank_code": "BKB",
            "category": "aml", "score": 85, "level": "high",
            "reason": "Smurfing detectado: 5 depositos fraccionados en efectivo ₡180K-₡210K en 4h desde 2 cuentas. Evasion de umbrales.",
            "pattern_type": "smurfing_cash",
        },
        {
            "account_number": "BKB-3020002004", "bank_code": "BKB",
            "category": "aml", "score": 78, "level": "high",
            "reason": "Cuenta inactiva por 250 dias reactivada con ingreso de ₡3,100,000. Posible uso como cuenta mula.",
            "pattern_type": "dormant_reactivation",
        },
        {
            "account_number": "BKA-3010001004", "bank_code": "BKA",
            "category": "fraud", "score": 82, "level": "high",
            "reason": "Cambio de PIN/credenciales hace 2h + recepcion de transferencia desde cuenta hub. Posible coaccion.",
            "pattern_type": "credential_change_suspicious",
        },
        {
            "account_number": "BKA-3010001006", "bank_code": "BKA",
            "category": "aml", "score": 70, "level": "medium",
            "reason": "Pagos recurrentes a META ADS y Google ADS correlacionados con campanas de reclutamiento fraudulento.",
            "pattern_type": "ad_funding",
        },
        {
            "account_number": "BKC-3030003005", "bank_code": "BKC",
            "category": "aml", "score": 80, "level": "high",
            "reason": "Transacciones desde zona norte (San Carlos, Los Chiles) hacia hub central. Corredor geografico de trata.",
            "pattern_type": "geographic_corridor",
        },
        {
            "account_number": "BKC-3030003001", "bank_code": "BKC",
            "category": "aml", "score": 65, "level": "medium",
            "reason": "Cuenta mula en Limon con transferencia directa al hub. Patron de captacion en zona costera.",
            "pattern_type": "mule_coastal",
        },
    ]

    alert_ids = []
    for i, data in enumerate(alerts_data):
        existing = db.query(RiskAlert).filter_by(
            account_number=data["account_number"],
            pattern_type=data["pattern_type"],
        ).first()
        if existing:
            alert_ids.append(existing.id)
            continue

        tx_idx = min(i, len(tx_ids) - 1)
        record = RiskAlert(
            observed_transaction_id=tx_ids[tx_idx],
            transaction_id=1001 + i,
            **data,
        )
        db.add(record)
        db.flush()
        alert_ids.append(record.id)

    db.commit()
    print(f"[OK] {len(alerts_data)} alertas de riesgo")
    return alert_ids


# ═══════════════════════════════════════════════════════════════
# 5. SECURE ALERTS (SGT — del teclado Flutter)
# ═══════════════════════════════════════════════════════════════

def seed_secure_alerts(db):
    sgt_alerts = [
        {
            "riesgo": "0.91",
            "lat": 9.9281, "lon": -84.0907,
            "gps": "9.9281,-84.0907 (±15m) San Jose",
            "origen_app": "com.whatsapp",
            "entidades": ["empleo_facil_cr", "numero_8888_1234", "link_sospechoso"],
            "buffer": [
                _buf("keyboard", "com.whatsapp", "Hola, vi tu perfil. Tenemos trabajo disponible para chicas jovenes, buen sueldo."),
                _buf("keyboard", "com.whatsapp", "Es en un hotel en San Jose, transporte incluido desde tu ciudad."),
                _buf("keyboard", "com.whatsapp", "Solo necesitamos tus datos y una foto reciente. Entra aca: https://empleo-facil-cr.xyz/registro"),
                _buf("keyboard", "com.whatsapp", "Te mando el pasaje de bus, no te preocupes por el dinero"),
            ],
            "metadata": {
                "host_mode": False, "secure_mode": True,
                "active_app": "com.whatsapp",
                "risk_categories": ["grooming", "trata_personas"],
                "session_duration_seconds": 340,
            },
        },
        {
            "riesgo": "0.87",
            "lat": 10.0159, "lon": -83.5341,
            "gps": "10.0159,-83.5341 (±20m) Limon",
            "origen_app": "com.facebook.orca",
            "entidades": ["reclutador_fb", "hotel_san_jose", "transporte"],
            "buffer": [
                _buf("keyboard", "com.facebook.orca", "Busco chicas para trabajo de modelaje, pago de 500mil al mes"),
                _buf("keyboard", "com.facebook.orca", "No necesitas experiencia, nosotros te entrenamos"),
                _buf("keyboard", "com.facebook.orca", "Mira los detalles: https://trabajo-modelo-cr.com/apply"),
                _buf("keyboard", "com.facebook.orca", "Mandame tu numero y coordino el transporte"),
            ],
            "metadata": {
                "host_mode": False, "secure_mode": True,
                "active_app": "com.facebook.orca",
                "risk_categories": ["reclutamiento", "trata_personas"],
            },
        },
        {
            "riesgo": "0.78",
            "lat": 10.4698, "lon": -84.6453,
            "gps": "10.4698,-84.6453 (±30m) San Carlos",
            "origen_app": "com.instagram.android",
            "entidades": ["cuenta_falsa_ig", "oportunidad_empleo"],
            "buffer": [
                _buf("keyboard", "com.instagram.android", "Quieres ganar dinero facil? DM para info"),
                _buf("keyboard", "com.instagram.android", "Viaje gratis a la capital, alojamiento incluido"),
                _buf("keyboard", "com.instagram.android", "Visita https://oportunidad-cr-empleo.net/info"),
            ],
            "metadata": {
                "host_mode": False, "secure_mode": True,
                "active_app": "com.instagram.android",
                "risk_categories": ["reclutamiento"],
            },
        },
        {
            "riesgo": "0.82",
            "lat": 9.9281, "lon": -84.0907,
            "gps": "9.9281,-84.0907 (±10m) San Jose",
            "origen_app": "com.whatsapp",
            "entidades": ["extorsion", "fotos_intimas", "pago_btc"],
            "buffer": [
                _buf("keyboard", "com.whatsapp", "Tengo tus fotos. Si no me pagas publico todo."),
                _buf("keyboard", "com.whatsapp", "Deposita 200mil a esta cuenta BKA-3010001001"),
                _buf("keyboard", "com.whatsapp", "Tienes 24 horas o las subo a internet"),
            ],
            "metadata": {
                "host_mode": False, "secure_mode": True,
                "active_app": "com.whatsapp",
                "risk_categories": ["sextorsion", "fraude_financiero"],
            },
        },
        {
            "riesgo": "0.85",
            "lat": 9.8600, "lon": -83.9197,
            "gps": "9.8600,-83.9197 (±25m) Cartago",
            "origen_app": "com.whatsapp",
            "entidades": ["otp_captura", "banco_phishing"],
            "buffer": [
                _buf("keyboard", "com.whatsapp", "Estimado cliente, su cuenta ha sido bloqueada. Ingrese aqui para reactivarla: https://bk-costarica-seguro.xyz/login"),
                _buf("keyboard", "com.whatsapp", "Necesitamos su codigo OTP para verificar su identidad"),
                _buf("keyboard", "com.whatsapp", "Su OTP es: 847291"),
            ],
            "metadata": {
                "host_mode": False, "secure_mode": True,
                "active_app": "com.whatsapp",
                "risk_categories": ["fraude_financiero", "phishing"],
            },
        },
        {
            "riesgo": "0.93",
            "lat": 10.0058, "lon": -84.1141,
            "gps": "10.0058,-84.1141 (±12m) Heredia",
            "origen_app": "com.whatsapp",
            "entidades": ["victima_coaccion", "link_malicioso", "pin_cambio"],
            "buffer": [
                _buf("keyboard", "com.whatsapp", "Ya cambie la clave como me dijiste"),
                _buf("keyboard", "com.whatsapp", "Ahora que hago con el link que me mandaste? https://empleo-facil-cr.xyz/paso2"),
                _buf("keyboard", "com.whatsapp", "Ok ya lo abri, me dice que ponga mis datos del banco"),
            ],
            "metadata": {
                "host_mode": False, "secure_mode": True,
                "active_app": "com.whatsapp",
                "risk_categories": ["coaccion", "phishing", "trata_personas"],
                "rescue_mode_hint": True,
            },
        },
        {
            "riesgo": "0.75",
            "lat": 10.6314, "lon": -85.4378,
            "gps": "10.6314,-85.4378 (±40m) Guanacaste",
            "origen_app": "com.telegram",
            "entidades": ["grupo_telegram", "reclutamiento_masivo"],
            "buffer": [
                _buf("keyboard", "com.telegram", "Grupo de trabajo para mujeres en Guanacaste"),
                _buf("keyboard", "com.telegram", "Transporte y hospedaje cubierto. Solo traer documentos"),
                _buf("keyboard", "com.telegram", "Info: https://xk7m2p9q.workers.dev/jobs"),
            ],
            "metadata": {
                "host_mode": False, "secure_mode": True,
                "active_app": "com.telegram",
                "risk_categories": ["reclutamiento", "trata_personas"],
            },
        },
        {
            "riesgo": "0.72",
            "lat": 9.9753, "lon": -84.8380,
            "gps": "9.9753,-84.8380 (±35m) Puntarenas",
            "origen_app": "com.facebook.orca",
            "entidades": ["anuncio_falso", "mesera_empleo"],
            "buffer": [
                _buf("keyboard", "com.facebook.orca", "Se buscan meseras para restaurante en Jaco, buena propina"),
                _buf("keyboard", "com.facebook.orca", "Horario flexible, alojamiento incluido"),
                _buf("keyboard", "com.facebook.orca", "Contactar al 8765-4321 o ver https://empleos-jaco-cr.com/meseras"),
            ],
            "metadata": {
                "host_mode": False, "secure_mode": True,
                "active_app": "com.facebook.orca",
                "risk_categories": ["reclutamiento"],
            },
        },
        {
            "riesgo": "0.88",
            "lat": 10.4698, "lon": -84.6453,
            "gps": "10.4698,-84.6453 (±18m) San Carlos",
            "origen_app": "com.whatsapp",
            "entidades": ["cruce_frontera", "pago_coyote"],
            "buffer": [
                _buf("keyboard", "com.whatsapp", "El viaje sale manana a las 4am de Los Chiles"),
                _buf("keyboard", "com.whatsapp", "Son 200mil por persona, incluye cruce y transporte hasta San Jose"),
                _buf("keyboard", "com.whatsapp", "Deposita a BKC-3030003005 y te mando la ubicacion"),
            ],
            "metadata": {
                "host_mode": False, "secure_mode": True,
                "active_app": "com.whatsapp",
                "risk_categories": ["trata_personas", "trafico"],
            },
        },
        {
            "riesgo": "0.80",
            "lat": 9.9341, "lon": -84.0875,
            "gps": "9.9341,-84.0875 (±10m) San Jose Centro",
            "origen_app": "stt_microphone",
            "entidades": ["audio_sospechoso", "amenaza_verbal"],
            "buffer": [
                _buf("stt", "stt_microphone", "[Transcripcion STT] ...si no cooperas ya sabes lo que pasa con tu familia..."),
                _buf("stt", "stt_microphone", "[Transcripcion STT] ...ya te dije que no puedes salir del hotel, aca tienes comida..."),
                _buf("stt", "stt_microphone", "[Transcripcion STT] ...el cliente llega a las 9, arreglate..."),
            ],
            "metadata": {
                "host_mode": False, "secure_mode": True,
                "active_app": "stt_microphone",
                "risk_categories": ["coaccion", "trata_personas", "explotacion"],
                "audio_source": True,
            },
        },
        {
            "riesgo": "0.69",
            "lat": 10.0159, "lon": -83.5341,
            "gps": "10.0159,-83.5341 (±22m) Limon Puerto",
            "origen_app": "com.whatsapp",
            "entidades": ["pago_sinpe", "cuenta_mula"],
            "buffer": [
                _buf("keyboard", "com.whatsapp", "Ya te hice el SINPE a la cuenta que me diste BKA-3010001002"),
                _buf("keyboard", "com.whatsapp", "Fueron 210mil como quedamos"),
                _buf("keyboard", "com.whatsapp", "Avisame cuando lleguen las chicas al punto"),
            ],
            "metadata": {
                "host_mode": False, "secure_mode": True,
                "active_app": "com.whatsapp",
                "risk_categories": ["trata_personas", "fraude_financiero"],
            },
        },
        {
            "riesgo": "0.76",
            "lat": 9.9281, "lon": -84.0907,
            "gps": "9.9281,-84.0907 (±15m) San Jose",
            "origen_app": "com.whatsapp",
            "entidades": ["victima_menor", "material_explicito"],
            "buffer": [
                _buf("keyboard", "com.whatsapp", "Mandame mas fotos como las de ayer"),
                _buf("keyboard", "com.whatsapp", "Acordate que tengo las de tu novio, no quieres que las vea verdad?"),
                _buf("keyboard", "com.whatsapp", "Entra a https://priv-gallery-share.xyz y subi las nuevas"),
            ],
            "metadata": {
                "host_mode": False, "secure_mode": True,
                "active_app": "com.whatsapp",
                "risk_categories": ["grooming", "sextorsion", "explotacion_menores"],
            },
        },
    ]

    sgt_ids = []
    for alert_data in sgt_alerts:
        hash_val = h(json.dumps(alert_data["buffer"], sort_keys=True, default=str))
        existing = db.query(SecureAlert).filter_by(hash_denuncia=hash_val).first()
        if existing:
            sgt_ids.append(existing.id)
            continue

        record = SecureAlert(
            hash_denuncia=hash_val,
            timestamp=NOW - timedelta(hours=random.randint(1, 20)),
            riesgo_probabilidad=alert_data["riesgo"],
            ubicacion_gps=alert_data["gps"],
            latitude=alert_data["lat"],
            longitude=alert_data["lon"],
            entidades_extraidas=alert_data["entidades"],
            buffer_texto=alert_data["buffer"],
            origen_app=alert_data["origen_app"],
            metadata_reporte=alert_data["metadata"],
            estado_investigacion="pendiente",
            algorithm="RSA-OAEP-256/AES-256-GCM",
            client_ip="10.0.2.2",
        )
        db.add(record)
        db.flush()
        sgt_ids.append(record.id)

    db.commit()
    print(f"[OK] {len(sgt_alerts)} alertas SGT (teclado Flutter)")
    return sgt_ids


def _buf(source, origin_app, payload):
    return {
        "source": source,
        "origin_app": origin_app,
        "payload": payload,
        "timestamp": (NOW - timedelta(hours=random.randint(1, 18))).isoformat(),
    }


# ═══════════════════════════════════════════════════════════════
# 6. BLACKLIST LINKS
# ═══════════════════════════════════════════════════════════════

def seed_blacklist_links(db):
    links = [
        {
            "url": "https://empleo-facil-cr.xyz/registro",
            "plataforma": "Web",
            "descripcion": "Sitio de reclutamiento fraudulento — captacion de victimas de trata con fachada de empleo. Dominio registrado hace 15 dias.",
        },
        {
            "url": "https://empleo-facil-cr.xyz/paso2",
            "plataforma": "Web",
            "descripcion": "Segunda etapa del sitio de reclutamiento — recoleccion de datos bancarios de victimas.",
        },
        {
            "url": "https://trabajo-modelo-cr.com/apply",
            "plataforma": "FB",
            "descripcion": "Landing page de captacion via Facebook Messenger — promete empleo de modelaje. Redirige a formulario de datos personales.",
        },
        {
            "url": "https://oportunidad-cr-empleo.net/info",
            "plataforma": "IG",
            "descripcion": "Anuncio de Instagram con empleo falso — vinculado a red de reclutamiento en zona norte de Costa Rica.",
        },
        {
            "url": "https://bk-costarica-seguro.xyz/login",
            "plataforma": "Web",
            "descripcion": "Sitio phishing bancario — replica la interfaz de banco costarricense para robar credenciales y OTP.",
        },
        {
            "url": "https://xk7m2p9q.workers.dev/jobs",
            "plataforma": "Web",
            "descripcion": "Dominio DGA (Cloudflare Workers) usado para distribuir ofertas de empleo falsas en Telegram. Alta probabilidad de generacion automatica.",
        },
        {
            "url": "https://priv-gallery-share.xyz",
            "plataforma": "Web",
            "descripcion": "Sitio de alojamiento de material intimo — usado para coaccionar victimas menores. Reportado por grooming.",
        },
        {
            "url": "https://empleos-jaco-cr.com/meseras",
            "plataforma": "FB",
            "descripcion": "Oferta de empleo fraudulenta en Jaco — fachada de restaurante para captacion de mujeres jovenes.",
        },
    ]

    for link in links:
        from analytics.app.services.infrastructure_service import extract_domain
        existing = db.query(BlacklistLink).filter_by(url=link["url"]).first()
        if existing:
            continue
        domain = extract_domain(link["url"])
        db.add(BlacklistLink(
            url=link["url"],
            dominio=domain,
            plataforma=link["plataforma"],
            descripcion=link["descripcion"],
            hits_reportados=random.randint(3, 25),
        ))

    db.commit()
    print(f"[OK] {len(links)} links en blacklist")


# ═══════════════════════════════════════════════════════════════
# 7. ANUNCIOS SOSPECHOSOS
# ═══════════════════════════════════════════════════════════════

def seed_suspicious_ads(db):
    ads = [
        {
            "url": "https://facebook.com/ads/empleo-facil-cr",
            "plataforma": "FB",
            "titulo": "Gana ₡500mil/mes — Trabajo facil para chicas",
            "descripcion": "Anuncio de Facebook con lenguaje de captacion. Perfil creado hace 7 dias con foto robada. Redirige a empleo-facil-cr.xyz.",
        },
        {
            "url": "https://instagram.com/p/empleo_cr_modelaje",
            "plataforma": "IG",
            "titulo": "Buscamos modelos — transporte incluido",
            "descripcion": "Post de Instagram con oferta de modelaje. Cuenta con 200 seguidores y 0 publicaciones previas. Contacto via DM.",
        },
        {
            "url": "https://facebook.com/ads/meseras-jaco-2026",
            "plataforma": "FB",
            "titulo": "Se necesitan meseras en Jaco — alojamiento gratis",
            "descripcion": "Anuncio segmentado a mujeres 18-25 en zonas rurales de Costa Rica. Patron de segmentacion consistente con captacion.",
        },
        {
            "url": "https://facebook.com/ads/oportunidad-norte",
            "plataforma": "FB",
            "titulo": "Oportunidades de trabajo en San Carlos",
            "descripcion": "Anuncio dirigido a zona norte. Promete transporte desde Nicaragua. Vinculado a cuenta que paga con BKA-3010001006.",
        },
        {
            "url": "https://instagram.com/stories/dinero_rapido_cr",
            "plataforma": "IG",
            "titulo": "Dinero rapido — sin experiencia",
            "descripcion": "Historia de Instagram con promesas de dinero facil. Cuenta automatizada con patrones de bot. Redirige a Telegram.",
        },
    ]

    for ad in ads:
        from analytics.app.services.infrastructure_service import extract_domain
        existing = db.query(SuspiciousAd).filter_by(url=ad["url"]).first()
        if existing:
            continue
        domain = extract_domain(ad["url"])
        db.add(SuspiciousAd(
            url=ad["url"],
            dominio=domain,
            plataforma=ad["plataforma"],
            titulo=ad["titulo"],
            descripcion=ad["descripcion"],
            hits_reportados=random.randint(5, 40),
        ))

    db.commit()
    print(f"[OK] {len(ads)} anuncios sospechosos")


# ═══════════════════════════════════════════════════════════════
# 8. EXTERNAL ALERTS (SafeCall)
# ═══════════════════════════════════════════════════════════════

def seed_external_alerts(db):
    alerts = [
        {
            "alert_type": "phone_fraud",
            "severity": "high",
            "description": "SafeCall: Numero 8888-1234 reportado 14 veces. Categorias: estafa (8), suplantacion (4), extorsion (2). Score riesgo: 87. Vinculado a campana de empleo falso.",
            "source_service": "safecall",
        },
        {
            "alert_type": "phone_fraud",
            "severity": "critical",
            "description": "SafeCall: Numero 8765-4321 reportado 22 veces. Categorias: extorsion (12), fraude (7), phishing (3). Score riesgo: 95. Mismo numero en buffer de alerta SGT.",
            "source_service": "safecall",
        },
        {
            "alert_type": "phone_fraud",
            "severity": "medium",
            "description": "SafeCall: Numero 7654-3210 reportado 6 veces. Categorias: spam (3), phishing (2), otro (1). Score riesgo: 62. Posible numero desechable.",
            "source_service": "safecall",
        },
        {
            "alert_type": "phone_spam",
            "severity": "high",
            "description": "SafeCall: Numero 6543-2100 reportado 18 veces como spam telefonico. Llamadas automatizadas ofreciendo 'oportunidades de empleo'. Patron de robocall.",
            "source_service": "safecall",
        },
        {
            "alert_type": "phone_fraud",
            "severity": "critical",
            "description": "SafeCall: Numero 8800-0001 reportado como linea de captacion. Multiples victimas reportan que el numero se usa para coordinar transporte de personas.",
            "source_service": "safecall",
        },
        {
            "alert_type": "phone_impersonation",
            "severity": "high",
            "description": "SafeCall: Numero 2222-0000 suplanta linea de atencion bancaria. Pide OTP a victimas. 9 reportes en 48h. Vinculado a phishing en bk-costarica-seguro.xyz.",
            "source_service": "safecall",
        },
    ]

    count = db.query(ExternalAlert).filter_by(source_service="safecall").count()
    if count >= len(alerts):
        print(f"[OK] {len(alerts)} alertas externas (ya existen)")
        return

    for alert in alerts:
        db.add(ExternalAlert(**alert))

    db.commit()
    print(f"[OK] {len(alerts)} alertas externas (SafeCall)")


# ═══════════════════════════════════════════════════════════════
# 9. FINSTA ALERTS (redes sociales)
# ═══════════════════════════════════════════════════════════════

def seed_finsta_alerts(db):
    alerts = [
        {
            "source": "finsta", "category": "reclutamiento_ilicito",
            "pattern_type": "recruitment_language", "score": 85, "level": "high",
            "reason": "Post con lenguaje de captacion: 'trabajo facil para chicas jovenes, transporte incluido'. Patron semantico de reclutamiento de trata.",
            "username": "empleo_facil_cr", "target_type": "post", "target_id": 1,
            "rules_triggered": [{"rule": "recruitment_keywords", "confidence": 0.85}],
        },
        {
            "source": "finsta", "category": "reclutamiento_ilicito",
            "pattern_type": "fake_profile", "score": 78, "level": "high",
            "reason": "Perfil creado hace 5 dias, 0 seguidores reales, 3 posts identicos con ofertas de empleo. Patron de cuenta fake de captacion.",
            "username": "modelo_cr_oficial", "target_type": "user", "target_id": 2,
            "rules_triggered": [{"rule": "new_profile_spam", "confidence": 0.78}],
        },
        {
            "source": "finsta", "category": "grooming",
            "pattern_type": "grooming_dm", "score": 90, "level": "critical",
            "reason": "DM con patron de grooming: adulto contacta menor ofreciendo regalos y pidiendo fotos. 8 mensajes en escalacion progresiva.",
            "username": "user_anon_42", "target_type": "message", "target_id": 3,
            "rules_triggered": [{"rule": "grooming_escalation", "confidence": 0.90}],
        },
        {
            "source": "finsta", "category": "sextorsion",
            "pattern_type": "extortion_threat", "score": 92, "level": "critical",
            "reason": "DM con amenaza explicita: 'tengo tus fotos, paga o publico'. Patron clasico de sextorsion digital.",
            "username": "threat_actor_7", "target_type": "message", "target_id": 4,
            "rules_triggered": [{"rule": "extortion_keywords", "confidence": 0.92}],
        },
        {
            "source": "finsta", "category": "landing_page_phishing",
            "pattern_type": "phishing_landing", "score": 88, "level": "high",
            "reason": "Landing page detectada con formulario de captura de datos personales. Dominio empleo-facil-cr.xyz registrado con privacidad whois.",
            "username": "empleo_facil_cr", "target_type": "landing_page", "target_id": 5,
            "rules_triggered": [{"rule": "landing_page_suspicious", "confidence": 0.88}],
        },
        {
            "source": "finsta", "category": "reclutamiento_ilicito",
            "pattern_type": "mass_dm_spam", "score": 75, "level": "high",
            "reason": "Usuario envia DMs masivos (50+ en 2h) con contenido identico de oferta de empleo. Patron de spam de captacion.",
            "username": "trabajo_jaco_2026", "target_type": "message", "target_id": 6,
            "rules_triggered": [{"rule": "mass_dm_detection", "confidence": 0.75}],
        },
        {
            "source": "finsta", "category": "fraude_digital",
            "pattern_type": "ad_network_fraud", "score": 70, "level": "medium",
            "reason": "Cuenta publica anuncios pagados con segmentacion a mujeres 18-25 en zonas rurales. Patron de targeting de captacion.",
            "username": "oportunidades_norte", "target_type": "post", "target_id": 7,
            "rules_triggered": [{"rule": "suspicious_ad_targeting", "confidence": 0.70}],
        },
        {
            "source": "finsta", "category": "trata_personas",
            "pattern_type": "transport_coordination", "score": 82, "level": "high",
            "reason": "Conversacion detectada coordinando transporte de personas desde zona norte. Menciona 'cruce', 'Los Chiles', 'grupo de 5'.",
            "username": "coordinador_norte", "target_type": "message", "target_id": 8,
            "rules_triggered": [{"rule": "transport_coordination", "confidence": 0.82}],
        },
    ]

    count = db.query(FinstaAlert).filter_by(source="finsta").count()
    if count >= len(alerts):
        print(f"[OK] {len(alerts)} alertas Finsta (ya existen)")
        return

    for alert in alerts:
        db.add(FinstaAlert(**alert))

    db.commit()
    print(f"[OK] {len(alerts)} alertas Finsta")


# ═══════════════════════════════════════════════════════════════
# 10. INVESTIGACIONES
# ═══════════════════════════════════════════════════════════════

def seed_investigations(db):
    investigations = [
        {
            "case_number": f"FL-{NOW.strftime('%Y%m%d')}-00001",
            "account_number": "BKA-3010001001",
            "bank_code": "BKA",
            "category": "legitimacion_capitales",
            "status": "open",
            "priority": "critical",
            "assigned_to": "Unidad AML — CONATT",
            "notes": "Cuenta hub con patron many-to-one. Recibe de 6 mulas y transfiere a corredor offshore. Vinculada a alertas SGT de reclutamiento.",
            "risk_score": 95,
            "pattern_types": ["many_to_one_hub", "rapid_inflow_outflow", "layering_corridor"],
        },
        {
            "case_number": f"FL-{NOW.strftime('%Y%m%d')}-00002",
            "account_number": "BKB-3020002003",
            "bank_code": "BKB",
            "category": "legitimacion_capitales",
            "status": "in_progress",
            "priority": "high",
            "assigned_to": "Analista CR-042",
            "notes": "Red de smurfing con 5 depositos fraccionados en efectivo desde 2 cuentas en Alajuela. Fondos consolidados y enviados offshore.",
            "risk_score": 85,
            "pattern_types": ["smurfing_cash", "integration_offshore"],
        },
        {
            "case_number": f"FL-{NOW.strftime('%Y%m%d')}-00003",
            "account_number": "BKA-3010001004",
            "bank_code": "BKA",
            "category": "trata_personas",
            "status": "escalated",
            "priority": "critical",
            "assigned_to": "Fiscalia Especial — OIJ",
            "notes": "Victima potencial: cambio de PIN reciente + link de blacklist abierto + transferencia desde hub. MODO RESCATE activado.",
            "risk_score": 93,
            "pattern_types": ["credential_change_suspicious", "rescue_mode"],
        },
    ]

    for inv in investigations:
        existing = db.query(Investigation).filter_by(case_number=inv["case_number"]).first()
        if existing:
            continue
        db.add(Investigation(**inv))

    db.commit()
    print(f"[OK] {len(investigations)} investigaciones")


# ═══════════════════════════════════════════════════════════════

if __name__ == "__main__":
    main()
