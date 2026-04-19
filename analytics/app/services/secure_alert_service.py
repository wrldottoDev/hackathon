import hashlib
import json
from typing import Any

from sqlalchemy.orm import Session

from ..models.secure_alert import SecureAlert
from ..schemas.secure_alert import DecryptedAlertReport
from .geo_utils import parse_coordinates_from_text
from .infrastructure_service import detect_alert_link_indicators, evaluate_rescue_mode_for_alert


def persist_secure_alert(
    db: Session,
    *,
    report: DecryptedAlertReport,
    client_ip: str | None,
    algorithm: str,
) -> SecureAlert:
    payload = report.model_dump(mode="json")
    hash_denuncia = build_report_hash(payload)

    existing = (
        db.query(SecureAlert)
        .filter(SecureAlert.hash_denuncia == hash_denuncia)
        .one_or_none()
    )
    if existing is not None:
        return existing

    formatted_location = format_location(report.ubicacion_gps)
    coordinates = parse_coordinates_from_text(formatted_location)
    metadata = dict(report.metadata)

    alert = SecureAlert(
        hash_denuncia=hash_denuncia,
        ubicacion_gps=formatted_location,
        latitude=coordinates[0] if coordinates else None,
        longitude=coordinates[1] if coordinates else None,
        entidades_extraidas=list(report.entidades_extraidas),
        metadata_reporte=metadata,
        buffer_texto=[event.model_dump(mode="json") for event in report.buffer_texto],
        origen_app=report.origen_app,
        riesgo_probabilidad=f"{report.riesgo_probabilidad:.2f}",
        client_ip=client_ip,
        algorithm=algorithm,
        notas="Registro local con hash de integridad estilo blockchain mock.",
    )
    db.add(alert)
    db.commit()
    db.refresh(alert)

    link_indicators = detect_alert_link_indicators(db, alert, increment_hits=True)
    rescue_mode = evaluate_rescue_mode_for_alert(
        db,
        alert,
        link_indicators=link_indicators,
    )
    if link_indicators or rescue_mode.get("triggered"):
        alert.metadata_reporte = {
            **dict(alert.metadata_reporte or {}),
            "infrastructure_links": link_indicators,
            "rescue_mode": rescue_mode,
        }
        db.add(alert)
        db.commit()
        db.refresh(alert)
    return alert


def get_secure_alert(db: Session, alert_id: int) -> SecureAlert | None:
    return db.query(SecureAlert).filter(SecureAlert.id == alert_id).one_or_none()


def build_report_hash(payload: dict[str, Any]) -> str:
    canonical_payload = json.dumps(
        payload,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    )
    return hashlib.sha256(canonical_payload.encode("utf-8")).hexdigest()


def format_location(location) -> str:
    if location is None:
        return "sin_datos"
    if location.latitude is None or location.longitude is None:
        return "sin_datos"

    latitude = f"{location.latitude:.6f}"
    longitude = f"{location.longitude:.6f}"
    if location.precision_meters is None:
        return f"{latitude},{longitude}"
    return f"{latitude},{longitude} (±{location.precision_meters:.1f}m)"
