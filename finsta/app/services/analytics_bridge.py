from __future__ import annotations

import logging
from datetime import datetime, timezone

import httpx

from ..schemas.analysis import AnalysisResult, FinstaAlertForAnalytics
from ..settings import ANALYTICS_API_KEY, ANALYTICS_API_URL

logger = logging.getLogger(__name__)

CATEGORY_MAP = {
    "enlace_sospechoso": "captacion_digital",
    "analisis_semantico": "captacion_digital",
    "anomalia_perfil": "captacion_digital",
    "spam_mensajes_directos": "captacion_digital",
}


def _score_to_level(score: int) -> str:
    if score <= 30:
        return "low"
    if score <= 60:
        return "medium"
    if score <= 80:
        return "high"
    return "critical"


def build_alert_for_analytics(result: AnalysisResult) -> FinstaAlertForAnalytics:
    primary_rule = result.rules_triggered[0].rule_name if result.rules_triggered else "unknown"
    category = CATEGORY_MAP.get(primary_rule, "captacion_digital")

    reasons = [r.detail for r in result.rules_triggered]
    reason_text = " | ".join(reasons) if reasons else "Sin detalle"

    return FinstaAlertForAnalytics(
        source="finsta",
        category=category,
        pattern_type=f"finsta_{primary_rule}",
        score=result.total_score,
        level=_score_to_level(result.total_score),
        reason=reason_text,
        username=result.username,
        target_type=result.target_type,
        target_id=result.target_id,
        rules_triggered=result.rules_triggered,
        created_at=result.analyzed_at,
    )


async def send_alerts_to_analytics(
    alerts: list[FinstaAlertForAnalytics],
) -> dict:
    payload = [alert.model_dump(mode="json") for alert in alerts]

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(
                f"{ANALYTICS_API_URL}/finsta-alerts",
                json=payload,
                headers={"X-API-Key": ANALYTICS_API_KEY},
            )
            response.raise_for_status()
            return {"status": "sent", "count": len(alerts)}
    except Exception as exc:
        logger.warning("Failed to send alerts to analytics: %s", exc)
        return {"status": "error", "detail": str(exc), "count": len(alerts)}
