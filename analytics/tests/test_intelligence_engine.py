from __future__ import annotations

import unittest
from datetime import datetime, timedelta, timezone
from decimal import Decimal

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from analytics.app.database import Base
from analytics.app.models.observed_transaction import ObservedTransaction
from analytics.app.models.secure_alert import SecureAlert
from analytics.app.schemas.resolved_case import GeminiCorrelationOutput
from analytics.app.services.intelligence_engine import (
    InsufficientCorrelationData,
    IntelligenceEngine,
)


class _StubAnalyzer:
    def __init__(self) -> None:
        self.last_prompt = ""
        self.last_model_name = ""

    def analyze(self, *, prompt: str, model_name: str) -> GeminiCorrelationOutput:
        self.last_prompt = prompt
        self.last_model_name = model_name
        return GeminiCorrelationOutput(
            score_de_vinculacion=0.87,
            justificacion_tecnica=(
                "Se observa convergencia entre los tokens financieros "
                "mencionados en las alertas y los beneficiarios de las "
                "transacciones del mismo periodo, con actividad tambien "
                "alineada en Zona Norte."
            ),
            coincidencias_financieras=["ACCT_ABCDEF123456", "SINPE_123456ABCDEF"],
            patron_muchas_a_una=["ACCT_ABCDEF123456"],
            correlacion_geografica="Coincidencia operativa en zona_norte.",
            beneficiarios_prioritarios=["ACCT_ABCDEF123456"],
        )


class IntelligenceEngineTest(unittest.TestCase):
    def setUp(self) -> None:
        engine = create_engine("sqlite:///:memory:", future=True)
        Base.metadata.create_all(bind=engine)
        self.Session = sessionmaker(bind=engine, autoflush=False, autocommit=False)

    def test_correlates_recent_alerts_and_masks_pii(self) -> None:
        analyzer = _StubAnalyzer()
        intelligence = IntelligenceEngine(
            analyzer=analyzer,
            model_name="gemini-2.5-pro",
            tokenization_salt="unit-test-salt",
        )

        with self.Session() as db:
            now = datetime.now(timezone.utc)
            db.add(
                SecureAlert(
                    hash_denuncia="hash-a",
                    timestamp=now - timedelta(hours=1),
                    ubicacion_gps="10.402000,-84.430000",
                    entidades_extraidas=["Cuenta BKB-1043968696"],
                    estado_investigacion="pendiente",
                    metadata_reporte={"canal": "ime"},
                    buffer_texto=[
                        {
                            "source": "Keyboard",
                            "origin_app": "com.whatsapp",
                            "payload": "Deposita al SINPE 88887777 o a la cuenta BKB-1043968696",
                            "timestamp": (now - timedelta(hours=1)).isoformat(),
                        }
                    ],
                    origen_app="com.whatsapp",
                    riesgo_probabilidad="0.92",
                    client_ip="127.0.0.1",
                    algorithm="RSA-OAEP-256/AES-256-GCM",
                )
            )
            db.add_all(
                [
                    ObservedTransaction(
                        bank_code="BKB",
                        external_transaction_id=1001,
                        source_account_number="BKA-9919812708",
                        destination_account_number="BKB-1043968696",
                        source_bank_code="BKA",
                        destination_bank_code="BKB",
                        amount=Decimal("245000.00"),
                        currency="CRC",
                        transaction_type="transfer",
                        status="completed",
                        channel="sinpe_movil",
                        location="San Carlos, Alajuela",
                        beneficiary="Jose Perez",
                        concept="SINPE a 88887777",
                        description="Pago inmediato",
                        external_reference="REF-01",
                        created_at=now - timedelta(minutes=50),
                    ),
                    ObservedTransaction(
                        bank_code="BKC",
                        external_transaction_id=1002,
                        source_account_number="BKC-1111222233",
                        destination_account_number="BKB-1043968696",
                        source_bank_code="BKC",
                        destination_bank_code="BKB",
                        amount=Decimal("98000.00"),
                        currency="CRC",
                        transaction_type="deposit",
                        status="completed",
                        channel="branch",
                        location="San Carlos, Alajuela",
                        beneficiary="Jose Perez",
                        concept="Deposito en ventanilla",
                        description="Abono",
                        external_reference="REF-02",
                        created_at=now - timedelta(minutes=40),
                    ),
                ]
            )
            db.commit()

            case = intelligence.correlate_recent_activity(
                db,
                lookback_hours=24,
                alert_limit=10,
                transaction_limit=20,
            )

            self.assertAlmostEqual(case.score_de_vinculacion, 0.87)
            self.assertEqual(case.gemini_model, "gemini-2.5-pro")
            self.assertEqual(len(case.alert_ids), 1)
            self.assertEqual(len(case.transaction_ids), 2)
            self.assertIn("zona_norte", analyzer.last_prompt)
            self.assertNotIn("BKB-1043968696", analyzer.last_prompt)
            self.assertNotIn("88887777", analyzer.last_prompt)
            self.assertNotIn("Jose Perez", analyzer.last_prompt)
            self.assertIn("ACCT_", analyzer.last_prompt)
            self.assertIn("SINPE_", analyzer.last_prompt)

    def test_raises_when_no_recent_alerts_exist(self) -> None:
        intelligence = IntelligenceEngine(
            analyzer=_StubAnalyzer(),
            model_name="gemini-2.5-pro",
            tokenization_salt="unit-test-salt",
        )
        with self.Session() as db:
            with self.assertRaises(InsufficientCorrelationData):
                intelligence.correlate_recent_activity(
                    db,
                    lookback_hours=24,
                    alert_limit=10,
                    transaction_limit=20,
                )


if __name__ == "__main__":
    unittest.main()
