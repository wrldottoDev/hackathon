# FlowLens

FlowLens es una plataforma distribuida de simulación bancaria y análisis transaccional orientada a demo técnica.

El sistema simula un ecosistema financiero con tres bancos independientes, comunicación interbancaria real y un motor externo de analytics con visualización de redes transaccionales.

## Disclaimer

FlowLens **no es un banco real**.

- No mueve dinero real.
- No se conecta con entidades financieras reales.
- Usa datos sintéticos generados exclusivamente para demostración.
- Analytics está completamente separado del core bancario.
- No almacena ni procesa datos personales reales.

---

## Arquitectura

```
FlowLens/
├── banco_a/          → Banco A (BKA) · backend + frontend · puerto 8001 / 5173
├── banco_b/          → Banco B (BKB) · backend + frontend · puerto 8002 / 5174
├── banco_c/          → Banco C (BKC) · backend + frontend · puerto 8004 / 5176
├── analytics/        → Analytics externo · backend + frontend · puerto 8003 / 5175
├── docs/             → Documentación del proyecto
├── seed_flowlens.py  → Seed interbancario demo (A↔B + analytics)
└── requirements.txt  → Dependencias globales (venv compartido)
```

Cada banco es un servicio independiente con su propia base de datos SQLite. Analytics observa los bancos registrados desde fuera.

---

## Stack

| Capa | Tecnología |
|------|-----------|
| Backend | FastAPI, Uvicorn, SQLAlchemy ORM |
| Autenticación | JWT (python-jose), bcrypt_sha256 (passlib) |
| Base de datos | SQLite (por servicio) |
| Comunicación | httpx (HTTP síncrono entre servicios) |
| Frontend | React 18, React Router 6, Vite |
| Visualización de red | ReactFlow (@xyflow/react) |

---

## Servicios

### Banco A, Banco B y Banco C

Cada banco expone los mismos endpoints:

```
POST  /auth/register              → Registro de usuario
POST  /auth/login                 → Login, devuelve JWT
GET   /auth/me                    → Usuario autenticado actual

POST  /accounts                   → Crear cuenta con saldo inicial
GET   /accounts/my                → Listar mis cuentas
GET   /accounts/{id}              → Detalle de cuenta (solo propietario)

POST  /transactions/internal      → Transferencia interna (mismo banco)
POST  /transactions/interbank     → Transferencia interbancaria (otro banco)
GET   /transactions/my            → Historial del usuario
GET   /transactions/export        → Export para analytics (token de servicio)

POST  /interbank/receive          → Recibir transferencia desde otro banco
POST  /interbank/reverse          → Revertir transferencia interbancaria

GET   /health                     → Health check con identidad del banco
```

**Reglas de negocio implementadas:**

- Hash de contraseña con `bcrypt_sha256`; compatibilidad de lectura para hashes `bcrypt` antiguos
- Número de cuenta único con prefijo de banco (`BKA-XXXXXXXXXX`)
- Saldo suficiente obligatorio; monto mayor que cero; cuenta origen ≠ destino
- Trazabilidad interbancaria con `external_reference` único por operación
- Flujo de 2 fases: acreditar en destino → debitar en origen
- Compensación automática si el debit falla después del credit

### Analytics

```
POST  /banks/register             → Registrar un banco para observación
GET   /banks                      → Listar bancos registrados

GET   /transactions/fetch         → Capturar transacciones de los bancos registrados

GET   /alerts                     → Listar alertas con filtros
GET   /alerts/summary             → Resumen de alertas por nivel y patrón

GET   /network/graph              → Grafo dirigido de relaciones entre cuentas

GET   /accounts/{account}/follow-up → Análisis profundo de una cuenta

GET   /health
```

**Todos los endpoints de analytics requieren header:**
```
X-Analytics-Key: flowlens-analytics-key-dev
```

**Reglas de riesgo (heurísticas explicables):**

| Patrón | Score | Condición |
|--------|-------|-----------|
| `high_amount` | 80 | Monto ≥ 10 000 |
| `rapid_in_out` | 75 | Salida ≥ 70% del ingreso reciente en 2h |
| `rapid_chain` | 85 | Cadena A→B→C en menos de 1h |
| `burst_small_transactions` | 55 | 5+ txs ≤ 250 en 1h desde la misma cuenta |
| `star_concentration` | 65 | 4+ fuentes distintas enviando al mismo destino en 24h |
| `repeated_destination` | 40 | 3+ transferencias al mismo destino en 24h |

Clasificación de niveles: `0–30` → low · `31–70` → medium · `71–100` → high

---

## Instalación

Puedes usar un único entorno virtual compartido desde la raíz del proyecto o uno por servicio.

### Opción A — venv compartido (recomendado para demo)

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### Opción B — venv por servicio

```bash
cd banco_a && python3 -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt
cd banco_b && python3 -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt
cd banco_c && python3 -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt
cd analytics && python3 -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt
```

---

## Ejecución

Abre un terminal por servicio:

```bash
# Terminal 1
python banco_a/run.py          # Puerto 8001

# Terminal 2
python banco_b/run.py          # Puerto 8002

# Terminal 3
python banco_c/run.py          # Puerto 8004

# Terminal 4
python analytics/run.py        # Puerto 8003
```

### Frontends

```bash
# Banco A
cd banco_a/frontend && npm install && npm run dev    # http://127.0.0.1:5173

# Banco B
cd banco_b/frontend && npm install && npm run dev    # http://127.0.0.1:5174

# Analytics
cd analytics/frontend && npm install && npm run dev  # http://127.0.0.1:5175

# Banco C
cd banco_c/frontend && npm install && npm run dev    # http://127.0.0.1:5176
```

---

## Seeds

### 1. Datos locales en cada banco

Con el entorno activado, corre cada seed desde la raíz del proyecto:

```bash
python banco_a/seed.py
python banco_b/seed.py
python banco_c/seed.py
```

Usuarios demo creados:

| Banco | Email | Password |
|-------|-------|----------|
| Banco A | `demo@bancoa.com` | `DemoPass123` |
| Banco B | `demo@bancob.com` | `DemoPass123` |
| Banco C | `demo@bancoc.com` | `DemoPass123` |

### 2. Transferencias interbancarias + analytics

Con los 4 servicios levantados:

```bash
python seed_flowlens.py
```

Este script:

- Autentica los usuarios demo de Banco A y Banco B
- Crea transferencias interbancarias A↔B
- Registra Banco A y Banco B en analytics
- Ejecuta la primera captura de transacciones

---

## Flujo interbancario

```
Usuario → POST /transactions/interbank (banco origen)
         ↓ valida usuario, cuenta, saldo, banco destino
         ↓ genera external_reference UUID
Banco origen → POST /interbank/receive (banco destino)
               ↓ destino acredita + registra interbank_incoming
Banco origen  ← 200 OK
         ↓ origen debita + registra interbank_outgoing
         ↓ si falla debit → POST /interbank/reverse (compensación)
```

---

## Flujo de analytics

```
POST /banks/register         → registrar bancos observados (demo: A y B)
GET  /transactions/fetch     → captura incremental por banco registrado
GET  /alerts                 → ver alertas generadas
GET  /network/graph          → grafo de cuentas y relaciones
GET  /accounts/{id}/follow-up → análisis profundo de cuenta
```

---

## Variables de entorno

Valores por defecto (funcionan sin configuración adicional):

```bash
FLOWLENS_SERVICE_TOKEN=flowlens-service-token-dev
FLOWLENS_ANALYTICS_API_KEY=flowlens-analytics-key-dev
```

Opcionales para entornos personalizados:

```bash
FLOWLENS_BANK_A_URL=http://127.0.0.1:8001
FLOWLENS_BANK_B_URL=http://127.0.0.1:8002
FLOWLENS_BANK_C_URL=http://127.0.0.1:8004
FLOWLENS_ANALYTICS_URL=http://127.0.0.1:8003
FLOWLENS_BANK_REGISTRY="BKA=http://127.0.0.1:8001,BKB=http://127.0.0.1:8002"
```

---

## Estado del proyecto

### Listo y funcional

- Banco A, Banco B y Banco C: backends completos con auth, cuentas y transferencias
- Transferencias internas e interbancarias con trazabilidad completa
- Compensación automática en fallo de operaciones interbancarias
- Export transaccional para analytics con paginación y filtro por fecha
- Analytics con motor de riesgo heurístico (6 patrones)
- Grafo de red transaccional con visualización circular por banco (ReactFlow)
- Follow-up profundo de cuenta: historial, contrapartes, métricas, alertas
- Frontends funcionales para los 4 servicios
- Seeds completos con patrones de riesgo para demo

### Limitaciones conocidas (adecuadas para demo)

- SQLite y tokens de servicio simples, no aptos para producción
- Reglas de riesgo heurísticas, sin ML
- Sin orquestación distribuida ni colas de eventos
- El flujo interbancario es HTTP síncrono (no transaccional distribuido)
