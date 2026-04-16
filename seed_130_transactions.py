"""
seed_130_transactions.py
━━━━━━━━━━━━━━━━━━━━━━━━
Genera 130 transacciones distribuidas entre los tres bancos (BKA, BKB, BKC)
con patrones variados que activan múltiples alertas de riesgo en analytics.

Requisitos previos:
  1. Los tres bancos y analytics deben estar corriendo:
       python banco_a/run.py &   # puerto 8001
       python banco_b/run.py &   # puerto 8002
       python banco_c/run.py &   # puerto 8004
       python analytics/run.py & # puerto 8003
  2. Los seeds locales deben haberse ejecutado:
       python banco_a/seed.py
       python banco_b/seed.py
       python banco_c/seed.py

Uso:
    python seed_130_transactions.py

Al terminar ejecuta /transactions/fetch en analytics para reflejar los nuevos datos.
"""

import os
import random
import time
from typing import Any

import httpx


# ── Configuración ────────────────────────────────────────────────────────────

BANK_A_URL = os.getenv("FLOWLENS_BANK_A_URL", "http://127.0.0.1:8001")
BANK_B_URL = os.getenv("FLOWLENS_BANK_B_URL", "http://127.0.0.1:8002")
BANK_C_URL = os.getenv("FLOWLENS_BANK_C_URL", "http://127.0.0.1:8004")
ANALYTICS_URL = os.getenv("FLOWLENS_ANALYTICS_URL", "http://127.0.0.1:8003")
ANALYTICS_API_KEY = os.getenv("FLOWLENS_ANALYTICS_API_KEY", "flowlens-analytics-key-dev")
DEFAULT_PASSWORD = "DemoPass123"

BANK_CONFIGS = {
    "BKA": {"url": BANK_A_URL, "demo_email": "demo@bancoa.com"},
    "BKB": {"url": BANK_B_URL, "demo_email": "demo@bancob.com"},
    "BKC": {"url": BANK_C_URL, "demo_email": "demo@bancoc.com"},
}

# Usuarios de cada banco (deben existir en la BD tras ejecutar seed.py)
BANK_USERS = {
    "BKA": [
        "demo@bancoa.com",
        "ana@bancoa.com",
        "carlos@bancoa.com",
        "luisa@bancoa.com",
        "pablo@bancoa.com",
        "sofia@bancoa.com",
    ],
    "BKB": [
        "demo@bancob.com",
        "juan@bancob.com",
        "maria@bancob.com",
        "pedro@bancob.com",
        "laura@bancob.com",
        "jorge@bancob.com",
    ],
    "BKC": [
        "demo@bancoc.com",
        "roberto@bancoc.com",
        "elena@bancoc.com",
        "miguel@bancoc.com",
        "valeria@bancoc.com",
        "diego@bancoc.com",
    ],
}

LOCATIONS = [
    "San Jose, CR", "Heredia, CR", "Alajuela, CR",
    "Cartago, CR", "Limón, CR", "Guanacaste, CR",
]
CHANNELS = ["web", "mobile", "api"]


# ── HTTP helpers ──────────────────────────────────────────────────────────────

def request_json(
    client: httpx.Client,
    method: str,
    url: str,
    *,
    headers: dict[str, str] | None = None,
    json: dict[str, Any] | None = None,
) -> Any:
    response = client.request(method, url, headers=headers, json=json, timeout=10.0)
    response.raise_for_status()
    if response.content:
        return response.json()
    return None


def login(client: httpx.Client, base_url: str, email: str) -> tuple[str, list[dict]]:
    payload = request_json(
        client, "POST", f"{base_url}/auth/login",
        json={"email": email, "password": DEFAULT_PASSWORD},
    )
    token = payload["access_token"]
    accounts = request_json(
        client, "GET", f"{base_url}/accounts/my",
        headers={"Authorization": f"Bearer {token}"},
    )
    return token, accounts


def transfer_internal(
    client: httpx.Client,
    base_url: str,
    token: str,
    src: str,
    dst: str,
    amount: float,
    description: str = "Transferencia demo",
) -> dict | None:
    try:
        return request_json(
            client, "POST", f"{base_url}/transactions/internal",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "source_account_number": src,
                "destination_account_number": dst,
                "amount": amount,
                "channel": random.choice(CHANNELS),
                "location": random.choice(LOCATIONS),
                "description": description,
            },
        )
    except httpx.HTTPStatusError as exc:
        print(f"  [WARN] internal {src}→{dst} {amount}: {exc.response.status_code}")
        return None


def transfer_interbank(
    client: httpx.Client,
    base_url: str,
    token: str,
    src: str,
    dst: str,
    amount: float,
    description: str = "Transferencia interbancaria demo",
) -> dict | None:
    try:
        return request_json(
            client, "POST", f"{base_url}/transactions/interbank",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "source_account_number": src,
                "destination_account_number": dst,
                "amount": amount,
                "channel": random.choice(CHANNELS),
                "location": random.choice(LOCATIONS),
                "description": description,
            },
        )
    except httpx.HTTPStatusError as exc:
        print(f"  [WARN] interbank {src}→{dst} {amount}: {exc.response.status_code}")
        return None


# ── Carga de sesiones ─────────────────────────────────────────────────────────

def load_sessions(client: httpx.Client) -> dict:
    """Devuelve {bank_code: {email: (token, [accounts])}}"""
    sessions: dict = {}
    for bank_code, users in BANK_USERS.items():
        base_url = BANK_CONFIGS[bank_code]["url"]
        sessions[bank_code] = {}
        for email in users:
            try:
                token, accounts = login(client, base_url, email)
                sessions[bank_code][email] = (token, accounts)
                print(f"  ✓ login {bank_code} {email} → {len(accounts)} cuenta(s)")
            except Exception as exc:
                print(f"  ✗ login fallido {bank_code} {email}: {exc}")
    return sessions


# ── Bloques de transacciones ──────────────────────────────────────────────────

def block_internal_regular(client, sessions, counter):
    """30 transferencias internas rutinarias en los tres bancos."""
    print("\n[Bloque 1] 30 transferencias internas regulares")
    done = 0
    for bank_code in ["BKA", "BKB", "BKC"]:
        bank_sessions = sessions.get(bank_code, {})
        accounts_all = []
        tokens_map = {}
        for email, (token, accs) in bank_sessions.items():
            for acc in accs:
                accounts_all.append(acc["account_number"])
                tokens_map[acc["account_number"]] = (token, BANK_CONFIGS[bank_code]["url"])

        if len(accounts_all) < 2:
            continue

        for _ in range(10):
            src, dst = random.sample(accounts_all, 2)
            token, base_url = tokens_map[src]
            amount = round(random.uniform(500, 4000), 2)
            result = transfer_internal(
                client, base_url, token, src, dst, amount,
                description="Pago rutinario interno",
            )
            if result:
                done += 1
                counter[0] += 1
                print(f"  [{counter[0]:03d}] {bank_code} int {src[-6:]}→{dst[-6:]} ₡{amount:,.0f}")
    return done


def block_high_amount(client, sessions, counter):
    """10 transferencias de alto monto (≥10,000) — activa HIGH_AMOUNT."""
    print("\n[Bloque 2] 10 transferencias de alto monto")
    done = 0
    pairs = [
        ("BKA", "demo@bancoa.com", "BKB", "demo@bancob.com"),
        ("BKB", "demo@bancob.com", "BKA", "demo@bancoa.com"),
        ("BKA", "demo@bancoa.com", "BKC", "demo@bancoc.com"),
        ("BKC", "demo@bancoc.com", "BKB", "demo@bancob.com"),
        ("BKB", "demo@bancob.com", "BKC", "demo@bancoc.com"),
    ]
    for src_bank, src_email, dst_bank, dst_email in pairs:
        src_token, src_accs = sessions[src_bank].get(src_email, (None, []))
        _, dst_accs = sessions[dst_bank].get(dst_email, (None, []))
        if not src_token or not src_accs or not dst_accs:
            continue
        src_acc = src_accs[0]["account_number"]
        dst_acc = dst_accs[0]["account_number"]
        for _ in range(2):
            amount = round(random.uniform(10_500, 28_000), 2)
            result = transfer_interbank(
                client, BANK_CONFIGS[src_bank]["url"], src_token,
                src_acc, dst_acc, amount,
                description="Transferencia de alto valor",
            )
            if result:
                done += 1
                counter[0] += 1
                print(f"  [{counter[0]:03d}] {src_bank}→{dst_bank} ₡{amount:,.0f} [ALTO MONTO]")
    return done


def block_burst_small(client, sessions, counter):
    """20 ráfagas de montos pequeños (≤250) en <1h — activa BURST_SMALL."""
    print("\n[Bloque 3] 20 ráfagas de pequeños pagos")
    done = 0
    burst_configs = [
        ("BKA", "demo@bancoa.com", "ana@bancoa.com"),
        ("BKB", "demo@bancob.com", "juan@bancob.com"),
        ("BKC", "demo@bancoc.com", "diego@bancoc.com"),
        ("BKA", "carlos@bancoa.com", "sofia@bancoa.com"),
    ]
    for src_bank, src_email, dst_email in burst_configs:
        src_token, src_accs = sessions[src_bank].get(src_email, (None, []))
        _, dst_accs = sessions[src_bank].get(dst_email, (None, []))
        if not src_token or not src_accs or not dst_accs:
            continue
        src_acc = src_accs[0]["account_number"]
        dst_acc = dst_accs[0]["account_number"]
        for _ in range(5):
            amount = round(random.uniform(50, 245), 2)
            result = transfer_internal(
                client, BANK_CONFIGS[src_bank]["url"], src_token,
                src_acc, dst_acc, amount,
                description="Micropago ráfaga",
            )
            if result:
                done += 1
                counter[0] += 1
                print(f"  [{counter[0]:03d}] {src_bank} burst ₡{amount:.0f} [RÁFAGA]")
    return done


def block_star_concentration(client, sessions, counter):
    """20 tx de múltiples cuentas → un hub — activa STAR_CONCENTRATION."""
    print("\n[Bloque 4] 20 concentraciones tipo estrella")
    done = 0
    star_configs = [
        # (banco_hub, email_hub, banco_spokes, emails_spokes)
        (
            "BKA", "demo@bancoa.com",
            "BKA", ["carlos@bancoa.com", "luisa@bancoa.com", "pablo@bancoa.com", "sofia@bancoa.com"],
        ),
        (
            "BKB", "demo@bancob.com",
            "BKB", ["juan@bancob.com", "maria@bancob.com", "pedro@bancob.com", "laura@bancob.com"],
        ),
        (
            "BKC", "demo@bancoc.com",
            "BKC", ["roberto@bancoc.com", "elena@bancoc.com", "miguel@bancoc.com", "valeria@bancoc.com"],
        ),
    ]
    for hub_bank, hub_email, spoke_bank, spoke_emails in star_configs:
        _, hub_accs = sessions[hub_bank].get(hub_email, (None, []))
        if not hub_accs:
            continue
        hub_acc = hub_accs[0]["account_number"]
        for spoke_email in spoke_emails:
            spoke_token, spoke_accs = sessions[spoke_bank].get(spoke_email, (None, []))
            if not spoke_token or not spoke_accs:
                continue
            spoke_acc = spoke_accs[0]["account_number"]
            amount = round(random.uniform(800, 2500), 2)
            result = transfer_internal(
                client, BANK_CONFIGS[spoke_bank]["url"], spoke_token,
                spoke_acc, hub_acc, amount,
                description="Concentración hacia hub central",
            )
            if result:
                done += 1
                counter[0] += 1
                print(f"  [{counter[0]:03d}] {spoke_bank} spoke→hub ₡{amount:,.0f} [ESTRELLA]")
        time.sleep(0.05)
    return done


def block_rapid_exit(client, sessions, counter):
    """20 tx: ingreso seguido de salida rápida — activa RAPID_IN_OUT."""
    print("\n[Bloque 5] 20 entradas y salidas rápidas")
    done = 0
    exit_configs = [
        ("BKA", "demo@bancoa.com", "carlos@bancoa.com", "ana@bancoa.com"),
        ("BKB", "demo@bancob.com", "juan@bancob.com", "maria@bancob.com"),
        ("BKC", "demo@bancoc.com", "roberto@bancoc.com", "elena@bancoc.com"),
        ("BKA", "luisa@bancoa.com", "demo@bancoa.com", "sofia@bancoa.com"),
    ]
    for bank, src_email, hub_email, dst_email in exit_configs:
        src_token, src_accs = sessions[bank].get(src_email, (None, []))
        hub_token, hub_accs = sessions[bank].get(hub_email, (None, []))
        _, dst_accs = sessions[bank].get(dst_email, (None, []))
        if not all([src_token, src_accs, hub_token, hub_accs, dst_accs]):
            continue
        src_acc = src_accs[0]["account_number"]
        hub_acc = hub_accs[0]["account_number"]
        dst_acc = dst_accs[0]["account_number"]
        in_amount = round(random.uniform(3000, 7000), 2)
        out_amount = round(in_amount * random.uniform(0.72, 0.92), 2)
        # entrada al hub
        r1 = transfer_internal(
            client, BANK_CONFIGS[bank]["url"], src_token,
            src_acc, hub_acc, in_amount,
            description="Ingreso previo a salida rápida",
        )
        # salida desde hub
        r2 = transfer_internal(
            client, BANK_CONFIGS[bank]["url"], hub_token,
            hub_acc, dst_acc, out_amount,
            description="Salida rápida de fondos",
        )
        for r in [r1, r2]:
            if r:
                done += 1
                counter[0] += 1
        if r1 and r2:
            print(f"  [{counter[0]:03d}] {bank} in ₡{in_amount:,.0f} → out ₡{out_amount:,.0f} [RAPID EXIT]")
    return done


def block_interbank_chain(client, sessions, counter):
    """10 cadenas interbancarias A→B→C y C→A — activa RAPID_CHAIN."""
    print("\n[Bloque 6] 10 cadenas interbancarias (A↔B↔C)")
    done = 0
    chains = [
        # (src_bank, src_email, mid_bank, mid_email, dst_bank, dst_email)
        ("BKA", "demo@bancoa.com", "BKB", "demo@bancob.com", "BKC", "demo@bancoc.com"),
        ("BKC", "demo@bancoc.com", "BKA", "demo@bancoa.com", "BKB", "demo@bancob.com"),
        ("BKB", "demo@bancob.com", "BKC", "demo@bancoc.com", "BKA", "demo@bancoa.com"),
    ]
    for _ in range(3):
        for src_bank, src_email, mid_bank, mid_email, dst_bank, dst_email in chains:
            src_token, src_accs = sessions[src_bank].get(src_email, (None, []))
            mid_token, mid_accs = sessions[mid_bank].get(mid_email, (None, []))
            _, dst_accs = sessions[dst_bank].get(dst_email, (None, []))
            if not all([src_token, src_accs, mid_token, mid_accs, dst_accs]):
                continue
            src_acc = src_accs[0]["account_number"]
            mid_acc = mid_accs[0]["account_number"]
            dst_acc = dst_accs[0]["account_number"]
            hop1 = round(random.uniform(5000, 12000), 2)
            hop2 = round(hop1 * random.uniform(0.71, 0.88), 2)
            r1 = transfer_interbank(
                client, BANK_CONFIGS[src_bank]["url"], src_token,
                src_acc, mid_acc, hop1,
                description=f"Cadena interbancaria paso 1 ({src_bank}→{mid_bank})",
            )
            r2 = transfer_interbank(
                client, BANK_CONFIGS[mid_bank]["url"], mid_token,
                mid_acc, dst_acc, hop2,
                description=f"Cadena interbancaria paso 2 ({mid_bank}→{dst_bank})",
            )
            for r in [r1, r2]:
                if r:
                    done += 1
                    counter[0] += 1
            if r1 and r2:
                print(f"  [{counter[0]:03d}] cadena {src_bank}→{mid_bank}→{dst_bank} ₡{hop1:,.0f}→₡{hop2:,.0f} [CHAIN]")
    return done


def block_repeated_destination(client, sessions, counter):
    """20 envíos al mismo destino en 24h — activa REPEATED_DESTINATION."""
    print("\n[Bloque 7] 20 envíos repetidos al mismo destino")
    done = 0
    repeat_configs = [
        ("BKA", "demo@bancoa.com", "BKB", "demo@bancob.com"),
        ("BKB", "demo@bancob.com", "BKC", "demo@bancoc.com"),
        ("BKC", "demo@bancoc.com", "BKA", "demo@bancoa.com"),
        ("BKA", "carlos@bancoa.com", "BKB", "juan@bancob.com"),
    ]
    for src_bank, src_email, dst_bank, dst_email in repeat_configs:
        src_token, src_accs = sessions[src_bank].get(src_email, (None, []))
        _, dst_accs = sessions[dst_bank].get(dst_email, (None, []))
        if not src_token or not src_accs or not dst_accs:
            continue
        src_acc = src_accs[0]["account_number"]
        dst_acc = dst_accs[0]["account_number"]
        for _ in range(5):
            amount = round(random.uniform(300, 1200), 2)
            result = transfer_interbank(
                client, BANK_CONFIGS[src_bank]["url"], src_token,
                src_acc, dst_acc, amount,
                description="Pago recurrente mismo destino",
            )
            if result:
                done += 1
                counter[0] += 1
                print(f"  [{counter[0]:03d}] {src_bank}→{dst_bank} repet ₡{amount:.0f} [REPETIDO]")
    return done


# ── Analytics sync ────────────────────────────────────────────────────────────

def register_and_fetch(client: httpx.Client):
    """Registra BKA y BKB en analytics y ejecuta fetch (BKC no se registra)."""
    headers = {"X-Analytics-Key": ANALYTICS_API_KEY}
    print("\n[Analytics] Registrando bancos BKA y BKB (BKC no registrado)…")
    for bank_name, bank_code, api_url in [
        ("Banco A", "BKA", BANK_A_URL),
        ("Banco B", "BKB", BANK_B_URL),
    ]:
        try:
            request_json(
                client, "POST", f"{ANALYTICS_URL}/banks/register",
                headers=headers,
                json={
                    "bank_name": bank_name,
                    "bank_code": bank_code,
                    "api_url": api_url,
                    "status": "active",
                },
            )
        except httpx.HTTPStatusError as exc:
            if exc.response.status_code == 409:
                pass  # ya registrado
            else:
                raise

    print("[Analytics] Ejecutando /transactions/fetch…")
    summary = request_json(
        client, "GET", f"{ANALYTICS_URL}/transactions/fetch",
        headers=headers,
    )
    return summary


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    random.seed(42)
    print("=" * 60)
    print("FlowLens — seed de 130 transacciones")
    print("=" * 60)

    with httpx.Client(timeout=15.0) as client:
        print("\nCargando sesiones…")
        sessions = load_sessions(client)

        counter = [0]  # lista para mutabilidad dentro de funciones anidadas

        block_internal_regular(client, sessions, counter)
        block_high_amount(client, sessions, counter)
        block_burst_small(client, sessions, counter)
        block_star_concentration(client, sessions, counter)
        block_rapid_exit(client, sessions, counter)
        block_interbank_chain(client, sessions, counter)
        block_repeated_destination(client, sessions, counter)

        total = counter[0]
        print(f"\n{'='*60}")
        print(f"Transacciones completadas: {total}/130")
        print(f"{'='*60}")

        try:
            summary = register_and_fetch(client)
            print("\n[Analytics] Resumen de alertas:")
            print(summary)
        except Exception as exc:
            print(f"\n[Analytics] No se pudo sincronizar: {exc}")
            print("  Ejecuta manualmente: GET /transactions/fetch con X-Analytics-Key")


if __name__ == "__main__":
    main()
