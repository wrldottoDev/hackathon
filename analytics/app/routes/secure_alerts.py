from fastapi import APIRouter, Depends, HTTPException, Request, status
from pydantic import ValidationError
from sqlalchemy.orm import Session

from ..database import get_db
from ..schemas.secure_alert import (
    DecryptedAlertReport,
    EncryptedAlertEnvelope,
    SecureAlertDetailResponse,
    SecureAlertReceiptResponse,
)
from ..services.crypto_service import SecureAlertCryptographyError, decrypt_alert_envelope
from ..services.secure_alert_service import get_secure_alert, persist_secure_alert

router = APIRouter(
    prefix="/api/v1/alertas",
    tags=["secure-alerts"],
)


@router.post("", response_model=SecureAlertReceiptResponse, status_code=status.HTTP_201_CREATED)
def create_secure_alert(
    envelope: EncryptedAlertEnvelope,
    request: Request,
    db: Session = Depends(get_db),
):
    try:
        decrypted_payload = decrypt_alert_envelope(envelope)
        report = DecryptedAlertReport.model_validate(decrypted_payload)
        alert = persist_secure_alert(
            db,
            report=report,
            client_ip=getattr(request.state, "secure_alert_client_ip", None),
            algorithm=envelope.algorithm,
        )
    except (SecureAlertCryptographyError, ValidationError) as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No se pudo procesar la alerta cifrada.",
        ) from exc
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="No se pudo completar la solicitud.",
        ) from exc

    return SecureAlertReceiptResponse(
        id=alert.id,
        hash_denuncia=alert.hash_denuncia,
        recibo_inmutabilidad=alert.hash_denuncia,
        timestamp=alert.timestamp,
        estado_investigacion=alert.estado_investigacion,
    )


@router.get("/{alert_id}", response_model=SecureAlertDetailResponse)
def get_secure_alert_detail(
    alert_id: int,
    db: Session = Depends(get_db),
):
    alert = get_secure_alert(db, alert_id)
    if alert is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Alerta no encontrada.",
        )

    return SecureAlertDetailResponse(
        id=alert.id,
        hash_denuncia=alert.hash_denuncia,
        recibo_inmutabilidad=alert.hash_denuncia,
        timestamp=alert.timestamp,
        estado_investigacion=alert.estado_investigacion,
        ubicacion_gps=alert.ubicacion_gps,
        entidades_extraidas=list(alert.entidades_extraidas or []),
        metadata_reporte=dict(alert.metadata_reporte or {}),
        buffer_texto=list(alert.buffer_texto or []),
        origen_app=alert.origen_app,
        riesgo_probabilidad=alert.riesgo_probabilidad,
    )
