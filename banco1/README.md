# Banco 1

El proyecto ahora soporta tres instancias bancarias separadas sobre la misma base de código:

- `Banco 1`
- `Banco 2`
- `Banco 3`

Y dos tipos de interfaz:

- `frontend`: portal bancario para clientes, enfocado en login, cuentas, transferencias e historial
- `analytics`: consola externa de análisis para alertas, monitoreo de riesgo y grafo transaccional

## Stack

- Backend: FastAPI, SQLAlchemy ORM, SQLite, Pydantic, passlib, JWT
- Frontend: React + Vite
- Base de datos: SQLite con creación automática de tablas

## Funcionalidad implementada

- Registro, login y perfil autenticado con JWT
- Creación y consulta de cuentas bancarias simuladas
- Transferencias con validaciones de negocio
- Historial de transacciones del usuario
- Motor básico de riesgo por reglas
- Alertas persistidas en `risk_alerts`
- Grafo simple de red de transacciones
- Seed reproducible con datos normales y sospechosos
- Consola externa conectada a `Banco 1`, `Banco 2` y `Banco 3`

## Estructura

- `backend/app`: API principal, modelos, rutas, auth y lógica de riesgo
- `backend/bank.db`: SQLite de `Banco 1`
- `backend/banco2.db`: SQLite de `Banco 2`
- `backend/banco3.db`: SQLite de `Banco 3`
- `frontend`: portal bancario del cliente
- `analytics`: consola externa de análisis multi-banco
- `seed.py`: resetea y puebla la base de datos
- `seed_banco2.py`: resetea y puebla `Banco 2`
- `seed_banco3.py`: resetea y puebla `Banco 3`
- `run.py`: levanta `Banco 1`
- `run_banco2.py`: levanta `Banco 2`
- `run_banco3.py`: levanta `Banco 3`
- `requirements.txt`: dependencias Python

## Backends

1. Crear o activar tu entorno virtual.
2. Instalar dependencias:

```bash
pip install -r requirements.txt
```

3. Levantar las APIs:

```bash
python run.py
python run_banco2.py
python run_banco3.py
```

Puertos:

- `Banco 1`: `http://127.0.0.1:8000`
- `Banco 2`: `http://127.0.0.1:8001`
- `Banco 3`: `http://127.0.0.1:8002`

## Portal bancario

1. Instalar dependencias:

```bash
cd frontend
npm install
```

2. Levantar el portal del banco que quieras:

```bash
npm run dev
npm run dev:banco2
npm run dev:banco3
```

Puertos:

- `Banco 1`: `http://127.0.0.1:5173`
- `Banco 2`: `http://127.0.0.1:5175`
- `Banco 3`: `http://127.0.0.1:5176`

## Consola de análisis

1. Instalar dependencias:

```bash
cd analytics
npm install
```

2. Levantar la consola:

```bash
npm run dev
```

La consola queda en `http://127.0.0.1:5174`.

Actualmente el selector ya incluye:

- `Banco 1`
- `Banco 2`
- `Banco 3`

Y puedes agregar más bancos editando `analytics/src/banks.js`.

## Seed de datos

Cada seed recrea su base correspondiente desde cero, crea usuarios, cuentas, transacciones normales y patrones sospechosos.

```bash
python seed.py
python seed_banco2.py
python seed_banco3.py
```

Salida esperada aproximada:

- 25 usuarios
- 25 cuentas
- 180+ transacciones
- alertas `low`, `medium` y `high`

### Credenciales demo

- Email: `demo@example.com`
- Password: `demo1234`

## Endpoints principales

### Auth

- `POST /auth/register`
- `POST /auth/login`
- `GET /auth/me`

### Users

- `GET /users`

### Accounts

- `POST /accounts`
- `GET /accounts`
- `GET /accounts/{account_id}`
- `GET /accounts/my`

### Transactions

- `POST /transactions`
- `GET /transactions`
- `GET /transactions/my`
- `GET /transactions/{transaction_id}`

### Risk / Analytics

- `GET /risk/alerts`
- `GET /risk/summary`
- `GET /network/graph`
- `GET /network/report`

## Reglas de riesgo implementadas

- monto alto sobre umbral fijo
- varias transacciones pequeñas en poco tiempo
- entrada y salida rápida de fondos
- transferencias repetidas al mismo destino
- montos cercanos al umbral sospechoso

## Verificación local realizada

- `python seed.py` ejecutado con éxito
- `python seed_banco2.py` ejecutado con éxito
- `python seed_banco3.py` ejecutado con éxito
- `python run_banco2.py` levantado y validado
- `python run_banco3.py` levantado y validado
- registro y login probados contra la API
- creación de cuenta probada
- transferencia probada con actualización de saldos
- alertas y resumen de riesgo consultados
- grafo de red consultado
- `npm run build` ejecutado con éxito en `frontend`
- `npm run build:banco2` ejecutado con éxito en `frontend`
- `npm run build:banco3` ejecutado con éxito en `frontend`
- `npm run build` ejecutado con éxito en `analytics`

## Notas

- No hay migraciones complejas: las tablas se crean automáticamente al iniciar la API.
- El modelo usa SQLite y está pensado para MVP/demo local, no para producción bancaria real.
