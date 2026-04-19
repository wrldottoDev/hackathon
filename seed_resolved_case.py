#!/usr/bin/env python3
"""
═══════════════════════════════════════════════════════════════════
Sentinel-Link — Genera un Resolved Case (con o sin Gemini)
═══════════════════════════════════════════════════════════════════

Si Gemini está disponible, ejecuta la correlación real.
Si no (rate limit o sin API key), genera un caso con hallazgos
simulados realistas para demostración.

Uso:
  python seed_resolved_case.py          # intenta Gemini, fallback a simulado
  python seed_resolved_case.py --force-simulated   # siempre simulado
  python seed_resolved_case.py --force-gemini      # solo Gemini (falla si no hay cuota)

Después de ejecutar, accede a:
  GET /cases/resolved                         → lista de casos
  GET /reports/cases/{id}/evidence.json       → dossier JSON
  GET /reports/cases/{id}/evidence.pdf        → dossier PDF
═══════════════════════════════════════════════════════════════════
"""

from __future__ import annotations

import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

project_root = Path(__file__).resolve().parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from analytics.app.database import SessionLocal, engine, Base
from analytics.app.models.observed_transaction import ObservedTransaction
from analytics.app.models.resolved_case import ResolvedCase
from analytics.app.models.secure_alert import SecureAlert
from analytics.app.services.intelligence_engine import (
    IntelligenceEngine,
    GeminiCorrelationFailure,
    InsufficientCorrelationData,
    IntelligenceEngineUnavailable,
)

NOW = datetime.now(timezone.utc).replace(microsecond=0)


def try_gemini(db) -> ResolvedCase | None:
    try:
        engine_instance = IntelligenceEngine()
        case = engine_instance.correlate_recent_activity(
            db,
            lookback_hours=48,
            alert_limit=20,
            transaction_limit=200,
        )
        return case
    except IntelligenceEngineUnavailable as e:
        print(f"  Gemini no disponible: {e}")
        return None
    except GeminiCorrelationFailure as e:
        print(f"  Gemini fallo (rate limit?): {e}")
        return None
    except InsufficientCorrelationData as e:
        print(f"  Datos insuficientes: {e}")
        return None


def create_simulated_case(db) -> ResolvedCase:
    period_end = NOW
    period_start = NOW - timedelta(hours=48)

    alert_ids = [
        a.id for a in
        db.query(SecureAlert)
        .filter(SecureAlert.timestamp >= period_start)
        .order_by(SecureAlert.timestamp.desc())
        .limit(20)
        .all()
    ]
    transaction_ids = [
        t.id for t in
        db.query(ObservedTransaction)
        .filter(ObservedTransaction.created_at >= period_start)
        .order_by(ObservedTransaction.created_at.desc())
        .limit(200)
        .all()
    ]

    case = ResolvedCase(
        period_start=period_start,
        period_end=period_end,
        score_de_vinculacion=0.94,
        justificacion_tecnica=(
            "Analisis de correlacion identifica una red estructurada de legitimacion "
            "de capitales vinculada a trata de personas. Se detectaron 6 cuentas mula "
            "que depositan a un hub central (BKA-3010001001), el cual canaliza fondos "
            "a traves de un corredor financiero (BKB-3020002001) hacia una cuenta "
            "offshore en Panama (BKC-3030003004). Paralelamente, 12 alertas SGT del "
            "teclado muestran patrones de grooming, reclutamiento fraudulento y "
            "sextorsion en WhatsApp, Facebook Messenger, Instagram y Telegram. Los "
            "links detectados (empleo-facil-cr.xyz, trabajo-modelo-cr.com, "
            "oportunidad-cr-empleo.net) coinciden con la blacklist interna y con "
            "anuncios sospechosos en Facebook e Instagram. El dominio "
            "xk7m2p9q.workers.dev presenta patron DGA con score 0.78. Se activo el "
            "Modo Rescate: la cuenta BKA-3010001004 registra cambio de PIN hace 2h "
            "en la misma zona geografica (Heredia) donde se detecto un link de "
            "blacklist. La correlacion geografica muestra concentracion de actividad "
            "en Zona Norte (San Carlos/Los Chiles) consistente con corredor de trafico "
            "transfronterizo. Smurfing detectado en Alajuela con 5 depositos "
            "fraccionados en efectivo (₡175K-₡210K) desde 2 cuentas hacia el receptor "
            "BKB-3020002003. Monto total correlacionado: ₡14.2M en 48h."
        ),
        hallazgos_json={
            "coincidencias_financieras": [
                "Token acct_BKA3010001001 aparece en 4 alertas SGT y recibe de 6 cuentas",
                "Token acct_BKB3020002001 es corredor entre hub y offshore",
                "Token acct_BKC3030003004 (Panama Holdings LLC) recibe fondos consolidados",
                "Referencia 'META ADS' en transacciones coincide con pagos de campanas de reclutamiento",
                "Mencion de SINPE y cuenta BKA-3010001002 en buffer de chat sobre coordinacion de traslado de personas",
            ],
            "patron_muchas_a_una": [
                "6 cuentas → BKA-3010001001 (hub): ₡960,000 en 12h",
                "2 cuentas smurfing → BKB-3020002003: ₡965,000 fraccionados en cash",
                "Hub + smurfing + dormida → BKC-3030003004 (offshore): ₡5,630,000",
            ],
            "correlacion_geografica": (
                "Zona Norte (San Carlos, Los Chiles): 3 alertas SGT + 2 transacciones. "
                "Corredor costero Limon: 2 alertas + 2 transacciones mula. "
                "Concentracion en GAM (San Jose, Heredia, Alajuela): 7 alertas + 15 transacciones. "
                "Guanacaste: 1 alerta reclutamiento + 1 transaccion mula."
            ),
            "beneficiarios_prioritarios": [
                "Panama Holdings LLC — receptor offshore de fondos consolidados",
                "Inversiones CR S.A. — entidad intermedia en corredor financiero",
                "Transporte Norte S.A. — pagos de logistica fronteriza",
                "META ADS / Google ADS CR — financiamiento de campanas de reclutamiento",
            ],
            "links_con_patron_dga": [
                "xk7m2p9q.workers.dev — DGA score: 0.78, usado en Telegram para distribuir ofertas falsas",
            ],
            "coincidencias_anuncios_fraudulentos": [
                "empleo-facil-cr.xyz vinculado a anuncio FB 'Gana ₡500mil/mes — Trabajo facil para chicas'",
                "trabajo-modelo-cr.com vinculado a anuncio FB 'Buscamos modelos — transporte incluido'",
                "empleos-jaco-cr.com vinculado a anuncio FB 'Se necesitan meseras en Jaco — alojamiento gratis'",
                "oportunidad-cr-empleo.net vinculado a anuncio IG segmentado a mujeres 18-25 en zonas rurales",
            ],
            "coincidencias_blacklist_links": [
                "empleo-facil-cr.xyz/registro — blacklist match, 15 hits reportados",
                "empleo-facil-cr.xyz/paso2 — blacklist match, recoleccion de datos bancarios",
                "bk-costarica-seguro.xyz/login — phishing bancario, 22 hits",
                "priv-gallery-share.xyz — material intimo coercitivo, grooming",
                "xk7m2p9q.workers.dev/jobs — DGA, distribucion via Telegram",
            ],
            "alerta_rescate": True,
            "resumen_precalculado": {
                "conteo_alertas": len(alert_ids),
                "conteo_transacciones": len(transaction_ids),
                "correlacion_geografica": {
                    "zona_norte_alertas": 3,
                    "zona_norte_transacciones": 2,
                },
                "tokens_financieros_coincidentes": [
                    "acct_hub_principal",
                    "acct_corredor_financiero",
                    "acct_offshore_panama",
                    "META ADS",
                    "SINPE",
                ],
            },
        },
        alert_ids=alert_ids,
        transaction_ids=transaction_ids,
        gemini_model="gemini-2.5-pro-simulated",
        prompt_hash="simulated_" + NOW.strftime("%Y%m%d%H%M%S"),
    )
    db.add(case)
    db.commit()
    db.refresh(case)
    return case


def main():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    force_simulated = "--force-simulated" in sys.argv
    force_gemini = "--force-gemini" in sys.argv

    try:
        print("=" * 60)
        print("  Sentinel-Link — Generating Resolved Case")
        print("=" * 60)

        case = None

        if not force_simulated:
            print("\n[1] Intentando correlacion con Gemini...")
            case = try_gemini(db)
            if case:
                print(f"  Caso creado con Gemini real! ID: {case.id}")
                print(f"  Score de vinculacion: {case.score_de_vinculacion}")

        if case is None and not force_gemini:
            print("\n[2] Generando caso con hallazgos simulados...")
            case = create_simulated_case(db)
            print(f"  Caso simulado creado. ID: {case.id}")
            print(f"  Score de vinculacion: {case.score_de_vinculacion}")

        if case is None:
            print("\n[!] No se pudo crear el caso. Verifica la API key de Gemini.")
            return

        print(f"\n{'=' * 60}")
        print(f"  Caso Resuelto ID: {case.id}")
        print(f"  Periodo: {case.period_start} → {case.period_end}")
        print(f"  Score: {case.score_de_vinculacion}")
        print(f"  Alertas vinculadas: {len(case.alert_ids)}")
        print(f"  Transacciones vinculadas: {len(case.transaction_ids)}")
        print(f"  Modelo: {case.gemini_model}")
        print(f"{'=' * 60}")
        print()
        print("  Endpoints disponibles:")
        print(f"    GET /cases/resolved/{case.id}")
        print(f"    GET /reports/cases/{case.id}/evidence.json")
        print(f"    GET /reports/cases/{case.id}/evidence.pdf")
        print()
        print("  Ejemplo:")
        print(f"    curl -s http://127.0.0.1:8003/cases/resolved/{case.id} \\")
        print(f'      -H "X-Analytics-Key: flowlens-analytics-key-dev" | python3 -m json.tool')

    finally:
        db.close()


if __name__ == "__main__":
    main()
