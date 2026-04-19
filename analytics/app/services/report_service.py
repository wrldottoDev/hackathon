from __future__ import annotations

from collections import Counter, defaultdict
from datetime import datetime, timezone
from statistics import mean
from typing import Iterable

from sqlalchemy.orm import Session

from ..models.observed_transaction import ObservedTransaction
from ..models.resolved_case import ResolvedCase
from ..models.secure_alert import SecureAlert
from ..schemas.infrastructure import EvidenceDossierResponse
from .detection_engine import Cuenta, ResultadoRegla
from .follow_up_service import get_account_follow_up
from .geo_utils import haversine_meters, normalize_alert_region
from .infrastructure_service import detect_alert_link_indicators
from .risk_service import list_alerts


def _get_fpdf():
    try:
        from fpdf import FPDF
    except ModuleNotFoundError as exc:
        raise RuntimeError(
            "La generacion de PDF requiere instalar fpdf2 en el entorno de analytics."
        ) from exc
    return FPDF


def _pdf_bytes(pdf) -> bytes:
    payload = pdf.output(dest="S")
    if isinstance(payload, bytearray):
        return bytes(payload)
    if isinstance(payload, bytes):
        return payload
    if isinstance(payload, str):
        return payload.encode("latin-1", "replace")
    return bytes(payload)


def _safe(value: object) -> str:
    return str(value).encode("latin-1", "replace").decode("latin-1")


def _section_title(pdf, text: str) -> None:
    pdf.set_font("Helvetica", "B", 13)
    pdf.set_text_color(18, 64, 108)
    pdf.cell(0, 8, _safe(text), new_x="LMARGIN", new_y="NEXT")
    pdf.set_text_color(30, 30, 30)


def _full_width_text(pdf, height: int, text: object) -> None:
    pdf.set_x(pdf.l_margin)
    pdf.multi_cell(
        pdf.w - pdf.l_margin - pdf.r_margin,
        height,
        _safe(text if text not in (None, "") else "-"),
    )


def _line(pdf, label: str, value: object) -> None:
    usable_width = pdf.w - pdf.l_margin - pdf.r_margin
    label_width = 52
    value_width = max(usable_width - label_width, 40)
    start_x = pdf.get_x()
    start_y = pdf.get_y()
    pdf.set_font("Helvetica", "B", 10)
    pdf.cell(label_width, 6, _safe(f"{label}:"))
    pdf.set_xy(start_x + label_width, start_y)
    pdf.set_font("Helvetica", "", 10)
    pdf.multi_cell(value_width, 6, _safe(value if value not in (None, "") else "-"))


def _buffer_item_text(item: object) -> str:
    if isinstance(item, dict):
        payload = item.get("payload")
        if payload not in (None, ""):
            return str(payload)
        return _safe(item)
    if isinstance(item, str):
        return item
    return _safe(item)


def build_account_report_pdf(db: Session, account_number: str) -> bytes:
    FPDF = _get_fpdf()
    follow_up = get_account_follow_up(db, account_number)
    alerts = list_alerts(db, account_number=account_number.strip().upper(), limit=200)

    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()

    pdf.set_font("Helvetica", "B", 18)
    pdf.cell(
        0,
        10,
        _safe(f"FlowLens Reporte de Cuenta - {follow_up.account_number_display}"),
        new_x="LMARGIN",
        new_y="NEXT",
    )
    pdf.set_font("Helvetica", "", 10)
    _full_width_text(
        pdf,
        5,
        "Reporte consolidado de analytics con metadata de cuenta, alertas, "
        "resumen de red y transacciones recientes.",
    )
    pdf.ln(2)

    _section_title(pdf, "Resumen de cuenta")
    _line(pdf, "Cuenta", follow_up.account_number_display)
    _line(pdf, "Banco", follow_up.bank_code)
    _line(pdf, "Estado", follow_up.account_status)
    _line(pdf, "Saldo actual", f"{follow_up.current_balance:,.2f} {follow_up.currency}")
    _line(pdf, "Ultima actividad", follow_up.last_activity_at or "-")
    _line(pdf, "Ultimo cambio PIN", follow_up.last_credentials_change_at or "-")
    _line(pdf, "Ubicacion actual", follow_up.current_location or "-")
    _line(pdf, "Cuenta reportada", "Si" if follow_up.reported else "No")
    _line(pdf, "Datos protegidos", "Si" if follow_up.data_protected_by_investigation else "No")

    pdf.ln(2)
    _section_title(pdf, "Metricas")
    _line(pdf, "Entradas", follow_up.incoming_count)
    _line(pdf, "Salidas", follow_up.outgoing_count)
    _line(pdf, "Monto entrante", f"{follow_up.total_incoming_amount:,.2f} {follow_up.currency}")
    _line(pdf, "Monto saliente", f"{follow_up.total_outgoing_amount:,.2f} {follow_up.currency}")
    _line(pdf, "Promedio entrante", f"{follow_up.average_incoming_amount:,.2f} {follow_up.currency}")
    _line(pdf, "Promedio saliente", f"{follow_up.average_outgoing_amount:,.2f} {follow_up.currency}")
    _line(pdf, "Tx alto monto", follow_up.high_amount_count)

    pdf.ln(2)
    _section_title(pdf, "Alertas")
    if not alerts:
        pdf.set_font("Helvetica", "", 10)
        _full_width_text(pdf, 6, "No hay alertas vigentes para esta cuenta.")
    else:
        for alert in alerts:
            pdf.set_font("Helvetica", "B", 10)
            _full_width_text(
                pdf,
                6,
                f"[{alert.category}] {alert.pattern_type} | score {alert.score} | {alert.level.upper()}",
            )
            pdf.set_font("Helvetica", "", 10)
            _full_width_text(pdf, 5, alert.reason)
            _full_width_text(pdf, 5, f"Fecha: {alert.created_at}")
            pdf.ln(1)

    pdf.ln(2)
    _section_title(pdf, "Red y contrapartes")
    _line(pdf, "Aristas entrantes", follow_up.network_position.incoming_edges)
    _line(pdf, "Aristas salientes", follow_up.network_position.outgoing_edges)
    _line(pdf, "Contrapartes unicas", follow_up.network_position.unique_counterparties)
    _line(pdf, "Contrapartes indirectas", follow_up.network_position.indirect_counterparties)
    _line(
        pdf,
        "Contrapartes frecuentes",
        ", ".join(
            item.account_number_display
            for item in follow_up.frequent_counterparties[:8]
        ) or "-",
    )

    pdf.add_page()
    _section_title(pdf, "Transacciones recientes")
    if not follow_up.recent_transactions:
        pdf.set_font("Helvetica", "", 10)
        _full_width_text(pdf, 6, "No hay transacciones recientes.")
    else:
        for transaction in follow_up.recent_transactions:
            pdf.set_font("Helvetica", "B", 10)
            _full_width_text(
                pdf,
                6,
                f"Tx #{transaction.transaction_id} | {transaction.created_at} | "
                f"{transaction.amount:,.2f} {transaction.currency}",
            )
            pdf.set_font("Helvetica", "", 10)
            _full_width_text(
                pdf,
                5,
                f"{transaction.source_account_number_display} -> "
                f"{transaction.destination_account_number_display}",
            )
            _full_width_text(
                pdf,
                5,
                f"Beneficiario: {transaction.beneficiary or '-'} | "
                f"Concepto: {transaction.concept or transaction.description or '-'}",
            )
            _full_width_text(
                pdf,
                5,
                f"Canal: {transaction.channel} | Ubicacion: {transaction.location or '-'} | "
                f"Estado: {transaction.status}",
            )
            pdf.ln(1)

    return _pdf_bytes(pdf)


def build_detection_demo_report_pdf(
    cuentas: Iterable[Cuenta],
    alerts: Iterable[ResultadoRegla],
) -> bytes:
    FPDF = _get_fpdf()
    cuentas = list(cuentas)
    alerts = list(alerts)
    counter = Counter(alert.category for alert in alerts)

    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 18)
    pdf.cell(
        0,
        10,
        "FlowLens Demo - Motor de Deteccion",
        new_x="LMARGIN",
        new_y="NEXT",
    )
    pdf.set_font("Helvetica", "", 10)
    _full_width_text(
        pdf,
        5,
        "Resumen del caso de prueba para reglas de trata/trafico, fraude ATO, AML y contagio relacional.",
    )
    pdf.ln(2)

    _section_title(pdf, "Resumen")
    _line(pdf, "Cuentas evaluadas", len(cuentas))
    _line(pdf, "Alertas generadas", len(alerts))
    _line(pdf, "Trata y trafico", counter.get("trata_y_trafico", 0))
    _line(pdf, "Fraude ATO", counter.get("fraude_ato", 0))
    _line(pdf, "AML", counter.get("aml", 0))
    _line(pdf, "Riesgo relacional", counter.get("riesgo_relacional", 0))

    pdf.ln(2)
    _section_title(pdf, "Alertas")
    for alert in alerts:
        pdf.set_font("Helvetica", "B", 10)
        _full_width_text(
            pdf,
            6,
            f"{alert.cuenta_numero} | {alert.pattern_type} | "
            f"score {alert.score_riesgo} | {alert.category}",
        )
        pdf.set_font("Helvetica", "", 10)
        _full_width_text(pdf, 5, alert.motivo)
        pdf.ln(1)

    pdf.add_page()
    _section_title(pdf, "Estado de cuentas")
    for cuenta in cuentas:
        pdf.set_font("Helvetica", "B", 10)
        _full_width_text(
            pdf,
            6,
            f"{cuenta.numero_cuenta} | protegida: "
            f"{'Si' if cuenta.datos_protegidos_por_investigacion else 'No'}",
        )
        pdf.set_font("Helvetica", "", 10)
        _full_width_text(
            pdf,
            5,
            f"Transacciones: {len(cuenta.transacciones)} | "
            f"Ubicacion actual: {cuenta.ubicacion_actual or '-'}",
        )
        pdf.ln(1)

    return _pdf_bytes(pdf)


def build_evidence_dossier_json(
    db: Session,
    case_id: int,
) -> EvidenceDossierResponse:
    case = (
        db.query(ResolvedCase)
        .filter(ResolvedCase.id == case_id)
        .one_or_none()
    )
    if case is None:
        raise RuntimeError("Caso resuelto no encontrado para generar expediente.")

    alerts = (
        db.query(SecureAlert)
        .filter(SecureAlert.id.in_(list(case.alert_ids or [])))
        .order_by(SecureAlert.timestamp.asc())
        .all()
    )
    transactions = (
        db.query(ObservedTransaction)
        .filter(ObservedTransaction.id.in_(list(case.transaction_ids or [])))
        .order_by(ObservedTransaction.created_at.asc())
        .all()
    )

    chat_alerts = [
        {
            "alert_id": alert.id,
            "timestamp": alert.timestamp,
            "origen_app": alert.origen_app,
            "ubicacion_gps": alert.ubicacion_gps,
            "latitude": alert.latitude,
            "longitude": alert.longitude,
            "riesgo_probabilidad": alert.riesgo_probabilidad,
            "buffer_texto": list(alert.buffer_texto or []),
            "entidades_extraidas": alert.entidades_extraidas,
        }
        for alert in alerts
    ]
    financial_transactions = [
        {
            "transaction_id": transaction.id,
            "external_transaction_id": transaction.external_transaction_id,
            "source_account_number": transaction.source_account_number,
            "destination_account_number": transaction.destination_account_number,
            "bank_code": transaction.bank_code,
            "amount": float(transaction.amount),
            "currency": transaction.currency,
            "beneficiary": transaction.beneficiary,
            "concept": transaction.concept,
            "channel": transaction.channel,
            "location": transaction.location,
            "created_at": transaction.created_at,
        }
        for transaction in transactions
    ]

    links: list[dict] = []
    rescue_mode = {
        "triggered": False,
        "external_alert_ids": [],
        "regions": [],
    }
    for alert in alerts:
        indicators = list(
            (alert.metadata_reporte or {}).get("infrastructure_links", [])
        ) or detect_alert_link_indicators(db, alert)
        links.extend(
            {
                **indicator,
                "alert_id": alert.id,
            }
            for indicator in indicators
        )
        rescue_state = (alert.metadata_reporte or {}).get("rescue_mode", {})
        if rescue_state.get("triggered"):
            rescue_mode["triggered"] = True
            rescue_mode["regions"].append(rescue_state.get("region"))
            if rescue_state.get("external_alert_id") is not None:
                rescue_mode["external_alert_ids"].append(
                    rescue_state["external_alert_id"]
                )

    map_summary = _build_case_map_summary(alerts)
    return EvidenceDossierResponse(
        case_id=case.id,
        expediente_generado_en=datetime.now(timezone.utc),
        case_summary={
            "score_de_vinculacion": case.score_de_vinculacion,
            "justificacion_tecnica": case.justificacion_tecnica,
            "period_start": case.period_start,
            "period_end": case.period_end,
            "gemini_model": case.gemini_model,
        },
        chat_alerts=chat_alerts,
        transacciones_financieras=financial_transactions,
        links_captacion=links,
        mapa_ubicacion=map_summary,
        hallazgos_gemini=dict(case.hallazgos_json or {}),
        rescue_mode=rescue_mode,
    )


def build_evidence_dossier_pdf(
    db: Session,
    case_id: int,
) -> bytes:
    dossier = build_evidence_dossier_json(db, case_id)
    FPDF = _get_fpdf()
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()

    pdf.set_font("Helvetica", "B", 18)
    pdf.cell(
        0,
        10,
        _safe(f"FlowLens Expediente Digital - Caso #{dossier.case_id}"),
        new_x="LMARGIN",
        new_y="NEXT",
    )
    pdf.set_font("Helvetica", "", 10)
    _full_width_text(
        pdf,
        5,
        "Expediente consolidado para remision interna y entrega a OIJ: "
        "chat, transacciones, links de captacion y mapa de ubicacion.",
    )
    pdf.ln(2)

    _section_title(pdf, "Resumen del caso")
    _line(
        pdf,
        "Score vinculacion",
        f"{dossier.case_summary['score_de_vinculacion']:.2f}",
    )
    _line(pdf, "Modelo", dossier.case_summary["gemini_model"])
    _line(pdf, "Periodo inicio", dossier.case_summary["period_start"])
    _line(pdf, "Periodo fin", dossier.case_summary["period_end"])
    _full_width_text(pdf, 5, dossier.case_summary["justificacion_tecnica"])

    pdf.ln(2)
    _section_title(pdf, "Chat y denuncias")
    for alert in dossier.chat_alerts:
        pdf.set_font("Helvetica", "B", 10)
        _full_width_text(
            pdf,
            6,
            f"Alerta #{alert['alert_id']} | {alert['timestamp']} | "
            f"{alert.get('origen_app') or '-'} | {alert.get('ubicacion_gps') or '-'}",
        )
        pdf.set_font("Helvetica", "", 10)
        for item in alert["buffer_texto"][:5]:
            _full_width_text(pdf, 5, _buffer_item_text(item))
        pdf.ln(1)

    pdf.add_page()
    _section_title(pdf, "Transaccion financiera")
    for transaction in dossier.transacciones_financieras:
        pdf.set_font("Helvetica", "B", 10)
        _full_width_text(
            pdf,
            6,
            f"Tx #{transaction['transaction_id']} | {transaction['created_at']} | "
            f"{transaction['amount']:,.2f} {transaction['currency']}",
        )
        pdf.set_font("Helvetica", "", 10)
        _full_width_text(
            pdf,
            5,
            f"{transaction['source_account_number']} -> "
            f"{transaction['destination_account_number']}",
        )
        _full_width_text(
            pdf,
            5,
            f"Beneficiario: {transaction.get('beneficiary') or '-'} | "
            f"Concepto: {transaction.get('concept') or '-'} | "
            f"Ubicacion: {transaction.get('location') or '-'}",
        )
        pdf.ln(1)

    pdf.add_page()
    _section_title(pdf, "Link de captacion")
    if not dossier.links_captacion:
        _full_width_text(pdf, 6, "No se detectaron links de captacion en el caso.")
    else:
        for link in dossier.links_captacion:
            pdf.set_font("Helvetica", "B", 10)
            _full_width_text(
                pdf,
                6,
                f"Alerta #{link['alert_id']} | {link['url']}",
            )
            pdf.set_font("Helvetica", "", 10)
            _full_width_text(
                pdf,
                5,
                f"Dominio: {link.get('domain') or '-'} | "
                f"DGA: {'Si' if link.get('probable_dga') else 'No'} "
                f"({link.get('dga_score', 0):.2f}) | "
                f"Blacklist: {'Si' if link.get('blacklist_match') else 'No'} | "
                f"Anuncio sospechoso: {'Si' if link.get('suspicious_ad_match') else 'No'}",
            )
            pdf.ln(1)

    pdf.add_page()
    _section_title(pdf, "Mapa de ubicacion")
    _line(pdf, "Total puntos", len(dossier.mapa_ubicacion.get("points", [])))
    _line(pdf, "Clusters", len(dossier.mapa_ubicacion.get("clusters", [])))
    for cluster in dossier.mapa_ubicacion.get("clusters", []):
        _full_width_text(
            pdf,
            5,
            f"{cluster['cluster_id']} | hits {cluster['hit_count']} | "
            f"centro {cluster['centroid_latitude']:.6f}, "
            f"{cluster['centroid_longitude']:.6f} | zona {cluster.get('region_bucket') or '-'}",
        )

    if dossier.rescue_mode.get("triggered"):
        pdf.ln(2)
        _section_title(pdf, "Modo Rescate")
        _full_width_text(
            pdf,
            5,
            "Alerta de alta prioridad activada por coincidencia entre link blacklist "
            "y zona con activacion reciente de PIN/credenciales.",
        )
        _line(
            pdf,
            "Alertas externas",
            ", ".join(str(item) for item in dossier.rescue_mode["external_alert_ids"]),
        )

    return _pdf_bytes(pdf)


def _build_case_map_summary(alerts: list[SecureAlert]) -> dict:
    points = [
        {
            "alert_id": alert.id,
            "latitude": float(alert.latitude),
            "longitude": float(alert.longitude),
            "region_bucket": normalize_alert_region(alert.ubicacion_gps),
            "riesgo_probabilidad": float(alert.riesgo_probabilidad or 0),
        }
        for alert in alerts
        if alert.latitude is not None and alert.longitude is not None
    ]
    clusters = _cluster_points(points, eps_meters=5000.0, min_points=1)
    return {
        "points": points,
        "clusters": clusters,
    }


def _cluster_points(
    points: list[dict],
    *,
    eps_meters: float,
    min_points: int,
) -> list[dict]:
    if not points:
        return []

    adjacency: dict[int, set[int]] = defaultdict(set)
    for index_a, point_a in enumerate(points):
        for index_b in range(index_a + 1, len(points)):
            point_b = points[index_b]
            if (
                haversine_meters(
                    point_a["latitude"],
                    point_a["longitude"],
                    point_b["latitude"],
                    point_b["longitude"],
                )
                <= eps_meters
            ):
                adjacency[index_a].add(index_b)
                adjacency[index_b].add(index_a)

    visited: set[int] = set()
    clusters: list[dict] = []
    for index in range(len(points)):
        if index in visited:
            continue
        stack = [index]
        component: list[int] = []
        while stack:
            current = stack.pop()
            if current in visited:
                continue
            visited.add(current)
            component.append(current)
            stack.extend(adjacency.get(current, set()) - visited)

        if len(component) < min_points:
            continue
        cluster_points = [points[item] for item in component]
        clusters.append(
            {
                "cluster_id": f"case-cluster-{len(clusters)}",
                "hit_count": len(cluster_points),
                "avg_risk": round(
                    mean(point["riesgo_probabilidad"] for point in cluster_points), 4
                ),
                "centroid_latitude": sum(
                    point["latitude"] for point in cluster_points
                )
                / len(cluster_points),
                "centroid_longitude": sum(
                    point["longitude"] for point in cluster_points
                )
                / len(cluster_points),
                "alert_ids": [point["alert_id"] for point in cluster_points],
                "region_bucket": max(
                    Counter(
                        point["region_bucket"] for point in cluster_points
                    ).items(),
                    key=lambda item: item[1],
                )[0],
            }
        )
    return clusters
