# NEXO Risk — Backend

> Plataforma de inteligencia financiera explicable para detectar patrones de riesgo asociados a redes de trata y crimen organizado.
> Hackathon **Rastrea la Red**

---

## Stack

| Capa        | Tecnología                     |
|-------------|--------------------------------|
| API         | FastAPI + Uvicorn              |
| Motor       | Python puro (reglas explicables)|
| BD          | SQLite (dev) / PostgreSQL (prod)|
| Datos test  | Faker + generador sintético    |

---

## Instalación rápida

```bash
# 1. Clonar / descomprimir
cd nexo-risk

# 2. Crear entorno virtual
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

# 3. Instalar dependencias
pip install -r requirements.txt

# 4. Levantar servidor
uvicorn app.main:app --reload --port 8000
```

Ir a **http://localhost:8000/docs** para ver Swagger UI completo.

---

## Primeros pasos (flujo de demo)

```bash
# 1. Poblar con datos sintéticos
curl -X POST http://localhost:8000/api/seed

# 2. Analizar todas las cuentas en batch
curl -X POST http://localhost:8000/api/analyze/batch

# 3. Ver casos de riesgo alto
curl "http://localhost:8000/api/cases?risk_level=escalate"

# 4. Ver detalle de un caso
curl http://localhost:8000/api/cases/{case_id}

# 5. Actualizar decisión del analista
curl -X PATCH http://localhost:8000/api/cases/{case_id} \
  -H "Content-Type: application/json" \
  -d '{"status": "escalated", "analyst_note": "Confirmado por oficial senior"}'

# 6. Ver grafo de relaciones de una cuenta
curl "http://localhost:8000/api/graph/{account_id}?depth=2"
```

---

## Señales del motor de scoring

| Código | Señal                      | Peso | Descripción                                              |
|--------|----------------------------|------|----------------------------------------------------------|
| S1     | Depósitos pequeños múltiples| 30  | >5 depósitos ≤$500 en ventana de 24h                    |
| S2     | Remitentes múltiples        | 25  | >4 remitentes distintos en 7 días                        |
| S3     | Dispersión rápida           | 20  | >70% de lo recibido sale en 48h                          |
| S4     | Actividad nocturna          | 15  | >35% de transacciones entre 22:00 y 06:00                |
| S5     | Reincidencia relacional     | 10  | ≥3 cuentas relacionadas aparecen en otros casos activos  |

**Niveles de riesgo:**

| Score   | Nivel    | Recomendación                                      |
|---------|----------|----------------------------------------------------|
| 0–24    | low      | Sin acción requerida                               |
| 25–49   | medium   | Monitorear 7 días                                  |
| 50–74   | high     | Revisar en 24h                                     |
| 75–100  | escalate | Escalar a oficial de cumplimiento senior           |

---

## Endpoints principales

```
POST /api/seed                          Datos sintéticos de prueba
POST /api/analyze/{account_id}          Analiza una cuenta
POST /api/analyze/batch                 Analiza todas las cuentas
GET  /api/cases                         Lista casos (filtros: risk_level, status)
GET  /api/cases/{id}                    Detalle de caso
PATCH /api/cases/{id}                   Actualizar decisión del analista
GET  /api/accounts                      Lista cuentas
GET  /api/accounts/{id}/transactions    Transacciones de una cuenta
GET  /api/graph/{account_id}            Grafo de relaciones
GET  /api/dashboard                     Métricas del dashboard
POST /api/upload/transactions           Cargar CSV de transacciones
```

---

## Cargar CSV propio

El archivo debe tener estas columnas:

```
sender_code, receiver_code, amount, timestamp, channel (opcional)
```

Ejemplo:
```csv
sender_code,receiver_code,amount,timestamp,channel
ACC-0001,ACC-0002,450.00,2024-05-10T23:14:00,cash
ACC-0003,ACC-0002,380.00,2024-05-10T23:47:00,transfer
```

---

## Próximos pasos (post-hackathon)

- [ ] Autenticación JWT para analistas
- [ ] Migración a PostgreSQL
- [ ] Calibración de pesos con datos reales autorizados
- [ ] Integración con listas OFAC/PEP
- [ ] Exportación de reportes ROS (Reporte de Operación Sospechosa)

---

*NEXO Risk detecta la red. La decisión final es siempre humana.*
