"""
NEXO Risk — Generador de Datos Sintéticos
==========================================
Produce dos archivos CSV listos para cargar al backend:
  - accounts.csv
  - transactions.csv

Tipologías implementadas (basadas en FATF/FinCEN):
  T1 - Smurfing         : depósitos pequeños fraccionados hacia una cuenta hub
  T2 - Layering         : fondos que pasan por cadena de cuentas puente
  T3 - Nómina fantasma  : pagos regulares a cuentas inactivas ("salarios")
  T4 - Cash-intensive   : alto ratio de transacciones en efectivo
  T5 - Nocturna-cruzada : red activa fuera de horario laboral

Cuentas normales generan tráfico aleatorio sin patrones.
"""

import random
import csv
import uuid
from datetime import datetime, timedelta
from faker import Faker

fake = Faker("es_MX")
random.seed(99)

# ── Contadores globales ────────────────────────────────────────────────────────
txn_counter  = 1
acc_counter  = 1
accounts_db  = {}      # code → dict
transactions = []


# ── Helpers ────────────────────────────────────────────────────────────────────

def new_acc_code(prefix="ACC") -> str:
    global acc_counter
    code = f"{prefix}-{acc_counter:04d}"
    acc_counter += 1
    return code


def new_txn_ref() -> str:
    global txn_counter
    ref = f"TXN-{txn_counter:06d}"
    txn_counter += 1
    return ref


def rand_ts(days_back=30, night=False, early_morning=False) -> datetime:
    base = datetime.utcnow() - timedelta(days=random.randint(0, days_back))
    if night:
        base = base.replace(hour=random.choice([22, 23, 0, 1, 2, 3, 4, 5]))
    elif early_morning:
        base = base.replace(hour=random.randint(6, 9))
    else:
        base = base.replace(hour=random.randint(9, 21))
    return base.replace(minute=random.randint(0, 59), second=0, microsecond=0)


def make_account(prefix="ACC", country=None, label="normal") -> dict:
    code    = new_acc_code(prefix)
    country = country or random.choice(["CR", "CR", "CR", "MX", "PA", "CO", "US"])
    acc = {
        "code":    code,
        "name":    fake.name(),
        "country": country,
        "label":   label,     # normal / smurfing / layering / nomina / cash / nocturna
    }
    accounts_db[code] = acc
    return acc


def add_txn(sender_code, receiver_code, amount, timestamp, channel="transfer"):
    transactions.append({
        "ref":           new_txn_ref(),
        "sender_code":   sender_code,
        "receiver_code": receiver_code,
        "amount":        round(amount, 2),
        "currency":      "USD",
        "timestamp":     timestamp.strftime("%Y-%m-%dT%H:%M:%S"),
        "channel":       channel,
    })


# ── Cuentas normales ───────────────────────────────────────────────────────────

def gen_normal(n=25):
    accs = [make_account("ACC", label="normal") for _ in range(n)]
    for acc in accs:
        for _ in range(random.randint(2, 6)):
            other = random.choice([a for a in accs if a["code"] != acc["code"]])
            amount = random.uniform(200, 8000)
            ts     = rand_ts(30)
            ch     = random.choice(["transfer", "mobile", "transfer", "transfer"])
            add_txn(acc["code"], other["code"], amount, ts, ch)
    return accs


# ── T1 – Smurfing (fractured deposits → hub) ──────────────────────────────────

def gen_smurfing(normal_accs, n_hubs=3):
    """
    Varios 'pitufos' depositan montos pequeños (<$490) hacia
    una cuenta hub en ventana corta. Hub luego dispersa.
    Los depósitos ocurren en las últimas 8h para garantizar
    que caen dentro de la ventana de 24h del motor S1.
    """
    hubs = [make_account("HUB", country="CR", label="smurfing") for _ in range(n_hubs)]

    for hub in hubs:
        n_pitufos = random.randint(6, 10)
        pitufos   = random.sample(normal_accs, min(n_pitufos, len(normal_accs)))
        # Anclar al momento actual y retroceder máximo 6h para mantenerse en ventana
        anchor = datetime.utcnow() - timedelta(hours=random.randint(1, 6))

        for i, p in enumerate(pitufos):
            ts = anchor + timedelta(minutes=random.randint(5, 30) * i)
            add_txn(p["code"], hub["code"], random.uniform(80, 490), ts, "cash")

        # Hub dispersa hacia otras cuentas poco después
        targets = random.sample(normal_accs, min(4, len(normal_accs)))
        for t in targets:
            ts_out = anchor + timedelta(hours=random.randint(8, 20))
            add_txn(hub["code"], t["code"], random.uniform(300, 1400), ts_out, "transfer")

    return hubs


# ── T2 – Layering (cadena de cuentas puente) ──────────────────────────────────

def gen_layering(normal_accs, n_chains=3):
    """
    Dinero entra de múltiples fuentes y pasa por cuentas puente
    hacia el destino final. Cada cuenta puente recibe de varias
    fuentes (activa S2) y dispersa rápido (activa S3).
    """
    chain_accs = []

    for _ in range(n_chains):
        depth  = random.randint(3, 4)
        chain  = [make_account("LAY", label="layering") for _ in range(depth)]
        chain_accs.extend(chain)

        # Múltiples fuentes hacia el primer nodo de la cadena (activa S2)
        n_sources = random.randint(5, 8)
        sources   = random.sample(normal_accs, min(n_sources, len(normal_accs)))
        base_ts   = datetime.utcnow() - timedelta(hours=random.randint(20, 120))

        for s in sources:
            offset = timedelta(hours=random.randint(0, 12))
            add_txn(s["code"], chain[0]["code"], random.uniform(400, 1500), base_ts + offset, "transfer")

        # Propagación rápida a través de la cadena (activa S3)
        ts = base_ts + timedelta(hours=random.randint(6, 18))
        amount = random.uniform(3000, 9000)
        for i in range(len(chain) - 1):
            amount *= random.uniform(0.85, 0.97)
            ts = ts + timedelta(hours=random.randint(1, 8))
            add_txn(chain[i]["code"], chain[i+1]["code"], amount, ts, "transfer")

        # Salida a destino "normal"
        dest = random.choice(normal_accs)
        add_txn(chain[-1]["code"], dest["code"], amount * 0.9,
                ts + timedelta(hours=random.randint(1, 6)), "transfer")

    return chain_accs


# ── T3 – Nómina fantasma ───────────────────────────────────────────────────────

def gen_nomina_fantasma(n_empleadores=2):
    """
    Una cuenta 'empleadora' envía montos fijos cada semana
    a varias cuentas receptoras que no tienen otro movimiento.
    """
    empleadores = [make_account("EMP", label="nomina") for _ in range(n_empleadores)]
    fantasmas   = []

    for emp in empleadores:
        n_empleados = random.randint(5, 8)
        empleados   = [make_account("FAN", label="nomina") for _ in range(n_empleados)]
        fantasmas.extend(empleados)
        salario     = random.uniform(400, 900)

        # 4 semanas de pagos
        for week in range(4):
            ts = rand_ts(0, early_morning=True) - timedelta(weeks=week)
            for emp_acc in empleados:
                variation = salario * random.uniform(0.98, 1.02)
                add_txn(emp["code"], emp_acc["code"], variation, ts, "transfer")

    return empleadores, fantasmas


# ── T4 – Cash-intensive ───────────────────────────────────────────────────────

def gen_cash_intensive(normal_accs, n=4):
    """
    Cuentas que reciben muchas transacciones en efectivo
    (canal 'cash') en proporciones anómalas.
    """
    cash_accs = [make_account("CSH", label="cash") for _ in range(n)]

    for acc in cash_accs:
        sources = random.sample(normal_accs, min(8, len(normal_accs)))
        for s in sources:
            for _ in range(random.randint(2, 4)):
                ts = rand_ts(20)
                add_txn(s["code"], acc["code"], random.uniform(100, 800), ts, "cash")

        # Algunas salidas en transfer para mezclar
        targets = random.sample(normal_accs, 3)
        for t in targets:
            add_txn(acc["code"], t["code"], random.uniform(500, 2000), rand_ts(5), "transfer")

    return cash_accs


# ── T5 – Red nocturna cruzada ─────────────────────────────────────────────────

def gen_nocturna(n=4):
    """
    Cluster de cuentas que operan principalmente de noche
    y se transfieren entre sí de forma repetida.
    """
    nocturnas = [make_account("NOC", label="nocturna") for _ in range(n)]

    for _ in range(40):
        a, b = random.sample(nocturnas, 2)
        ts   = rand_ts(20, night=True)
        add_txn(a["code"], b["code"], random.uniform(150, 900), ts, "mobile")

    # Algunas conexiones con cuentas normales (para activar S5)
    return nocturnas


# ── Main ───────────────────────────────────────────────────────────────────────

def generate(output_dir="."):
    print("🏗️  Generando datos sintéticos NEXO Risk...\n")

    # 1. Base normal
    normals = gen_normal(25)
    print(f"  ✅ {len(normals)} cuentas normales")

    # 2. Tipologías de riesgo
    hubs      = gen_smurfing(normals, n_hubs=3)
    print(f"  ✅ {len(hubs)} hubs de smurfing (T1)")

    layers    = gen_layering(normals, n_chains=3)
    print(f"  ✅ {len(layers)} cuentas de layering (T2)")

    emps, fans = gen_nomina_fantasma(n_empleadores=2)
    print(f"  ✅ {len(emps)} empleadoras + {len(fans)} fantasmas (T3)")

    cash_accs = gen_cash_intensive(normals, n=3)
    print(f"  ✅ {len(cash_accs)} cuentas cash-intensive (T4)")

    noct      = gen_nocturna(n=4)
    print(f"  ✅ {len(noct)} cuentas nocturnas (T5)")

    # ── Escribir accounts.csv ──────────────────────────────────────────────────
    acc_path = f"{output_dir}/accounts.csv"
    with open(acc_path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["code", "name", "country", "label"])
        w.writeheader()
        for acc in accounts_db.values():
            w.writerow(acc)

    # ── Escribir transactions.csv ──────────────────────────────────────────────
    txn_path = f"{output_dir}/transactions.csv"
    with open(txn_path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["ref","sender_code","receiver_code","amount","currency","timestamp","channel"])
        w.writeheader()
        w.writerows(transactions)

    print(f"\n📊 Resumen:")
    print(f"   Cuentas totales      : {len(accounts_db)}")
    print(f"   Transacciones totales: {len(transactions)}")
    print(f"\n📁 Archivos generados:")
    print(f"   {acc_path}")
    print(f"   {txn_path}")

    return acc_path, txn_path


if __name__ == "__main__":
    generate(output_dir="data")
