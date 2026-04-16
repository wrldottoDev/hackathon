import { useEffect, useState } from "react";
import { bankRequest, formatCurrency, formatDate } from "../api";
import { useAnalysisAuth } from "../auth";

export default function OverviewPage() {
  const { token, selectedBank } = useAnalysisAuth();
  const [summary, setSummary] = useState(null);
  const [alerts, setAlerts] = useState([]);
  const [usersCount, setUsersCount] = useState(0);
  const [error, setError] = useState("");

  useEffect(() => {
    let active = true;

    Promise.all([
      bankRequest(selectedBank.apiUrl, "/risk/summary", { token }),
      bankRequest(selectedBank.apiUrl, "/risk/alerts", { token }),
      bankRequest(selectedBank.apiUrl, "/users", { token }),
    ])
      .then(([summaryPayload, alertsPayload, usersPayload]) => {
        if (!active) {
          return;
        }
        setSummary(summaryPayload);
        setAlerts(alertsPayload);
        setUsersCount(usersPayload.length);
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
          <p className="eyebrow">Resumen</p>
          <h2>Monitoreo de {selectedBank.label}</h2>
        </div>
        <p className="page-copy">
          Vista consolidada del banco conectado para priorizar alertas y revisar actividad sospechosa.
        </p>
      </header>

      {error ? <p className="form-error">{error}</p> : null}

      <div className="metric-grid">
        <article className="metric-card accent">
          <span>Total alertas</span>
          <strong>{summary?.total_alerts ?? 0}</strong>
        </article>
        <article className="metric-card">
          <span>High</span>
          <strong>{summary?.high ?? 0}</strong>
        </article>
        <article className="metric-card">
          <span>Medium</span>
          <strong>{summary?.medium ?? 0}</strong>
        </article>
        <article className="metric-card">
          <span>Clientes visibles</span>
          <strong>{usersCount}</strong>
        </article>
      </div>

      <div className="two-column-grid">
        <article className="panel">
          <div className="panel-header">
            <h3>Últimas alertas</h3>
            <span>{alerts.length} registros</span>
          </div>
          <div className="detail-list">
            {alerts.slice(0, 6).map((alert) => (
              <div className="detail-item" key={alert.id}>
                <div>
                  <p>{alert.reason}</p>
                  <span>{formatDate(alert.created_at)}</span>
                </div>
                <div className="detail-item-side">
                  <span className={`risk-pill ${alert.level}`}>{alert.level}</span>
                  <strong>{formatCurrency(alert.transaction_amount || 0)}</strong>
                </div>
              </div>
            ))}
            {!alerts.length ? <p className="empty-state">No hay alertas todavía.</p> : null}
          </div>
        </article>

        <article className="panel">
          <div className="panel-header">
            <h3>Distribución de riesgo</h3>
            <span>{selectedBank.label}</span>
          </div>
          <div className="summary-grid">
            <div>
              <small>Low</small>
              <strong>{summary?.low ?? 0}</strong>
            </div>
            <div>
              <small>Medium</small>
              <strong>{summary?.medium ?? 0}</strong>
            </div>
            <div>
              <small>High</small>
              <strong>{summary?.high ?? 0}</strong>
            </div>
          </div>
          <p className="empty-state analytics-note">
            Agrega nuevos bancos en <code>analytics/src/banks.js</code> para usar esta misma consola con más instancias.
          </p>
        </article>
      </div>
    </section>
  );
}
