from __future__ import annotations

from datetime import datetime, timedelta, timezone
from decimal import Decimal
from pathlib import Path

from app.services.detection_engine import Cuenta, MotorDeteccion, Transaccion
from app.services.report_service import build_detection_demo_report_pdf


def _tx(
    transaction_id: int,
    *,
    source: str,
    destination: str,
    amount: str,
    when: datetime,
    location: str,
    beneficiary: str,
    concept: str,
    channel: str = "web",
    source_balance_before: str | None = None,
    source_balance_after: str | None = None,
) -> Transaccion:
    return Transaccion(
        transaction_id=transaction_id,
        observed_transaction_id=transaction_id,
        cuenta_origen=source,
        cuenta_destino=destination,
        banco_origen=source.split("-", 1)[0],
        banco_destino=destination.split("-", 1)[0],
        monto=Decimal(amount),
        fecha_hora=when,
        ubicacion_geografica=location,
        beneficiario=beneficiary,
        concepto=concept,
        canal=channel,
        tipo="transfer",
        estado="completed",
        saldo_origen_antes=Decimal(source_balance_before) if source_balance_before else None,
        saldo_origen_despues=Decimal(source_balance_after) if source_balance_after else None,
    )


def build_demo_case() -> list[Cuenta]:
    now = datetime.now(timezone.utc).replace(microsecond=0)

    hub = Cuenta(
        numero_cuenta="BKA-9000000001",
        banco_codigo="BKA",
        estado="active",
        saldo_actual=Decimal("1200.00"),
        fecha_creacion=now - timedelta(days=200),
        fecha_ultima_actividad=now,
        fecha_ultimo_cambio_pin=now - timedelta(days=30),
        ubicacion_actual="San Jose, Costa Rica",
    )
    leaves = [
        Cuenta(
            numero_cuenta=f"BKA-90000000{i:02d}",
            banco_codigo="BKA",
            estado="active",
            saldo_actual=Decimal("100.00"),
            fecha_creacion=now - timedelta(days=120),
            fecha_ultima_actividad=now - timedelta(hours=6),
            fecha_ultimo_cambio_pin=now - timedelta(days=40),
            ubicacion_actual="Limon, Costa Rica",
        )
        for i in range(2, 8)
    ]

    corridor = Cuenta(
        numero_cuenta="BKB-8000000001",
        banco_codigo="BKB",
        estado="active",
        saldo_actual=Decimal("2400.00"),
        fecha_creacion=now - timedelta(days=100),
        fecha_ultima_actividad=now,
        fecha_ultimo_cambio_pin=now - timedelta(days=10),
        ubicacion_actual="San Jose, Costa Rica",
    )
    digital = Cuenta(
        numero_cuenta="BKA-7000000001",
        banco_codigo="BKA",
        estado="active",
        saldo_actual=Decimal("3100.00"),
        fecha_creacion=now - timedelta(days=90),
        fecha_ultima_actividad=now,
        fecha_ultimo_cambio_pin=now - timedelta(days=9),
        ubicacion_actual="San Jose, Costa Rica",
    )
    inactive = Cuenta(
        numero_cuenta="BKB-6000000001",
        banco_codigo="BKB",
        estado="active",
        saldo_actual=Decimal("900.00"),
        fecha_creacion=now - timedelta(days=400),
        fecha_ultima_actividad=now - timedelta(days=250),
        fecha_ultimo_cambio_pin=now - timedelta(days=200),
        ubicacion_actual="Cartago, Costa Rica",
    )
    takeover = Cuenta(
        numero_cuenta="BKA-5000000001",
        banco_codigo="BKA",
        estado="active",
        saldo_actual=Decimal("600.00"),
        fecha_creacion=now - timedelta(days=160),
        fecha_ultima_actividad=now,
        fecha_ultimo_cambio_pin=now - timedelta(hours=6),
        ubicacion_actual="Heredia, Costa Rica",
    )
    smurfing = Cuenta(
        numero_cuenta="BKB-4000000001",
        banco_codigo="BKB",
        estado="active",
        saldo_actual=Decimal("9800.00"),
        fecha_creacion=now - timedelta(days=200),
        fecha_ultima_actividad=now,
        fecha_ultimo_cambio_pin=now - timedelta(days=30),
        ubicacion_actual="Alajuela, Costa Rica",
    )
    mule = Cuenta(
        numero_cuenta="BKA-3000000001",
        banco_codigo="BKA",
        estado="active",
        saldo_actual=Decimal("300.00"),
        fecha_creacion=now - timedelta(days=110),
        fecha_ultima_actividad=now,
        fecha_ultimo_cambio_pin=now - timedelta(days=20),
        ubicacion_actual="San Jose, Costa Rica",
    )
    contagio_directo = Cuenta(
        numero_cuenta="BKB-2000000001",
        banco_codigo="BKB",
        estado="active",
        saldo_actual=Decimal("450.00"),
        fecha_creacion=now - timedelta(days=70),
        fecha_ultima_actividad=now - timedelta(hours=4),
        fecha_ultimo_cambio_pin=now - timedelta(days=18),
        ubicacion_actual="Puntarenas, Costa Rica",
    )
    puente = Cuenta(
        numero_cuenta="BKB-2000000002",
        banco_codigo="BKB",
        estado="active",
        saldo_actual=Decimal("520.00"),
        fecha_creacion=now - timedelta(days=85),
        fecha_ultima_actividad=now - timedelta(hours=6),
        fecha_ultimo_cambio_pin=now - timedelta(days=21),
        ubicacion_actual="Liberia, Costa Rica",
    )
    contagio_indirecto = Cuenta(
        numero_cuenta="BKA-2000000003",
        banco_codigo="BKA",
        estado="active",
        saldo_actual=Decimal("380.00"),
        fecha_creacion=now - timedelta(days=60),
        fecha_ultima_actividad=now - timedelta(hours=8),
        fecha_ultimo_cambio_pin=now - timedelta(days=15),
        ubicacion_actual="Nicoya, Costa Rica",
    )

    transactions = [
        _tx(
            index,
            source=leaf.numero_cuenta,
            destination=hub.numero_cuenta,
            amount="120.00",
            when=now - timedelta(hours=12 - index),
            location="Limon, Costa Rica",
            beneficiary=hub.numero_cuenta,
            concept="Envio coordinado",
        )
        for index, leaf in enumerate(leaves, start=1)
    ]
    transactions.extend(
        [
            _tx(
                100,
                source="BKB-1111111111",
                destination=corridor.numero_cuenta,
                amount="1400.00",
                when=now - timedelta(days=18),
                location="Bogota, Colombia",
                beneficiary=corridor.numero_cuenta,
                concept="Ingreso corredor",
            ),
            _tx(
                101,
                source=corridor.numero_cuenta,
                destination="BKB-1111111112",
                amount="600.00",
                when=now - timedelta(days=12),
                location="Colon, Panama",
                beneficiary="Transportes Panama",
                concept="Pago logistica",
                source_balance_before="2200.00",
                source_balance_after="1600.00",
            ),
            _tx(
                102,
                source=corridor.numero_cuenta,
                destination="BKB-1111111113",
                amount="500.00",
                when=now - timedelta(days=5),
                location="Paso Canoas, Costa Rica",
                beneficiary="Operador CR",
                concept="Pago traslado",
                source_balance_before="1600.00",
                source_balance_after="1100.00",
            ),
            _tx(
                110,
                source="BKA-1222222222",
                destination=digital.numero_cuenta,
                amount="400.00",
                when=now - timedelta(days=2, hours=2),
                location="San Jose, Costa Rica",
                beneficiary=digital.numero_cuenta,
                concept="Deposito nocturno",
                channel="cash",
            ),
            _tx(
                111,
                source=digital.numero_cuenta,
                destination="BKA-1222222223",
                amount="350.00",
                when=now - timedelta(days=1, hours=23),
                location="San Jose, Costa Rica",
                beneficiary="META ADS",
                concept="META ADS campaign",
                source_balance_before="3600.00",
                source_balance_after="3250.00",
            ),
            _tx(
                120,
                source="BKB-1333333333",
                destination=inactive.numero_cuenta,
                amount="900.00",
                when=now - timedelta(hours=20),
                location="Cartago, Costa Rica",
                beneficiary=inactive.numero_cuenta,
                concept="Reactivacion inesperada",
            ),
            _tx(
                121,
                source=inactive.numero_cuenta,
                destination="BKB-1333333334",
                amount="700.00",
                when=now - timedelta(hours=10),
                location="Cartago, Costa Rica",
                beneficiary="Nuevo destino",
                concept="Fuga posterior",
                source_balance_before="1800.00",
                source_balance_after="1100.00",
            ),
            _tx(
                130,
                source=takeover.numero_cuenta,
                destination="BKC-1444444444",
                amount="4400.00",
                when=now - timedelta(hours=2),
                location="Heredia, Costa Rica",
                beneficiary="Nuevo beneficiario offshore",
                concept="Transfer urgente",
                source_balance_before="5500.00",
                source_balance_after="1100.00",
            ),
        ]
    )
    transactions.extend(
        [
            _tx(
                200 + idx,
                source=f"BKB-15555555{idx:02d}",
                destination=smurfing.numero_cuenta,
                amount=amount,
                when=now - timedelta(days=2, hours=idx),
                location="Alajuela, Costa Rica",
                beneficiary=smurfing.numero_cuenta,
                concept="Deposito fraccionado",
                channel="cash",
            )
            for idx, amount in enumerate(
                ["1800.00", "2100.00", "1950.00", "1700.00", "2050.00"],
                start=1,
            )
        ]
    )
    transactions.extend(
        [
            _tx(
                300,
                source="BKA-1666666661",
                destination=mule.numero_cuenta,
                amount="8000.00",
                when=now - timedelta(hours=15),
                location="San Jose, Costa Rica",
                beneficiary=mule.numero_cuenta,
                concept="Ingreso alto",
            ),
            _tx(
                301,
                source=mule.numero_cuenta,
                destination="BKA-1666666662",
                amount="3800.00",
                when=now - timedelta(hours=7),
                location="San Jose, Costa Rica",
                beneficiary="Tercero A",
                concept="Redistribucion 1",
                source_balance_before="8300.00",
                source_balance_after="4500.00",
            ),
            _tx(
                302,
                source=mule.numero_cuenta,
                destination="BKB-1666666663",
                amount="3500.00",
                when=now - timedelta(hours=3),
                location="San Jose, Costa Rica",
                beneficiary="Tercero B",
                concept="Redistribucion 2",
                source_balance_before="4500.00",
                source_balance_after="1000.00",
            ),
            _tx(
                310,
                source=hub.numero_cuenta,
                destination=contagio_directo.numero_cuenta,
                amount="85.00",
                when=now - timedelta(hours=4),
                location="Puntarenas, Costa Rica",
                beneficiary=contagio_directo.numero_cuenta,
                concept="Transferencia de enlace",
                source_balance_before="1200.00",
                source_balance_after="1115.00",
            ),
            _tx(
                311,
                source=puente.numero_cuenta,
                destination=mule.numero_cuenta,
                amount="140.00",
                when=now - timedelta(hours=9),
                location="Liberia, Costa Rica",
                beneficiary=mule.numero_cuenta,
                concept="Transferencia hacia semilla",
                source_balance_before="660.00",
                source_balance_after="520.00",
            ),
            _tx(
                312,
                source=contagio_indirecto.numero_cuenta,
                destination=puente.numero_cuenta,
                amount="45.00",
                when=now - timedelta(hours=5),
                location="Nicoya, Costa Rica",
                beneficiary=puente.numero_cuenta,
                concept="Transferencia hacia puente",
                source_balance_before="425.00",
                source_balance_after="380.00",
            ),
        ]
    )

    accounts = [
        hub,
        *leaves,
        corridor,
        digital,
        inactive,
        takeover,
        smurfing,
        mule,
        contagio_directo,
        puente,
        contagio_indirecto,
    ]
    by_account = {account.numero_cuenta: account for account in accounts}
    for transaction in transactions:
        by_account.setdefault(
            transaction.cuenta_origen,
            Cuenta(
                numero_cuenta=transaction.cuenta_origen,
                banco_codigo=transaction.banco_origen,
                estado="active",
                saldo_actual=Decimal("0.00"),
                fecha_creacion=transaction.fecha_hora - timedelta(days=1),
                fecha_ultima_actividad=transaction.fecha_hora,
                fecha_ultimo_cambio_pin=None,
                ubicacion_actual=transaction.ubicacion_geografica,
            ),
        ).registrar_transaccion(transaction)
        by_account.setdefault(
            transaction.cuenta_destino,
            Cuenta(
                numero_cuenta=transaction.cuenta_destino,
                banco_codigo=transaction.banco_destino,
                estado="active",
                saldo_actual=Decimal("0.00"),
                fecha_creacion=transaction.fecha_hora - timedelta(days=1),
                fecha_ultima_actividad=transaction.fecha_hora,
                fecha_ultimo_cambio_pin=None,
                ubicacion_actual=transaction.ubicacion_geografica,
            ),
        ).registrar_transaccion(transaction)

    return list(by_account.values())


def main() -> None:
    cuentas = build_demo_case()
    motor = MotorDeteccion()
    alertas = motor.evaluar_cuentas(cuentas)

    print("=" * 72)
    print("FlowLens demo del motor de deteccion")
    print("=" * 72)
    for alerta in alertas:
        print(
            f"[{alerta.category}] {alerta.pattern_type} | {alerta.cuenta_numero} | "
            f"score={alerta.score_riesgo} | {alerta.motivo}"
        )

    protegidas = [
        cuenta.numero_cuenta
        for cuenta in cuentas
        if cuenta.datos_protegidos_por_investigacion
    ]
    print("\nCuentas protegidas por investigacion:")
    print(", ".join(protegidas) if protegidas else "Ninguna")

    try:
        payload = build_detection_demo_report_pdf(cuentas, alertas)
    except RuntimeError as exc:
        print(f"\nNo se genero PDF: {exc}")
        return

    output_path = Path(__file__).resolve().parent / "analytics_demo_report.pdf"
    output_path.write_bytes(payload)
    print(f"\nReporte PDF generado en: {output_path}")


if __name__ == "__main__":
    main()
