import { useEffect, useState } from "react";
import { apiRequest, formatCurrency, formatDate } from "../api";
import { useAuth } from "../auth";

export default function RiskPage() {
  const { token } = useAuth();
  const [summary, setSummary] = useState(null);
  const [alerts, setAlerts] = useState([]);
  const [error, setError] = useState("");

  useEffect(() => {
    let active = true;

    Promise.all([
      apiRequest("/risk/summary", { token }),
      apiRequest("/risk/alerts", { token }),
    ])
      .then(([summaryData, alertData]) => {
        if (!active) {
          return;
        }
        setSummary(summaryData);
        setAlerts(alertData);
      })
      .catch((loadError) => {
        if (active) {
          setError(loadError.message);
        }
      });

    return () => {
      active = false;
    };
  }, [token]);

  return (
    <section className="page">
      <header className="page-header">
        <div>
          <p className="eyebrow">Riesgo</p>
          <h2>Alertas y scoring</h2>
        </div>
        <p className="page-copy">
          Reglas simples para demo: monto alto, structuring, repetición y movimiento rápido de fondos.
        </p>
      </header>

      {error ? <p className="form-error">{error}</p> : null}

      <div className="metric-grid">
        <article className="metric-card">
          <span>Total alertas</span>
          <strong>{summary?.total_alerts ?? 0}</strong>
        </article>
        <article className="metric-card">
          <span>Low</span>
          <strong>{summary?.low ?? 0}</strong>
        </article>
        <article className="metric-card">
          <span>Medium</span>
          <strong>{summary?.medium ?? 0}</strong>
        </article>
        <article className="metric-card accent">
          <span>High</span>
          <strong>{summary?.high ?? 0}</strong>
        </article>
      </div>

      <article className="panel">
        <div className="panel-header">
          <h3>Últimas alertas</h3>
          <span>Ordenadas por fecha</span>
        </div>
        <div className="table-wrapper">
          <table>
            <thead>
              <tr>
                <th>Nivel</th>
                <th>Score</th>
                <th>Cuenta</th>
                <th>Monto</th>
                <th>Razón</th>
                <th>Fecha</th>
              </tr>
            </thead>
            <tbody>
              {alerts.map((alert) => (
                <tr key={alert.id}>
                  <td>
                    <span className={`risk-pill ${alert.level}`}>{alert.level}</span>
                  </td>
                  <td>{alert.score}</td>
                  <td>{alert.account_number || alert.account_id || "-"}</td>
                  <td>{alert.transaction_amount ? formatCurrency(alert.transaction_amount) : "-"}</td>
                  <td>{alert.reason}</td>
                  <td>{formatDate(alert.created_at)}</td>
                </tr>
              ))}
            </tbody>
          </table>
          {!alerts.length ? <p className="empty-state">No se han generado alertas todavía.</p> : null}
        </div>
      </article>
    </section>
  );
}
