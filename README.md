# FlowLens

FlowLens es una plataforma demostrativa de simulación bancaria y análisis transaccional. El proyecto queda separado en tres servicios:

- `banco_a`: backend bancario con usuarios, cuentas, transferencias internas e interbancarias.
- `banco_b`: segundo banco independiente con la misma lógica base y base de datos separada.
- `analytics`: servicio externo que observa transacciones, consolida datos, genera alertas y expone un grafo de relaciones.

## Disclaimer

FlowLens no es un banco real.

- No mueve dinero real.
- No se conecta con entidades financieras reales.
- Usa datos sintéticos generados para demo.
- Analytics está separado del core bancario.

## Arquitectura

```text
.
├── banco_a/
│   ├── app/
│   ├── frontend/
│   ├── requirements.txt
│   ├── run.py
│   └── seed.py
├── banco_b/
│   ├── app/
│   ├── requirements.txt
│   ├── run.py
│   └── seed.py
├── analytics/
│   ├── app/
│   ├── requirements.txt
│   └── run.py
├── docs/
└── seed_flowlens.py
```

## Qué Hace Cada Servicio

### Banco A y Banco B

Cada banco expone:

- `POST /auth/register`
- `POST /auth/login`
- `GET /auth/me`
- `POST /accounts`
- `GET /accounts/my`
- `GET /accounts/{account_id}`
- `POST /transactions/internal`
- `POST /transactions/interbank`
- `GET /transactions/my`
- `GET /transactions/export` protegido por token de servicio
- `POST /interbank/receive` protegido por token de servicio
- `POST /interbank/reverse` protegido por token de servicio
- `GET /health`

Reglas implementadas:

- hash de contraseña con `bcrypt_sha256` y compatibilidad de lectura para hashes `bcrypt` viejos;
- validación de passwords largas con error `422` claro;
- número de cuenta único con prefijo por banco;
- saldo suficiente obligatorio;
- no monto menor o igual a cero;
- no transferir a la misma cuenta;
- registro de operaciones internas e interbancarias;
- trazabilidad con `external_reference` y manejo de reversa compensatoria.

### Analytics

Analytics expone:

- `POST /banks/register`
- `GET /banks`
- `GET /transactions/fetch`
- `GET /alerts`
- `GET /alerts/summary`
- `GET /network/graph`
- `GET /accounts/{account_number}/follow-up`
- `GET /health`

Capacidades implementadas:

- registro de bancos observables;
- ingesta de transacciones desde Banco A y Banco B;
- almacenamiento local de transacciones observadas;
- alertas por reglas explicables;
- resumen de alertas;
- grafo agregando nodos y aristas por cuenta;
- seguimiento profundo por cuenta.

## Reglas De Riesgo En Analytics

Se detectan estas señales:

- monto alto sobre umbral fijo;
- muchas transacciones pequeñas en poco tiempo;
- entrada y salida rápida de fondos;
- repetición al mismo destino;
- concentración tipo estrella;
- cadenas rápidas `A -> B -> C`.

Clasificación:

- `0-30`: `low`
- `31-70`: `medium`
- `71-100`: `high`

## Variables Útiles

Valores por defecto:

```bash
export FLOWLENS_SERVICE_TOKEN=flowlens-service-token-dev
export FLOWLENS_ANALYTICS_API_KEY=flowlens-analytics-key-dev
```

Opcionales:

```bash
export FLOWLENS_BANK_REGISTRY="BKA=http://127.0.0.1:8001,BKB=http://127.0.0.1:8002"
export FLOWLENS_BANK_A_URL="http://127.0.0.1:8001"
export FLOWLENS_BANK_B_URL="http://127.0.0.1:8002"
export FLOWLENS_ANALYTICS_URL="http://127.0.0.1:8003"
```

## Instalación

Puedes usar un entorno virtual por servicio o uno compartido.

### Banco A

```bash
cd banco_a
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### Banco B

```bash
cd banco_b
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### Analytics

```bash
cd analytics
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Seeds

### 1. Cargar datos locales en cada banco

```bash
python banco_a/seed.py
python banco_b/seed.py
```

Usuarios demo creados:

- Banco A: `demo@bancoa.com`
- Banco B: `demo@bancob.com`
- Password: `DemoPass123`

### 2. Levantar servicios

```bash
cd banco_a && uvicorn app.main:app --reload --port 8001
cd banco_b && uvicorn app.main:app --reload --port 8002
cd analytics && uvicorn app.main:app --reload --port 8003
```

También puedes usar:

```bash
python banco_a/run.py
python banco_b/run.py
python analytics/run.py
```

### 3. Crear transferencias interbancarias y poblar analytics

Con los tres servicios arriba:

```bash
python seed_flowlens.py
```

Ese script:

- crea transferencias interbancarias reales entre Banco A y Banco B;
- registra ambos bancos en analytics;
- ejecuta `GET /transactions/fetch`.

## Flujo Interbancario

1. El usuario autenticado llama `POST /transactions/interbank` en el banco origen.
2. El banco origen valida usuario, cuenta origen, monto, saldo y banco destino.
3. El banco origen llama `POST /interbank/receive` en el banco destino.
4. El banco destino acredita y registra `interbank_incoming`.
5. El banco origen debita y registra `interbank_outgoing`.
6. Si el origen falla después de acreditar en destino, intenta `POST /interbank/reverse`.

## Flujo De Analytics

1. Registrar bancos con `POST /banks/register`.
2. Ejecutar `GET /transactions/fetch`.
3. Consultar:
   - `GET /alerts`
   - `GET /alerts/summary`
   - `GET /network/graph`
   - `GET /accounts/{account_number}/follow-up`

Todos esos endpoints requieren header:

```bash
X-Analytics-Key: flowlens-analytics-key-dev
```

## Stack

- FastAPI
- SQLAlchemy
- SQLite
- Passlib + bcrypt
- JWT con `python-jose`
- httpx para integración entre servicios
- React/Vite en el frontend existente de `banco_a`

## Estado Actual

Listo:

- Banco A funcional
- Banco B funcional
- auth, cuentas y transferencias internas
- transferencias interbancarias con trazabilidad
- export transaccional para analytics
- analytics separado con alertas, resumen, grafo y follow-up
- scripts de seed

Limitaciones actuales:

- SQLite y tokens compartidos simples, adecuados para demo pero no para producción
- reglas de riesgo heurísticas, sin ML
- no hay orquestación distribuida fuerte ni cola de eventos
- el frontend existente solo está mantenido en `banco_a`
