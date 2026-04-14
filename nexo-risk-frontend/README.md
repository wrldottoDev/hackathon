# NEXO Risk — Frontend

Dashboard de inteligencia financiera para el analista de cumplimiento.

## Stack

- React 18 + Vite
- Recharts (gráfico de distribución)
- D3 v7 (grafo de relaciones)
- Lucide React (iconos)

## Arrancar en desarrollo

```bash
npm install
npm run dev
# → http://localhost:3000
```

El proxy de Vite redirige `/api` → `http://localhost:8000`  
→ El backend de FastAPI debe estar corriendo antes de abrir el frontend.

## Flujo de demo

1. Abrir **http://localhost:3000**
2. Click **"Generar datos"** → seed de cuentas y transacciones sintéticas
3. Click **"Analizar todo"** → scoring batch de todas las cuentas
4. Ver los casos en la tabla ordenados por score
5. Click en cualquier fila → ver detalle de señales + recomendación
6. Usar **"Escalar", "Revisado" o "Descartar"** como analista
7. Click **"Ver grafo"** → visualización D3 de relaciones entre cuentas

## Build de producción

```bash
npm run build
# → dist/ listo para servir
```
