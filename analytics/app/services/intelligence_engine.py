from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from decimal import Decimal
from typing import Protocol

from sqlalchemy.orm import Session

from ..models.observed_transaction import ObservedTransaction
from ..models.resolved_case import ResolvedCase
from ..models.secure_alert import SecureAlert
from ..schemas.resolved_case import GeminiCorrelationOutput
from ..settings import (
    GEMINI_API_KEY,
    GEMINI_CORRELATION_ALERT_LIMIT,
    GEMINI_CORRELATION_TRANSACTION_LIMIT,
    GEMINI_CORRELATION_WINDOW_HOURS,
    GEMINI_MODEL,
    PII_TOKENIZATION_SALT,
)
from .pii_tokenizer import PiiTokenizer


class IntelligenceEngineError(Exception):
    pass


class IntelligenceEngineUnavailable(IntelligenceEngineError):
    pass


class InsufficientCorrelationData(IntelligenceEngineError):
    pass


class GeminiCorrelationFailure(IntelligenceEngineError):
    pass


class CorrelationAnalyzer(Protocol):
    def analyze(
        self,
        *,
        prompt: str,
        model_name: str,
    ) -> GeminiCorrelationOutput: ...


@dataclass(frozen=True)
class CorrelationWindow:
    period_start: datetime
    period_end: datetime
    alerts: list[SecureAlert]
    transactions: list[ObservedTransaction]


class GeminiCorrelationAnalyzer:
    """Uses the supported Google GenAI SDK.

    The legacy `google-generativeai` Python package is deprecated and not actively
    maintained. This implementation uses `google-genai`, which is the official
    replacement recommended by Google.
    """

    def __init__(self, api_key: str | None) -> None:
        if not api_key:
            raise IntelligenceEngineUnavailable(
                "GEMINI_API_KEY no esta configurada para ejecutar correlacion."
            )
        self._api_key = api_key

    def analyze(
        self,
        *,
        prompt: str,
        model_name: str,
    ) -> GeminiCorrelationOutput:
        try:
            from google import genai
            from google.genai import types
        except ModuleNotFoundError as exc:
            raise IntelligenceEngineUnavailable(
                "google-genai no esta instalado en el entorno de analytics."
            ) from exc

        client = genai.Client(api_key=self._api_key)
        try:
            response = client.models.generate_content(
                model=model_name,
                contents=prompt,
                config=types.GenerateContentConfig(
                    temperature=0.1,
                    max_output_tokens=1200,
                    response_mime_type="application/json",
                    response_schema=GeminiCorrelationOutput,
                ),
            )
        except Exception as exc:  # noqa: BLE001
            raise GeminiCorrelationFailure(
                "La API de Gemini no pudo completar el analisis de correlacion."
            ) from exc
        finally:
            client.close()

        parsed = getattr(response, "parsed", None)
        if isinstance(parsed, GeminiCorrelationOutput):
            return parsed
        if isinstance(parsed, dict):
            return GeminiCorrelationOutput.model_validate(parsed)

        text = getattr(response, "text", "")
        if text:
            return GeminiCorrelationOutput.model_validate_json(text)
        raise GeminiCorrelationFailure("Gemini devolvio una respuesta vacia.")


class IntelligenceEngine:
    def __init__(
        self,
        *,
        analyzer: CorrelationAnalyzer | None = None,
        model_name: str = GEMINI_MODEL,
        tokenization_salt: str = PII_TOKENIZATION_SALT,
    ) -> None:
        self._analyzer = analyzer or GeminiCorrelationAnalyzer(GEMINI_API_KEY)
        self._model_name = model_name
        self._tokenizer = PiiTokenizer(tokenization_salt)

    def correlate_recent_activity(
        self,
        db: Session,
        *,
        lookback_hours: int = GEMINI_CORRELATION_WINDOW_HOURS,
        alert_limit: int = GEMINI_CORRELATION_ALERT_LIMIT,
        transaction_limit: int = GEMINI_CORRELATION_TRANSACTION_LIMIT,
    ) -> ResolvedCase:
        window = self._load_window(
            db,
            lookback_hours=lookback_hours,
            alert_limit=alert_limit,
            transaction_limit=transaction_limit,
        )
        alert_payloads = [self._serialize_alert(alert) for alert in window.alerts]
        transaction_payloads = [
            self._serialize_transaction(transaction)
            for transaction in window.transactions
        ]
        precomputed = self._build_precomputed_summary(
            alert_payloads,
            transaction_payloads,
        )
        prompt = self.build_prompt(
            period_start=window.period_start,
            period_end=window.period_end,
            alert_payloads=alert_payloads,
            transaction_payloads=transaction_payloads,
            precomputed_summary=precomputed,
        )
        analysis = self._analyzer.analyze(
            prompt=prompt,
            model_name=self._model_name,
        )
        return self._persist_case(
            db,
            window=window,
            prompt=prompt,
            analysis=analysis,
            precomputed=precomputed,
        )

    def list_cases(self, db: Session, *, limit: int = 50) -> list[ResolvedCase]:
        return (
            db.query(ResolvedCase)
            .order_by(ResolvedCase.created_at.desc())
            .limit(limit)
            .all()
        )

    def get_case(self, db: Session, case_id: int) -> ResolvedCase | None:
        return db.query(ResolvedCase).filter(ResolvedCase.id == case_id).one_or_none()

    def build_prompt(
        self,
        *,
        period_start: datetime,
        period_end: datetime,
        alert_payloads: list[dict],
        transaction_payloads: list[dict],
        precomputed_summary: dict,
    ) -> str:
        payload = {
            "periodo_analisis": {
                "inicio": period_start.astimezone(timezone.utc).isoformat(),
                "fin": period_end.astimezone(timezone.utc).isoformat(),
            },
            "resumen_precalculado": precomputed_summary,
            "alertas_anonimizadas": alert_payloads,
            "transacciones_legitimacion_anonimizadas": transaction_payloads,
        }
        payload_json = json.dumps(payload, ensure_ascii=False, sort_keys=True, indent=2)
        return (
            "Eres un analista senior de ciberdelito financiero y fraude digital.\n"
            "Recibiras datos anonimizados y tokenizados. Nunca intentes desanonimizar.\n"
            "Evalua solo la evidencia disponible y determina:\n"
            "1. Coincidencias entre tokens financieros (cuentas o SINPE) mencionados en alertas y transacciones reales.\n"
            "2. Patrones muchas-a-una donde varias alertas y varias transacciones convergen hacia un mismo beneficiario financiero tokenizado.\n"
            "3. Correlacion geografica, con foco explicito en Zona Norte frente a depositos o movimientos inusuales del mismo periodo.\n"
            "4. Si no hay evidencia suficiente, reduce el score y explica la limitacion.\n"
            "Usa exclusivamente los datos entregados a continuacion.\n\n"
            f"{payload_json}"
        )

    def _load_window(
        self,
        db: Session,
        *,
        lookback_hours: int,
        alert_limit: int,
        transaction_limit: int,
    ) -> CorrelationWindow:
        period_end = datetime.now(timezone.utc)
        period_start = period_end - timedelta(hours=lookback_hours)

        alerts = (
            db.query(SecureAlert)
            .filter(SecureAlert.timestamp >= period_start)
            .filter(SecureAlert.timestamp <= period_end)
            .order_by(SecureAlert.timestamp.desc())
            .limit(alert_limit)
            .all()
        )
        if not alerts:
            raise InsufficientCorrelationData(
                "No hay alertas recientes para correlacionar en el periodo solicitado."
            )

        transactions = (
            db.query(ObservedTransaction)
            .filter(ObservedTransaction.created_at >= period_start)
            .filter(ObservedTransaction.created_at <= period_end)
            .order_by(ObservedTransaction.created_at.desc())
            .limit(transaction_limit)
            .all()
        )
        if not transactions:
            raise InsufficientCorrelationData(
                "No hay transacciones sospechosas recientes en el mismo periodo."
            )

        return CorrelationWindow(
            period_start=period_start,
            period_end=period_end,
            alerts=alerts,
            transactions=transactions,
        )

    def _serialize_alert(self, alert: SecureAlert) -> dict:
        buffer_items = list(alert.buffer_texto or [])
        combined_payload = "\n".join(
            str(item.get("payload", ""))
            for item in buffer_items
            if isinstance(item, dict)
        )
        mentioned_tokens = self._tokenizer.extract_financial_tokens(
            combined_payload,
            " ".join(str(entity) for entity in (alert.entidades_extraidas or [])),
        )
        excerpt = [
            {
                "source": str(item.get("source", "")),
                "origin_app": str(item.get("origin_app", "")),
                "payload_masked": self._tokenizer.mask_text(str(item.get("payload", ""))),
            }
            for item in buffer_items[:5]
            if isinstance(item, dict)
        ]
        return {
            "alert_id": alert.id,
            "timestamp": _to_utc(alert.timestamp).isoformat(),
            "origen_app": alert.origen_app or "desconocida",
            "region_bucket": _normalize_alert_region(alert.ubicacion_gps),
            "riesgo_probabilidad": _safe_float(alert.riesgo_probabilidad),
            "entidades_tokenizadas": [
                self._tokenizer.mask_text(str(entity))
                for entity in (alert.entidades_extraidas or [])
            ],
            "menciones_financieras": mentioned_tokens,
            "buffer_extracto": excerpt,
        }

    def _serialize_transaction(self, transaction: ObservedTransaction) -> dict:
        source_token = self._tokenizer.tokenize_identifier(
            transaction.source_account_number,
            "acct",
        )
        destination_token = self._tokenizer.tokenize_identifier(
            transaction.destination_account_number,
            "acct",
        )
        beneficiary_token = self._tokenizer.tokenize_name(transaction.beneficiary)
        descriptive_text = " ".join(
            part
            for part in [
                transaction.beneficiary,
                transaction.concept,
                transaction.description,
                transaction.external_reference,
            ]
            if part
        )
        text_tokens = self._tokenizer.extract_financial_tokens(descriptive_text)
        return {
            "transaction_id": transaction.id,
            "timestamp": _to_utc(transaction.created_at).isoformat(),
            "source_account_token": source_token,
            "destination_account_token": destination_token,
            "beneficiary_token": beneficiary_token or destination_token,
            "region_bucket": _normalize_transaction_region(transaction.location),
            "amount": float(_to_decimal(transaction.amount)),
            "currency": transaction.currency,
            "channel": transaction.channel,
            "status": transaction.status,
            "reference_tokens": text_tokens,
        }

    def _build_precomputed_summary(
        self,
        alert_payloads: list[dict],
        transaction_payloads: list[dict],
    ) -> dict:
        alert_tokens: set[str] = set()
        for alert in alert_payloads:
            alert_tokens.update(alert.get("menciones_financieras", []))
            alert_tokens.update(alert.get("entidades_tokenizadas", []))

        destination_index: dict[str, dict[str, int]] = {}
        transaction_tokens: set[str] = set()
        zona_norte_transactions = 0
        for transaction in transaction_payloads:
            transaction_tokens.add(transaction["source_account_token"])
            transaction_tokens.add(transaction["destination_account_token"])
            transaction_tokens.add(transaction["beneficiary_token"])
            transaction_tokens.update(transaction.get("reference_tokens", []))
            if transaction.get("region_bucket") == "zona_norte":
                zona_norte_transactions += 1

            entry = destination_index.setdefault(
                transaction["destination_account_token"],
                {"transaction_count": 0, "alert_mentions": 0},
            )
            entry["transaction_count"] += 1

        overlap = sorted(alert_tokens & transaction_tokens)
        for token in overlap:
            if token in destination_index:
                destination_index[token]["alert_mentions"] += 1

        many_to_one_candidates = [
            {
                "beneficiary_token": token,
                "transaction_count": metrics["transaction_count"],
                "alert_mentions": metrics["alert_mentions"],
            }
            for token, metrics in destination_index.items()
            if metrics["transaction_count"] >= 2 or metrics["alert_mentions"] >= 2
        ]
        many_to_one_candidates.sort(
            key=lambda item: (item["alert_mentions"], item["transaction_count"]),
            reverse=True,
        )

        zona_norte_alerts = sum(
            1 for alert in alert_payloads if alert.get("region_bucket") == "zona_norte"
        )
        return {
            "tokens_financieros_coincidentes": overlap[:25],
            "candidatos_muchas_a_una": many_to_one_candidates[:20],
            "correlacion_geografica": {
                "zona_norte_alertas": zona_norte_alerts,
                "zona_norte_transacciones": zona_norte_transactions,
            },
            "conteo_alertas": len(alert_payloads),
            "conteo_transacciones": len(transaction_payloads),
        }

    def _persist_case(
        self,
        db: Session,
        *,
        window: CorrelationWindow,
        prompt: str,
        analysis: GeminiCorrelationOutput,
        precomputed: dict,
    ) -> ResolvedCase:
        case = ResolvedCase(
            period_start=window.period_start,
            period_end=window.period_end,
            score_de_vinculacion=float(analysis.score_de_vinculacion),
            justificacion_tecnica=analysis.justificacion_tecnica,
            hallazgos_json={
                "coincidencias_financieras": analysis.coincidencias_financieras,
                "patron_muchas_a_una": analysis.patron_muchas_a_una,
                "correlacion_geografica": analysis.correlacion_geografica,
                "beneficiarios_prioritarios": analysis.beneficiarios_prioritarios,
                "resumen_precalculado": precomputed,
            },
            alert_ids=[alert.id for alert in window.alerts],
            transaction_ids=[transaction.id for transaction in window.transactions],
            gemini_model=self._model_name,
            prompt_hash=hashlib.sha256(prompt.encode("utf-8")).hexdigest(),
        )
        db.add(case)
        db.commit()
        db.refresh(case)
        return case


def _normalize_alert_region(location_value: str | None) -> str:
    if not location_value:
        return "sin_datos"

    value = location_value.strip()
    coordinates = re.search(r"(-?\d+\.\d+)\s*,\s*(-?\d+\.\d+)", value)
    if coordinates:
        latitude = float(coordinates.group(1))
        longitude = float(coordinates.group(2))
        if 10.2 <= latitude <= 11.4 and -85.7 <= longitude <= -83.8:
            return "zona_norte"
        if 9.7 <= latitude <= 10.2 and -84.5 <= longitude <= -83.7:
            return "valle_central"

    return _normalize_transaction_region(value)


def _normalize_transaction_region(location_value: str | None) -> str:
    if not location_value:
        return "sin_datos"

    normalized = location_value.upper()
    if "CROSS-BANK API" in normalized or "API" in normalized:
        return "virtual"
    if any(keyword in normalized for keyword in ["SAN CARLOS", "CIUDAD QUESADA", "LOS CHILES", "UPALA", "GUATUSO", "PITAL", "FORTUNA", "SARAPIQUI"]):
        return "zona_norte"
    if any(keyword in normalized for keyword in ["SAN JOSE", "ALAJUELA", "HEREDIA", "CARTAGO"]):
        return "valle_central"
    if any(keyword in normalized for keyword in ["LIMON", "POCOCI", "SIQUIRRES", "TALAMANCA"]):
        return "caribe"
    if any(keyword in normalized for keyword in ["PUNTARENAS", "QUEPOS", "OSA", "GOLFITO", "PARRITA"]):
        return "pacifico"
    if any(keyword in normalized for keyword in ["GUANACASTE", "LIBERIA", "NICOYA", "SANTA CRUZ", "CAÑAS"]):
        return "guanacaste"
    if any(keyword in normalized for keyword in ["PANAMA", "COLOMBIA", "NICARAGUA"]):
        return "transfronterizo"
    return "otra_region"


def _safe_float(value: object) -> float:
    if value is None:
        return 0.0
    try:
        return float(value)
    except (TypeError, ValueError):
        return 0.0


def _to_decimal(value: object) -> Decimal:
    if isinstance(value, Decimal):
        return value
    if value is None:
        return Decimal("0.00")
    return Decimal(str(value))


def _to_utc(value: datetime) -> datetime:
    if value.tzinfo is None:
        return value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc)
