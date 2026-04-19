from __future__ import annotations

from collections import Counter
from typing import Iterable

from sqlalchemy.orm import Session

from .detection_engine import Cuenta, ResultadoRegla
from .follow_up_service import get_account_follow_up
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
