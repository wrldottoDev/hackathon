from __future__ import annotations

from collections import deque
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from decimal import Decimal
from typing import Iterable


TRATA_CATEGORY = "trata_y_trafico"
ATO_CATEGORY = "fraude_ato"
AML_CATEGORY = "aml"
RELATIONAL_CATEGORY = "riesgo_relacional"


@dataclass(slots=True)
class Transaccion:
    transaction_id: int
    observed_transaction_id: int
    cuenta_origen: str
    cuenta_destino: str
    banco_origen: str
    banco_destino: str
    monto: Decimal
    fecha_hora: datetime
    ubicacion_geografica: str
    beneficiario: str
    concepto: str
    canal: str
    tipo: str
    estado: str
    saldo_origen_antes: Decimal | None = None
    saldo_origen_despues: Decimal | None = None

    def es_entrante_para(self, numero_cuenta: str) -> bool:
        return self.estado == "completed" and self.cuenta_destino == numero_cuenta

    def es_saliente_de(self, numero_cuenta: str) -> bool:
        return self.estado == "completed" and self.cuenta_origen == numero_cuenta


@dataclass(slots=True)
class Cuenta:
    numero_cuenta: str
    banco_codigo: str
    estado: str
    saldo_actual: Decimal
    fecha_creacion: datetime | None
    fecha_ultima_actividad: datetime | None
    fecha_ultimo_cambio_pin: datetime | None
    ubicacion_actual: str
    ubicaciones_historicas: list[str] = field(default_factory=list)
    reportada: bool = False
    datos_protegidos_por_investigacion: bool = False
    transacciones: list[Transaccion] = field(default_factory=list)

    def registrar_transaccion(self, transaccion: Transaccion) -> None:
        self.transacciones.append(transaccion)
        if transaccion.ubicacion_geografica:
            if (
                not self.ubicaciones_historicas
                or self.ubicaciones_historicas[-1] != transaccion.ubicacion_geografica
            ):
                self.ubicaciones_historicas.append(transaccion.ubicacion_geografica)
            self.ubicacion_actual = transaccion.ubicacion_geografica
        if (
            self.fecha_ultima_actividad is None
            or transaccion.fecha_hora > self.fecha_ultima_actividad
        ):
            self.fecha_ultima_actividad = transaccion.fecha_hora

    def transacciones_ordenadas(self) -> list[Transaccion]:
        return sorted(self.transacciones, key=lambda item: item.fecha_hora)

    def transacciones_entrantes(self) -> list[Transaccion]:
        return [
            item
            for item in self.transacciones_ordenadas()
            if item.es_entrante_para(self.numero_cuenta)
        ]

    def transacciones_salientes(self) -> list[Transaccion]:
        return [
            item
            for item in self.transacciones_ordenadas()
            if item.es_saliente_de(self.numero_cuenta)
        ]


@dataclass(slots=True)
class ResultadoRegla:
    cuenta_numero: str
    bank_code: str
    category: str
    pattern_type: str
    score_riesgo: int
    motivo: str
    transaction_id: int
    observed_transaction_id: int
    created_at: datetime
    data_protection_applied: bool = False


class MotorDeteccion:
    def __init__(
        self,
        *,
        micro_transfer_max: Decimal = Decimal("250.00"),
        leaf_nodes_threshold: int = 5,
        recruitment_window: timedelta = timedelta(hours=36),
        corridor_window: timedelta = timedelta(days=21),
        inactivity_window: timedelta = timedelta(days=180),
        recent_pin_change_window: timedelta = timedelta(hours=48),
        structuring_threshold: Decimal = Decimal("10000.00"),
        structuring_floor_ratio: Decimal = Decimal("0.85"),
        mule_large_incoming_threshold: Decimal = Decimal("5000.00"),
        association_seed_threshold: int = 80,
        association_low_risk_threshold: int = 30,
        association_max_depth: int = 2,
        cobros_victimas_min_remitentes: int = 10,
        cobros_victimas_max_monto: Decimal = Decimal("50.00"),
        cobros_victimas_min_pagos: int = 15,
        cobros_victimas_window: timedelta = timedelta(hours=48),
        coordinadora_min_depositos: int = 5,
        coordinadora_redistribucion_ratio: Decimal = Decimal("0.70"),
        coordinadora_min_destinos: int = 3,
        coordinadora_window: timedelta = timedelta(hours=6),
        mula_nueva_max_edad_dias: int = 30,
        mula_nueva_redistribucion_ratio: Decimal = Decimal("0.80"),
        mula_nueva_window: timedelta = timedelta(hours=24),
        nocturna_min_transacciones: int = 5,
        nocturna_window_dias: int = 7,
        nocturna_hora_inicio: int = 21,
        nocturna_hora_fin: int = 5,
        fragmentacion_min_micropagos: int = 8,
        fragmentacion_max_monto_micro: Decimal = Decimal("30.00"),
        fragmentacion_min_destinos: int = 4,
        red_cerrada_min_nodos: int = 3,
        red_cerrada_min_density: float = 0.6,
        cambio_brusco_factor: Decimal = Decimal("5.0"),
        cambio_brusco_min_historico: int = 5,
        geografia_max_horas: int = 4,
    ) -> None:
        self.micro_transfer_max = micro_transfer_max
        self.leaf_nodes_threshold = leaf_nodes_threshold
        self.recruitment_window = recruitment_window
        self.corridor_window = corridor_window
        self.inactivity_window = inactivity_window
        self.recent_pin_change_window = recent_pin_change_window
        self.structuring_threshold = structuring_threshold
        self.structuring_floor_ratio = structuring_floor_ratio
        self.mule_large_incoming_threshold = mule_large_incoming_threshold
        self.association_seed_threshold = association_seed_threshold
        self.association_low_risk_threshold = association_low_risk_threshold
        self.association_max_depth = association_max_depth
        self.corridor_sequence = ["COLOMBIA", "PANAMA", "COSTA RICA"]
        self.ads_keywords = (
            "META ADS",
            "FACEBOOK ADS",
            "INSTAGRAM ADS",
            "GOOGLE ADS",
            "TIKTOK ADS",
            "SOCIAL ADS",
        )
        self.cash_channels = {"cash", "branch_cash", "atm_cash", "branch", "cash_deposit"}
        self.cobros_victimas_min_remitentes = cobros_victimas_min_remitentes
        self.cobros_victimas_max_monto = cobros_victimas_max_monto
        self.cobros_victimas_min_pagos = cobros_victimas_min_pagos
        self.cobros_victimas_window = cobros_victimas_window
        self.coordinadora_min_depositos = coordinadora_min_depositos
        self.coordinadora_redistribucion_ratio = coordinadora_redistribucion_ratio
        self.coordinadora_min_destinos = coordinadora_min_destinos
        self.coordinadora_window = coordinadora_window
        self.mula_nueva_max_edad_dias = mula_nueva_max_edad_dias
        self.mula_nueva_redistribucion_ratio = mula_nueva_redistribucion_ratio
        self.mula_nueva_window = mula_nueva_window
        self.nocturna_min_transacciones = nocturna_min_transacciones
        self.nocturna_window_dias = nocturna_window_dias
        self.nocturna_hora_inicio = nocturna_hora_inicio
        self.nocturna_hora_fin = nocturna_hora_fin
        self.fragmentacion_min_micropagos = fragmentacion_min_micropagos
        self.fragmentacion_max_monto_micro = fragmentacion_max_monto_micro
        self.fragmentacion_min_destinos = fragmentacion_min_destinos
        self.red_cerrada_min_nodos = red_cerrada_min_nodos
        self.red_cerrada_min_density = red_cerrada_min_density
        self.cambio_brusco_factor = cambio_brusco_factor
        self.cambio_brusco_min_historico = cambio_brusco_min_historico
        self.geografia_max_horas = geografia_max_horas
        self._paises_conocidos = (
            "COLOMBIA", "PANAMA", "COSTA RICA", "NICARAGUA", "HONDURAS",
            "GUATEMALA", "MEXICO", "EL SALVADOR", "PERU", "ECUADOR",
            "VENEZUELA", "REPUBLICA DOMINICANA", "BRASIL", "ARGENTINA",
        )

    def evaluar_cuentas(self, cuentas: Iterable[Cuenta]) -> list[ResultadoRegla]:
        cuentas_por_numero = {cuenta.numero_cuenta: cuenta for cuenta in cuentas}
        alertas_directas: list[ResultadoRegla] = []

        for cuenta in cuentas_por_numero.values():
            resultados = [
                self.detectar_red_captacion(cuenta, cuentas_por_numero),
                self.detectar_corredores_transcontinentales(cuenta),
                self.detectar_captacion_digital(cuenta),
                self.detectar_activacion_cuenta_inactiva(cuenta),
                self.detectar_takeover_pin_fuga(cuenta),
                self.detectar_estructuracion(cuenta),
                self.detectar_cuenta_mula(cuenta),
                self.detectar_cobros_repetitivos_victimas(cuenta),
                self.detectar_cuenta_coordinadora(cuenta),
                self.detectar_mula_cuenta_nueva(cuenta),
                self.detectar_actividad_nocturna(cuenta),
                self.detectar_fragmentacion_fondos(cuenta),
                self.detectar_red_cerrada(cuenta, cuentas_por_numero),
                self.detectar_cambio_brusco_comportamiento(cuenta),
                self.detectar_geografia_inconsistente(cuenta),
                self.detectar_beneficiario_reportado(cuenta, cuentas_por_numero),
            ]
            alertas_cuenta = [resultado for resultado in resultados if resultado is not None]
            if any(resultado.category == TRATA_CATEGORY for resultado in alertas_cuenta):
                cuenta.datos_protegidos_por_investigacion = True
                for resultado in alertas_cuenta:
                    if resultado.category == TRATA_CATEGORY:
                        resultado.data_protection_applied = True
            alertas_directas.extend(alertas_cuenta)

        alertas_contagio = self.detectar_contagio_por_asociacion(
            cuentas_por_numero,
            alertas_directas,
        )
        alertas = [*alertas_directas, *alertas_contagio]
        return sorted(alertas, key=lambda item: (item.created_at, item.pattern_type))

    # ──────────────────────────────────────────────────────────────────────
    # REGLAS ORIGINALES
    # ──────────────────────────────────────────────────────────────────────

    def detectar_red_captacion(
        self,
        cuenta: Cuenta,
        cuentas_por_numero: dict[str, Cuenta],
    ) -> ResultadoRegla | None:
        incoming = cuenta.transacciones_entrantes()
        if len(incoming) < self.leaf_nodes_threshold:
            return None

        best_match: tuple[Transaccion, int] | None = None
        for pivot in incoming:
            if pivot.monto > self.micro_transfer_max:
                continue
            window_start = pivot.fecha_hora - self.recruitment_window
            window_transactions = [
                tx
                for tx in incoming
                if window_start <= tx.fecha_hora <= pivot.fecha_hora
                and tx.monto <= self.micro_transfer_max
            ]
            leaf_nodes = {
                tx.cuenta_origen
                for tx in window_transactions
                if self._is_leaf_like_source(
                    tx.cuenta_origen,
                    cuenta.numero_cuenta,
                    cuentas_por_numero,
                )
            }
            if len(leaf_nodes) >= self.leaf_nodes_threshold and (
                best_match is None or len(leaf_nodes) > best_match[1]
            ):
                best_match = (pivot, len(leaf_nodes))

        if best_match is None:
            return None

        pivot, leaf_count = best_match
        return ResultadoRegla(
            cuenta_numero=cuenta.numero_cuenta,
            bank_code=cuenta.banco_codigo,
            category=TRATA_CATEGORY,
            pattern_type="red_captacion",
            score_riesgo=min(99, 70 + (leaf_count * 4)),
            motivo=(
                f"La cuenta central recibe micro-transferencias de {leaf_count} nodos hoja "
                f"en menos de {int(self.recruitment_window.total_seconds() // 3600)} horas."
            ),
            transaction_id=pivot.transaction_id,
            observed_transaction_id=pivot.observed_transaction_id,
            created_at=pivot.fecha_hora,
        )

    def detectar_corredores_transcontinentales(
        self,
        cuenta: Cuenta,
    ) -> ResultadoRegla | None:
        transactions = [
            tx
            for tx in cuenta.transacciones_ordenadas()
            if tx.ubicacion_geografica
        ]
        if len(transactions) < len(self.corridor_sequence):
            return None

        path: list[tuple[str, Transaccion]] = []
        for tx in transactions:
            region = self._normalize_region(tx.ubicacion_geografica)
            if region is None:
                continue
            if path and path[-1][0] == region:
                continue
            path.append((region, tx))

        if len(path) < len(self.corridor_sequence):
            return None

        for start_index in range(0, len(path) - len(self.corridor_sequence) + 1):
            window = path[start_index : start_index + len(self.corridor_sequence)]
            regions = [item[0] for item in window]
            if regions == self.corridor_sequence:
                first_tx = window[0][1]
                last_tx = window[-1][1]
                if last_tx.fecha_hora - first_tx.fecha_hora <= self.corridor_window:
                    return ResultadoRegla(
                        cuenta_numero=cuenta.numero_cuenta,
                        bank_code=cuenta.banco_codigo,
                        category=TRATA_CATEGORY,
                        pattern_type="corredor_transcontinental",
                        score_riesgo=88,
                        motivo=(
                            "El historial geografico sigue un corredor fronterizo "
                            "Colombia -> Panama -> Costa Rica en pocas semanas."
                        ),
                        transaction_id=last_tx.transaction_id,
                        observed_transaction_id=last_tx.observed_transaction_id,
                        created_at=last_tx.fecha_hora,
                    )
        return None

    def detectar_captacion_digital(self, cuenta: Cuenta) -> ResultadoRegla | None:
        outgoing_ads = [
            tx
            for tx in cuenta.transacciones_salientes()
            if self._looks_like_ads_payment(tx)
        ]
        incoming_cash = [
            tx
            for tx in cuenta.transacciones_entrantes()
            if self._is_cash_at_dawn(tx)
        ]
        if not outgoing_ads or not incoming_cash:
            return None

        for incoming in incoming_cash:
            for outgoing in outgoing_ads:
                if abs(outgoing.fecha_hora - incoming.fecha_hora) <= timedelta(days=7):
                    trigger = outgoing if outgoing.fecha_hora >= incoming.fecha_hora else incoming
                    return ResultadoRegla(
                        cuenta_numero=cuenta.numero_cuenta,
                        bank_code=cuenta.banco_codigo,
                        category=TRATA_CATEGORY,
                        pattern_type="captacion_digital",
                        score_riesgo=91,
                        motivo=(
                            "La cuenta combina pagos a plataformas de anuncios con "
                            "depositos en efectivo de madrugada."
                        ),
                        transaction_id=trigger.transaction_id,
                        observed_transaction_id=trigger.observed_transaction_id,
                        created_at=trigger.fecha_hora,
                    )
        return None

    def detectar_activacion_cuenta_inactiva(self, cuenta: Cuenta) -> ResultadoRegla | None:
        ordered = cuenta.transacciones_ordenadas()
        if len(ordered) < 2:
            return None

        for index, transaction in enumerate(ordered):
            if not transaction.es_entrante_para(cuenta.numero_cuenta):
                continue

            previous_activity = ordered[index - 1].fecha_hora if index > 0 else cuenta.fecha_creacion
            if previous_activity is None:
                continue
            if transaction.fecha_hora - previous_activity < self.inactivity_window:
                continue

            outgoing_after = next(
                (
                    candidate
                    for candidate in ordered[index + 1 :]
                    if candidate.es_saliente_de(cuenta.numero_cuenta)
                    and candidate.fecha_hora - transaction.fecha_hora <= timedelta(hours=48)
                ),
                None,
            )
            if outgoing_after is not None:
                return ResultadoRegla(
                    cuenta_numero=cuenta.numero_cuenta,
                    bank_code=cuenta.banco_codigo,
                    category=ATO_CATEGORY,
                    pattern_type="activacion_cuenta_inactiva",
                    score_riesgo=76,
                    motivo=(
                        "Una cuenta inactiva por mas de 6 meses se reactiva, recibe fondos "
                        "y ejecuta una salida inmediata."
                    ),
                    transaction_id=outgoing_after.transaction_id,
                    observed_transaction_id=outgoing_after.observed_transaction_id,
                    created_at=outgoing_after.fecha_hora,
                )
        return None

    def detectar_takeover_pin_fuga(self, cuenta: Cuenta) -> ResultadoRegla | None:
        if cuenta.fecha_ultimo_cambio_pin is None:
            return None

        outgoing = cuenta.transacciones_salientes()
        known_beneficiaries: set[str] = set()
        for tx in outgoing:
            beneficiary_key = (tx.beneficiario or tx.cuenta_destino).upper()
            if tx.fecha_hora < cuenta.fecha_ultimo_cambio_pin:
                known_beneficiaries.add(beneficiary_key)
                continue

            if tx.fecha_hora - cuenta.fecha_ultimo_cambio_pin > self.recent_pin_change_window:
                continue
            if tx.saldo_origen_antes is None or tx.saldo_origen_antes <= 0:
                continue

            empties_account = tx.monto >= (tx.saldo_origen_antes * Decimal("0.75"))
            is_new_beneficiary = beneficiary_key not in known_beneficiaries
            if empties_account and is_new_beneficiary:
                return ResultadoRegla(
                    cuenta_numero=cuenta.numero_cuenta,
                    bank_code=cuenta.banco_codigo,
                    category=ATO_CATEGORY,
                    pattern_type="takeover_cambio_pin_fuga",
                    score_riesgo=96,
                    motivo=(
                        "Cambio reciente de credenciales seguido por una transferencia "
                        "que drena mas del 75% del saldo hacia un nuevo beneficiario."
                    ),
                    transaction_id=tx.transaction_id,
                    observed_transaction_id=tx.observed_transaction_id,
                    created_at=tx.fecha_hora,
                )
            known_beneficiaries.add(beneficiary_key)
        return None

    def detectar_estructuracion(self, cuenta: Cuenta) -> ResultadoRegla | None:
        incoming = cuenta.transacciones_entrantes()
        if len(incoming) < 4:
            return None

        lower_bound = self.structuring_threshold * self.structuring_floor_ratio
        for pivot in incoming:
            window_start = pivot.fecha_hora - timedelta(days=3)
            window_transactions = [
                tx
                for tx in incoming
                if window_start <= tx.fecha_hora <= pivot.fecha_hora
            ]
            total = sum((tx.monto for tx in window_transactions), Decimal("0.00"))
            fragmented = all(
                tx.monto < (self.structuring_threshold * Decimal("0.35"))
                for tx in window_transactions
            )
            if (
                lower_bound <= total < self.structuring_threshold
                and len(window_transactions) >= 4
                and fragmented
            ):
                return ResultadoRegla(
                    cuenta_numero=cuenta.numero_cuenta,
                    bank_code=cuenta.banco_codigo,
                    category=AML_CATEGORY,
                    pattern_type="estructuracion_smurfing",
                    score_riesgo=79,
                    motivo=(
                        "Las entradas fraccionadas de los ultimos 3 dias suman un monto "
                        "cercano al umbral regulatorio sin rebasarlo."
                    ),
                    transaction_id=pivot.transaction_id,
                    observed_transaction_id=pivot.observed_transaction_id,
                    created_at=pivot.fecha_hora,
                )
        return None

    def detectar_cuenta_mula(self, cuenta: Cuenta) -> ResultadoRegla | None:
        incoming = cuenta.transacciones_entrantes()
        outgoing = cuenta.transacciones_salientes()
        if not incoming or not outgoing:
            return None

        for incoming_tx in incoming:
            if incoming_tx.monto < self.mule_large_incoming_threshold:
                continue

            outgoing_window = [
                tx
                for tx in outgoing
                if incoming_tx.fecha_hora <= tx.fecha_hora <= incoming_tx.fecha_hora + timedelta(hours=24)
            ]
            total_out = sum((tx.monto for tx in outgoing_window), Decimal("0.00"))
            unique_targets = {tx.cuenta_destino for tx in outgoing_window}
            if total_out >= (incoming_tx.monto * Decimal("0.90")) and len(unique_targets) >= 2:
                trigger = outgoing_window[-1]
                return ResultadoRegla(
                    cuenta_numero=cuenta.numero_cuenta,
                    bank_code=cuenta.banco_codigo,
                    category=AML_CATEGORY,
                    pattern_type="cuenta_mula",
                    score_riesgo=89,
                    motivo=(
                        "La cuenta recibe fondos altos y en menos de 24 horas redistribuye "
                        "entre multiples terceros casi todo el monto."
                    ),
                    transaction_id=trigger.transaction_id,
                    observed_transaction_id=trigger.observed_transaction_id,
                    created_at=trigger.fecha_hora,
                )
        return None

    # ──────────────────────────────────────────────────────────────────────
    # REGLAS NUEVAS — FLOWLENS 360
    # ──────────────────────────────────────────────────────────────────────

    def detectar_cobros_repetitivos_victimas(
        self,
        cuenta: Cuenta,
    ) -> ResultadoRegla | None:
        """Regla A: Muchos pagos pequenos de multiples remitentes distintos a una sola cuenta."""
        incoming = cuenta.transacciones_entrantes()
        if len(incoming) < self.cobros_victimas_min_pagos:
            return None

        for pivot in incoming:
            window_start = pivot.fecha_hora - self.cobros_victimas_window
            window_txs = [
                tx for tx in incoming
                if window_start <= tx.fecha_hora <= pivot.fecha_hora
                and tx.monto <= self.cobros_victimas_max_monto
            ]
            if len(window_txs) < self.cobros_victimas_min_pagos:
                continue
            remitentes = {tx.cuenta_origen for tx in window_txs}
            if len(remitentes) >= self.cobros_victimas_min_remitentes:
                return ResultadoRegla(
                    cuenta_numero=cuenta.numero_cuenta,
                    bank_code=cuenta.banco_codigo,
                    category=TRATA_CATEGORY,
                    pattern_type="cobros_repetitivos_victimas",
                    score_riesgo=min(99, 82 + len(remitentes)),
                    motivo=(
                        f"La cuenta recibe {len(window_txs)} pagos menores a "
                        f"${self.cobros_victimas_max_monto} de {len(remitentes)} remitentes "
                        f"distintos en {int(self.cobros_victimas_window.total_seconds() // 3600)}h. "
                        f"Patron consistente con cobros de explotacion."
                    ),
                    transaction_id=pivot.transaction_id,
                    observed_transaction_id=pivot.observed_transaction_id,
                    created_at=pivot.fecha_hora,
                )
        return None

    def detectar_cuenta_coordinadora(
        self,
        cuenta: Cuenta,
    ) -> ResultadoRegla | None:
        """Regla B: Recibe multiples depositos y redistribuye a terceros en pocas horas."""
        incoming = cuenta.transacciones_entrantes()
        outgoing = cuenta.transacciones_salientes()
        if len(incoming) < self.coordinadora_min_depositos or not outgoing:
            return None

        for pivot_in in incoming:
            window_end = pivot_in.fecha_hora + self.coordinadora_window
            depositos_window = [
                tx for tx in incoming
                if pivot_in.fecha_hora <= tx.fecha_hora <= window_end
            ]
            if len(depositos_window) < self.coordinadora_min_depositos:
                continue
            origenes = {tx.cuenta_origen for tx in depositos_window}
            if len(origenes) < 3:
                continue
            total_in = sum((tx.monto for tx in depositos_window), Decimal("0.00"))

            salidas_window = [
                tx for tx in outgoing
                if pivot_in.fecha_hora <= tx.fecha_hora <= window_end
            ]
            if not salidas_window:
                continue
            total_out = sum((tx.monto for tx in salidas_window), Decimal("0.00"))
            destinos = {tx.cuenta_destino for tx in salidas_window}

            if (
                total_out >= total_in * self.coordinadora_redistribucion_ratio
                and len(destinos) >= self.coordinadora_min_destinos
            ):
                trigger = salidas_window[-1]
                return ResultadoRegla(
                    cuenta_numero=cuenta.numero_cuenta,
                    bank_code=cuenta.banco_codigo,
                    category=TRATA_CATEGORY,
                    pattern_type="cuenta_coordinadora_logistica",
                    score_riesgo=min(99, 85 + len(destinos)),
                    motivo=(
                        f"Cuenta coordinadora: recibe {len(depositos_window)} depositos de "
                        f"{len(origenes)} origenes y redistribuye {total_out} a {len(destinos)} "
                        f"destinos en menos de "
                        f"{int(self.coordinadora_window.total_seconds() // 3600)}h."
                    ),
                    transaction_id=trigger.transaction_id,
                    observed_transaction_id=trigger.observed_transaction_id,
                    created_at=trigger.fecha_hora,
                )
        return None

    def detectar_mula_cuenta_nueva(
        self,
        cuenta: Cuenta,
    ) -> ResultadoRegla | None:
        """Regla C: Cuenta nueva (<30 dias) que recibe dinero y reenvia 80%+ rapidamente."""
        if cuenta.fecha_creacion is None or cuenta.fecha_ultima_actividad is None:
            return None
        edad_dias = (cuenta.fecha_ultima_actividad - cuenta.fecha_creacion).days
        if edad_dias > self.mula_nueva_max_edad_dias:
            return None

        incoming = cuenta.transacciones_entrantes()
        outgoing = cuenta.transacciones_salientes()
        if not incoming or not outgoing:
            return None

        total_in = sum((tx.monto for tx in incoming), Decimal("0.00"))
        if total_in <= Decimal("0"):
            return None

        for in_tx in incoming:
            rapidas = [
                tx for tx in outgoing
                if in_tx.fecha_hora <= tx.fecha_hora <= in_tx.fecha_hora + self.mula_nueva_window
            ]
            if not rapidas:
                continue
            total_rapido = sum((tx.monto for tx in rapidas), Decimal("0.00"))
            ratio = total_rapido / in_tx.monto if in_tx.monto > 0 else Decimal("0")
            if ratio >= self.mula_nueva_redistribucion_ratio:
                trigger = rapidas[-1]
                return ResultadoRegla(
                    cuenta_numero=cuenta.numero_cuenta,
                    bank_code=cuenta.banco_codigo,
                    category=AML_CATEGORY,
                    pattern_type="mula_cuenta_nueva",
                    score_riesgo=min(99, 84 + min(15, self.mula_nueva_max_edad_dias - edad_dias)),
                    motivo=(
                        f"Cuenta nueva ({edad_dias} dias) recibe fondos y redistribuye "
                        f"el {int(ratio * 100)}% en menos de "
                        f"{int(self.mula_nueva_window.total_seconds() // 3600)}h. "
                        f"Patron de mula financiera con cuenta recien creada."
                    ),
                    transaction_id=trigger.transaction_id,
                    observed_transaction_id=trigger.observed_transaction_id,
                    created_at=trigger.fecha_hora,
                )
        return None

    def detectar_actividad_nocturna(
        self,
        cuenta: Cuenta,
    ) -> ResultadoRegla | None:
        """Regla D: Ingresos frecuentes entre 9PM y 5AM en multiples dias."""
        incoming = cuenta.transacciones_entrantes()
        nocturnas = [
            tx for tx in incoming
            if tx.fecha_hora.hour >= self.nocturna_hora_inicio
            or tx.fecha_hora.hour < self.nocturna_hora_fin
        ]
        if len(nocturnas) < self.nocturna_min_transacciones:
            return None

        nocturnas_sorted = sorted(nocturnas, key=lambda tx: tx.fecha_hora)
        window = timedelta(days=self.nocturna_window_dias)
        for pivot in nocturnas_sorted:
            window_txs = [
                tx for tx in nocturnas_sorted
                if pivot.fecha_hora - window <= tx.fecha_hora <= pivot.fecha_hora
            ]
            if len(window_txs) < self.nocturna_min_transacciones:
                continue
            dias_unicos = len({tx.fecha_hora.date() for tx in window_txs})
            if dias_unicos >= 3:
                total_nocturno = sum((tx.monto for tx in window_txs), Decimal("0.00"))
                return ResultadoRegla(
                    cuenta_numero=cuenta.numero_cuenta,
                    bank_code=cuenta.banco_codigo,
                    category=TRATA_CATEGORY,
                    pattern_type="actividad_nocturna_repetitiva",
                    score_riesgo=min(99, 75 + len(window_txs) * 2),
                    motivo=(
                        f"La cuenta recibe {len(window_txs)} transacciones nocturnas "
                        f"(entre {self.nocturna_hora_inicio}:00 y {self.nocturna_hora_fin}:00) "
                        f"por un total de {total_nocturno} en {dias_unicos} dias distintos. "
                        f"Patron consistente con explotacion sexual o laboral."
                    ),
                    transaction_id=pivot.transaction_id,
                    observed_transaction_id=pivot.observed_transaction_id,
                    created_at=pivot.fecha_hora,
                )
        return None

    def detectar_fragmentacion_fondos(
        self,
        cuenta: Cuenta,
    ) -> ResultadoRegla | None:
        """Regla E: Recibe muchos micropagos y dispersa a varias cuentas."""
        incoming = cuenta.transacciones_entrantes()
        outgoing = cuenta.transacciones_salientes()
        micropagos = [
            tx for tx in incoming
            if tx.monto <= self.fragmentacion_max_monto_micro
        ]
        if len(micropagos) < self.fragmentacion_min_micropagos:
            return None
        destinos = {tx.cuenta_destino for tx in outgoing}
        if len(destinos) < self.fragmentacion_min_destinos:
            return None

        total_micro = sum((tx.monto for tx in micropagos), Decimal("0.00"))
        trigger = micropagos[-1]
        return ResultadoRegla(
            cuenta_numero=cuenta.numero_cuenta,
            bank_code=cuenta.banco_codigo,
            category=AML_CATEGORY,
            pattern_type="fragmentacion_fondos",
            score_riesgo=min(99, 72 + len(micropagos) + len(destinos) * 2),
            motivo=(
                f"La cuenta recibe {len(micropagos)} micropagos "
                f"(monto <= ${self.fragmentacion_max_monto_micro}, total: {total_micro}) "
                f"y dispersa fondos a {len(destinos)} cuentas distintas. "
                f"Posible fragmentacion para evadir umbrales."
            ),
            transaction_id=trigger.transaction_id,
            observed_transaction_id=trigger.observed_transaction_id,
            created_at=trigger.fecha_hora,
        )

    def detectar_red_cerrada(
        self,
        cuenta: Cuenta,
        cuentas_por_numero: dict[str, Cuenta],
    ) -> ResultadoRegla | None:
        """Regla F: Grupo de cuentas se envia dinero constantemente entre si."""
        contrapartes_salientes = {
            tx.cuenta_destino for tx in cuenta.transacciones_salientes()
        }
        contrapartes_entrantes = {
            tx.cuenta_origen for tx in cuenta.transacciones_entrantes()
        }
        bidireccionales = contrapartes_salientes & contrapartes_entrantes
        if len(bidireccionales) < self.red_cerrada_min_nodos - 1:
            return None

        clique = {cuenta.numero_cuenta} | bidireccionales
        if len(clique) < self.red_cerrada_min_nodos:
            return None

        total_pairs = len(clique) * (len(clique) - 1)
        if total_pairs == 0:
            return None
        connected_pairs = 0
        for member_num in clique:
            member = cuentas_por_numero.get(member_num)
            if member is None:
                continue
            peers = (
                {tx.cuenta_destino for tx in member.transacciones_salientes()}
                | {tx.cuenta_origen for tx in member.transacciones_entrantes()}
            ) & clique - {member_num}
            connected_pairs += len(peers)

        density = connected_pairs / total_pairs
        if density < self.red_cerrada_min_density:
            return None

        ordered = cuenta.transacciones_ordenadas()
        if not ordered:
            return None
        trigger_tx = ordered[-1]
        return ResultadoRegla(
            cuenta_numero=cuenta.numero_cuenta,
            bank_code=cuenta.banco_codigo,
            category=AML_CATEGORY,
            pattern_type="red_cerrada_criminal",
            score_riesgo=min(99, 81 + len(clique) * 3),
            motivo=(
                f"La cuenta forma parte de una red cerrada de {len(clique)} cuentas "
                f"con intercambio bidireccional constante (densidad: {density:.0%}). "
                f"Patron tipico de organizacion criminal o lavado circular."
            ),
            transaction_id=trigger_tx.transaction_id,
            observed_transaction_id=trigger_tx.observed_transaction_id,
            created_at=trigger_tx.fecha_hora,
        )

    def detectar_cambio_brusco_comportamiento(
        self,
        cuenta: Cuenta,
    ) -> ResultadoRegla | None:
        """Regla G: Montos de transaccion significativamente mayores al promedio historico."""
        outgoing = cuenta.transacciones_salientes()
        if len(outgoing) < self.cambio_brusco_min_historico:
            return None

        montos = [tx.monto for tx in outgoing]
        promedio = sum(montos, Decimal("0.00")) / len(montos)
        if promedio <= Decimal("0"):
            return None

        for tx in reversed(outgoing):
            factor = tx.monto / promedio
            if factor >= self.cambio_brusco_factor:
                return ResultadoRegla(
                    cuenta_numero=cuenta.numero_cuenta,
                    bank_code=cuenta.banco_codigo,
                    category=AML_CATEGORY,
                    pattern_type="cambio_brusco_comportamiento",
                    score_riesgo=min(99, 70 + int(min(Decimal("29"), (factor - 1) * 5))),
                    motivo=(
                        f"Transferencia de {tx.monto} supera {factor:.1f}x "
                        f"el promedio historico de {promedio:.2f}. "
                        f"Cambio brusco de comportamiento transaccional."
                    ),
                    transaction_id=tx.transaction_id,
                    observed_transaction_id=tx.observed_transaction_id,
                    created_at=tx.fecha_hora,
                )
        return None

    def detectar_geografia_inconsistente(
        self,
        cuenta: Cuenta,
    ) -> ResultadoRegla | None:
        """Regla H: Transacciones desde ubicaciones incompatibles en pocas horas."""
        txs_con_ubicacion = [
            tx for tx in cuenta.transacciones_ordenadas()
            if tx.ubicacion_geografica
        ]
        if len(txs_con_ubicacion) < 2:
            return None

        max_delta = timedelta(hours=self.geografia_max_horas)
        for i in range(len(txs_con_ubicacion) - 1):
            tx_a = txs_con_ubicacion[i]
            tx_b = txs_con_ubicacion[i + 1]
            delta = tx_b.fecha_hora - tx_a.fecha_hora
            if delta > max_delta or delta <= timedelta(0):
                continue
            loc_a = tx_a.ubicacion_geografica.upper()
            loc_b = tx_b.ubicacion_geografica.upper()
            if loc_a != loc_b and self._ubicaciones_incompatibles(loc_a, loc_b):
                horas = delta.total_seconds() / 3600
                return ResultadoRegla(
                    cuenta_numero=cuenta.numero_cuenta,
                    bank_code=cuenta.banco_codigo,
                    category=ATO_CATEGORY,
                    pattern_type="geografia_inconsistente",
                    score_riesgo=83,
                    motivo=(
                        f"Transacciones desde {tx_a.ubicacion_geografica} y "
                        f"{tx_b.ubicacion_geografica} en {horas:.1f} horas. "
                        f"Ubicaciones geograficamente incompatibles."
                    ),
                    transaction_id=tx_b.transaction_id,
                    observed_transaction_id=tx_b.observed_transaction_id,
                    created_at=tx_b.fecha_hora,
                )
        return None

    def detectar_beneficiario_reportado(
        self,
        cuenta: Cuenta,
        cuentas_por_numero: dict[str, Cuenta],
    ) -> ResultadoRegla | None:
        """Regla I: Envio de fondos a cuenta previamente reportada o bajo investigacion."""
        for tx in reversed(cuenta.transacciones_salientes()):
            destino = cuentas_por_numero.get(tx.cuenta_destino)
            if destino is None:
                continue
            if destino.reportada or destino.datos_protegidos_por_investigacion:
                bajo_investigacion = destino.datos_protegidos_por_investigacion
                return ResultadoRegla(
                    cuenta_numero=cuenta.numero_cuenta,
                    bank_code=cuenta.banco_codigo,
                    category=RELATIONAL_CATEGORY,
                    pattern_type="beneficiario_reportado",
                    score_riesgo=88 if bajo_investigacion else 75,
                    motivo=(
                        f"La cuenta envia fondos a {tx.cuenta_destino} que se encuentra "
                        f"{'bajo investigacion protegida' if bajo_investigacion else 'previamente reportada'}. "
                        f"Monto: {tx.monto}."
                    ),
                    transaction_id=tx.transaction_id,
                    observed_transaction_id=tx.observed_transaction_id,
                    created_at=tx.fecha_hora,
                )
        return None

    # ──────────────────────────────────────────────────────────────────────
    # CONTAGIO POR ASOCIACION (grafo transaccional)
    # ──────────────────────────────────────────────────────────────────────

    def detectar_contagio_por_asociacion(
        self,
        cuentas_por_numero: dict[str, Cuenta],
        alertas_directas: list[ResultadoRegla],
    ) -> list[ResultadoRegla]:
        puntajes_base = self._max_score_por_cuenta(alertas_directas)
        cuentas_semilla = {
            numero_cuenta
            for numero_cuenta, cuenta in cuentas_por_numero.items()
            if puntajes_base.get(numero_cuenta, 0) > self.association_seed_threshold
            or cuenta.reportada
        }
        if not cuentas_semilla:
            return []

        grafo = self._build_transaction_graph(cuentas_por_numero)
        alertas: list[ResultadoRegla] = []
        for cuenta in cuentas_por_numero.values():
            puntaje_actual = puntajes_base.get(cuenta.numero_cuenta, 0)
            if cuenta.numero_cuenta in cuentas_semilla:
                continue
            if puntaje_actual > self.association_low_risk_threshold:
                continue

            exposicion = self._find_association_exposure(
                cuenta.numero_cuenta,
                cuentas_semilla,
                puntajes_base,
                cuentas_por_numero,
                grafo,
            )
            if exposicion is None:
                continue

            trigger = exposicion["trigger"]
            profundidad = int(exposicion["depth"])
            puntaje_semilla = int(exposicion["seed_score"])
            semilla_protegida = bool(exposicion["seed_protected"])
            semilla_reportada = bool(exposicion["seed_reported"])
            motivo = (
                "La cuenta mantiene una relacion transaccional directa con una cuenta "
                "de alto riesgo o previamente reportada."
                if profundidad == 1
                else "La cuenta queda expuesta a 2 niveles de profundidad en el grafo "
                "transaccional por relacion con una cuenta sospechosa."
            )
            if semilla_reportada:
                motivo += " La cuenta semilla ya habia sido reportada en analytics."
            elif puntaje_semilla:
                motivo += f" La cuenta semilla presenta un score base de {puntaje_semilla}."

            alertas.append(
                ResultadoRegla(
                    cuenta_numero=cuenta.numero_cuenta,
                    bank_code=cuenta.banco_codigo,
                    category=RELATIONAL_CATEGORY,
                    pattern_type="contagio_asociacion",
                    score_riesgo=self._association_score(
                        depth=profundidad,
                        seed_score=puntaje_semilla,
                        seed_reported=semilla_reportada,
                        seed_protected=semilla_protegida,
                    ),
                    motivo=motivo,
                    transaction_id=trigger.transaction_id,
                    observed_transaction_id=trigger.observed_transaction_id,
                    created_at=trigger.fecha_hora,
                )
            )

        return alertas

    # ──────────────────────────────────────────────────────────────────────
    # METODOS AUXILIARES PRIVADOS
    # ──────────────────────────────────────────────────────────────────────

    def _is_leaf_like_source(
        self,
        source_account_number: str,
        target_account_number: str,
        cuentas_por_numero: dict[str, Cuenta],
    ) -> bool:
        source_account = cuentas_por_numero.get(source_account_number)
        if source_account is None:
            return True

        outgoing_counterparties = {
            tx.cuenta_destino
            for tx in source_account.transacciones_salientes()
        }
        if outgoing_counterparties == {target_account_number}:
            return True
        return len(outgoing_counterparties) <= 1 and len(source_account.transacciones) <= 3

    def _normalize_region(self, location: str) -> str | None:
        normalized = location.upper()
        if "COLOMBIA" in normalized:
            return "COLOMBIA"
        if "PANAMA" in normalized:
            return "PANAMA"
        if "COSTA RICA" in normalized or "SAN JOSE, CR" in normalized:
            return "COSTA RICA"
        return None

    def _looks_like_ads_payment(self, tx: Transaccion) -> bool:
        text = f"{tx.beneficiario} {tx.concepto}".upper()
        return any(keyword in text for keyword in self.ads_keywords)

    def _is_cash_at_dawn(self, tx: Transaccion) -> bool:
        channel = tx.canal.lower().strip()
        return (channel in self.cash_channels or "cash" in channel) and tx.fecha_hora.hour < 6

    def _max_score_por_cuenta(
        self,
        alertas: list[ResultadoRegla],
    ) -> dict[str, int]:
        puntajes: dict[str, int] = {}
        for alerta in alertas:
            puntajes[alerta.cuenta_numero] = max(
                puntajes.get(alerta.cuenta_numero, 0),
                alerta.score_riesgo,
            )
        return puntajes

    def _build_transaction_graph(
        self,
        cuentas_por_numero: dict[str, Cuenta],
    ) -> dict[str, dict[str, Transaccion]]:
        grafo = {numero_cuenta: {} for numero_cuenta in cuentas_por_numero}
        transacciones_vistas: set[tuple[int, int]] = set()

        for cuenta in cuentas_por_numero.values():
            for tx in cuenta.transacciones:
                clave_tx = (tx.transaction_id, tx.observed_transaction_id)
                if clave_tx in transacciones_vistas or tx.estado != "completed":
                    continue
                transacciones_vistas.add(clave_tx)
                if tx.cuenta_origen == tx.cuenta_destino:
                    continue

                grafo.setdefault(tx.cuenta_origen, {})
                grafo.setdefault(tx.cuenta_destino, {})
                previa = grafo[tx.cuenta_origen].get(tx.cuenta_destino)
                if previa is None or tx.fecha_hora >= previa.fecha_hora:
                    grafo[tx.cuenta_origen][tx.cuenta_destino] = tx
                    grafo[tx.cuenta_destino][tx.cuenta_origen] = tx

        return grafo

    def _find_association_exposure(
        self,
        cuenta_objetivo: str,
        cuentas_semilla: set[str],
        puntajes_base: dict[str, int],
        cuentas_por_numero: dict[str, Cuenta],
        grafo: dict[str, dict[str, Transaccion]],
    ) -> dict[str, object] | None:
        if cuenta_objetivo not in grafo:
            return None

        queue = deque([(cuenta_objetivo, 0, None)])
        visitados = {cuenta_objetivo}
        mejores_candidatos: list[dict[str, object]] = []

        while queue:
            actual, profundidad, edge_to_actual = queue.popleft()
            if profundidad >= self.association_max_depth:
                continue

            for vecino, tx in sorted(
                grafo.get(actual, {}).items(),
                key=lambda item: item[1].fecha_hora,
                reverse=True,
            ):
                siguiente_profundidad = profundidad + 1
                if vecino in cuentas_semilla:
                    trigger = tx if edge_to_actual is None else max(
                        (edge_to_actual, tx),
                        key=lambda item: item.fecha_hora,
                    )
                    mejores_candidatos.append(
                        {
                            "depth": siguiente_profundidad,
                            "seed_account": vecino,
                            "seed_score": puntajes_base.get(vecino, 0),
                            "seed_reported": cuentas_por_numero[vecino].reportada,
                            "seed_protected": cuentas_por_numero[vecino].datos_protegidos_por_investigacion,
                            "trigger": trigger,
                        }
                    )
                    continue

                if vecino in visitados or siguiente_profundidad >= self.association_max_depth:
                    continue
                visitados.add(vecino)
                queue.append((vecino, siguiente_profundidad, tx if edge_to_actual is None else edge_to_actual))

        if not mejores_candidatos:
            return None

        mejores_candidatos.sort(
            key=lambda item: (
                int(item["depth"]),
                -int(item["seed_score"]),
                0 if bool(item["seed_reported"]) else 1,
                0 if bool(item["seed_protected"]) else 1,
                -item["trigger"].fecha_hora.timestamp(),
            )
        )
        return mejores_candidatos[0]

    def _association_score(
        self,
        *,
        depth: int,
        seed_score: int,
        seed_reported: bool,
        seed_protected: bool,
    ) -> int:
        score = 64 if depth == 1 else 48
        if seed_score >= 95:
            score += 12
        elif seed_score >= 90:
            score += 8
        elif seed_score >= 85:
            score += 5
        elif seed_score > self.association_seed_threshold:
            score += 3
        if seed_reported:
            score += 8
        if seed_protected:
            score += 3
        return min(89, score)

    def _ubicaciones_incompatibles(self, loc_a: str, loc_b: str) -> bool:
        pais_a = self._extraer_pais(loc_a)
        pais_b = self._extraer_pais(loc_b)
        if pais_a and pais_b:
            return pais_a != pais_b
        return loc_a != loc_b

    def _extraer_pais(self, ubicacion: str) -> str | None:
        for pais in self._paises_conocidos:
            if pais in ubicacion:
                return pais
        return None
