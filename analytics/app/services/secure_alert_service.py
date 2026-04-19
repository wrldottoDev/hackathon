import hashlib
import json
from typing import Any

from sqlalchemy.orm import Session

from ..models.secure_alert import SecureAlert
from ..schemas.secure_alert import DecryptedAlertReport


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

    alert = SecureAlert(
        hash_denuncia=hash_denuncia,
        ubicacion_gps=format_location(report.ubicacion_gps),
        entidades_extraidas=list(report.entidades_extraidas),
        metadata_reporte=dict(report.metadata),
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
