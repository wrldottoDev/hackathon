from __future__ import annotations

import unittest
from datetime import datetime, timedelta, timezone

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from analytics.app.database import Base
from analytics.app.models.blacklist_link import BlacklistLink
from analytics.app.models.external_alert import ExternalAlert
from analytics.app.models.observed_account import ObservedAccount
from analytics.app.models.secure_alert import SecureAlert
from analytics.app.models.suspicious_ad import SuspiciousAd
from analytics.app.services.infrastructure_service import (
    build_heatmap,
    detect_alert_link_indicators,
    evaluate_rescue_mode_for_alert,
)


class InfrastructureServiceTest(unittest.TestCase):
    def setUp(self) -> None:
        engine = create_engine("sqlite:///:memory:", future=True)
        Base.metadata.create_all(bind=engine)
        self.Session = sessionmaker(bind=engine, autoflush=False, autocommit=False)

    def test_detects_blacklist_and_triggers_rescue_mode(self) -> None:
        with self.Session() as db:
            now = datetime.now(timezone.utc)
            db.add(
                BlacklistLink(
                    url="https://trabajo-urgente-xj92ab.com/oferta",
                    dominio="trabajo-urgente-xj92ab.com",
                    ip_origen="198.51.100.10",
                    plataforma="Web",
                    hits_reportados=0,
                    descripcion="Captacion laboral fraudulenta",
                )
            )
            db.add(
                SuspiciousAd(
                    url="https://trabajo-urgente-xj92ab.com/oferta",
                    dominio="trabajo-urgente-xj92ab.com",
                    ip_origen="198.51.100.10",
                    plataforma="Web",
                    hits_reportados=0,
                    titulo="Empleo remoto inmediato",
                    descripcion="Anuncio previamente indexado por fraude.",
                )
            )
            db.add(
                ObservedAccount(
                    bank_code="BKA",
                    account_number="BKA-1234567890",
                    balance=0,
                    currency="CRC",
                    status="active",
                    current_location="San Carlos, Alajuela",
                    last_credentials_change_at=now - timedelta(hours=2),
                    created_at=now - timedelta(days=1),
                )
            )
            alert = SecureAlert(
                hash_denuncia="case-1",
                timestamp=now - timedelta(minutes=30),
                ubicacion_gps="10.323000,-84.431000",
                latitude=10.323,
                longitude=-84.431,
                entidades_extraidas=[],
                estado_investigacion="pendiente",
                metadata_reporte={},
                buffer_texto=[
                    {
                        "source": "Keyboard",
                        "origin_app": "com.instagram.android",
                        "payload": (
                            "Escribime por https://trabajo-urgente-xj92ab.com/oferta "
                            "para activar el pago."
                        ),
                        "timestamp": now.isoformat(),
                    }
                ],
                origen_app="com.instagram.android",
                riesgo_probabilidad="0.93",
                client_ip="127.0.0.1",
                algorithm="RSA-OAEP-256/AES-256-GCM",
            )
            db.add(alert)
            db.commit()
            db.refresh(alert)

            indicators = detect_alert_link_indicators(db, alert, increment_hits=True)
            self.assertEqual(len(indicators), 1)
            self.assertTrue(indicators[0]["blacklist_match"])
            self.assertTrue(indicators[0]["suspicious_ad_match"])

            rescue = evaluate_rescue_mode_for_alert(
                db,
                alert,
                link_indicators=indicators,
            )
            self.assertTrue(rescue["triggered"])
            self.assertEqual(rescue["region"], "zona_norte")
            self.assertEqual(
                db.query(ExternalAlert).filter(
                    ExternalAlert.alert_type == "modo_rescate_blacklist"
                ).count(),
                1,
            )

    def test_heatmap_fallback_groups_alerts_by_distance(self) -> None:
        with self.Session() as db:
            now = datetime.now(timezone.utc)
            alerts = [
                SecureAlert(
                    hash_denuncia="hm-1",
                    timestamp=now - timedelta(minutes=15),
                    ubicacion_gps="10.320000,-84.430000",
                    latitude=10.320000,
                    longitude=-84.430000,
                    entidades_extraidas=[],
                    estado_investigacion="pendiente",
                    metadata_reporte={},
                    buffer_texto=[],
                    origen_app="com.whatsapp",
                    riesgo_probabilidad="0.80",
                    client_ip="127.0.0.1",
                    algorithm="RSA-OAEP-256/AES-256-GCM",
                ),
                SecureAlert(
                    hash_denuncia="hm-2",
                    timestamp=now - timedelta(minutes=10),
                    ubicacion_gps="10.321000,-84.431000",
                    latitude=10.321000,
                    longitude=-84.431000,
                    entidades_extraidas=[],
                    estado_investigacion="pendiente",
                    metadata_reporte={},
                    buffer_texto=[],
                    origen_app="com.whatsapp",
                    riesgo_probabilidad="0.90",
                    client_ip="127.0.0.1",
                    algorithm="RSA-OAEP-256/AES-256-GCM",
                ),
                SecureAlert(
                    hash_denuncia="hm-3",
                    timestamp=now - timedelta(minutes=5),
                    ubicacion_gps="9.930000,-84.080000",
                    latitude=9.930000,
                    longitude=-84.080000,
                    entidades_extraidas=[],
                    estado_investigacion="pendiente",
                    metadata_reporte={},
                    buffer_texto=[],
                    origen_app="com.whatsapp",
                    riesgo_probabilidad="0.20",
                    client_ip="127.0.0.1",
                    algorithm="RSA-OAEP-256/AES-256-GCM",
                ),
            ]
            db.add_all(alerts)
            db.commit()

            clusters = build_heatmap(
                db,
                lookback_hours=24,
                eps_meters=500.0,
                min_points=2,
                limit=100,
            )
            self.assertEqual(len(clusters), 1)
            self.assertEqual(clusters[0]["hit_count"], 2)
            self.assertEqual(sorted(clusters[0]["alert_ids"]), [1, 2])


if __name__ == "__main__":
    unittest.main()
