# Banco 1

Banco 1 es un simulador bancario full stack para demo local. Permite registrar usuarios, abrir cuentas, transferir dinero, consultar historial, generar alertas básicas de riesgo y visualizar una red de transacciones sospechosas.

## Stack

- Backend: FastAPI, SQLAlchemy ORM, SQLite, Pydantic, passlib, JWT
- Frontend: React + Vite
- Base de datos: SQLite con creación automática de tablas

## Funcionalidad implementada

- Registro, login y perfil autenticado con JWT
- Creación y consulta de cuentas bancarias simuladas
- Transferencias con validaciones de negocio
- Historial de transacciones del usuario y vista global de demo
- Motor básico de riesgo por reglas
- Alertas persistidas en `risk_alerts`
- Grafo simple de red de transacciones
- Seed reproducible con datos normales y sospechosos

## Estructura

- `backend/app`: API principal, modelos, rutas, auth y lógica de riesgo
- `backend/bank.db`: SQLite usada por la API
- `frontend`: app React + Vite
- `seed.py`: resetea y puebla la base de datos
- `requirements.txt`: dependencias Python

## Backend

1. Crear o activar tu entorno virtual.
2. Instalar dependencias:

```bash
pip install -r requirements.txt
```

3. Levantar la API:

```bash
uvicorn app.main:app --reload
```

La API queda disponible en `http://127.0.0.1:8000` y la documentación en `http://127.0.0.1:8000/docs`.

## Frontend

1. Instalar dependencias:

```bash
cd frontend
npm install
```

2. Levantar Vite:

```bash
npm run dev
```

El frontend queda en `http://127.0.0.1:5173` y por defecto consume la API en `http://127.0.0.1:8000`.

Si quieres apuntar a otra URL del backend:

```bash
VITE_API_URL=http://127.0.0.1:8001 npm run dev
```

## Seed de datos

El seed recrea `backend/bank.db` desde cero, crea usuarios, cuentas, transacciones normales y patrones sospechosos.

```bash
python seed.py
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

## Reglas de riesgo implementadas

- monto alto sobre umbral fijo
- varias transacciones pequeñas en poco tiempo
- entrada y salida rápida de fondos
- transferencias repetidas al mismo destino
- montos cercanos al umbral sospechoso

## Verificación local realizada

- `python seed.py` ejecutado con éxito
- `uvicorn app.main:app --reload` levantado sin errores de importación
- registro y login probados contra la API
- creación de cuenta probada
- transferencia probada con actualización de saldos
- alertas y resumen de riesgo consultados
- grafo de red consultado
- `npm run build` ejecutado con éxito en el frontend

## Notas

- No hay migraciones complejas: las tablas se crean automáticamente al iniciar la API.
- El modelo usa SQLite y está pensado para MVP/demo local, no para producción bancaria real.
