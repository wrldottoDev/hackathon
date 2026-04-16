import { useEffect, useState } from "react";
import { bankRequest, formatCurrency, formatDate } from "../api";
import { useAnalysisAuth } from "../auth";

export default function AlertsPage() {
  const { token, selectedBank } = useAnalysisAuth();
  const [summary, setSummary] = useState(null);
  const [alerts, setAlerts] = useState([]);
  const [error, setError] = useState("");

  useEffect(() => {
    let active = true;

    Promise.all([
      bankRequest(selectedBank.apiUrl, "/risk/summary", { token }),
      bankRequest(selectedBank.apiUrl, "/risk/alerts", { token }),
    ])
      .then(([summaryPayload, alertsPayload]) => {
        if (!active) {
          return;
        }
        setSummary(summaryPayload);
        setAlerts(alertsPayload);
      })
      .catch((loadError) => {
        if (active) {
          setError(loadError.message);
        }
      });

    return () => {
      active = false;
    };
  }, [selectedBank.apiUrl, token]);

  return (
    <section className="page">
      <header className="page-header">
        <div>
          <p className="eyebrow">Alertas</p>
          <h2>Alertas de {selectedBank.label}</h2>
        </div>
        <p className="page-copy">
          Lista completa de alertas generadas por el motor heurístico del banco seleccionado.
        </p>
      </header>

      {error ? <p className="form-error">{error}</p> : null}

      <div className="metric-grid">
        <article className="metric-card">
          <span>Total</span>
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
          <h3>Listado completo</h3>
          <span>{alerts.length} alertas</span>
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
                  <td><span className={`risk-pill ${alert.level}`}>{alert.level}</span></td>
                  <td>{alert.score}</td>
                  <td>{alert.account_number || alert.account_id || "-"}</td>
                  <td>{alert.transaction_amount ? formatCurrency(alert.transaction_amount) : "-"}</td>
                  <td>{alert.reason}</td>
                  <td>{formatDate(alert.created_at)}</td>
                </tr>
              ))}
            </tbody>
          </table>
          {!alerts.length ? <p className="empty-state">No hay alertas registradas.</p> : null}
        </div>
      </article>
    </section>
  );
}
